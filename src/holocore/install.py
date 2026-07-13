from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .archive import Archive
from .commands import render_all_commands
from .layout import render_start_here, world_paths
from .policy import render_policy


@dataclass
class BootstrapReport:
    root: Path
    created: list[Path]
    skipped: list[Path]
    git: str
    updated: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "root": str(self.root),
            "created": [str(p) for p in self.created],
            "updated": [str(p) for p in self.updated],
            "skipped": [str(p) for p in self.skipped],
            "git": self.git,
            "paths": world_paths(self.root),
            "next_steps": [
                "Restart or reopen your AI client in this World.",
                "Claude Code: run /mcp once to approve HoloCore, then /holocore-search.",
                "Codex: invoke $holocore-search (project skills are in .agents/skills).",
                "Obsidian: open the top-level Archive folder as a vault (optional).",
            ],
            "warnings": self.warnings,
        }


def _mcp_server(root: Path) -> dict:
    # Using the exact Python environment is more reliable than assuming an AI
    # desktop/client inherited the shell PATH containing `holocore-mcp`.
    return {
        "command": str(Path(sys.executable).resolve()),
        "args": ["-m", "holocore.mcp_server"],
        "cwd": str(root),
    }


def _write_generated(target: Path, content: str, created: list[Path], updated: list[Path], skipped: list[Path]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text(content, encoding="utf-8")
        created.append(target)
    elif target.read_text(encoding="utf-8") != content:
        target.write_text(content, encoding="utf-8")
        updated.append(target)
    else:
        skipped.append(target)


def _merge_json(target: Path, patch: dict, created: list[Path], updated: list[Path], skipped: list[Path], warnings: list[str]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text(json.dumps(patch, indent=2), encoding="utf-8")
        created.append(target)
        return
    try:
        current = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        skipped.append(target)
        warnings.append(f"Could not merge invalid JSON in {target}: {exc}")
        return

    def merge(base: dict, incoming: dict) -> None:
        for key, value in incoming.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                merge(base[key], value)
            else:
                base[key] = value

    before = json.dumps(current, sort_keys=True)
    merge(current, patch)
    if json.dumps(current, sort_keys=True) == before:
        skipped.append(target)
    else:
        target.write_text(json.dumps(current, indent=2), encoding="utf-8")
        updated.append(target)


def _merge_codex_toml(target: Path, server: dict, created: list[Path], updated: list[Path], skipped: list[Path]) -> None:
    command = json.dumps(server["command"])
    args = json.dumps(server["args"])
    cwd = json.dumps(server["cwd"])
    block = f'[mcp_servers.holocore]\ncommand = {command}\nargs = {args}\ncwd = {cwd}\n'
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(block, encoding="utf-8")
        created.append(target)
        return
    original = target.read_text(encoding="utf-8")
    try:
        current = tomllib.loads(original).get("mcp_servers", {}).get("holocore", {})
        if current == server:
            skipped.append(target)
            return
    except tomllib.TOMLDecodeError:
        # Replace a recognizable HoloCore section even when an older generated
        # Windows path made that section invalid TOML.
        pass
    pattern = re.compile(r"(?ms)^\[mcp_servers\.holocore\]\s*\n.*?(?=^\[|\Z)")
    replacement = pattern.sub(lambda _match: block + "\n", original) if pattern.search(original) else original.rstrip() + "\n\n" + block
    if replacement == original:
        skipped.append(target)
    else:
        target.write_text(replacement, encoding="utf-8")
        updated.append(target)


def _merge_instructions(target: Path, instructions: str, created: list[Path], updated: list[Path], skipped: list[Path]) -> None:
    if not target.exists():
        target.write_text(instructions, encoding="utf-8")
        created.append(target)
        return
    original = target.read_text(encoding="utf-8")
    marker = "<!-- holocore:project-instructions -->"
    if marker in original or original == instructions:
        skipped.append(target)
        return
    addition = (
        f"\n\n{marker}\n## HoloCore project context\n\n"
        "Read `HOLOCORE.md` before project-context work. Use HoloCore's check-first route and never loop a result back into HoloCore.\n"
    )
    target.write_text(original.rstrip() + addition, encoding="utf-8")
    updated.append(target)


def _protect_private_state(root: Path, created: list[Path], updated: list[Path], skipped: list[Path]) -> None:
    target = root / ".gitignore"
    marker = "# HoloCore private conversation data"
    block = f"{marker}\n.holocore/raw-chats/\n.holocore/animus.db*\n"
    if not target.exists():
        target.write_text(block, encoding="utf-8")
        created.append(target)
        return
    original = target.read_text(encoding="utf-8")
    if marker in original:
        skipped.append(target)
    else:
        target.write_text(original.rstrip() + "\n\n" + block, encoding="utf-8")
        updated.append(target)


def bootstrap_project(project: Path, *, init_git: bool = True, platforms: list[str] | None = None) -> BootstrapReport:
    root = project.resolve()
    root.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    updated: list[Path] = []
    skipped: list[Path] = []
    warnings: list[str] = []
    selected = set(["codex", "claude", "gemini", "cursor", "opencode", "generic"] if platforms is None else platforms)
    server = _mcp_server(root)
    mcp = {"mcpServers": {"holocore": server}}
    instructions = render_policy()

    generated = {
        ".holocore/instructions.md": instructions,
        ".holocore/policy.md": instructions,
        ".holocore/mcp.json": json.dumps(mcp, indent=2),
        "HOLOCORE.md": instructions,
        "HOLOCORE-START-HERE.md": render_start_here(root),
    }
    for relative, content in generated.items():
        _write_generated(root / relative, content, created, updated, skipped)

    config_patch = {
        "version": 1,
        "world": root.name,
        "root": str(root),
        "archive": str(root / "Archive"),
        "state_dir": str(root / ".holocore"),
    }
    _merge_json(root / ".holocore/config.json", config_patch, created, updated, skipped, warnings)

    if "codex" in selected:
        _merge_instructions(root / "AGENTS.md", instructions, created, updated, skipped)
        _merge_codex_toml(root / ".codex/config.toml", server, created, updated, skipped)
    if "claude" in selected:
        _merge_instructions(root / "CLAUDE.md", instructions, created, updated, skipped)
        _merge_json(root / ".mcp.json", mcp, created, updated, skipped, warnings)
    if "gemini" in selected:
        _merge_instructions(root / "GEMINI.md", instructions, created, updated, skipped)
        _merge_json(root / ".gemini/settings.json", mcp, created, updated, skipped, warnings)
    if "cursor" in selected:
        _merge_json(root / ".cursor/mcp.json", mcp, created, updated, skipped, warnings)
        _write_generated(root / ".cursor/rules/holocore.mdc", instructions, created, updated, skipped)
    if "opencode" in selected:
        _merge_json(
            root / "opencode.json",
            {"mcp": {"holocore": {"type": "local", "command": [server["command"], *server["args"]], "cwd": str(root)}}},
            created, updated, skipped, warnings,
        )

    for platform, command_files in render_all_commands().items():
        if platform in selected:
            for relative, content in command_files.items():
                _write_generated(root / relative, content, created, updated, skipped)

    _protect_private_state(root, created, updated, skipped)

    archive = root / "Archive"
    archive_existed = archive.exists()
    archive_report = Archive(archive).init_vault()
    if not archive_existed:
        created.append(archive)
    created.extend(archive / relative for relative in archive_report["created"])
    raw_chats = root / ".holocore" / "raw-chats"
    if not raw_chats.exists():
        raw_chats.mkdir(parents=True)
        created.append(raw_chats)

    git = "skipped"
    if init_git and not (root / ".git").exists():
        try:
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
            git = "created"
        except (OSError, subprocess.CalledProcessError):
            git = "unavailable"
    elif (root / ".git").exists():
        git = "existing"
    return BootstrapReport(root, created, skipped, git, updated, warnings)


def bootstrap(project: Path, *, init_git: bool = True, platforms: list[str] | None = None) -> dict:
    return bootstrap_project(project, init_git=init_git, platforms=platforms).as_dict()
