"""HoloCore upgrade and registered-World reconciliation workflows."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from .home import HomeManager
from .install import bootstrap_project


REPOSITORY = "https://github.com/VenomD846/HoloCore.git"


def sync_all(home: Path | None = None) -> dict[str, Any]:
    manager = HomeManager(home)
    listing = manager.list_worlds()
    results: list[dict[str, Any]] = []
    for world in listing["worlds"]:
        root = Path(str(world.get("root", ""))).expanduser()
        if not root.is_dir():
            results.append({"id": world.get("id"), "root": str(root), "updated": False, "reason": "missing-world"})
            continue
        try:
            report = bootstrap_project(root, init_git=False, home=manager.home)
            from .engine import HoloCoreEngine

            atlas = HoloCoreEngine(root).ensure_atlas()
            results.append({
                "id": report.world_id,
                "root": str(root.resolve()),
                "updated": True,
                "files_changed": len(report.created) + len(report.updated),
                "atlas": atlas,
            })
        except Exception as exc:
            results.append({"id": world.get("id"), "root": str(root), "updated": False, "reason": str(exc)})
    return {
        "home": str(manager.home),
        "worlds": results,
        "count": len(results),
        "updated": sum(1 for item in results if item["updated"]),
        "failed": sum(1 for item in results if not item["updated"]),
    }


def update_install(home: Path | None = None, *, repository: str = REPOSITORY) -> dict[str, Any]:
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError("uv is required for self-update. Install uv, then run `holocore update` again.")
    command = [uv, "tool", "install", "--force", f"git+{repository}"]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return {
        "updated": True,
        "command": command,
        "installer_output": completed.stdout.strip(),
        "reconciliation": sync_all(home),
    }


__all__ = ["REPOSITORY", "sync_all", "update_install"]
