# Capability status

This page is the source of truth for what users can run now versus later work.

| Area | Implemented now | Planned |
|---|---|---|
| Archive | Initialize, search, read, create/update, validate, backlinks, health in native Python | Additional command coverage and docs drift checks |
| Atlas | Incremental native JSON graph, check-first freshness policy, search, resolve, path, affected analysis, self-contained searchable/filterable HTML | Edge-detail inspection, large-graph gates, broader language extraction |
| Animus | Native SQLite Worlds, Sectors, Memory Shards, provenance, deduplication, search, sync, raw-chat audits, deterministic local or OpenAI-compatible distillation | Provider/model shard metadata, graceful remote failure policy, vector reranking, periodic consolidation |
| CLI | `setup`, `paths`, `connect`, `doctor`, `open-archive`, `status`, `search`, Atlas, Animus, and Archive commands | Additional research/media workflows |
| MCP | Unified Archive, Atlas, Animus, chat-refinement, graph HTML, search, status tools, and generated prompts | Additional research/media tools |
| Client setup | Non-destructive folder/MCP bootstrap, client-native command definitions, Gemini TOML commands, and `$`-invoked Codex project skills | Additional client-version compatibility automation |
| Routing | Required-folder and Atlas-freshness checks, one-way Atlas → Archive → optional Animus order, one call per selected source, recursive-route rejection | Semantic reranking inside the bounded result set |
| Packaging | Python 3.11+ wheel with `holocore` and `holocore-mcp`; `uv tool install` workflow | Public registry and signed installer |
| Documentation | Complete guide/reference set in `docs/` | Automated interface-drift validation |

No row in the planned column should be treated as a current command or compatibility promise until implemented and verified.

`holocore atlas-view` generates and opens the HTML graph in the default browser. The MCP tool `holocore_atlas_html` only generates and returns the path, allowing the calling AI client to decide whether to open it.
