# Capability status

This page is the source of truth for what HoloCore `0.5.0` implements now versus later work.

| Area | Implemented now | Planned or not promised |
|---|---|---|
| HoloCore Home | One user-selected Home, persisted user-level pointer, one `Archive` vault, atomic `worlds.json` registry, readable collision-resistant World IDs | Automated relocation or merge between two Homes |
| Archive | Active-World plus Shared view; initialize, search, read, create/update, validate, backlinks, health, atomic writes, safe legacy Markdown import, explicit conflict-aware World-to-Shared promotion | Automatic conflict resolution remains deliberately explicit |
| Atlas | Project-local incremental JSON graph, Git-ignore-aware freshness, search, resolve, path, affected, explain, neighborhood, deterministic Constellations, audit reports, JSON/HTML/Markdown/manifest exports, self-contained searchable/filterable HTML, polling watch, optional watchdog native watch, lightweight JS/TS/Go/Rust/Java/C#/C/C++ extraction | Full compiler-grade parsing semantics for every language |
| Animus | Project-local SQLite Worlds, Sectors, Memory Shards, provenance, deduplication, scoped file/conversation/Git mining, resumable checkpoints, lexical and optional OpenAI-compatible embedding retrieval, diary timeline, consolidation, export, raw-chat audits, deterministic local or OpenAI-compatible extraction | Provider-specific embedding availability and unusual proprietary conversation formats |
| Automatic capture | Claude `SessionEnd`, Codex `Stop`, incremental transcript cursors, retry-safe commit, tool/system filtering, adjacent deduplication, non-blocking hook entry point | Automatic capture for other clients |
| Memory promotion | Automatic promotion of useful extracted facts, decisions, preferences, entities, and summaries into the active World's `wiki/memory`; digest deduplication | Automatic promotion into Shared |
| Routing | Check first, Atlas → active World Archive + Shared → optional Animus → exact sources; one call per selected source; recursive-route rejection | LLM-planned routing or semantic reranking inside the bounded set |
| Lifecycle | `home`, `worlds`, `sync-all`, and Git-based `update`; all-World non-destructive reconciliation and Atlas freshness | Registry-wide data migration between Homes |
| CLI | Setup, connection, status, paths, lifecycle, unified search, Atlas, Animus, and Archive commands | Additional research/media workflows |
| MCP | Unified search/status, Archive/Atlas/Animus, chat refinement, Home, Worlds, setup, and sync-all tools plus generated prompts | Remote transport or server authentication |
| Client setup | Non-destructive Claude/Codex/Gemini/Cursor/OpenCode bootstrap, generated commands and skills, Claude/Codex hooks | Automatic trust approval inside clients |
| Packaging | Python 3.11+ wheel with `holocore` and `holocore-mcp`; Git install through `uv`; built-in Git update | Public registry and signed installer |
| Documentation | v0.5.0 guide/reference set, parity release workflow, and five architecture/workflow diagrams | Signed installer and registry publication |

Client trust remains explicit:

- Claude Code users approve or confirm the MCP server through `/mcp`.
- Codex users review and trust the Stop hook through `/hooks`.

`holocore atlas-view` generates and opens the active World's HTML graph in the default browser. The MCP tool `holocore_atlas_html` generates the file and returns its path, leaving the calling client in control of opening it. Atlas parity commands include `atlas-explain`, `atlas-path`, `atlas-affected`, `atlas-neighborhood`, `atlas-constellations`, `atlas-audit`, and `atlas-export`. Animus parity commands include `animus-sync`, `animus-checkpoint`, `diary`, `timeline`, `consolidate`, and `animus-export`.

No item in the planned column is a current command or compatibility promise.
