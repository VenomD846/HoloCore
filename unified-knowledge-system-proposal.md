# Unified Knowledge System Proposal

## Objective

Create one installable local system that combines:

- Obsidian Second Brain for curated, durable knowledge.
- Graphify for deterministic code and document structure.
- MemPalace for episodic project and conversation memory.

The user should install one system and receive one workflow. The underlying engines may remain separate internally so they can be upgraded independently.

## Recommended product model

Use one public vocabulary and keep compatibility aliases for the original tools.

| Unified term | Current concept | Role |
| --- | --- | --- |
| **Workspace** | Project / wing | Top-level project or knowledge area |
| **Map** | Graphify graph | Structural map of files, symbols, and relationships |
| **Library** | Obsidian vault | Curated decisions, notes, rules, and references |
| **Timeline** | MemPalace drawers | Episodic history, prior attempts, and conversations |
| **Section** | Room | Scoped topic or workflow area |
| **Record** | Drawer / note | One retrievable memory or knowledge item |

Internally, retain `wing`, `room`, `drawer`, `graph.json`, and existing Obsidian paths until migration is proven. Public commands can use the new names and expose old names as aliases.

## Retrieval workflow

The unified router should use relevance gates rather than query every store on every task.

1. Identify the active Workspace and task type.
2. Search the Library index for durable project guidance when relevant.
3. Search the Timeline only when the task continues previous work or references a prior decision/error.
4. Query the Map for code structure, dependencies, and relationships.
5. Read exact project files only after targeted retrieval identifies what is needed.

For simple isolated edits, skip Timeline and Map. For architecture or debugging work, use all relevant layers.

## Write workflow

After meaningful project work:

1. Update the Map with local AST-only Graphify processing.
2. Save episodic context to the Timeline through MemPalace hooks or scoped mining.
3. Promote only verified, durable, reusable knowledge into the Library.
4. Update existing Library notes before creating duplicates.
5. Link new notes from the Workspace index or relevant project note.

Raw interaction history belongs in the Timeline. Curated knowledge belongs in the Library. Structural facts belong in the Map. Do not copy all raw data into all three stores.

## Proposed install experience

The new installer should be one command, for example:

```powershell
unified-brain install
```

It should:

1. Detect Python and the supported AI clients.
2. Install or verify Graphify and MemPalace in isolated environments.
3. Ask for the Obsidian vault path and validate it.
4. Create one configuration file containing the vault, palace, and project roots.
5. Register the MemPalace MCP server and the unified MCP/router server.
6. Install project-session hooks for Map updates and Timeline capture.
7. Install the unified skill/rules for Codex, Claude, and other supported clients.
8. Run a read-only health check and a small fixture test.

No external API key should be required for the baseline install. Graphify AST mapping and MemPalace retrieval are local. Semantic enrichment can be optional.

## Proposed configuration

```yaml
version: 1
vault: C:\\Cursor projects\\Second Brain Obsidian\\Second Brain
palace: C:\\Users\\<user>\\.unified-brain\\timeline
projects_root: C:\\Cursor projects
defaults:
  graph_mode: ast
  auto_update_map: true
  auto_capture_timeline: true
  auto_promote_library: true
  routine_reports: false
sources:
  library: obsidian
  map: graphify
  timeline: mempalace
```

## Integration boundaries

Do not merge all source code into one Python package initially.

- Reuse MemPalace's existing CLI, MCP server, Codex plugin, and hooks.
- Reuse Graphify's CLI and `graphify-out` format.
- Reuse Obsidian Second Brain's command source, adapters, AI-first note rules, and vault MCP server.
- Add a small unified orchestrator for configuration, routing, health checks, and lifecycle events.

This keeps the first release maintainable and avoids forking three active projects unnecessarily.

## First implementation milestone

Build a local `unified-brain` launcher with:

- `unified-brain init`
- `unified-brain doctor`
- `unified-brain search <query>`
- `unified-brain update <project>`
- `unified-brain mine <project>`
- `unified-brain status`

The launcher should delegate to the existing engines and return a compact source-labelled result such as `LIBRARY`, `TIMELINE`, `MAP`, or `SOURCE`.

## Acceptance test

Use one fixture project containing:

- A code dependency path.
- A documented architecture decision.
- A prior conversation or debugging record.
- An unrelated file.

The system passes when it:

- Finds the decision from the Library.
- Finds prior history from the Timeline.
- Finds the dependency path from the Map.
- Excludes the unrelated file from targeted context.
- Updates the Map after a source change.
- Does not duplicate the Library note.
- Performs the baseline workflow without an LLM API key.

## Main risks

- Duplicate facts across MemPalace and Obsidian.
- Hooks mining sensitive conversation content without clear scope.
- Querying every source on every task and increasing latency.
- Breaking upstream plugin compatibility through a premature fork.
- Writing uncertain or transient debugging details into the curated Library.

The design addresses these with source ownership, relevance gates, scoped project wings, explicit promotion rules, and a compatibility-first implementation.
