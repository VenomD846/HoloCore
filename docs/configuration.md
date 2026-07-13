# Configuration guide

## Project state

Initialization writes `.holocore/config.json` with `version`, `world`, `root`, `archive`, and `state_dir`. Runtime `Config.load` also recognizes `.holocore/world.json` with `archive` (or legacy `vault`) and `state_dir`. If it is absent, defaults are used.

Environment overrides:

- `HOLOCORE_VAULT`: Archive directory; defaults to `<root>\Archive`.
- `HOLOCORE_STATE`: state directory; defaults to `<root>\.holocore`.

Native runtime state includes Atlas JSON and the Animus SQLite database under the state directory. Treat these as HoloCore-owned generated state; back them up before manual changes.

## Command options

- `--root <path>` selects the World root; default is the current directory.
- `--json` emits JSON and must appear before the subcommand.
- `search --world <name>` overrides the Animus World used by unified search.
- `mine --sector <name>`, `remember --sector <name>`, and `recall --sector <name>` scope episodic operations.

## MCP configuration

Clients launch `holocore-mcp` with the project root as `cwd`. Examples are in the [portability guide](portability-ai-clients.md).

## Optional memory-refinement LLM

The default is local and keyless. To use DeepSeek, Ollama, LM Studio, or another OpenAI-compatible endpoint, add `llm` to `.holocore/config.json`:

```json
{
  "llm": {
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-v4-flash",
    "api_key_env": "HOLOCORE_LLM_API_KEY",
    "custom_instructions": "Extract durable project facts, decisions, preferences, constraints, and outcomes. Exclude secrets and filler."
  }
}
```

Set the secret outside the file:

```powershell
$env:HOLOCORE_LLM_API_KEY = "..."
```

If `base_url` or `model` is absent, HoloCore uses deterministic local extraction. Raw chats are retained under `.holocore/raw-chats`; distilled summaries and facts are stored in Animus.
