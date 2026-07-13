# Architecture and technical guide

## Runtime boundary

HoloCore is one Python package under `src/holocore`. `holocore.sources.json` marks Obsidian Second Brain, Graphify, and MemPalace source trees as `runtime: false`. They are parity references, not imports, subprocesses, services, or installation prerequisites.

## Components

- `cli.py`: command parsing and human/JSON output.
- `mcp_server.py`: local stdio MCP surface.
- `engine.py`: shared runtime, search cache, lifecycle entry points.
- `router.py`: one-pass relevance routing.
- `archive.py`: bounded native Markdown vault operations with AI-first validation and atomic writes.
- `atlas.py`: incremental Python AST and generic-file graph extraction, node-link JSON, freshness, paths, and affected analysis.
- `animus.py`: SQLite Worlds, Sectors, Memory Shards, provenance, deduplication, search, and sync.
- `install.py` and `platforms.py`: non-destructive project/client bootstrap.

## Data flow

`CLI or MCP -> HoloCoreEngine -> Router -> Archive / Atlas / Animus -> source-labelled result`

Archive is always searched by unified search. Atlas is selected for structural terms; Animus is selected for history terms. Each selected subsystem runs at most once. This is deterministic keyword routing today, not semantic LLM routing.

## Storage and safety

Archive stores user-owned Markdown. Atlas writes generated JSON atomically. Animus uses SQLite with foreign keys, scoped uniqueness, and provenance. Writes are explicit; bootstrap skips existing files. The runtime uses only the Python standard library.

## Feature 002 implementation

Memory refinement uses an optional provider boundary around Animus while preserving raw-chat audits and the keyless local fallback. Atlas HTML exports native graph data into a self-contained view. Generated slash commands and Codex skills are client adapters over the stable CLI/MCP intent; they are not a second runtime.
