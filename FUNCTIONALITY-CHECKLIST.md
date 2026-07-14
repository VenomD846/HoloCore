# HoloCore functionality acceptance checklist

This is the minimum bar for the original HoloCore premise. A release is not
ready while an essential row is only represented by a command or folder.

| Source app | Required behavior | HoloCore status |
| --- | --- | --- |
| Graphify | Incremental graph JSON + interactive HTML + Markdown report | PASS (Atlas exports) |
| Graphify | Semantic concept/topic nodes and explained relationships, not filename-only nodes | PARTIAL; verify wiki/archive extraction on every refresh |
| Graphify | Search, path, explain, neighborhoods, clusters/constellations | PASS |
| Graphify | Wiki/community output with source provenance and confidence | PARTIAL; archive promotion supplies project wiki, Atlas community wiki remains limited |
| MemPalace | Immutable raw AI chat capture, resumable and idempotent | PASS for Claude/Codex hooks and Home raw-chat audit files |
| MemPalace | Scoped World/Sector retrieval of remembered chat history | PASS after Home config resolution; must be checked with exact project name |
| MemPalace | SQLite episodic timeline/diary plus distilled shards | FIXED: chat refinement now writes a conversation diary record and shards |
| MemPalace | One export payload an AI can read (timeline + shards + provenance) | FIXED: `animus-export` includes diary and memory-shard records |
| MemPalace | Temporal entity graph, wings/rooms/drawers, full MCP parity | Decks + Signal Chronicles/Constellations implemented; full drawer UI parity remains |
| Second Brain | One Obsidian-compatible Archive with atomic AI-first wiki notes | PASS/PARTIAL; promotion creates managed notes with provenance, links, and summaries |
| Second Brain | Raw source kept separate from curated notes; safe updates preserve user edits | PASS |
| Second Brain | Capture, search, distill, research/architect, health/export workflows | PARTIAL; capture/search/distill/health/export exist, research/architect need explicit adapters |
| HoloCore premise | One Home, World folder named exactly like the project, no Shared Archive | PASS in Home registry; stale legacy project configs are now ignored |
| HoloCore premise | No generated HoloCore runtime/client tree inside user project | PASS for new setup; `holocore cleanup` previews/removes verified legacy artifacts |

## Release acceptance

1. `Config.load` for a registered project resolves `Home/Projects/<project name>`,
   `Home/Animus/animus.db`, and `Home/Animus/raw-chats/<project name>`.
2. `ingest-chat` accepts ChatGPT, Slack, and generic exports through the common
   normalizer, preserves the raw transcript, writes a diary/session record,
   writes distilled shards with provenance, and creates/updates one wiki note.
3. `recall`, `timeline`, and `animus-export` return records for the exact World
   name used by the project folder.
4. Atlas refresh produces meaningful semantic labels and relationships from
   Archive wiki notes and reports its source coverage.
5. Every acceptance item above has an automated test or a documented manual
   verification command.
