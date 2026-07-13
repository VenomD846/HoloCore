# Slash-command and skill reference

`holocore setup` generates commands non-destructively for supported clients: Markdown command files for Claude, Cursor, and OpenCode; TOML command definitions under `.gemini/commands` for Gemini; and `$`-invoked Codex project skills under `.agents/skills/`.

| Command/skill | Purpose |
|---|---|
| `holocore-setup` | Prepare the current World, Archive, runtime, MCP, and client files |
| `holocore-init` | Initialize storage and integrations without rebuilding Atlas |
| `holocore-connect` | Add or repair AI-client MCP and command/skill files |
| `holocore-paths` | Print every data and integration location |
| `holocore-open-archive` | Open the visible Archive folder |
| `holocore-status` | Report Archive, Atlas, and Animus health |
| `holocore-search` | Run relevance-gated combined search |
| `holocore-archive-search` | Search the curated wiki |
| `holocore-archive-create` | Create an explicit AI-first note |
| `holocore-atlas-refresh` | Rebuild the native graph |
| `holocore-atlas-view` | Generate the self-contained HTML viewer |
| `holocore-remember` | Store one explicit Memory Shard |
| `holocore-recall` | Recall scoped episodic memory |
| `holocore-doctor` | Run read-only diagnostics |

Claude Code invokes `/holocore-search` as a generated slash command and `/mcp__holocore__search` as the generated MCP prompt. Run `/mcp` to check the server connection. Codex does not use these slash commands: it discovers project skills in `.agents/skills` and invokes `$holocore-search`.

Restart Claude after setup. Restart Codex or reopen the project. The generated files include CLI fallbacks for clients without command discovery.
