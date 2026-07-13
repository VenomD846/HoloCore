# User guide

## Mental model

- Archive owns curated, durable Markdown knowledge.
- Atlas owns structural signals and relationships extracted from project files.
- Animus owns episodic history in scoped Worlds and Sectors.
- HoloCore routes a query to Archive always, to Atlas for structure-oriented terms, and to Animus for history-oriented terms.

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
