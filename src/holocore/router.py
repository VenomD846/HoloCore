from __future__ import annotations

from pathlib import Path

from .animus import Animus
from .archive import Archive
from .atlas import Atlas
from .config import Config
from .models import Result


class Router:
    """Native one-pass router; every selected subsystem runs at most once."""

    STRUCTURE = ("file", "function", "class", "import", "dependency", "code", "graph", "path", "affected")
    HISTORY = ("previous", "prior", "earlier", "error", "debug", "conversation", "history", "remember")

    def __init__(self, root: Path, config: Config | None = None):
        self.root = root.resolve(); self.config = config or Config.load(root=self.root)
        self.archive = Archive(self.config.vault); self.atlas = Atlas(self.root, self.config.atlas_path); self.animus = Animus(self.config.animus_path)
        self.animus.create_world(self.root.name)
        for sector in ("general", "project", "conversations"):
            self.animus.create_sector(self.root.name, sector)

    def search(self, query: str, world: str | None = None) -> list[Result]:
        q = query.casefold(); results: list[Result] = []
        for hit in self.archive.search(query): results.append(Result("ARCHIVE", hit["title"], hit["snippet"], hit["path"]))
        if any(term in q for term in self.STRUCTURE):
            for hit in self.atlas.search(query): results.append(Result("ATLAS", hit.get("label", hit["id"]), hit.get("kind", "signal"), hit.get("source_file", "")))
        if any(term in q for term in self.HISTORY):
            for hit in self.animus.search(query, world=world or self.root.name):
                source = hit.provenance[0].source_ref if hit.provenance else ""
                results.append(Result("ANIMUS", f"Memory Shard {hit.id}", hit.content, source))
        return results
