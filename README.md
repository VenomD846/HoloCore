# HoloCore

HoloCore is a self-contained local knowledge engine combining a curated Markdown Archive, a native structural Atlas, and SQLite-backed episodic Animus behind one CLI and MCP server.

![HoloCore overview showing AI clients connected through one engine to Archive, Atlas, and Animus](docs/assets/holocore-overview.svg)

Current version: `0.3.0`. The runtime is HoloCore-native and does **not** import, launch, or require the original Obsidian Second Brain, Graphify, or MemPalace applications. Those projects served as behavioral references during the rewrite and are not included as runtime components.

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
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
holocore --root "C:\path\to\project" init
holocore --root "C:\path\to\project" status
```

Implemented today: native Archive operations, Atlas JSON/HTML graph extraction and queries, Animus memory storage and recall, raw-chat auditing with distilled memory, configurable OpenAI-compatible LLM providers, unified search, CLI/MCP tools, generated slash commands/skills, and non-destructive client bootstrap.

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
- [Acknowledgments and third-party provenance](THIRD_PARTY_NOTICES.md)

## Safety model

Reads and health checks are safe by default. Initialization never overwrites existing integration files. Archive creation, Atlas refresh/HTML generation, and Animus capture/refinement are explicit writes. The baseline remains local and keyless when no remote LLM is configured.

## Development verification

```powershell
$env:PYTHONPATH = "src"
python -m pytest -q
uv build
```
