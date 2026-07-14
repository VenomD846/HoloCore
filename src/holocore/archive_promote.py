"""AI-first, deterministic promotion of source material into a World wiki."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .llm import MemoryProvider, provider_from_config
from .memory_pipeline import MemoryExtraction

SKIP = {
    ".agents", ".claude", ".codex", ".cursor", ".gemini", ".git", ".next",
    ".obsidian", ".opencode", ".holocore", "holocore-out", "graphify-out",
    "node_modules", "raw", "wiki", "Archive", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".venv", "venv", "build", "dist",
}
SKIP_CASEFOLD = frozenset(part.casefold() for part in SKIP)
EXTENSIONS = {".md", ".txt", ".rst", ".html", ".htm"}
MANAGED = "<!-- holocore:managed-archive-entry -->"
INDEX_START = "<!-- holocore:managed-wiki-index:start -->"
INDEX_END = "<!-- holocore:managed-wiki-index:end -->"


def _slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return result[:72].rstrip("-") or "archive-entry"


def _title(path: Path, text: str) -> str:
    heading = next((m.group(1).strip() for line in text.splitlines() if (m := re.match(r"^#\s+(.+?)\s*$", line))), "")
    return heading or re.sub(r"[-_]+", " ", path.stem).strip().title() or "Archive Entry"


def _plain_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if path.suffix.casefold() in {".html", ".htm"}:
        text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"[ \t]+", " ", text).strip()


def _source_id(root: Path, path: Path) -> str:
    relative = path.relative_to(root).as_posix().casefold()
    return hashlib.sha256(relative.encode("utf-8")).hexdigest()[:20]


def _render_note(
    *, title: str, source: Path, root: Path, source_id: str, source_hash: str,
    world: str, extraction: MemoryExtraction, mode: str,
) -> str:
    provenance = {
        "system": "holocore", "operation": "archive-promote", "source": str(source),
        "source_id": source_id, "source_hash": source_hash,
        "source_mtime": datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(),
        "world": world, "promotion_mode": mode,
    }
    tags = ["archive-entry", *[_slug(item) for item in extraction.entities[:5]]]
    lines = [
        "---", "type: archive-entry", "ai-first: true",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        f"source_id: {source_id}", f"source_hash: {source_hash}",
        f"tags: {json.dumps(list(dict.fromkeys(tags)), ensure_ascii=False)}",
        f"provenance: {json.dumps(provenance, ensure_ascii=False, sort_keys=True)}",
        "---", "", MANAGED, f"# {title}", "",
        "Related: [[system/index|World Archive index]]", "", "## Summary", "",
        extraction.summary.strip() or "No reliable summary was extracted.",
    ]
    for heading, values in (
        ("Facts", extraction.facts[:12]), ("Decisions", extraction.decisions[:8]),
        ("Preferences", extraction.preferences[:8]), ("Entities", extraction.entities[:12]),
    ):
        cleaned = list(dict.fromkeys(value.strip() for value in values if value.strip()))
        if cleaned:
            lines.extend(["", f"## {heading}", "", *[f"- {value}" for value in cleaned]])
    lines.extend(["", "## Provenance", "", f"- Source: `{source}`", f"- Relative source: `{source.relative_to(root).as_posix()}`", f"- SHA-256: `{source_hash}`", ""])
    return "\n".join(lines)


def _update_index(vault: Path, entries: list[tuple[str, str]], *, dry_run: bool) -> bool:
    index = vault / "system" / "index.md"
    existing = index.read_text(encoding="utf-8-sig", errors="replace") if index.exists() else "# World Archive\n"
    block = "\n".join([INDEX_START, "## Generated Archive Entries", "", *[f"- [[{path[:-3]}|{title}]]" for title, path in sorted(entries)], INDEX_END])
    pattern = re.compile(re.escape(INDEX_START) + r".*?" + re.escape(INDEX_END), re.S)
    updated = pattern.sub(block, existing) if pattern.search(existing) else existing.rstrip() + "\n\n" + block + "\n"
    if updated == existing:
        return False
    if not dry_run:
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(updated, encoding="utf-8")
    return True


def promote_sources(
    source: str | Path,
    destination: str | Path,
    *,
    scope: str = "docs",
    summarize: bool = True,
    dry_run: bool = False,
    world: str = "world",
    llm: Mapping[str, Any] | None = None,
    provider: MemoryProvider | None = None,
) -> dict[str, Any]:
    root = Path(source).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(root)
    vault = Path(destination).expanduser().resolve()
    candidates = [root] if root.is_file() else sorted(root.rglob("*"))
    created: list[str] = []; updated: list[str] = []; unchanged: list[str] = []
    conflicts: list[str] = []; excluded: list[str] = []; entries: list[tuple[str, str]] = []
    extractor = provider or provider_from_config(llm)
    base = root.parent if root.is_file() else root
    for path in candidates:
        if not path.is_file() or path.suffix.casefold() not in EXTENSIONS:
            continue
        relative = path.relative_to(base)
        if any(part.casefold() in SKIP_CASEFOLD for part in relative.parts) or path.stat().st_size > 500_000:
            excluded.append(relative.as_posix()); continue
        if scope == "docs" and root.is_dir() and len(relative.parts) > 1 and relative.parts[0].casefold() not in {"docs", "doc", "documentation", "notes"}:
            excluded.append(relative.as_posix()); continue
        text = _plain_text(path)
        if not text:
            excluded.append(relative.as_posix()); continue
        if len(relative.parts) == 1 and (
            text.startswith("# HoloCore Knowledge Policy")
            or text.startswith("# HoloCore — Start Here")
        ):
            excluded.append(relative.as_posix()); continue
        source_id = _source_id(base, path)
        source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        title = _title(path, text)
        extraction = MemoryExtraction.from_mapping(
            extractor.extract(
                [{"role": "user", "content": text[:100_000]}],
                instructions="Create a concise durable wiki entry. Extract only source-supported facts, decisions, preferences, and named entities.",
            ) if summarize else {"summary": text[:1200], "facts": [], "decisions": [], "preferences": [], "entities": []}
        )
        relative_target = f"wiki/{_slug(title)}--{source_id}.md"
        target = vault / relative_target
        content = _render_note(title=title, source=path, root=base, source_id=source_id, source_hash=source_hash, world=world, extraction=extraction, mode="local-ai" if summarize else "deterministic")
        entries.append((title, relative_target))
        if target.exists():
            current = target.read_text(encoding="utf-8-sig", errors="replace")
            if current == content:
                unchanged.append(relative_target)
            elif MANAGED not in current:
                conflicts.append(relative_target)
            else:
                updated.append(relative_target)
                if not dry_run:
                    target.write_text(content, encoding="utf-8")
        else:
            created.append(relative_target)
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
    index_updated = _update_index(vault, entries, dry_run=dry_run) if entries else False
    return {
        "source": str(root), "destination": str(vault), "scope": scope,
        "summarized": summarize, "dry_run": dry_run, "world": world,
        "created": created, "updated": updated, "unchanged": unchanged,
        "conflicts": conflicts, "excluded": excluded, "index_updated": index_updated,
        "count": len(created) + len(updated), "one_way": True,
    }
