"""Promote existing text sources into deduplicated Markdown Archive entries."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .archive import Archive, ArchiveConflictError

SKIP = {".git", ".obsidian", ".holocore", "holocore-out", "graphify-out", "node_modules", "raw", "wiki", "Archive"}
EXTENSIONS = {".md", ".txt", ".rst", ".html"}


def promote_sources(source: str | Path, destination: str | Path) -> dict[str, Any]:
    root = Path(source).expanduser().resolve()
    vault = Archive(destination)
    vault.init_vault()
    created: list[str] = []; skipped: list[str] = []; conflicts: list[str] = []
    for file in sorted(root.rglob("*")):
        if not file.is_file() or file.suffix.lower() not in EXTENSIONS:
            continue
        rel = file.relative_to(root)
        if any(part in SKIP for part in rel.parts) or file.stat().st_size > 200_000:
            continue
        digest = hashlib.sha256(file.read_bytes()).hexdigest()[:16]
        name = file.stem.replace("/", "-") + "--" + digest + ".md"
        target = Path("wiki") / name
        body = file.read_text(encoding="utf-8", errors="replace")
        note = {"type": "archive-entry", "date": __import__("datetime").date.today().isoformat(), "tags": ["promoted", "source"], "ai-first": True, "provenance": {"system": "holocore", "operation": "archive-promote", "source": str(file)}}
        try:
            result = vault.create(target, body, frontmatter=note)
            if result.get("created"):
                created.append(str(target))
            else:
                skipped.append(str(target))
        except ArchiveConflictError:
            skipped.append(str(target))
    return {"source": str(root), "destination": str(vault.vault), "created": created, "skipped": skipped, "conflicts": conflicts, "count": len(created), "one_way": True}
