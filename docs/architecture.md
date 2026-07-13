# Architecture and technical guide

![HoloCore architecture overview](assets/holocore-overview.svg)

## Runtime boundary

HoloCore is one Python package under `src/holocore`. Obsidian Second Brain, Graphify, and MemPalace served as behavioral references during the rewrite; they are not imports, subprocesses, services, bundled source trees, or installation prerequisites.

## Components

- `cli.py`: command parsing and human/JSON output.
- `mcp_server.py`: local stdio MCP surface.
- `engine.py`: shared runtime, search cache, lifecycle entry points.
- `router.py`: check-first, non-recursive route planning and ordered retrieval.
- `archive.py`: bounded native Markdown vault operations with AI-first validation and atomic writes.
- `atlas.py`: incremental Python AST and generic-file graph extraction, node-link JSON, freshness, paths, and affected analysis.
- `animus.py`: SQLite Worlds, Sectors, Memory Shards, provenance, deduplication, search, and sync.
- `install.py` and `platforms.py`: non-destructive project/client bootstrap.

## Data flow

`CLI or MCP -> readiness/freshness check -> Atlas -> Archive -> optional Animus -> exact sources -> source-labelled result`

Unified search checks Atlas freshness before retrieval. A fresh Atlas narrows the project scope first; one Archive search then uses that graph context to find corresponding durable notes. Animus runs last only when the query indicates prior work, errors, attempts, or conversations are relevant. A context-local recursion guard rejects a route that calls itself, and each selected subsystem runs at most once. Routing remains deterministic and local rather than LLM-based.

![Unified search routes each query once and avoids duplicate subsystem calls](assets/workflow-unified-search.svg)

## Storage and safety

Archive stores user-owned Markdown. Atlas writes generated JSON atomically. Animus uses SQLite with foreign keys, scoped uniqueness, and provenance. Writes are explicit; bootstrap skips existing files. The runtime uses only the Python standard library.

## Feature 002 implementation

Memory refinement uses an optional provider boundary around Animus while preserving raw-chat audits and the keyless local fallback. Atlas HTML exports native graph data into a self-contained view. Generated client commands, Gemini TOML command definitions, and `$`-invoked Codex skills are adapters over the stable CLI/MCP intent; they are not a second runtime.
