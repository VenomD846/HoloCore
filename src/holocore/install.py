from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from .commands import render_all_commands


@dataclass
class BootstrapReport:
    root: Path
    created: list[Path]
    skipped: list[Path]
    git: str

    def as_dict(self): return {"root": str(self.root), "created": [str(p) for p in self.created], "skipped": [str(p) for p in self.skipped], "git": self.git}


def bootstrap_project(project: Path, *, init_git: bool = True, platforms: list[str] | None = None) -> BootstrapReport:
    root = project.resolve(); root.mkdir(parents=True, exist_ok=True); created: list[Path] = []; skipped: list[Path] = []
    selected = set(platforms or ["codex", "claude", "gemini", "cursor", "opencode", "generic"])
    mcp = {"mcpServers": {"holocore": {"command": "holocore-mcp", "args": [], "cwd": str(root)}}}
    instructions = "# HoloCore\n\nUse HoloCore Archive, Atlas, and Animus through `holocore` or `holocore-mcp`. Writes must be explicit and scoped.\n"
    files: dict[str, str] = {
        ".holocore/config.json": json.dumps({"version": 1, "world": root.name, "root": str(root), "archive": str(root / "Archive"), "state_dir": str(root / ".holocore")}, indent=2),
        ".holocore/instructions.md": instructions,
        ".holocore/mcp.json": json.dumps(mcp, indent=2),
        "HOLOCORE.md": instructions,
    }
    if "codex" in selected: files.update({"AGENTS.md": instructions, ".codex/config.toml": f'[mcp_servers.holocore]\ncommand = "holocore-mcp"\ncwd = "{root}"\n'})
    if "claude" in selected: files.update({"CLAUDE.md": instructions, ".mcp.json": json.dumps(mcp, indent=2)})
    if "gemini" in selected: files.update({"GEMINI.md": instructions, ".gemini/settings.json": json.dumps(mcp, indent=2)})
    if "cursor" in selected: files.update({".cursor/mcp.json": json.dumps(mcp, indent=2), ".cursor/rules/holocore.mdc": instructions})
    if "opencode" in selected: files["opencode.json"] = json.dumps({"mcp": {"holocore": {"type": "local", "command": ["holocore-mcp"], "cwd": str(root)}}}, indent=2)
    rendered = render_all_commands()
    for platform, command_files in rendered.items():
        if platform in selected: files.update(command_files)
    for relative, content in files.items():
        target = root / relative
        if target.exists(): skipped.append(target); continue
        target.parent.mkdir(parents=True, exist_ok=True); target.write_text(content, encoding="utf-8"); created.append(target)
    archive = root / "Archive"
    if not archive.exists(): archive.mkdir(); created.append(archive)
    git = "skipped"
    if init_git and not (root / ".git").exists():
        try: subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True); git = "created"
        except (OSError, subprocess.CalledProcessError): git = "unavailable"
    elif (root / ".git").exists(): git = "existing"
    return BootstrapReport(root, created, skipped, git)


def bootstrap(project: Path, *, init_git: bool = True, platforms: list[str] | None = None) -> dict:
    return bootstrap_project(project, init_git=init_git, platforms=platforms).as_dict()
