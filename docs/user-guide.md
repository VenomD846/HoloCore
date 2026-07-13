# User guide

## Mental model

- **Archive is the project library.** It owns trusted, durable Markdown knowledge.
- **Atlas is the project map.** It owns structural signals and relationships extracted from project files.
- **Animus is the project diary.** It owns episodic history in scoped Worlds and Sectors.
- **HoloCore is the coordinator.** It checks readiness first, uses a fresh Atlas to narrow scope, searches corresponding Archive notes, and consults Animus only when history is relevant.

See the [visual guide](visual-guide.md) for a numbered explanation of every workflow.

## What setup puts in a project

- `Archive/Inbox`: uncurated knowledge waiting for review.
- `Archive/wiki`: verified, durable Archive Entries.
- `Archive/system/index.md`: the Archive's starting index.
- `.holocore/atlas.json`: the machine-readable structural Atlas.
- `.holocore/atlas.html`: the interactive Atlas for a web browser.
- `.holocore/animus.db`: SQLite storage for episodic Memory Shards. Shards are database rows, not separate files.
- `.holocore/raw-chats`: raw chat audits retained before refinement.
- `HOLOCORE-START-HERE.md`: the short entry point for people and AI clients.

`Archive` is intentionally visible and user-owned. `.holocore` contains generated runtime state. Open Obsidian with **Open folder as vault** and choose `<project>/Archive` if you want an optional visual knowledge interface.

## Canonical vocabulary

| Term | Simple definition |
|---|---|
| **Archive** | Verified knowledge |
| **Atlas** | Structural map |
| **Animus** | Remembered history |
| **World** | Project |
| **Sector** | Area inside a project |
| **Memory Shard** | Raw remembered fragment |
| **Archive Entry** | Polished durable note |
| **Signal** | One mapped thing |
| **Constellation** | Group of related mapped things |

## Everyday commands

Run HoloCore from the project directory. The first command for a project is `holocore setup`:

```powershell
cd C:\path\to\project
holocore setup
holocore doctor
holocore search "previous dependency error"
holocore atlas-refresh
holocore remember "Decision: keep the local keyless baseline" --sector project --source "meeting"
holocore recall "keyless baseline" --sector project
holocore ingest-chat ".\chat-export.json"
```

Use `holocore paths` to see where HoloCore stores this World's files, `holocore connect` to repair client registration, and `holocore open-archive` to open the visible top-level Archive. Add `--json` before a subcommand for stable JSON output. Advanced users can use `--root <path>` when operating outside the project directory.

## Current limitations

- Unified routing is keyword-gated, not LLM-based.
- Archive has richer native Python methods than the CLI currently exposes.
- `mine` reads eligible text files recursively and stores whole-file content; review scope before running it.
- Semantic vector reranking and periodic memory consolidation are not yet implemented.
- Atlas language-specific extraction is richest for Python; other files receive generic structural nodes.
- Raw chat audits can contain sensitive content; protect `.holocore/raw-chats` and configure extraction instructions carefully.

See [capability status](capability-status.md) before relying on a new feature.
