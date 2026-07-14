# User guide

## Mental model

- **HoloCore Home is the shared bookshelf.** You choose one location for all durable knowledge.
- **Archive is the library.** `<Home>/Archive` is one Obsidian-ready vault.
- **Worlds are projects.** Each project owns a durable section under `Archive/Worlds/<world-id>`.
- **Shared is the common shelf.** `Archive/Shared` holds knowledge intentionally useful across projects.
- **Atlas is a local project map.** Its public JSON and HTML stay in `<project>/graphify-out`; `.holocore` holds compatibility/runtime copies.
- **Animus is a local project diary.** It stores recalled history and refined conversation memory.
- **HoloCore is the coordinator.** It checks first, searches Atlas, reads the active World and Shared Archive, then consults Animus only when history matters.

See the [visual guide](visual-guide.md) for illustrated versions of these workflows.

## What lives where

| Location | Owner | Contents |
|---|---|---|
| `<Home>/Archive` | You | One visible Markdown/Obsidian vault |
| `<Home>/Archive/Worlds/<world-id>` | One World | Verified project notes and promoted memory |
| `<Home>/Archive/Shared` | All Worlds by explicit choice | Reusable cross-project notes |
| `<Home>/worlds.json` | HoloCore | Registered World IDs and project roots |
| `<project>/graphify-out/graph.json` | HoloCore | Machine-readable project structure used by AI clients |
| `<project>/graphify-out/atlas.html` | HoloCore | Interactive force-directed graph for people |
| `<project>/.holocore/atlas.json` and `atlas.html` | HoloCore | Compatibility copies; refreshed from the same focused graph |
| `<project>/.holocore/animus.db` | HoloCore | SQLite Memory Shards |
| `<project>/.holocore/raw-chats` | HoloCore | Original conversation audits |
| `<project>/.holocore/capture-state.json` | HoloCore | Incremental transcript cursors |

The Home Archive is visible and user-owned. Project `.holocore` state is generated and can contain sensitive history. Atlas follows Git ignore rules, so ignored reference applications, build output, and local configuration do not flood the graph.

## First setup

```powershell
cd <project>
holocore setup --home <Home>
```

Later projects use the saved Home:

```powershell
cd <another-project>
holocore setup
```

Useful orientation commands:

```powershell
holocore home
holocore worlds
holocore paths
holocore status
```

## Approve automatic client access

Setup installs connections and capture hooks, but the client asks you to trust them.

- **Claude Code:** restart the project, run `/mcp`, and approve or confirm HoloCore. Conversation capture runs at `SessionEnd`.
- **Codex:** restart or reopen the project, run `/hooks`, and trust the HoloCore hook. Conversation capture runs at `Stop`.

After approval, Claude can use `/holocore-search` and Codex can use `$holocore-search`.

## Everyday retrieval

```powershell
holocore search "Which files implement authentication?"
holocore search "What happened the last time login failed?"
holocore atlas-search "authentication"
holocore archive-search "authentication policy"
holocore recall "previous login failure" --sector project
```

Unified search follows one bounded route:

1. Check required paths and Atlas freshness.
2. Refresh Atlas when the normal unified-search entry point finds it stale.
3. Search Atlas once.
4. Search the active World Archive and `Shared` once using Atlas hints.
5. Search project-local Animus once only when the question needs history.
6. Return labelled evidence for exact-source inspection.

Other Worlds are not searched merely because they share the same vault.

## Saving knowledge

Store a concise event directly in Animus:

```powershell
holocore remember "Decision: keep the local keyless baseline" --sector project --source "meeting"
```

Import an exported chat manually:

```powershell
holocore ingest-chat <chat-export.json>
```

Create a durable note in the active World:

```powershell
holocore archive-create "wiki/deployment.md" "Verified deployment procedure."
```

Create a note in Shared by using the `shared/` prefix:

```powershell
holocore archive-create "shared/wiki/naming.md" "Naming rule shared by all Worlds."
```

Use Shared only when the knowledge is genuinely cross-project. Normal Archive creation and automatic memory promotion target the active World.

## What automatic capture does

At Claude `SessionEnd` or Codex `Stop`, HoloCore:

1. Reads only new user and assistant messages from the transcript.
2. Stores a raw audit inside the project.
3. Distills summary, facts, decisions, preferences, and entities in one local or configured provider pass.
4. Deduplicates and stores Memory Shards in project-local Animus.
5. Promotes useful extraction into the active World's `wiki/memory` folder.
6. Checks Atlas and refreshes it if project files changed.

The transcript cursor advances only after successful ingestion. Hook failures are reported without blocking the parent AI client.

Automatic does not mean unreviewed knowledge becomes global. Promotion is limited to the active World, and `Shared` always requires an explicit target.

## Keep registered Worlds synchronized

```powershell
holocore sync-all
```

This reruns non-destructive integration setup and ensures Atlas freshness for every available World in `<Home>/worlds.json`.

```powershell
holocore update
```

This updates the installed Git version through `uv`, then performs the same all-World reconciliation.

## Open the visual views

Open the shared knowledge vault:

```powershell
holocore open-archive
```

Or open `<Home>/Archive` manually in Obsidian.

Generate and open the active World's structural graph:

```powershell
holocore atlas-view
```

Archive's Obsidian graph and Atlas HTML answer different questions: Archive links knowledge; Atlas maps project structure. For the best visual graph experience, open `<Home>/Archive` in Obsidian; the HoloCore HTML Atlas is the portable, AI-friendly structural view.

## Canonical vocabulary

| Term | Simple definition |
|---|---|
| **Archive** | Verified knowledge |
| **Atlas** | Structural map |
| **Animus** | Remembered history |
| **World** | Project |
| **Sector** | Area inside a project |
| **Memory Shard** | Raw remembered fragment |
| **Archive Entry** | Polished durable note |
| **Signal** | One mapped thing |
| **Constellation** | Group of related mapped things |

## Current limits

- Unified routing is deterministic and keyword-gated rather than LLM-planned.
- Atlas language-specific extraction is richest for Python; other files receive generic structural nodes.
- `mine` recursively stores eligible whole-file content, so choose a narrow source.
- Remote memory refinement requires an explicitly configured OpenAI-compatible provider; the local fallback remains the default.
- Raw chats and Animus can contain sensitive information; protect project `.holocore` data.
- Selecting another Home does not move the old Archive or registry automatically.

See [capability status](capability-status.md) before relying on a new surface.
