# Portability and AI-client guide

## Portability contract

HoloCore's runtime is the `holocore` Python package plus local project state. Original Obsidian Second Brain, Graphify, and MemPalace applications are not required. Move a World by preserving its project files, Archive, and `.holocore` state, then update absolute paths and client `cwd` values.

## Current client bootstrap

`holocore init` creates only missing files for Codex, Claude, Gemini, Cursor, OpenCode, and generic clients. Depending on client, these include MCP configuration and project instruction files. Existing files are skipped, not merged or overwritten.

Generic MCP shape:

```json
{
  "mcpServers": {
    "holocore": {
      "command": "holocore-mcp",
      "args": [],
      "cwd": "C:\\path\\to\\project"
    }
  }
}
```

Codex uses an equivalent TOML `mcp_servers.holocore` entry. OpenCode uses its local command-array shape. Follow the client's current documented configuration format if it differs from generated files.

## Moving between machines

1. Install Python 3.11+ and HoloCore.
2. Copy or clone the World, including Archive and `.holocore` only if memory/graph state should travel.
3. Review `.holocore/config.json` and client configs for old absolute paths.
4. Run `holocore --root "<new path>" init`; existing files remain untouched.
5. Run `status`, refresh Atlas if paths or source content changed, and test MCP.

SQLite state should not be copied while HoloCore is writing to it. Treat Archive and Animus as potentially sensitive data.

## Slash commands and unsupported clients

`holocore init` installs native HoloCore command definitions for Claude, Cursor, Gemini, and OpenCode, plus equivalent Codex project skills under `.agents/skills`. Use MCP where supported; otherwise use the generated command files, the CLI, or `HOLOCORE.md` as a reusable instruction prompt. The CLI and prompt remain the portability path for clients that do not expose native project slash commands.

## Release limitations

The current build produces a local wheel and source archive in `dist`. Publication to a package registry, signed offline bundles, automated migration of absolute paths, and client-version compatibility matrices remain release work.
