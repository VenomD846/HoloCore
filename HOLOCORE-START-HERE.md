# HoloCore — Start Here

This folder is one **World**: `HoloCore`.

## Where everything lives

| What | Location | What it does |
|---|---|---|
| HoloCore Home | `C:\Brains\Holocore Home` | Shared home used by every registered project |
| Obsidian Archive | `C:\Brains\Holocore Home\Archive` | One visible knowledge vault containing every World |
| This World's wiki | `C:\Brains\Holocore Home\Archive\Worlds\HoloCore\wiki` | Durable knowledge scoped to this project |
| Source Inbox | `C:\Brains\Holocore Home\Projects\HoloCore\Inbox` | Drop files here for ingestion |
| Immutable raw sources | `C:\Brains\Holocore Home\Projects\HoloCore\Sources` | Content-addressed originals retained outside the curated Archive |
| Atlas JSON | `C:\Brains\Holocore Home\Projects\HoloCore\Atlas\graph.json` | Machine-readable structural and semantic map |
| Atlas HTML | `C:\Brains\Holocore Home\Projects\HoloCore\Atlas\atlas.html` | Interactive graph for people and AI tools |
| Memory Shards | `C:\Brains\Holocore Home\Animus\animus.db` | Shared SQLite store, scoped internally by World |
| Raw chat audit | `C:\Brains\Holocore Home\Animus\raw-chats\HoloCore` | Original chats retained per World |

The Archive is deliberately visible. In Obsidian, choose **Open folder as vault** and select:

`C:\Brains\Holocore Home\Archive`

Obsidian is optional; HoloCore and connected AI clients can read the Markdown directly.

## Connect an AI client

Setup registers this World with the same shared brain and installs its AI connections. Run `holocore connect` to repair them.

- Claude Code: run `/mcp` to approve/check HoloCore, then use `/holocore-search`.
- Codex: use `$holocore-search`; project skills live in `.agents/skills/`.
- Any MCP client: connect the generated `holocore` stdio server and call its tools.

Conversations are captured automatically at supported client hook points, useful shards are promoted into this World's Archive, and Atlas refreshes before search when source files changed. Run `holocore paths` at any time to print every absolute location, or `holocore doctor` to check the connection.
