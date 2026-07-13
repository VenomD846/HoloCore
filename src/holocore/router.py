from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .animus import Animus
from .archive import Archive
from .atlas import Atlas
from .config import Config
from .models import Result


class RouteLoopError(RuntimeError):
    """Raised when a unified search attempts to route back into itself."""


@dataclass(frozen=True)
class RoutePlan:
    """A checked, immutable execution plan for one unified search."""

    query: str
    world: str
    folders_ready: bool
    missing_paths: tuple[str, ...]
    atlas_state: str
    atlas_fresh: bool
    use_atlas: bool
    use_archive: bool
    use_animus: bool
    phases: tuple[str, ...]


_ROUTE_STACK: ContextVar[tuple[tuple[str, str], ...]] = ContextVar("holocore_route_stack", default=())


class Router:
    """Check-first router; selected subsystems execute once without recursion."""

    HISTORY = ("previous", "prior", "earlier", "error", "debug", "conversation", "history", "remember", "before", "again", "last time")

    def __init__(self, root: Path, config: Config | None = None):
        self.root = root.resolve()
        self.config = config or Config.load(root=self.root)
        self.archive = Archive(self.config.vault)
        self.atlas = Atlas(self.root, self.config.atlas_path)
        self.animus = Animus(self.config.animus_path)
        self.animus.create_world(self.root.name)
        for sector in ("general", "project", "conversations"):
            self.animus.create_sector(self.root.name, sector)
        self.last_plan: RoutePlan | None = None

    def plan(self, query: str, world: str | None = None) -> RoutePlan:
        """Check required folders and Atlas freshness before building a read route."""
        scope = world or self.root.name
        required_paths = (self.config.state_dir, self.config.vault)
        missing_paths = tuple(str(path) for path in required_paths if not path.is_dir())
        atlas_status = self.atlas.freshness()
        q = query.casefold()
        plan = RoutePlan(
            query=query,
            world=scope,
            folders_ready=not missing_paths,
            missing_paths=missing_paths,
            atlas_state=str(atlas_status.get("state", "unknown")),
            atlas_fresh=bool(atlas_status.get("fresh")),
            use_atlas=bool(atlas_status.get("fresh")),
            use_archive=True,
            use_animus=any(term in q for term in self.HISTORY),
            phases=("check", "atlas", "archive", "animus", "sources"),
        )
        self.last_plan = plan
        return plan

    @staticmethod
    def _expanded_query(query: str, hits: list[dict[str, Any]], fields: tuple[str, ...]) -> str:
        """Add bounded graph/note context while preserving one downstream call."""
        parts = [query]
        for hit in hits[:5]:
            for field in fields:
                value = str(hit.get(field, "")).strip()
                if value:
                    parts.append(value)
        return " ".join(dict.fromkeys(parts))

    def search(self, query: str, world: str | None = None) -> list[Result]:
        scope = world or self.root.name
        route_key = (query.casefold(), scope.casefold())
        stack = _ROUTE_STACK.get()
        if route_key in stack:
            raise RouteLoopError(f"recursive HoloCore route rejected for query: {query}")
        token = _ROUTE_STACK.set((*stack, route_key))
        try:
            plan = self.plan(query, scope)
            results: list[Result] = []
            if not plan.folders_ready:
                results.append(Result("CHECK", "Required folders missing", "Run holocore init before relying on project knowledge.", "; ".join(plan.missing_paths)))
            atlas_hits: list[dict[str, Any]] = []
            if plan.use_atlas:
                atlas_hits = self.atlas.search(query)
                for hit in atlas_hits:
                    results.append(Result("ATLAS", hit.get("label", hit["id"]), hit.get("kind", "signal"), hit.get("source_file", "")))
            else:
                results.append(Result("CHECK", f"Atlas {plan.atlas_state}", "Run atlas-refresh before relying on structural context.", str(self.atlas.output)))

            archive_query = self._expanded_query(query, atlas_hits, ("label", "qualified_name", "source_file"))
            archive_hits = self.archive.search(archive_query)
            for hit in archive_hits:
                results.append(Result("ARCHIVE", hit["title"], hit["snippet"], hit["path"]))

            if plan.use_animus:
                memory_query = self._expanded_query(archive_query, archive_hits, ("title", "path"))
                for hit in self.animus.search(memory_query, world=scope):
                    source = hit.provenance[0].source_ref if hit.provenance else ""
                    results.append(Result("ANIMUS", f"Memory Shard {hit.id}", hit.content, source))
            return results
        finally:
            _ROUTE_STACK.reset(token)


__all__ = ["RouteLoopError", "RoutePlan", "Router"]
