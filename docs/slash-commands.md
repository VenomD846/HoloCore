# Slash-command and skill reference

`holocore init` generates commands non-destructively for Claude, Gemini, Cursor, and OpenCode, plus Codex skills under `.agents/skills/`.

| Command/skill | Purpose |
|---|---|
| `holocore-init` | Initialize a World, Git, MCP, Archive, and client files |
| `holocore-status` | Report Archive, Atlas, and Animus health |
| `holocore-search` | Run relevance-gated combined search |
| `holocore-archive-search` | Search the curated wiki |
| `holocore-archive-create` | Create an explicit AI-first note |
| `holocore-atlas-refresh` | Rebuild the native graph |
| `holocore-atlas-view` | Generate the self-contained HTML viewer |
| `holocore-remember` | Store one explicit Memory Shard |
| `holocore-recall` | Recall scoped episodic memory |
| `holocore-doctor` | Run read-only diagnostics |

Claude-style clients invoke these as `/holocore-search ...`. Codex discovers them as project skills and invokes `$holocore-search`. The generated file includes the exact CLI fallback for clients without command discovery.
