"""Explicit, conflict-aware promotion of verified notes into a World wiki."""
from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any


def promote_entry(source: str | Path, world_archive: str | Path, *, destination: str | None = None, overwrite: bool = False) -> dict[str, Any]:
    source_path, archive = Path(source).resolve(), Path(world_archive).resolve()
    if not source_path.is_file(): raise FileNotFoundError(source_path)
    content = source_path.read_text(encoding="utf-8")
    relative = destination or f"wiki/{source_path.stem}.md"
    target = archive / relative
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    existed = target.exists()
    if existed:
        existing = target.read_text(encoding="utf-8")
        if hashlib.sha256(existing.encode("utf-8")).hexdigest() == digest:
            return {"status": "unchanged", "path": str(target), "sha256": digest}
        if not overwrite:
            return {"status": "conflict", "path": str(target), "source": str(source_path), "sha256": digest}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"status": "updated" if existed else "promoted", "path": str(target), "sha256": digest}


__all__ = ["promote_entry"]
