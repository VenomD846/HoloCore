# HoloCore Session Handover

Updated: 2026-07-14

The browser Console now includes a Home registry World selector, safe text
wrapping for long paths and transcripts, grouped command help, and a documented
Home/World structure diagram at `docs/assets/holocore-home-world-structure.svg`.
Its complete panel contract is Chat Deck, Animus, Archive, Atlas, Locations, AI
Commands, and Maintenance; hook events populate Chat Deck while ingest and
refresh operations populate the remaining views.

## User objective

HoloCore must be a genuinely new, local-first application combining the useful
workflow of Graphify, MemPalace, and the Obsidian Second Brain. It must preserve
functionality, avoid duplicate calls and recursive routes, reduce AI context
tokens, and provide a simple Claude Code/Codex/MCP experience.

Core definitions:

- Archive = verified knowledge.
- Atlas = structural map.
- Animus = remembered history.
- World = project.
- Sector = area inside a project.
- Memory Shard = raw remembered fragment.
- Archive Entry = polished durable note.
- Signal = one mapped thing.
- Constellation = group of related mapped things.

## Current architecture

HoloCore has a native Python engine with:

- Archive Markdown storage and search
- Atlas graph generation, HTML/JSON/Markdown export, clustering, audit, and path tools
- Animus SQLite memory, mining, checkpoints, diaries, retrieval, consolidation, and exports
- CLI and MCP server
- Claude Code, Codex, Gemini, Cursor, and OpenCode integration generation
- Conversation capture hooks for Claude and Codex
- Shared Home and registered World registry
- HoloCore output directory named `holocore-out`
- Update, install-check, uninstall, and safe `update --no-sync` lifecycle mode
- One-way `archive-source-sync`
- Initial `archive-promote` implementation

The 2026-07-14 continuation changed the storage boundary:

- HoloCore Home now owns runtime data under `Projects/<project-name>/` and the
  single Obsidian surface under `Archive/`.
- Project wikis live only at `Archive/Worlds/<project-name>/wiki`. Cross-project
  knowledge uses links and tags; there is no separate Shared Archive or runtime copy.
- New setup does not generate `.holocore`, `holocore-out`, `.agents`, client
  config folders, policy Markdown, or MCP files inside the user's project.
- Client connection manifests, hooks, commands, and skills are generated once
  under `Home/Connections`.
- Raw ingested sources live at `Projects/<project-name>/Sources`, outside the
  curated Obsidian Archive.
- Animus is one shared SQLite store at `Home/Animus/animus.db`; records remain
  isolated by World and raw chats live at `Home/Animus/raw-chats/<project-name>`.
- The former `Archive/Shared` scope was removed. Its 39 verified Second Brain
  notes were hash-verified into `Archive/Worlds/Second Brain/wiki`; cross-World
  knowledge now uses ordinary links and tags.
- The single MCP server accepts an active `root` and can resolve a registered
  World by id, name, or root.
- Legacy local Animus databases merge into the shared store without deleting the
  legacy source.

## Important current paths

Repository:

```text
C:\Cursor projects\HoloCore
```

Shared HoloCore Home:

```text
C:\Brains\Holocore Home
```

Obsidian Archive:

```text
C:\Brains\Holocore Home\Archive
```

Central HoloCore World:

```text
C:\Brains\Holocore Home\Projects\HoloCore
```

Second Brain vault:

```text
C:\Cursor projects\Second Brain Obsidian\Second Brain
```

Madinah Airport example project:

```text
C:\Cursor projects\Madinah Airport
```

Claude global rules:

```text
C:\Users\hnmah\.claude\rules
```

Codex global instructions:

```text
C:\Users\hnmah\.codex\AGENTS.md
```

## Current World arrangement

The Second Brain is registered as a HoloCore World and is connected to the shared
Home. Its status and doctor checks reported:

- Atlas fresh
- Claude connected, capture enabled, 36 commands/skills
- Codex connected, capture enabled, 36 skills

The intended long-term role of the Second Brain is a curated, read-mostly Archive
source. It should not become a second independent conversation-capture or Animus
engine. Existing Graphify and MemPalace remain compatibility/migration sources.

## Git status and repositories

HoloCore repository:

```text
https://github.com/VenomD846/HoloCore
```

Second Brain repository:

```text
https://github.com/VenomD846/Second-Brain
```

The Second Brain local `main` branch was made authoritative and pushed with
`--force-with-lease` because the remote had an unrelated initial commit.

Recent HoloCore commits include:

- `0c1a63f` safe `update --no-sync`
- `d79c1f6` explainer demo GIF
- `0bd5efd` one-way Archive source sync
- `3bf1054` source coordination policy
- `6665db3` initial automatic Archive promotion
- `7161fee` project wiki generation before shared sync
- `3a1c768` avoid re-ingesting generated wiki

Do not stage the local/generated repository files unless explicitly requested:

```text
AGENTS.md
CLAUDE.md
GEMINI.md
HOLOCORE.md
.agents\
HOLOCORE-START-HERE.md
worlds.json
```

