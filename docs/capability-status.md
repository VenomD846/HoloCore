# Capability status

This page is the source of truth for what users can run now versus later work.

| Area | Implemented now | Planned |
|---|---|---|
| Archive | Initialize, search, read, create/update, validate, backlinks, health in native Python | Additional command coverage and docs drift checks |
| Atlas | Incremental native JSON graph, check-first freshness policy, search, resolve, path, affected analysis, self-contained searchable/filterable HTML | Edge-detail inspection, large-graph gates, broader language extraction |
| Animus | Native SQLite Worlds, Sectors, Memory Shards, provenance, deduplication, search, sync, raw-chat audits, deterministic local or OpenAI-compatible distillation | Provider/model shard metadata, graceful remote failure policy, vector reranking, periodic consolidation |
| CLI | `init`, `status`, `doctor`, `search`, `atlas-refresh`, `atlas-search`, `atlas-html`/`atlas-view`, `mine`, `remember`, `recall`, `ingest-chat`, `archive-init`, `archive-search`, `archive-create` | Additional research/media workflows |
| MCP | Unified Archive, Atlas, Animus, chat-refinement, graph HTML, search, and status tools | Additional research/media tools |
| Client setup | Non-destructive folder/MCP bootstrap, portable knowledge policy, canonical vocabulary, and generated commands/skills for Codex, Claude, Gemini, Cursor, OpenCode, and generic use | Client-specific lifecycle hooks |
| Routing | Required-folder and Atlas-freshness checks, one-way Atlas → Archive → optional Animus order, one call per selected source, recursive-route rejection | Semantic reranking inside the bounded result set |
| Packaging | Python 3.11+ wheel with `holocore` and `holocore-mcp`; fresh-environment installation validated | Public registry and signed installer |
| Documentation | Complete guide/reference set in `docs/` | Automated interface-drift validation |

No row in the planned column should be treated as a current command or compatibility promise until implemented and verified.

Current limitation: `atlas-view` generates the HTML path but does not open a browser, despite the generated prompt's wording.
