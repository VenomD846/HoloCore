"""Safe removal of legacy HoloCore output from a project root."""
from __future__ import annotations

import shutil
from pathlib import Path

DIRECTORIES = (".holocore", "holocore-out", "graphify-out")
MARKER_FILES = ("HOLOCORE.md", "HOLOCORE-START-HERE.md", "GEMINI.md", "CLAUDE.md", "AGENTS.md")


def _is_generated_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return "HoloCore" in text or "holocore" in text.lower()


def find_legacy(root: str | Path) -> list[Path]:
    root = Path(root).expanduser().resolve()
    found = [root / name for name in DIRECTORIES if (root / name).is_dir()]
    found.extend(root / name for name in MARKER_FILES if (root / name).is_file() and _is_generated_file(root / name))
    for name in (".mcp.json",):
        path = root / name
        if path.is_file() and _is_generated_file(path): found.append(path)
    return sorted(set(found), key=lambda p: (len(p.parts), str(p).casefold()))


def cleanup_legacy(root: str | Path, *, apply: bool = False) -> dict[str, object]:
    root = Path(root).expanduser().resolve()
    candidates = find_legacy(root)
    removed: list[str] = []
    if apply:
        for path in candidates:
            if path.is_dir(): shutil.rmtree(path)
            elif path.is_file(): path.unlink()
            removed.append(str(path))
    return {"root": str(root), "dry_run": not apply, "candidates": [str(p) for p in candidates], "removed": removed}

