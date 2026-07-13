"""Human-facing World layout and onboarding helpers."""
from __future__ import annotations

from pathlib import Path
import json
import tomllib

from .config import Config


def world_paths(root: Path, config: Config | None = None) -> dict[str, str]:
    root = root.resolve()
    config = config or Config.load(root=root)
    return {
        "world": str(root),
        "start_here": str(root / "HOLOCORE-START-HERE.md"),
        "archive": str(config.vault),
        "archive_inbox": str(config.vault / "Inbox"),
        "archive_entries": str(config.vault / "wiki"),
        "archive_index": str(config.vault / "system" / "index.md"),
        "atlas_json": str(config.atlas_path),
        "atlas_html": str(config.state_dir / "atlas.html"),
        "memory_shards": str(config.animus_path),
        "raw_chats": str(config.state_dir / "raw-chats"),
        "runtime": str(config.state_dir),
        "claude_mcp": str(root / ".mcp.json"),
        "claude_commands": str(root / ".claude" / "commands"),
        "codex_mcp": str(root / ".codex" / "config.toml"),
        "codex_skills": str(root / ".agents" / "skills"),
    }


def render_start_here(root: Path) -> str:
    root = root.resolve()
    return f"""# HoloCore — Start Here

This folder is one **World**: `{root.name}`.

## Where everything lives

| What | Location | What it does |
|---|---|---|
| Archive | `Archive/` | Visible Obsidian-ready knowledge vault |
| Archive Inbox | `Archive/Inbox/` | Notes waiting to be polished |
| Archive Entries | `Archive/wiki/` | Verified, durable knowledge |
| Archive index | `Archive/system/index.md` | Starting map for the knowledge vault |
| Atlas JSON | `.holocore/atlas.json` | Machine-readable structural map |
| Atlas HTML | `.holocore/atlas.html` | Interactive graph for people and AI tools |
| Memory Shards | `.holocore/animus.db` | Searchable remembered history in SQLite |
| Raw chat audit | `.holocore/raw-chats/` | Original chats retained for traceability |

`Archive/` is deliberately visible. In Obsidian, choose **Open folder as vault** and select:

`{root / 'Archive'}`

Obsidian is optional; HoloCore and connected AI clients can read the Markdown directly.

## Connect an AI client

Run `holocore connect` from this World, then restart or reopen the project in your AI client.

- Claude Code: run `/mcp` to approve/check HoloCore, then use `/holocore-search`.
- Codex: use `$holocore-search`; project skills live in `.agents/skills/`.
- Any MCP client: connect the generated `holocore` stdio server and call its tools.

Run `holocore paths` at any time to print every absolute location, or `holocore doctor` to check the connection.
"""


def format_paths(paths: dict[str, str]) -> str:
    labels = {
        "world": "World (project root)",
        "archive": "Archive (Obsidian vault)",
        "archive_inbox": "Archive Inbox",
        "archive_entries": "Archive Entries",
        "archive_index": "Archive index",
        "atlas_json": "Atlas machine graph",
        "atlas_html": "Atlas visual graph",
        "memory_shards": "Memory Shards database",
        "raw_chats": "Raw chat audit",
        "start_here": "Start-here guide",
        "claude_mcp": "Claude MCP config",
        "claude_commands": "Claude slash commands",
        "codex_mcp": "Codex MCP config",
        "codex_skills": "Codex skills",
        "runtime": "HoloCore runtime",
    }
    return "\n".join(f"{labels.get(key, key):27} {value}" for key, value in paths.items())


def integration_status(root: Path) -> dict[str, dict[str, object]]:
    root = root.resolve()

    def json_mcp(path: Path, key: str = "mcpServers") -> tuple[bool, str]:
        if not path.exists():
            return False, "configuration missing"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return ("holocore" in data.get(key, {}), "connected" if "holocore" in data.get(key, {}) else "HoloCore entry missing")
        except (OSError, json.JSONDecodeError) as exc:
            return False, f"invalid JSON: {exc}"

    claude_ok, claude_detail = json_mcp(root / ".mcp.json")
    codex_path = root / ".codex" / "config.toml"
    try:
        codex_data = tomllib.loads(codex_path.read_text(encoding="utf-8")) if codex_path.exists() else {}
        codex_ok = "holocore" in codex_data.get("mcp_servers", {})
        codex_detail = "connected" if codex_ok else "configuration or HoloCore entry missing"
    except (OSError, tomllib.TOMLDecodeError) as exc:
        codex_ok, codex_detail = False, f"invalid TOML: {exc}"
    return {
        "claude": {
            "connected": claude_ok,
            "detail": claude_detail,
            "config": str(root / ".mcp.json"),
            "slash_commands": len(list((root / ".claude" / "commands").glob("holocore-*.md"))),
            "skills": len(list((root / ".claude" / "skills").glob("holocore-*/SKILL.md"))),
        },
        "codex": {
            "connected": codex_ok,
            "detail": codex_detail,
            "config": str(codex_path),
            "skills": len(list((root / ".agents" / "skills").glob("holocore-*/SKILL.md"))),
        },
    }
