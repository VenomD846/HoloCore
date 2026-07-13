# Troubleshooting

## `ModuleNotFoundError: holocore`

Activate the environment where HoloCore is installed, then run `python -m pip install -e "C:\path\to\HoloCore"`. For checkout-only development, `$env:PYTHONPATH = "src"` is a temporary alternative.

## `holocore` or `holocore-mcp` is not recognized

Confirm the virtual environment is active and run `python -m pip show holocore`. Reinstall in that environment if needed.

## MCP client cannot start the server

Run `Get-Command holocore-mcp`, verify the client's `cwd` exists, and restart the client after config changes. Prefer an absolute executable path if the client does not inherit the shell PATH.

## `status` reports Atlas missing or stale

Run `holocore --root "<project>" atlas-refresh`, then rerun status. Refresh is a write to HoloCore state.

## Animus reports an unknown World or Sector

Use the initialized project root and one of the default sectors: `general`, `project`, or `conversations`. A separate root is a separate World.

## Archive rejects a path or update

Archive rejects traversal and protected directories and refuses unexpected overwrites. Use a relative path inside the Archive, avoid protected directories, and resolve conflicts explicitly.

## `mine` captured too much

`mine` currently scans eligible readable files recursively and stores whole-file content. Stop before running it on broad roots; choose a narrow directory and Sector. There is no CLI rollback command today.

## Command does not appear in an AI client

Run `holocore init` in the World, then restart or reload the AI client so it discovers the generated commands, Codex skills, and MCP configuration. Check [capability status](capability-status.md) and use the documented CLI equivalent if the client does not support project commands.

## Original app is missing

That is expected and should not affect HoloCore. If an error references an original app runtime, report it as a regression against the native-runtime boundary.
