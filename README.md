# HoloCore Context Engine

**HoloCore Context Engine** is a self-contained local AI knowledge engine combining a curated Markdown Archive, a native structural Atlas, and SQLite-backed episodic Animus behind one CLI and MCP server. The product name is **HoloCore Context Engine**; its short name and CLI command remain `HoloCore` and `holocore`.

![HoloCore Context Engine checks Atlas, reads matching Archive knowledge, optionally recalls Animus history, and sends focused context to reduce input tokens](docs/assets/holocore-context-engine-token-savings.png)

Current version: `0.4.0`. The runtime is HoloCore-native and does **not** import, launch, or require the original Obsidian Second Brain, Graphify, or MemPalace applications. Those projects served as behavioral references during the rewrite and are not included as runtime components.

## In simple terms

HoloCore gives an AI assistant three things it normally loses between sessions:

- **Archive is the library:** trusted notes, rules, and decisions.
- **Atlas is the map:** files, functions, dependencies, and relationships.
- **Animus is the memory:** previous work, conversations, errors, and useful context.

You ask one question. HoloCore checks readiness first, uses Atlas to narrow the project scope, searches the corresponding Archive notes, consults Animus only when previous history matters, and then opens exact source files. Every selected stage runs at most once and the route cannot call itself. Read the [step-by-step visual guide](docs/visual-guide.md) for illustrated examples.

### Do I need Obsidian?

No. HoloCore's Atlas is a self-contained HTML graph that opens in a normal web browser. Obsidian is optional and is only needed if you want to use its visual graph interface for the linked Markdown notes in Archive. See [prerequisites and graph viewing options](docs/prerequisites.md).

### Canonical vocabulary

- **Archive** = verified knowledge.
- **Atlas** = structural map.
- **Animus** = remembered history.
- **World** = project.
- **Sector** = area inside a project.
- **Memory Shard** = raw remembered fragment.
- **Archive Entry** = polished durable note.
- **Signal** = one mapped thing.
- **Constellation** = group of related mapped things.

## Quick start

```powershell
uv tool install "git+https://github.com/VenomD846/HoloCore.git"
cd C:\path\to\project
holocore setup
```

After a PyPI release, the shorter install command will be:

```powershell
uv tool install holocore
```

`setup` turns the current project into a HoloCore World. It creates a visible top-level `Archive` Obsidian vault, private generated state in `.holocore`, `HOLOCORE-START-HERE.md`, client-native command definitions, and Codex project skills. It also registers the HoloCore MCP server for Claude Code, Codex, Gemini, Cursor, and OpenCode without overwriting existing configuration.

Open `HOLOCORE-START-HERE.md` after setup, or run `holocore paths` to see every generated location. Use `holocore doctor` to check the installation, `holocore connect` to add or repair client connections, and `holocore open-archive` to open the Archive.

Implemented today: native Archive operations, Atlas JSON/HTML graph extraction and queries, Animus memory storage and recall, raw-chat auditing with distilled memory, configurable OpenAI-compatible LLM providers, unified search, CLI/MCP tools, client-native commands, Codex project skills, and non-destructive client bootstrap.

## Use it from an AI client

For Claude Code, setup adds the project MCP connection to `.mcp.json` and creates slash commands such as `/holocore-search`. Restart Claude after setup, run `/mcp` to confirm the connection, then use `/holocore-search` or the generated MCP prompt `/mcp__holocore__search`.

For Codex, setup adds the project MCP connection to `.codex/config.toml` and creates `$`-invoked project skills under `.agents/skills`. Codex does not use HoloCore slash commands; restart Codex or reopen the project, then invoke `$holocore-search`.

Gemini receives TOML command definitions under `.gemini/commands`, while Cursor and OpenCode receive their native project command formats. All integrations are non-destructive. See the [AI-client guide](docs/portability-ai-clients.md) for details.

Recommended GitHub discovery topics are `claude-code`, `model-context-protocol`, `mcp-server`, `ai-context`, `knowledge-graph`, `second-brain`, `ai-memory`, `obsidian`, and `local-first`.

## Documentation

- [Visual guide](docs/visual-guide.md)
- [User guide](docs/user-guide.md)
- [Installation guide](docs/installation.md)
- [Prerequisites and optional graph tools](docs/prerequisites.md)
- [Workflow guide](docs/workflows.md)
- [Slash-command reference](docs/slash-commands.md)
- [Configuration guide](docs/configuration.md)
- [MCP reference](docs/mcp-reference.md)
- [Architecture and technical guide](docs/architecture.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Portability and AI-client guide](docs/portability-ai-clients.md)
- [Capability status](docs/capability-status.md)
- [Product identity and discovery tags](BRANDING.md)
- [Acknowledgments and third-party provenance](THIRD_PARTY_NOTICES.md)

## Safety model

Reads and health checks are safe by default. Setup adds or merges HoloCore integration entries without overwriting unrelated client configuration. Archive creation, Atlas refresh/HTML generation, and Animus capture/refinement are explicit writes. The baseline remains local and keyless when no remote LLM is configured.

## License and commercial use

HoloCore is licensed under the [Apache License 2.0](LICENSE). It may be used, modified, distributed, and used commercially subject to the license terms. The HoloCore name and branding are not granted by the software license except for reasonable attribution and identification of the project's origin.

Third-party behavioral inspirations and their licenses are recorded in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Development verification

```powershell
$env:PYTHONPATH = "src"
python -m pytest -q
uv build
```
