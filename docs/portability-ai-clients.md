# Portability and AI-client guide

## One setup command per project

From the project you want the AI client to use:

```powershell
cd C:\path\to\project
holocore setup
```

Setup registers the local `holocore-mcp` server and creates each client's native command definitions, including Gemini TOML commands and `$`-invoked Codex project skills. Registration is non-destructive: unrelated configuration remains in place, and HoloCore reports any entry it cannot merge safely.

Run `holocore paths` to inspect the paths selected for the current project. Run `holocore connect` after installing another client or to repair its HoloCore registration.

## Claude Code

HoloCore registers the project server in `<project>/.mcp.json` and creates project slash commands.

1. Run `holocore setup` from the project.
2. Restart Claude Code.
3. Run `/mcp` and confirm that `holocore` is connected.
4. Invoke `/holocore-search`, or use the generated MCP prompt `/mcp__holocore__search`.

If `.mcp.json` already contains other servers, setup preserves them and adds only the HoloCore entry.

## Codex

HoloCore registers the project server in `<project>/.codex/config.toml` and creates `$`-invoked project skills under `<project>/.agents/skills`. These are Codex skills, not slash commands.

1. Run `holocore setup` from the project.
2. Restart Codex or reopen the project.
3. Invoke `$holocore-search`.

Existing Codex settings and unrelated skills remain untouched.

## Gemini

Gemini MCP settings are stored in `<project>/.gemini/settings.json`. Its HoloCore commands are TOML definitions under `<project>/.gemini/commands`, for example `.gemini/commands/holocore-search.toml`.

## Cursor and OpenCode

Setup uses each client's native project command format. Restart or reload the client after setup. If command discovery is unavailable in a particular client version, use its HoloCore MCP tools or run `holocore search` in the project terminal.

## Generic MCP shape

HoloCore writes the exact Python environment that owns the installed package, so AI clients do not depend on inheriting your terminal's PATH. The generated entry has this shape (the executable path is selected automatically):

```json
{
  "mcpServers": {
    "holocore": {
      "command": "C:\\path\\to\\holocore-environment\\python.exe",
      "args": ["-m", "holocore.mcp_server"],
      "cwd": "C:\\path\\to\\project"
    }
  }
}
```

Codex stores the equivalent entry in TOML. OpenCode uses its command-array shape. Prefer `holocore connect` over manual editing because it writes every selected integration correctly and preserves existing settings.

## Moving a World between machines

1. Install HoloCore from the repository Git URL (or with `uv tool install holocore` after the PyPI release).
2. Copy or clone the project, including `Archive`. Include `.holocore` only if the generated Atlas and Animus history should travel.
3. Change into the copied project and run `holocore setup`.
4. Run `holocore doctor`, then restart or reopen each AI client.

Setup refreshes machine-specific client registrations without replacing unrelated configuration. Treat `Archive`, `.holocore/animus.db`, and `.holocore/raw-chats` as potentially sensitive project data. Do not copy the SQLite database while HoloCore is writing to it.

## Portability contract

HoloCore's runtime is the installed `holocore` package plus project-local data. The original Obsidian Second Brain, Graphify, and MemPalace applications are not required. Obsidian remains optional: choose **Open folder as vault** and select `<project>/Archive` if you want its Markdown and graph interface.
