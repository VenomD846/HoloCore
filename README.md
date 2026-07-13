# HoloCore

HoloCore is a self-contained local knowledge engine combining a curated Markdown Archive, a native structural Atlas, and SQLite-backed episodic Animus behind one CLI and MCP server.

Current version: `0.2.0`. The current runtime is HoloCore-native and does **not** import, launch, or require the original Obsidian Second Brain, Graphify, or MemPalace applications. Their source directories are reference material only.

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

- [User guide](docs/user-guide.md)
- [Installation guide](docs/installation.md)
- [Workflow guide](docs/workflows.md)
- [Slash-command reference](docs/slash-commands.md)
- [Configuration guide](docs/configuration.md)
- [MCP reference](docs/mcp-reference.md)
- [Architecture and technical guide](docs/architecture.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Portability and AI-client guide](docs/portability-ai-clients.md)
- [Capability status](docs/capability-status.md)

## Safety model

Reads and health checks are safe by default. Initialization never overwrites existing integration files. Archive creation, Atlas refresh/HTML generation, and Animus capture/refinement are explicit writes. The baseline remains local and keyless when no remote LLM is configured.

## Development verification

```powershell
$env:PYTHONPATH = "src"
python -m pytest -q
uv build
```
