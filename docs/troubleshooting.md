# Troubleshooting

## `ModuleNotFoundError: holocore`

Reinstall the tool with `uv tool install holocore`. Until PyPI publication, use the repository Git URL. Editable installs and `PYTHONPATH` are development-only alternatives.

## `holocore` or `holocore-mcp` is not recognized

Run `uv tool list` and confirm HoloCore is installed. Reinstall it with `uv tool install holocore` or the repository Git URL, then open a new terminal so the tool path is refreshed.

## MCP client cannot start the server

From the project, run `holocore doctor` and `holocore connect`. Then restart or reopen the client. Claude users should run `/mcp`; Codex users should inspect `.codex/config.toml` only if Doctor still reports a problem.

## `status` reports Atlas missing or stale

Change into the project, run `holocore atlas-refresh`, then rerun `holocore doctor`. Refresh is a write to HoloCore state.

## Animus reports an unknown World or Sector

Use the initialized project root and one of the default sectors: `general`, `project`, or `conversations`. A separate root is a separate World.

## Archive rejects a path or update

Archive rejects traversal and protected directories and refuses unexpected overwrites. Use a relative path inside the Archive, avoid protected directories, and resolve conflicts explicitly.

## `mine` captured too much

`mine` currently scans eligible readable files recursively and stores whole-file content. Stop before running it on broad roots; choose a narrow directory and Sector. There is no CLI rollback command today.

## Command does not appear in an AI client

Run `holocore setup` in the project, then restart or reload the AI client. Claude Code discovers `.mcp.json`, `/holocore-search`, and `/mcp__holocore__search`; Codex discovers `.codex/config.toml` and `.agents/skills`, including `$holocore-search`. Run `holocore connect` if the client was installed after setup.

## Original app is missing

That is expected and should not affect HoloCore. If an error references an original app runtime, report it as a regression against the native-runtime boundary.
