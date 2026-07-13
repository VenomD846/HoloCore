from __future__ import annotations

from pathlib import Path

from .config import Config
from .install import bootstrap
from .llm import provider_from_config
from .memory_pipeline import MemoryRefinementPipeline
from .models import Result
from .router import Router


class HoloCoreEngine:
    """The single HoloCore runtime: wiki, graph, memory, install, CLI and MCP."""

    def __init__(self, root: Path, config: Config | None = None):
        self.root = root.resolve(); self.router = Router(self.root, config); self._cache: dict[tuple[str, str | None], list[Result]] = {}

    def initialize(self, *, git: bool = True, platforms: list[str] | None = None) -> dict: return bootstrap(self.root, init_git=git, platforms=platforms)
    def search(self, query: str, world: str | None = None) -> list[Result]:
        key = (query, world)
        if key not in self._cache: self._cache[key] = self.router.search(query, world)
        return self._cache[key]
    def status(self) -> dict:
        return {"world": str(self.root), "archive": self.router.archive.health(), "atlas": self.router.atlas.freshness(), "animus": self.router.animus.status(self.root.name)}
    def refresh(self) -> dict:
        graph = self.router.atlas.refresh(); self._cache.clear()
        return {"path": str(self.router.atlas.output), "nodes": len(graph.get("nodes", [])), "edges": len(graph.get("links", graph.get("edges", []))), "fresh": True}
    def mine(self, world: Path | None = None, sector: str = "project") -> dict:
        root = (world or self.root).resolve(); added = deduplicated = 0
        for path in root.rglob("*"):
            if not path.is_file() or any(part in {".git", ".holocore", ".venv", "__pycache__", "engines", "graphify-out"} for part in path.parts): continue
            try: content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError): continue
            shard = self.router.animus.ingest(content, world=self.root.name, sector=sector, source_ref=str(path))
            added += int(not shard.deduplicated); deduplicated += int(shard.deduplicated)
        return {"added": added, "deduplicated": deduplicated}
    def remember(self, content: str, sector: str = "general", source: str = "") -> dict:
        shard = self.router.animus.ingest(content, world=self.root.name, sector=sector, source_ref=source or "manual"); self._cache.clear(); return {"id": shard.id, "created": shard.action == "inserted", "deduplicated": shard.action in {"deduplicated", "unchanged"}, "action": shard.action}
    def ingest_chat(self, messages: list[dict[str, str]], *, sector: str = "conversations", source: str = "chat", custom_instructions: str = "") -> dict:
        settings = self.router.config.llm or {}
        result = MemoryRefinementPipeline(self.router.animus, self.router.config.state_dir / "raw-chats", provider_from_config(settings)).refine(messages, world=self.root.name, sector=sector, source_ref=source, instructions=custom_instructions or str(settings.get("custom_instructions", "")))
        self._cache.clear(); return {"raw_chat": str(result.audit_path), "shard_ids": [item.id for item in result.shards], "extracted": result.extraction.__dict__}
