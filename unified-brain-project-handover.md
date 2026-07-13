# HoloCore Project Handover

## Purpose

Build one installable local knowledge system, working name **HoloCore**, that combines:

- Obsidian Second Brain as the curated long-term library.
- Graphify as the structural map for code, documents, and knowledge graphs.
- MemPalace as the episodic timeline for prior chats, project work, and debugging history.

The goal is not to rewrite all three projects immediately. The safer first project version is a compatibility-first coordinator that preserves each engine's existing functionality and adds one install, one config, one workflow, and one routing layer.

## Current Local Inputs

- Obsidian source archive: `C:\Users\hnmah\Downloads\obsidian-second-brain-main.zip`
- Graphify source archive: `C:\Users\hnmah\Downloads\graphify-8 (1).zip`
- MemPalace source archive: `C:\Users\hnmah\Downloads\mempalace-develop.zip`
- Active Obsidian vault: `C:\Cursor projects\Second Brain Obsidian\Second Brain`
- Current Codex skill: `C:\Users\hnmah\.codex\skills\second-brain-graphify\SKILL.md`
- Current Codex global workflow file: `C:\Users\hnmah\.codex\AGENTS.md`
- Current MemPalace CLI: `C:\Users\hnmah\.local\bin\mempalace.exe`
- Current MemPalace MCP: `C:\Users\hnmah\.local\bin\mempalace-mcp.exe`

## Current Project Location

Prototype project:

`C:\Users\hnmah\Documents\Codex\2026-07-12\referenced-chatgpt-conversation-this-is-untrusted\work\unified-brain`

Reviewed extracted source copies:

`C:\Users\hnmah\Documents\Codex\2026-07-12\referenced-chatgpt-conversation-this-is-untrusted\work\source-review`

Planning output:

`C:\Users\hnmah\Documents\Codex\2026-07-12\referenced-chatgpt-conversation-this-is-untrusted\outputs\unified-knowledge-system-proposal.md`

## What Exists Now

The prototype currently contains a Python package named `unified-brain` with:

- `src/unified_brain/config.py` for JSON config.
- `src/unified_brain/adapters.py` for delegating to Graphify and MemPalace.
- `src/unified_brain/vault.py` for Markdown vault search.
- `src/unified_brain/cli.py` with `init`, `install`, `status`, `doctor`, `search`, `update`, and `mine`.
- Basic `pyproject.toml` packaging metadata.
- Basic `README.md`.

The prototype has been tested against a fixture:

- `graphify update <project>` succeeded in AST-only mode.
- `mempalace mine <project> --wing <name>` succeeded.
- `unified-brain search <query>` returned results from both the Library and Timeline layers.

## Product Vocabulary

Use a HoloCore sci-fi vocabulary publicly while keeping compatibility with internal engine terms:

| Current term | HoloCore term | Meaning |
| --- | --- | --- |
| Unified system | **HoloCore** | The full combined local knowledge system. |
| Obsidian second brain / vault | **Archive** | Curated long-term knowledge and durable project facts. |
| Graphify graphs | **Atlas** | Structural maps of code, documents, concepts, and relationships. |
| MemPalace | **Animus** | Episodic memory replay for prior work, conversations, and debugging history. |
| Project / repository / wing | **World** | One project, repository, client, or knowledge domain. |
| Room | **Sector** | A focused area inside a World. |
| Drawer / captured memory | **Memory Shard** | A saved episode, extracted record, or retrieved prior-work fragment. |
| Obsidian note | **Archive Entry** | A durable curated note in the Archive. |
| Graph node | **Signal** | A detected file, function, concept, dependency, person, or entity. |
| Graph community / cluster | **Constellation** | A related group of Signals in the Atlas. |

Avoid exposing "drawers", "rooms", and "windows" as the main product language unless a compatibility screen needs to explain MemPalace internals.

Recommended command language for the future CLI:

```powershell
holocore world init "my-project"
holocore atlas refresh "my-project"
holocore animus search "auth decision"
holocore archive promote "deployment pattern"
```

## Core Workflow

For project work:

1. Check the Archive first through `system/index.md` and linked project notes.
2. Query Animus only when prior work, prior decisions, or earlier errors are relevant.
3. Update or query Atlas only for repository structure, code dependencies, and relationship questions.
4. Mine meaningful project/conversation work into Animus.
5. Promote durable verified knowledge into atomic Archive Entries.
6. Do not run expensive all-source searches in every chat.
7. Do not require an LLM API key for normal Graphify updates. Use AST-only Graphify by default.

## Design Decisions

- Preserve all existing functionality by delegating to the original engines first.
- Do not merge codebases blindly until the contracts are stable.
- Make the first install read-only-first, with explicit writes for mine/update/promote.
- Keep routine maintenance quiet. Report only failures, conflicts, or user-visible effects.
- Support source installation later from the three archives, but keep the initial coordinator lightweight.
- Keep Archive as curated knowledge and Animus as episodic history. Do not mine the entire vault into MemPalace.

## Immediate Next Engineering Steps

1. Promote the prototype into a durable project folder, ideally under `C:\Cursor projects\`.
2. Add `docs/architecture.md`, `docs/workflow.md`, and `docs/install.md`.
3. Add tests for config loading, vault search, CLI doctor, and adapter command construction.
4. Add a source manifest that points to the three upstream projects and records preserved capabilities.
5. Add a real installer command that can:
   - validate Graphify, MemPalace, and Obsidian vault paths;
   - register Codex MCP entries safely;
   - install or reuse MemPalace and Graphify commands;
   - create project-local config without overwriting user files.
6. Add a project bootstrap command:
   - `unified-brain project init <path>`
   - `unified-brain project refresh <path>`
   - `unified-brain project ingest <path>`
7. Add acceptance tests proving:
   - Library retrieves a curated note;
   - Timeline retrieves prior project context;
   - Map retrieves code structure;
   - irrelevant queries do not trigger every backend.

## Risks To Manage

- Full semantic Graphify extraction can require an external LLM API key, so AST-only must stay the default.
- MemPalace and Obsidian overlap if the vault is mined wholesale. Keep those responsibilities separate.
- Automatic writes to the vault must be conservative and atomic.
- Windows shell compatibility matters. Avoid scripts that assume Bash unless a PowerShell wrapper exists.
- Public naming should avoid direct trademark dependence if this becomes more than a personal tool.

## Name Decision

Working product name: **HoloCore**.

Internal subsystem names:

- **Archive**: Obsidian curated knowledge layer.
- **Atlas**: Graphify graph and relationship layer.
- **Animus**: MemPalace episodic memory layer.

Rejected or secondary name options:

- **Animus Atlas**: keep **Animus** as the memory subsystem rather than the whole product.
- **ArcHive**: useful as a later feature name, but less clear than HoloCore for the full system.

## Handoff Command Notes

From the current prototype folder:

```powershell
$project = "C:\Users\hnmah\Documents\Codex\2026-07-12\referenced-chatgpt-conversation-this-is-untrusted\work\unified-brain"
Set-Location $project
$env:PYTHONPATH = "$project\src"
python -m unified_brain.cli status
python -m unified_brain.cli doctor --project $project
```

To refresh the project map after more files are added:

```powershell
graphify update "C:\Users\hnmah\Documents\Codex\2026-07-12\referenced-chatgpt-conversation-this-is-untrusted\work\unified-brain"
```

To mine meaningful project state into Timeline after the project folder is stable:

```powershell
mempalace mine "C:\Users\hnmah\Documents\Codex\2026-07-12\referenced-chatgpt-conversation-this-is-untrusted\work\unified-brain" --wing unified-brain
```
