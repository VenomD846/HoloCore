# HoloCore visual guide

This page explains HoloCore without requiring knowledge of its Python modules or database schema.

## The whole system

![AI clients and people connect through the HoloCore engine to Archive, Atlas, and Animus](assets/holocore-overview.svg)

HoloCore gives every supported AI client the same three kinds of context:

- **Archive** holds durable Markdown knowledge and wiki links. It can be opened directly in Obsidian.
- **Atlas** maps files, symbols, dependencies, paths, and affected areas as JSON and searchable HTML.
- **Animus** keeps scoped episodic memory, provenance, and refined chat knowledge in SQLite.

The CLI and MCP server call the same engine, so command-line and AI-assisted workflows share behavior and storage.

## How unified search avoids duplicate work

![A query is routed once, relevant knowledge systems run at most once, and results are merged](assets/workflow-unified-search.svg)

The Router builds one execution plan per query. Archive always participates because durable project knowledge can answer any category of question. Atlas runs for structural questions, while Animus runs for historical questions. Selected sources are called once, then HoloCore merges and labels their results.

## How a chat becomes useful memory

![A chat is audited, distilled in one extraction pass, deduplicated, and stored in Animus](assets/workflow-memory-refinement.svg)

HoloCore preserves the original chat separately from refined memory. A configured OpenAI-compatible provider—or the local fallback—produces one structured result containing a summary, facts, decisions, preferences, and entities. Animus deduplicates those memory shards, records their provenance, and scopes them to the correct World and Sector.

This separation means raw evidence can be reprocessed without filling recall results with entire conversations.

## How another computer or AI client connects

![Installing HoloCore initializes a World and generates integrations for supported AI clients](assets/workflow-install-ai.svg)

After installing the package, `holocore init` prepares the selected project without overwriting existing client files. It creates the local World structure and missing integrations for Codex, Claude, Cursor, Gemini, OpenCode, and generic MCP or CLI clients. Reloading the project lets the client discover HoloCore commands, skills, instructions, and MCP tools.

The original Obsidian Second Brain, Graphify, and MemPalace applications are not runtime dependencies. HoloCore contains its own Archive, Atlas, and Animus implementations.

## Choose the right workflow

| Need | Use | Result |
|---|---|---|
| Record a durable rule or decision | Archive | Markdown note with links |
| Understand code or file relationships | Atlas | Search result, path, impact map, JSON or HTML graph |
| Recall prior work, errors, or conversations | Animus | Scoped memory shards with provenance |
| Ask a broad project question | Unified search | One merged, source-labelled result set |
| Connect an AI platform | Generated client integration or MCP | The same local HoloCore World from that client |
