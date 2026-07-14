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
        "world_id": config.world_id or root.name,
        "home": str(config.home or root),
        "shared_brain": str((config.home / "Archive") if config.home else config.vault),
        "worlds_registry": str((config.home / "worlds.json") if config.home else root / ".holocore" / "worlds.json"),
        "start_here": str(root / "HOLOCORE-START-HERE.md"),
        "archive": str((config.home / "Archive") if config.home else config.vault),
        "world_archive": str(config.vault),
        "shared_archive": str(config.shared_archive or config.vault),
        "ingest_inbox": str(((config.home / "Archive" / "Inbox" / str(config.world_id or root.name)) if config.home else root / "Archive" / "Inbox")),
        "raw_sources": str(config.vault / "raw"),
        "archive_inbox": str(config.vault / "Inbox"),
        "archive_entries": str(config.vault / "wiki"),
        "archive_index": str(config.vault / "system" / "index.md"),
        "atlas_json": str(root / "graphify-out" / "graph.json"),
        "atlas_html": str(root / "graphify-out" / "atlas.html"),
        "atlas_runtime": str(config.atlas_path),
        "memory_shards": str(config.animus_path),
        "raw_chats": str(config.raw_chats_path),
        "runtime": str(config.state_dir),
        "claude_mcp": str(root / ".mcp.json"),
        "claude_commands": str(root / ".claude" / "commands"),
        "claude_hooks": str(root / ".claude" / "settings.json"),
        "codex_mcp": str(root / ".codex" / "config.toml"),
        "codex_hooks": str(root / ".codex" / "hooks.json"),
        "codex_skills": str(root / ".agents" / "skills"),
    }


def render_start_here(root: Path, config: Config | None = None) -> str:
    root = root.resolve()
    config = config or Config.load(root=root)
    paths = world_paths(root, config)
    return f"""# HoloCore — Start Here

This folder is one **World**: `{root.name}`.

## Where everything lives

| What | Location | What it does |
|---|---|---|
| HoloCore Home | `{paths['home']}` | Shared home used by every registered project |
| Shared second brain | `{paths['archive']}` | One visible Obsidian-ready knowledge vault |
| This World's Archive | `{paths['world_archive']}` | Durable knowledge scoped to this project |
| Shared Archive Entries | `{paths['shared_archive']}` | Knowledge intentionally shared across projects |
| Source Inbox | `{paths['ingest_inbox']}` | Drop files here; HoloCore ingests new content on the next search or AI capture hook |
| Immutable raw sources | `{paths['raw_sources']}` | Content-addressed originals retained for audit and reprocessing |
| Atlas JSON | `graphify-out/graph.json` | Machine-readable structural map (`.holocore/atlas.json` remains a compatibility copy) |
| Atlas HTML | `graphify-out/atlas.html` | Interactive graph for people and AI tools (`.holocore/atlas.html` remains a compatibility copy) |
| Memory Shards | `.holocore/animus.db` | Searchable remembered history in SQLite |
| Raw chat audit | `.holocore/raw-chats/` | Original chats retained for traceability |

The shared Archive is deliberately visible. In Obsidian, choose **Open folder as vault** and select:

`{paths['archive']}`

Obsidian is optional; HoloCore and connected AI clients can read the Markdown directly.

## Connect an AI client

Setup registers this World with the same shared brain and installs its AI connections. Run `holocore connect` to repair them.

- Claude Code: run `/mcp` to approve/check HoloCore, then use `/holocore-search`.
- Codex: use `$holocore-search`; project skills live in `.agents/skills/`.
- Any MCP client: connect the generated `holocore` stdio server and call its tools.

Conversations are captured automatically at supported client hook points, useful shards are promoted into this World's Archive, and Atlas refreshes before search when source files changed. Run `holocore paths` at any time to print every absolute location, or `holocore doctor` to check the connection.
"""


def format_paths(paths: dict[str, str]) -> str:
    labels = {
        "world": "World (project root)",
        "world_id": "World ID",
        "home": "HoloCore Home",
        "shared_brain": "Shared brain (Obsidian vault)",
        "worlds_registry": "Registered Worlds",
        "archive": "Archive (Obsidian vault)",
        "world_archive": "This World's Archive",
        "shared_archive": "Shared Archive Entries",
        "ingest_inbox": "Automatic source Inbox",
        "raw_sources": "Immutable raw sources",
        "archive_inbox": "Archive Inbox",
        "archive_entries": "Archive Entries",
        "archive_index": "Archive index",
        "atlas_json": "Atlas machine graph",
        "atlas_html": "Atlas visual graph",
        "atlas_runtime": "Atlas runtime mirror",
        "memory_shards": "Memory Shards database",
        "raw_chats": "Raw chat audit",
        "start_here": "Start-here guide",
        "claude_mcp": "Claude MCP config",
        "claude_commands": "Claude slash commands",
        "claude_hooks": "Claude capture hook",
        "codex_mcp": "Codex MCP config",
        "codex_hooks": "Codex capture hook",
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

    def capture_hook(path: Path, event: str) -> bool:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        return "holocore.capture_hook" in json.dumps(data.get("hooks", {}).get(event, []))

    claude_capture = capture_hook(root / ".claude" / "settings.json", "SessionEnd")
    codex_capture = capture_hook(root / ".codex" / "hooks.json", "Stop")
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
            "capture": claude_capture,
        },
        "codex": {
            "connected": codex_ok,
            "detail": codex_detail,
            "config": str(codex_path),
            "skills": len(list((root / ".agents" / "skills").glob("holocore-*/SKILL.md"))),
            "capture": codex_capture,
        },
    }
