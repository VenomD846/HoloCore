# User guide

## Mental model

- **Archive is the project library.** It owns trusted, durable Markdown knowledge.
- **Atlas is the project map.** It owns structural signals and relationships extracted from project files.
- **Animus is the project diary.** It owns episodic history in scoped Worlds and Sectors.
- **HoloCore is the coordinator.** It checks readiness first, uses a fresh Atlas to narrow scope, searches corresponding Archive notes, and consults Animus only when history is relevant.

See the [visual guide](visual-guide.md) for a numbered explanation of every workflow.

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

Use a quoted absolute project path when operating outside the project directory:

```powershell
holocore --root "C:\path\to\project" status
holocore --root "C:\path\to\project" search "previous dependency error"
holocore --root "C:\path\to\project" atlas-refresh
holocore --root "C:\path\to\project" atlas-view
holocore --root "C:\path\to\project" remember "Decision: keep the local keyless baseline" --sector project --source "meeting"
holocore --root "C:\path\to\project" recall "keyless baseline" --sector project
holocore --root "C:\path\to\project" ingest-chat ".\chat-export.json"
```

Add `--json` before the subcommand for stable JSON output. `doctor` currently returns the same aggregate report as `status`.

## Current limitations

- Unified routing is keyword-gated, not LLM-based.
- Archive has richer native Python methods than the CLI currently exposes.
- `mine` reads eligible text files recursively and stores whole-file content; review scope before running it.
- Semantic vector reranking and periodic memory consolidation are not yet implemented.
- Atlas language-specific extraction is richest for Python; other files receive generic structural nodes.
- Raw chat audits can contain sensitive content; protect `.holocore/raw-chats` and configure extraction instructions carefully.

See [capability status](capability-status.md) before relying on a new feature.
