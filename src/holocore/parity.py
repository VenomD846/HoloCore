"""Compatibility and generated-interface parity diagnostics.

This module deliberately consumes the existing registries; it does not own a
second command or MCP definition.  That keeps drift checks useful in release
tests without making parity code another source of truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .commands import COMMANDS, render_all_commands


PLATFORMS = ("claude", "cursor", "gemini", "opencode", "codex")


@dataclass(frozen=True)
class ParityIssue:
    surface: str
    item: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"surface": self.surface, "item": self.item, "detail": self.detail}


def _command_names() -> set[str]:
    return {command.name for command in COMMANDS}


def _generated_names(files: dict[str, str], platform: str) -> set[str]:
    suffix = ".toml" if platform == "gemini" else ".md"
    names: set[str] = set()
    for path in files:
        # Codex files are one directory deeper and are named SKILL.md.
        if platform == "codex":
            parent = Path(path).parent.name
            if Path(path).name == "SKILL.md" and parent.startswith("holocore-"):
                names.add(parent.removeprefix("holocore-"))
            continue
        filename = Path(path).name
        if filename.startswith("holocore-") and filename.endswith(suffix):
            names.add(filename[len("holocore-") : -len(suffix)])
    return names


def _mcp_snapshot() -> tuple[dict[str, dict[str, Any]], set[str]]:
    # Lazy import avoids importing the MCP server for normal CLI use.
    from .mcp_server import PROMPTS, TOOLS

    tools = {str(item["name"]): item for item in TOOLS}
    prompts = {str(item["name"]) for item in PROMPTS}
    return tools, prompts


def compatibility_matrix() -> dict[str, Any]:
    """Return the stable CLI/generated/MCP compatibility matrix.

    The matrix is intentionally JSON-friendly so it can be printed by release
    checks or embedded in CI artifacts without a custom serializer.
    """
    tools, prompts = _mcp_snapshot()
    command_names = sorted(_command_names())
    generated = render_all_commands()
    return {
        "cli": command_names,
        "generated": {
            platform: sorted(_generated_names(files, platform))
            for platform, files in generated.items()
        },
        "mcp": {
            "prompts": sorted(prompts),
            "tools": sorted(tools),
        },
    }


def diagnose_parity() -> dict[str, Any]:
    """Diagnose interface drift without mutating the repository."""
    matrix = compatibility_matrix()
    expected = set(matrix["cli"])
    issues: list[ParityIssue] = []

    for platform in PLATFORMS:
        actual = set(matrix["generated"].get(platform, []))
        for name in sorted(expected - actual):
            issues.append(ParityIssue(platform, name, "missing generated interface"))
        for name in sorted(actual - expected):
            issues.append(ParityIssue(platform, name, "orphan generated interface"))

    prompts = set(matrix["mcp"]["prompts"])
    for name in sorted(expected - prompts):
        issues.append(ParityIssue("mcp-prompts", name, "missing MCP prompt"))
    for name in sorted(prompts - expected):
        issues.append(ParityIssue("mcp-prompts", name, "orphan MCP prompt"))

    # MCP tools are an operation surface, not a one-to-one copy of CLI
    # commands.  Check the expected prefix and schema shape here, while the
    # command/prompt parity above remains exact.
    tools, _ = _mcp_snapshot()
    for name, tool in tools.items():
        if not name.startswith("holocore_"):
            issues.append(ParityIssue("mcp-tools", name, "tool is outside HoloCore namespace"))
        if tool.get("inputSchema", {}).get("type") != "object":
            issues.append(ParityIssue("mcp-tools", name, "tool schema is not an object"))

    return {
        "ok": not issues,
        "matrix": matrix,
        "issues": [issue.as_dict() for issue in issues],
    }


def assert_parity() -> dict[str, Any]:
    """Return diagnostics or raise an assertion with actionable drift."""
    report = diagnose_parity()
    if not report["ok"]:
        details = "; ".join(
            f"{item['surface']}:{item['item']} ({item['detail']})"
            for item in report["issues"]
        )
        raise AssertionError(f"HoloCore interface drift: {details}")
    return report


__all__ = ["PLATFORMS", "ParityIssue", "compatibility_matrix", "diagnose_parity", "assert_parity"]