## Wiki and graph continuation completed

`archive-promote` is now an AI-first managed pipeline rather than a Markdown
copier. It supports explicit `docs`/`all` scope, exclusions, dry run, stable
source ids, full content hashes, local reasoning with configured-provider
support, managed updates, user-owned conflict protection, provenance, index
links, and optional one-way Shared sync.

Atlas now reads the central World Archive as a knowledge source. Archive titles,
sections, concepts, decisions, and preferences become semantic Signals. False
self-edges are removed and repeated relationships are collapsed with occurrence
evidence. Atlas HTML opens in `Knowledge` mode by default (153 knowledge Signals
and 232 knowledge relationships in the verified HoloCore World) while retaining
separate `Code structure` and `Everything` views.

The HoloCore documentation corpus was promoted into 12 managed World Archive
entries. The live Atlas contains 1,011 total Signals and 1,930 relationships,
with zero self-edges and zero duplicate relationship keys.

Animus central migration was verified: the 7 existing Memory Shards and 9
provenance records were copied from the legacy project database into the central
World database without deleting the source.

## Honest remaining work

The continuation audit found and fixed three regressions that were not covered
by the previous verification: registered Worlds now always override stale
project-local configs, `ingest-chat` uses the provider-neutral ChatGPT/Slack/
generic importer, and each imported/captured conversation writes a verbatim
session record into Animus `diary` alongside distilled shards. `animus-export`
now returns both the scoped diary timeline and memory shards. The live source
CLI was reinstalled and verified against `HoloCore` and `TPE Website concept`.

The next implementation pass added Animus Decks and temporal Signal Chronicles,
with CLI/MCP access through `animus-decks`, `animus-signal`, and
`animus-chronicle`. Atlas now promotes bullets from all managed wiki
sections to semantic concepts and marks binary assets with Markdown sidecars as
media evidence. `holocore cleanup` provides a dry-run-first legacy artifact
cleanup path.

1. Automatically link the shared `Home/Connections` bundle into every supported
   AI client's user-scope configuration. The bundle and root-aware MCP server
   exist, but client-specific user-scope installation is not yet uniform.
2. Add an explicit cleanup command for old generated project-local files. The new
   setup stops creating them, but existing `AGENTS.md`, `HOLOCORE.md`, `.agents`,
   `.holocore`, and other legacy files are deliberately not deleted automatically.
3. Add local-model discovery/configuration. When no compatible local model is
   configured, HoloCore uses deterministic local extraction; Ollama was not
   installed on the verified machine.
4. Add a reviewed migration path for older `Archive/Worlds` layouts. Generated
   legacy Archives are now detected and skipped instead of re-imported.

Suggested command surface:

```powershell
holocore archive-promote --source "<project>" --scope docs --dry-run
holocore archive-promote --source "<project>" --scope docs
holocore archive-source-sync --source "<project>\wiki"
```

## Verification

- Full suite: `94 passed, 1 skipped`.
- Focused central storage, Atlas, promotion, and memory tests pass.
- Live central Atlas: fresh at
  `C:\Brains\Holocore Home\Projects\HoloCore\Atlas\graph.json`.
- Live central Animus: 7 HoloCore shards in the shared database at
  `C:\Brains\Holocore Home\Animus\animus.db`.
- The newly created duplicate `Archive/Imported` migration copy was removed after
  path verification; the original project-local Archive was not modified.
- World IDs and `Projects` folders are now the exact project-folder names. Existing
  hashed registrations migrate in place; duplicate project names fail clearly.
- `TPE Website concept` was migrated and cleaned as the live compatibility test.
  Its World is `C:\Brains\Holocore Home\Projects\TPE Website concept`; obsolete
  project-local HoloCore clients, state, graph output, and boilerplate were removed.
- Atlas excludes generated application output and client bundles such as `.next`,
  `node_modules`, `.agents`, `.claude`, `.codex`, `.cursor`, `.gemini`, and
  `.opencode`. The TPE Atlas fell from 29,765 noisy nodes to 676 useful signals,
  including one managed project-overview wiki and zero README signals.

## Agent routing rule

The global Claude and Codex rules now state:

```text
HoloCore is the single routing layer.
Atlas first, selected Archive/Second Brain note second, Animus only when history
matters, exact source files last.
Do not fan out independently to Graphify, MemPalace, Atlas, Archive, and Animus.
Do not ingest generated output, caches, databases, or imported copies.
Do not write the same conversation or fact to both MemPalace and Animus.
Never route a HoloCore result back into HoloCore automatically.
```

## Useful verification commands

```powershell
holocore --version
holocore home
holocore worlds
holocore --root "<project>" paths
holocore --root "<project>" status
holocore --root "<project>" doctor
holocore --root "<project>" atlas-refresh
holocore update --no-sync
holocore sync-all
```

## Critical warning for the next session

Do not claim that global user-scope client linking or cleanup of legacy
project-local generated files is complete. Wiki promotion, central Memory Shards,
semantic Atlas integration, and clean new-World setup are implemented and tested.
