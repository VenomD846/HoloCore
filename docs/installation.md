# Installation guide

![HoloCore installation selects one shared Home, registers a World, and connects AI clients](assets/workflow-install-ai.svg)

HoloCore installs once as a command-line tool. During first setup, you choose one shared **HoloCore Home**. Every project then registers as a **World** in that Home while keeping its generated Atlas, Animus, and raw chats local.

## 1. Install HoloCore

Install [`uv`](https://docs.astral.sh/uv/) if it is not already available, then install HoloCore from Git:

```powershell
uv tool install "git+https://github.com/VenomD846/HoloCore.git"
```

The installation provides `holocore` and the local `holocore-mcp` server. Obsidian, an external graph tool, an external memory application, and an LLM API key are not required.

## 2. Choose the shared Home and set up the first World

Use a path you control and can keep backed up:

```powershell
cd <project>
holocore setup --home <Home>
```

If you omit `--home` in an interactive terminal, first setup asks where the shared second brain should live. You can also select it before setup:

```powershell
holocore home <Home>
holocore setup
```

When setup runs non-interactively without a previously selected Home, the portable default is `%USERPROFILE%\HoloCore` on Windows (or `~/HoloCore` on other systems). Use `--home` whenever you want a different location.

The selected location is remembered by a small user-level pointer. Later projects reuse it automatically:

```powershell
cd <another-project>
holocore setup
```

Use `holocore home` to show the selection and `holocore worlds` to list registered projects.

## 3. Understand the created layout

The Home contains one visible Archive vault:

```text
<Home>/
├── Archive/
│   ├── system/
│   │   └── index.md
│   ├── Shared/
│   │   └── wiki/                  Knowledge shared intentionally
│   └── Worlds/
│       └── <world-id>/
│           ├── Inbox/
│           ├── wiki/              Durable project knowledge
│           └── system/index.md
└── worlds.json                    Registered project paths and IDs
```

HoloCore runtime data is centralized in the project’s `.holocore/` folder. Claude,
Codex, and other AI clients still require a small number of standard bridge files
(`.mcp.json`, `.claude/`, `.codex/`, or `.agents/`) so they can discover HoloCore;
those bridges contain configuration/commands only, not the database or knowledge.

Each World keeps its runtime in the project:

```text
<project>/
├── .holocore/
│   ├── config.json
│   ├── atlas.json
│   ├── atlas.html
│   ├── animus.db
│   ├── capture-state.json
│   └── raw-chats/
├── HOLOCORE-START-HERE.md
├── .claude/settings.json          Claude SessionEnd capture hook
└── .codex/hooks.json              Codex Stop capture hook
```

Setup also merges MCP configuration, generated commands, client instructions, and Codex project skills. Unrelated settings are preserved. Existing invalid configuration is skipped or repaired only when HoloCore can safely identify its own section.

If the project has an older top-level `Archive`, setup copies Markdown into `<Home>/Archive/Worlds/<world-id>/Imported`. Identical files are skipped and conflicting files are left untouched.

## 4. Approve the client connections

AI clients discover project integrations when they start, so restart or reopen the project after setup.

### Claude Code

1. Restart Claude Code in the World.
2. Run `/mcp`.
3. Approve or confirm the project-local `holocore` server.
4. Use `/holocore-search` or `/mcp__holocore__search`.

Claude's automatic conversation capture runs at `SessionEnd`. The hook is installed in `<project>/.claude/settings.json`.

### Codex

1. Restart Codex or reopen the World.
2. Run `/hooks`.
3. Review and trust the HoloCore `Stop` hook.
4. Invoke `$holocore-search`.

Codex uses `$`-invoked skills under `<project>/.agents/skills`; it does not use HoloCore slash commands. The capture hook is installed in `<project>/.codex/hooks.json`.

### Other clients

Gemini receives project-local TOML commands. Cursor and OpenCode receive their native project command and MCP formats. Use `holocore connect` if a client was installed after setup.

## 5. Verify the result

```powershell
holocore status
holocore paths
holocore doctor
holocore worlds
```

`status` reports Home/World paths, Atlas freshness, Animus, client connection state, and whether Claude/Codex capture is installed.

## Optional: open the Archive in Obsidian

Obsidian is not required. To use it:

1. Choose **Open folder as vault**.
2. Select `<Home>/Archive`.

Open only this one Archive root. Do not open an individual World as a separate vault unless you intentionally want an incomplete view.

Atlas has a separate self-contained HTML graph:

```powershell
holocore atlas-view
```

## Useful setup and lifecycle commands

| Command | Purpose |
|---|---|
| `holocore home` | Show the selected Home |
| `holocore home <Home>` | Select and initialize another Home |
| `holocore setup [--home <Home>]` | Register the current World, connect clients, and build Atlas |
| `holocore connect` | Add or repair project client integration |
| `holocore paths` | Print all resolved Home, Archive, World, runtime, and integration paths |
| `holocore worlds` | List every World in the selected Home |
| `holocore sync-all` | Reconcile integrations and Atlas across all registered Worlds |
| `holocore update` | Update HoloCore from Git, then reconcile all Worlds |
| `holocore install-check` | Check the installed version and show update/uninstall commands |
| `holocore uninstall` | Remove the CLI while preserving Home and project data |
| `holocore open-archive` | Open `<Home>/Archive` |

Use `--platform` repeatedly with `setup` or `connect` to configure only selected clients.

## Upgrade or uninstall

The built-in upgrade path is:

```powershell
holocore update
```

It uses `uv` to reinstall HoloCore from the project Git repository and then runs all-World reconciliation. To reconcile without reinstalling:

```powershell
holocore sync-all
```

Uninstall the tool with:

```powershell
uv tool uninstall holocore
```

Uninstalling the tool does not delete `<Home>/Archive`, `<Home>/worlds.json`, project-local `.holocore` state, or generated project integrations.

Changing Home with `holocore home <Home>` selects a different registry and vault; it does not move data from the previous Home. Run setup in each project you want to register with the new Home.
