from __future__ import annotations

import json
from pathlib import Path

from .policy import render_policy


PLATFORMS = {
    "codex": ".agents/skills/holocore/SKILL.md",
    "claude": ".claude/commands/holocore.md",
    "gemini": ".gemini/commands/holocore.md",
    "cursor": ".cursor/rules/holocore.mdc",
    "opencode": ".opencode/commands/holocore.md",
    "generic": "HOLOCORE.md",
}


def instruction_text(platform: str) -> str:
    return render_policy(platform.title())


def mcp_config(command: str = "holocore-mcp") -> dict:
    return {"mcpServers": {"holocore": {"command": command, "args": []}}}


def install_platform_links(project: Path, platforms: list[str]) -> dict[str, list[str]]:
    created, skipped = [], []
    for platform in platforms:
        relative = PLATFORMS[platform]; target = project / relative
        if target.exists(): skipped.append(str(target)); continue
        target.parent.mkdir(parents=True, exist_ok=True); target.write_text(instruction_text(platform), encoding="utf-8"); created.append(str(target))
    mcp = project / ".holocore" / "mcp.json"
    if mcp.exists(): skipped.append(str(mcp))
    else: mcp.parent.mkdir(parents=True, exist_ok=True); mcp.write_text(json.dumps(mcp_config(), indent=2), encoding="utf-8"); created.append(str(mcp))
    return {"created": created, "skipped": skipped}
