"""Canonical HoloCore AI command definitions and platform renderers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CommandDefinition:
    name: str
    description: str
    invocation: str
    write: bool = False

    @property
    def slug(self) -> str:
        return f"holocore-{self.name.replace(' ', '-')}"


COMMANDS: tuple[CommandDefinition, ...] = (
    CommandDefinition("init", "Initialize HoloCore in the current project.", "holocore init $ARGUMENTS", True),
    CommandDefinition("search", "Search curated, structural, and episodic knowledge.", 'holocore search "$ARGUMENTS"'),
    CommandDefinition("remember", "Store a scoped episodic memory.", 'holocore remember "$ARGUMENTS"', True),
    CommandDefinition("recall", "Recall scoped episodic history.", 'holocore recall "$ARGUMENTS"'),
    CommandDefinition("atlas-refresh", "Refresh the native Atlas graph.", "holocore atlas-refresh", True),
    CommandDefinition("atlas-view", "Generate and open the self-contained Atlas HTML view.", "holocore atlas-view $ARGUMENTS"),
    CommandDefinition("archive-search", "Search the curated Archive.", 'holocore archive-search "$ARGUMENTS"'),
    CommandDefinition("archive-create", "Create an explicit, AI-first Archive note.", "holocore archive-create $ARGUMENTS", True),
    CommandDefinition("status", "Show HoloCore subsystem and freshness status.", "holocore status"),
    CommandDefinition("doctor", "Run read-only HoloCore diagnostics.", "holocore doctor"),
)
COMMAND_DEFINITIONS = COMMANDS


def get_command(name: str) -> CommandDefinition:
    normalized = name.removeprefix("holocore-").replace(" ", "-")
    for command in COMMANDS:
        if command.name == normalized:
            return command
    raise KeyError(name)


def _markdown(command: CommandDefinition, platform: str) -> str:
    safety = "This command may write project data; confirm the requested scope before running it." if command.write else "This is a read-only operation."
    return (
        "---\n"
        f"description: {command.description}\n"
        "---\n\n"
        f"# {command.slug}\n\n{command.description}\n\n"
        f"{safety}\n\nRun the following from the project root and return its output:\n\n"
        f"```text\n{command.invocation}\n```\n\n"
        f"Arguments supplied by the user: `$ARGUMENTS`\n"
    )


def render_claude_command(command: CommandDefinition | str) -> str:
    return _markdown(get_command(command) if isinstance(command, str) else command, "claude")


def render_cursor_command(command: CommandDefinition | str) -> str:
    return _markdown(get_command(command) if isinstance(command, str) else command, "cursor")


def render_gemini_command(command: CommandDefinition | str) -> str:
    return _markdown(get_command(command) if isinstance(command, str) else command, "gemini")


def render_opencode_command(command: CommandDefinition | str) -> str:
    return _markdown(get_command(command) if isinstance(command, str) else command, "opencode")


def render_codex_skill(command: CommandDefinition | str) -> str:
    item = get_command(command) if isinstance(command, str) else command
    return (
        "---\n"
        f"name: {item.slug}\n"
        f"description: {item.description}\n"
        "---\n\n"
        f"# {item.slug}\n\n{_markdown(item, 'codex').split('---\n\n', 1)[1]}"
    )


def _files(prefix: str, renderer, commands: Iterable[CommandDefinition] = COMMANDS) -> dict[str, str]:
    return {f"{prefix}/{item.slug}.md": renderer(item) for item in commands}


def render_claude_commands() -> dict[str, str]:
    return _files(".claude/commands", render_claude_command)


def render_cursor_commands() -> dict[str, str]:
    return _files(".cursor/commands", render_cursor_command)


def render_gemini_commands() -> dict[str, str]:
    return _files(".gemini/commands", render_gemini_command)


def render_opencode_commands() -> dict[str, str]:
    return _files(".opencode/commands", render_opencode_command)


def render_codex_skills() -> dict[str, str]:
    return {f".agents/skills/{item.slug}/SKILL.md": render_codex_skill(item) for item in COMMANDS}


def render_all_commands() -> dict[str, dict[str, str]]:
    return {
        "claude": render_claude_commands(), "cursor": render_cursor_commands(),
        "gemini": render_gemini_commands(), "opencode": render_opencode_commands(),
        "codex": render_codex_skills(),
    }


__all__ = [
    "CommandDefinition", "COMMANDS", "COMMAND_DEFINITIONS", "get_command",
    "render_claude_command", "render_cursor_command", "render_gemini_command",
    "render_opencode_command", "render_codex_skill", "render_claude_commands",
    "render_cursor_commands", "render_gemini_commands", "render_opencode_commands",
    "render_codex_skills", "render_all_commands",
]
