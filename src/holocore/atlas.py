"""Standard-library, HoloCore-native structural Atlas."""

from __future__ import annotations

import ast
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import tokenize
from typing import Any, Iterable, Iterator, Mapping
import unicodedata


ATLAS_VERSION = "1"
DEFAULT_AFFECTED_RELATIONS = frozenset(
    {"calls", "imports", "imports_from", "inherits", "references", "uses"}
)
_EXCLUDES = frozenset(
    {
        ".git", ".hg", ".svn", ".holocore", ".mypy_cache", ".pytest_cache", ".ruff_cache",
        ".tox", ".venv", "__pycache__", "build", "dist", "graphify-out",
        "node_modules", "venv",
    }
)


def content_hash(content: bytes | str | os.PathLike[str]) -> str:
    """Return location-independent SHA-256 for *content*."""
    if isinstance(content, os.PathLike):
        content = Path(content).read_bytes()
    elif isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _key(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"[^\w./:-]+", "_", value, flags=re.UNICODE)
    return re.sub(r"_+", "_", value).strip("_")


def _file_id(relative: str) -> str:
    return f"file:{_key(relative)}"


def _symbol_id(relative: str, qualified: str) -> str:
    return f"symbol:{_key(relative)}:{_key(qualified)}"


def _module(relative: str) -> str:
    parts = list(PurePosixPath(relative).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _edge(source: str, target: str, relation: str, owner: str, line: int = 1) -> dict[str, Any]:
    return {
        "source": source, "target": target, "relation": relation,
        "source_file": owner, "source_location": f"L{line}",
        "confidence": "EXTRACTED",
    }


def _dotted(node: ast.AST) -> str | None:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return ".".join(reversed(parts))


class _PyVisitor(ast.NodeVisitor):
    def __init__(self, relative: str, digest: str, module: str, aliases: Mapping[str, str]):
        self.relative, self.digest, self.module = relative, digest, module
        self.aliases = aliases
        self.file_id = _file_id(relative)
        self.scopes: list[tuple[str, str, str]] = []
        self.nodes: list[dict[str, Any]] = []
        self.edges: list[dict[str, Any]] = []
        self.references: list[dict[str, Any]] = []

    def _owner(self) -> str:
        return self.scopes[-1][1] if self.scopes else self.file_id

    def _qualname(self, name: str) -> str:
        return ".".join([scope[0] for scope in self.scopes] + [name])

    def _symbol(self, node: ast.AST, name: str, kind: str) -> tuple[str, str]:
        qualname = self._qualname(name)
        node_id = _symbol_id(self.relative, qualname)
        self.nodes.append({
            "id": node_id,
            "label": name if kind == "class" else f"{name}()",
            "kind": kind, "type": kind, "file_type": "code", "language": "python",
            "qualified_name": f"{self.module}.{qualname}".strip("."),
            "source_file": self.relative,
            "source_location": f"L{getattr(node, 'lineno', 1)}",
            "content_hash": self.digest, "confidence": "EXTRACTED",
        })
        relation = "method" if self.scopes and self.scopes[-1][2] == "class" and kind == "function" else "contains"
        self.edges.append(_edge(self._owner(), node_id, relation, self.relative, getattr(node, "lineno", 1)))
        return qualname, node_id

    def _target(self, node: ast.AST) -> str | None:
        dotted = _dotted(node)
        if not dotted:
            return None
        parts = dotted.split(".")
        if parts[0] in {"self", "cls"}:
            classes = [scope[0] for scope in self.scopes if scope[2] == "class"]
            return ".".join([self.module, *classes, *parts[1:]]).strip(".") if classes else None
        if parts[0] in self.aliases:
            return ".".join([self.aliases[parts[0]], *parts[1:]])
        if len(parts) == 1:
            # Prefer the nearest lexical scope, then resolution falls back to module/global.
            parents = [scope[0] for scope in self.scopes[:-1]]
            return ".".join([self.module, *parents, parts[0]]).strip(".")
        return dotted

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        _, node_id = self._symbol(node, node.name, "class")
        for base in node.bases:
            target = self._target(base)
            if target:
                self.references.append({"source": node_id, "target": target, "relation": "inherits", "line": node.lineno})
        self.scopes.append((node.name, node_id, "class"))
        self.generic_visit(node)
        self.scopes.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function(node)

    def _function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        _, node_id = self._symbol(node, node.name, "function")
        self.scopes.append((node.name, node_id, "function"))
        self.generic_visit(node)
        self.scopes.pop()

    def visit_Call(self, node: ast.Call) -> None:
        target = self._target(node.func)
        if target:
            self.references.append({"source": self._owner(), "target": target, "relation": "calls", "line": node.lineno})
        self.generic_visit(node)


class Atlas:
    """Incremental structural graph and in-process query facade."""

    def __init__(
        self,
        root: str | os.PathLike[str],
        output: str | os.PathLike[str] | None = None,
        *,
        exclude: Iterable[str] = (),
    ) -> None:
        self.root = Path(root).expanduser().resolve()
        destination = Path(output) if output is not None else Path("graphify-out") / "graph.json"
        self.graph_path = destination if destination.is_absolute() else self.root / destination
        # Native runtime compatibility path; graph_path remains the public
        # node-link output contract used by structural tooling.
        self.output = self.root / ".holocore" / "atlas.json"
        self.exclude = _EXCLUDES | frozenset(exclude)
        self._graph: dict[str, Any] | None = None

    def refresh(self) -> dict[str, Any]:
        previous = self._read(missing_ok=True)
        old_files = previous.get("graph", {}).get("files", {}) if previous else {}
        current = self._snapshot()
        records: dict[str, dict[str, Any]] = {}
        reused = extracted = 0
        for relative, info in current.items():
            old = old_files.get(relative)
            if (
                isinstance(old, dict)
                and old.get("content_hash") == info["content_hash"]
                and old.get("extractor_version") == ATLAS_VERSION
                and isinstance(old.get("fragment"), dict)
            ):
                records[relative] = {**old, **info}
                reused += 1
            else:
                records[relative] = {**info, **self._extract(relative, info["content_hash"])}
                extracted += 1

        nodes, links = self._assemble(records)
        deleted = sorted(set(old_files) - set(current))
        generated = _now()
        digest = self._source_digest(current)
        files = {
            relative: {
                "content_hash": record["content_hash"], "size": record["size"],
                "mtime_ns": record["mtime_ns"], "language": record.get("language", "generic"),
                "module": record.get("module", ""), "extractor_version": ATLAS_VERSION,
                "fragment": record["fragment"],
            }
            for relative, record in sorted(records.items())
        }
        stats = {
            "files": len(files), "nodes": len(nodes), "links": len(links),
            "edges": len(links), "extracted": extracted, "reused": reused,
            "deleted": len(deleted),
        }
        graph = {
            "directed": True, "multigraph": False,
            "graph": {
                "schema_version": 1, "atlas_version": ATLAS_VERSION,
                "generator": "holocore-atlas",
                "source_root": str(self.root), "generated_at": generated,
                "hash_algorithm": "sha256", "source_digest": digest, "files": files,
                "freshness": {"state": "fresh", "checked_at": generated, "source_digest": digest},
                "extracted_files": extracted, "reused_files": reused,
                "deleted_files": len(deleted),
                "stats": stats,
            },
            "nodes": nodes, "links": links,
        }
        self._write(graph)
        if self.output != self.graph_path:
            self._write(graph, destination=self.output)
        self._graph = graph
        return graph

    update = refresh
    build = refresh

    def load_graph(self) -> dict[str, Any]:
        if self._graph is None:
            self._graph = self._read()
        return self._graph

    def _load(self) -> dict[str, Any]:  # compatibility
        if not self.graph_path.exists():
            self.refresh()
        return self.load_graph()

    def freshness(self) -> dict[str, Any]:
        checked = _now()
        if not self.graph_path.is_file():
            return {"state": "missing", "fresh": False, "checked_at": checked, "changed": [], "deleted": []}
        graph = self._read()
        saved = graph.get("graph", {}).get("files", {})
        current = self._snapshot()
        changed = sorted(path for path, info in current.items() if path not in saved or saved[path].get("content_hash") != info["content_hash"])
        deleted = sorted(set(saved) - set(current))
        state = "fresh" if not changed and not deleted else "stale"
        return {
            "state": state, "fresh": state == "fresh", "checked_at": checked,
            "generated_at": graph.get("graph", {}).get("generated_at"),
            "source_digest": self._source_digest(current),
            "saved_source_digest": graph.get("graph", {}).get("source_digest"),
            "changed": changed, "deleted": deleted, "files": len(current),
        }

    status = freshness

    def is_current(self) -> bool:
        return bool(self.freshness()["fresh"])

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        terms = [_key(term) for term in re.findall(r"[\w./:-]+", query, flags=re.UNICODE)]
        if not terms or limit <= 0:
            return []
        found: list[tuple[int, str, dict[str, Any]]] = []
        for node in self.load_graph().get("nodes", []):
            label = _key(str(node.get("label", "")))
            qualified = _key(str(node.get("qualified_name", "")))
            source = _key(str(node.get("source_file", "")))
            node_id = _key(str(node.get("id", "")))
            score = sum(
                (8 if term == label else 0) + (5 if term in label else 0)
                + (3 if term in qualified else 0) + (2 if term in source else 0)
                + (1 if term in node_id else 0)
                for term in terms
            )
            if score:
                found.append((score, str(node["id"]), node))
        found.sort(key=lambda item: (-item[0], item[1]))
        return [dict(node, score=score) for score, _, node in found[:limit]]

    def resolve(self, query: str) -> str | None:
        nodes = self.load_graph().get("nodes", [])
        if any(str(node.get("id")) == query for node in nodes):
            return query
        normalized = unicodedata.normalize("NFKC", query).casefold().rstrip("/\\")
        labels = [node for node in nodes if str(node.get("label", "")).casefold().rstrip("()") == normalized.rstrip("()")]
        if len(labels) == 1:
            return str(labels[0]["id"])
        sources = [node for node in nodes if str(node.get("source_file", "")).casefold() == normalized and node.get("kind") == "file"]
        if len(sources) == 1:
            return str(sources[0]["id"])
        qualified = [node for node in nodes if str(node.get("qualified_name", "")).casefold() == normalized]
        if len(qualified) == 1:
            return str(qualified[0]["id"])
        partial = [node for node in nodes if normalized in str(node.get("label", "")).casefold()]
        return str(partial[0]["id"]) if len(partial) == 1 else None

    def shortest_path(self, source: str, target: str, *, max_depth: int | None = None) -> dict[str, Any] | None:
        source_id, target_id = self.resolve(source), self.resolve(target)
        if source_id is None or target_id is None:
            return None
        graph = self.load_graph()
        outgoing: dict[str, list[tuple[str, dict[str, Any]]]] = {}
        for link in graph.get("links", graph.get("edges", [])):
            outgoing.setdefault(str(link["source"]), []).append((str(link["target"]), link))
        queue: deque[str] = deque([source_id])
        previous: dict[str, tuple[str, dict[str, Any]] | None] = {source_id: None}
        depths = {source_id: 0}
        while queue:
            current = queue.popleft()
            if current == target_id:
                break
            if max_depth is not None and depths[current] >= max_depth:
                continue
            for neighbor, link in sorted(outgoing.get(current, []), key=lambda pair: pair[0]):
                if neighbor not in previous:
                    previous[neighbor] = (current, link)
                    depths[neighbor] = depths[current] + 1
                    queue.append(neighbor)
        if target_id not in previous:
            return None
        ids, path_links, cursor = [target_id], [], target_id
        while previous[cursor] is not None:
            parent, link = previous[cursor]  # type: ignore[misc]
            ids.append(parent)
            path_links.append(dict(link))
            cursor = parent
        ids.reverse(); path_links.reverse()
        by_id = {str(node["id"]): node for node in graph.get("nodes", [])}
        return {
            "source": source_id, "target": target_id, "depth": len(path_links),
            "nodes": [dict(by_id[node_id]) for node_id in ids], "links": path_links,
        }

    query_path = shortest_path

    def path(self, source: str, target: str, *, max_depth: int | None = None) -> list[dict[str, Any]]:
        """Return the ordered nodes on a directed shortest path."""
        result = self.shortest_path(source, target, max_depth=max_depth)
        return [] if result is None else result["nodes"]

    def affected(
        self,
        query: str,
        *,
        depth: int = 2,
        relations: Iterable[str] = DEFAULT_AFFECTED_RELATIONS,
    ) -> list[dict[str, Any]]:
        seed = self.resolve(query)
        if seed is None or depth < 1:
            return []
        graph = self.load_graph()
        incoming: dict[str, list[tuple[str, dict[str, Any]]]] = {}
        outgoing: dict[str, list[tuple[str, dict[str, Any]]]] = {}
        for link in graph.get("links", graph.get("edges", [])):
            source, target = str(link["source"]), str(link["target"])
            incoming.setdefault(target, []).append((source, link))
            outgoing.setdefault(source, []).append((target, link))
        allowed, seen = set(relations), {seed}
        queue: deque[tuple[str, int]] = deque([(seed, 0)])
        # Class/member seeding keeps callers bound to methods visible.
        for member, link in outgoing.get(seed, []):
            if link.get("relation") in {"method", "contains"} and member not in seen:
                seen.add(member); queue.append((member, 0))
        hits: list[tuple[str, int, str]] = []
        while queue:
            current, current_depth = queue.popleft()
            if current_depth >= depth:
                continue
            for source, link in incoming.get(current, []):
                relation = str(link.get("relation", ""))
                if relation in allowed and source not in seen:
                    seen.add(source); hits.append((source, current_depth + 1, relation))
                    queue.append((source, current_depth + 1))
        by_id = {str(node["id"]): node for node in graph.get("nodes", [])}
        relation_rank = {"calls": 0, "inherits": 1, "references": 2, "uses": 3, "imports_from": 4, "imports": 5}
        hits.sort(key=lambda hit: (hit[1], relation_rank.get(hit[2], 99), hit[0]))
        return [dict(by_id[node_id], depth=level, via_relation=relation) for node_id, level, relation in hits]

    affected_nodes = affected

    def _snapshot(self) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        if not self.root.is_dir():
            return result
        output = self.graph_path.resolve()
        for path in self._files():
            try:
                if path.resolve() == output:
                    continue
                raw, stat = path.read_bytes(), path.stat()
                relative = path.relative_to(self.root).as_posix()
            except (OSError, ValueError):
                continue
            result[relative] = {"content_hash": content_hash(raw), "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
        return dict(sorted(result.items()))

    def _files(self) -> Iterator[Path]:
        for directory, dirnames, filenames in os.walk(self.root):
            dirnames[:] = sorted(name for name in dirnames if name not in self.exclude)
            base = Path(directory)
            for name in sorted(filenames):
                path = base / name
                if name not in self.exclude and path.is_file():
                    yield path

    def _extract(self, relative: str, digest: str) -> dict[str, Any]:
        path = self.root / PurePosixPath(relative)
        python = path.suffix.casefold() == ".py"
        file_node = {
            "id": _file_id(relative), "label": PurePosixPath(relative).name,
            "kind": "file", "type": "file", "file_type": "code" if python else "generic",
            "language": "python" if python else "generic", "source_file": relative,
            "source_location": "L1", "content_hash": digest, "confidence": "EXTRACTED",
        }
        if python:
            return self._extract_python(path, relative, digest, file_node)
        return self._extract_generic(path, relative, digest, file_node)

    def _extract_python(self, path: Path, relative: str, digest: str, file_node: dict[str, Any]) -> dict[str, Any]:
        module = _module(relative)
        fragment: dict[str, Any] = {"nodes": [file_node], "edges": [], "references": []}
        try:
            with tokenize.open(path) as handle:
                tree = ast.parse(handle.read(), filename=relative)
        except (OSError, SyntaxError, UnicodeError) as exc:
            file_node["parse_error"] = f"{type(exc).__name__}: {exc}"
            return {"language": "python", "module": module, "fragment": fragment}
        aliases: dict[str, str] = {}
        imports: list[dict[str, Any]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    aliases[alias.asname or alias.name.split(".")[0]] = alias.name
                    imports.append({"source": file_node["id"], "target": alias.name, "relation": "imports", "line": node.lineno})
            elif isinstance(node, ast.ImportFrom) and node.module:
                base = "." * node.level + node.module
                for alias in node.names:
                    target = base if alias.name == "*" else f"{base}.{alias.name}"
                    if alias.name != "*":
                        aliases[alias.asname or alias.name] = target
                    imports.append({"source": file_node["id"], "target": target, "relation": "imports_from", "line": node.lineno})
        visitor = _PyVisitor(relative, digest, module, aliases)
        visitor.visit(tree)
        fragment["nodes"].extend(visitor.nodes)
        fragment["edges"].extend(visitor.edges)
        fragment["references"].extend(imports + visitor.references)
        return {"language": "python", "module": module, "fragment": fragment}

    def _extract_generic(self, path: Path, relative: str, digest: str, file_node: dict[str, Any]) -> dict[str, Any]:
        fragment: dict[str, Any] = {"nodes": [file_node], "edges": [], "references": []}
        try:
            raw = path.read_bytes()
        except OSError:
            return {"language": "generic", "module": "", "fragment": fragment}
        if b"\0" in raw[:8192]:
            file_node["binary"] = True
            return {"language": "generic", "module": "", "fragment": fragment}
        text = raw.decode("utf-8", errors="replace")
        if path.suffix.casefold() not in {".md", ".markdown"}:
            file_node["line_count"] = text.count("\n") + (1 if text else 0)
            return {"language": "generic", "module": "", "fragment": fragment}
        file_node["language"] = "markdown"
        occurrences: dict[str, int] = {}
        for line_number, line in enumerate(text.splitlines(), 1):
            heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
            if heading:
                label = heading.group(1).strip()
                anchor = re.sub(r"[^\w]+", "-", label.casefold()).strip("-") or "section"
                occurrences[anchor] = occurrences.get(anchor, 0) + 1
                node_id = f"section:{_key(relative)}:{_key(anchor)}:{occurrences[anchor]}"
                fragment["nodes"].append({
                    "id": node_id, "label": label, "kind": "section", "type": "section",
                    "file_type": "generic", "language": "markdown", "source_file": relative,
                    "source_location": f"L{line_number}", "content_hash": digest, "confidence": "EXTRACTED",
                })
                fragment["edges"].append(_edge(file_node["id"], node_id, "contains", relative, line_number))
            for link in re.finditer(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)", line):
                target = link.group(1).strip()
                if "://" not in target and not target.startswith(("mailto:", "#")):
                    fragment["references"].append({"source": file_node["id"], "target": target, "relation": "references", "line": line_number})
        return {"language": "markdown", "module": "", "fragment": fragment}

    def _assemble(self, records: Mapping[str, Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        nodes: dict[str, dict[str, Any]] = {}
        links: list[dict[str, Any]] = []
        references: list[tuple[str, Mapping[str, Any]]] = []
        module_files: dict[str, str] = {}
        symbols: dict[str, list[str]] = {}
        terminals: dict[str, list[str]] = {}
        for relative, record in records.items():
            fragment = record["fragment"]
            for node in fragment.get("nodes", []):
                nodes[str(node["id"])] = dict(node)
                qualified = str(node.get("qualified_name", ""))
                if qualified:
                    symbols.setdefault(qualified, []).append(str(node["id"]))
                    terminals.setdefault(qualified.rsplit(".", 1)[-1], []).append(str(node["id"]))
            links.extend(dict(link) for link in fragment.get("edges", []))
            references.extend((relative, reference) for reference in fragment.get("references", []))
            if record.get("module"):
                module_files[str(record["module"])] = _file_id(relative)
        for relative, reference in references:
            target = self._resolve_reference(relative, str(reference["target"]), records, module_files, symbols, terminals)
            if target and str(reference["source"]) in nodes and target in nodes:
                links.append(_edge(str(reference["source"]), target, str(reference["relation"]), relative, int(reference.get("line", 1))))
        unique = {
            (str(link["source"]), str(link["target"]), str(link.get("relation", "")), str(link.get("source_file", "")), str(link.get("source_location", ""))): link
            for link in links
        }
        return [nodes[key] for key in sorted(nodes)], [unique[key] for key in sorted(unique)]

    def _resolve_reference(
        self,
        relative: str,
        target: str,
        records: Mapping[str, Mapping[str, Any]],
        module_files: Mapping[str, str],
        symbols: Mapping[str, list[str]],
        terminals: Mapping[str, list[str]],
    ) -> str | None:
        module = str(records[relative].get("module", ""))
        if target.startswith("."):
            level = len(target) - len(target.lstrip("."))
            suffix = target[level:]
            target = ".".join([*module.split(".")[:-level], suffix]).strip(".")
        candidates = [target]
        if module and not target.startswith(module + "."):
            candidates.append(f"{module}.{target}")
            package = module.rsplit(".", 1)[0] if "." in module else ""
            if package:
                candidates.append(f"{package}.{target}")
        for candidate in candidates:
            if len(symbols.get(candidate, [])) == 1:
                return symbols[candidate][0]
            if candidate in module_files:
                return module_files[candidate]
            prefix = candidate
            while "." in prefix:
                prefix = prefix.rsplit(".", 1)[0]
                if prefix in module_files:
                    return module_files[prefix]
        terminal = target.rsplit(".", 1)[-1]
        if len(terminals.get(terminal, [])) == 1:
            return terminals[terminal][0]
        # Relative Markdown/file reference.
        candidate_path = (PurePosixPath(relative).parent / PurePosixPath(target)).as_posix()
        normalized = os.path.normpath(candidate_path).replace("\\", "/")
        return _file_id(normalized) if normalized in records else None

    @staticmethod
    def _source_digest(snapshot: Mapping[str, Mapping[str, Any]]) -> str:
        digest = hashlib.sha256()
        for relative, info in sorted(snapshot.items()):
            digest.update(relative.encode("utf-8") + b"\0" + str(info["content_hash"]).encode("ascii") + b"\n")
        return digest.hexdigest()

    def _read(self, *, missing_ok: bool = False) -> dict[str, Any]:
        try:
            data = json.loads(self.graph_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            if missing_ok:
                return {}
            raise
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Cannot read Atlas graph {self.graph_path}: {exc}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("nodes", []), list):
            raise RuntimeError(f"Invalid Atlas graph at {self.graph_path}")
        if "links" not in data and "edges" in data:
            data = {**data, "links": data["edges"]}
        return data

    def _write(self, graph: Mapping[str, Any], *, destination: Path | None = None) -> None:
        destination = destination or self.graph_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        fd, temporary = tempfile.mkstemp(prefix="atlas-", suffix=".tmp", dir=destination.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload); handle.flush(); os.fsync(handle.fileno())
            os.replace(temporary, destination)
        except Exception:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise


# Keep the public name introduced by the concurrent prototype while making it
# use the complete native implementation.
AtlasStore = Atlas

__all__ = ["Atlas", "AtlasStore", "ATLAS_VERSION", "DEFAULT_AFFECTED_RELATIONS", "content_hash"]
