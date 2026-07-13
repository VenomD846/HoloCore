# MCP reference

`holocore-mcp` is a local stdio JSON-RPC server implementing `initialize`, `tools/list`, and `tools/call`. It reports protocol version `2025-06-18` and server version `0.3.0`.

| Tool | Required inputs | Effect |
|---|---|---|
| `holocore_search` | `query`; optional `world` | Read; check-first Atlas → Archive → optional Animus search with recursive-route protection |
| `holocore_status` | None | Read; required-folder readiness plus World, Archive, Atlas, and Animus status |
| `holocore_archive_search` | `query` | Read; curated Markdown search |
| `holocore_archive_read` | `path` | Read; bounded note read |
| `holocore_archive_create` | `path`, `title`, `content` | Write; creates an AI-first Archive note and rejects unsafe/conflicting paths |
| `holocore_atlas_refresh` | None | Write; refreshes native Atlas JSON |
| `holocore_atlas_search` | `query` | Read; searches structural signals |
| `holocore_atlas_html` | None | Write; generates a self-contained local HTML viewer |
| `holocore_remember` | `content`; optional `sector`, `source` | Write; stores or deduplicates one scoped Memory Shard |
| `holocore_recall` | `query`; optional `sector` | Read; recalls scoped episodic memory |
| `holocore_ingest_chat` | `messages`; optional `sector`, `instructions` | Write; audits raw chat and stores distilled summary/facts |

Tool results are returned as JSON encoded in one MCP text-content item. Errors use JSON-RPC code `-32000` with the exception message.

Current limitations: the server has no resources/prompts surface and no authentication layer because it is a local stdio process. The launching client's `cwd` determines the active World.
