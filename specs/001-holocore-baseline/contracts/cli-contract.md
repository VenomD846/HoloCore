# CLI Contract: HoloCore Baseline

The CLI is a local, PowerShell-friendly interface. Human-readable output is the
default; `--json` is available for automation. Commands use absolute or explicitly
resolved paths and MUST return non-zero status for actionable errors.

## Commands

| Command | Read/write | Contract |
|---|---|---|
| `holocore init <world>` | write | Create missing HoloCore config/manifest only; validate paths; report effects. |
| `holocore status [<world>]` | read | Summarize configured sources, capabilities, freshness, and keyless readiness. |
| `holocore doctor [<world>]` | read | Run actionable dependency/path/version checks without modifying sources. |
| `holocore search <query> --world <world>` | read | Route by task type/relevance and return source-labelled results plus route reasons. |
| `holocore update <world>` | explicit write | Refresh Atlas within its declared output boundary; report changed/stale state. |
| `holocore mine <world> --sector <sector>` | explicit write | Capture scoped episodic history into Animus; reject unscoped broad capture. |
| `holocore promote <record> --world <world>` | explicit write | Search-before-create, preserve provenance, and stop on conflicts. |

Compatibility aliases MUST map representative existing command names to these
operations and show both terms in help and diagnostics.

## Search request

```json
{
  "world": "my-project",
  "query": "why was the router changed",
  "task_type": "history",
  "source_override": null,
  "limit": 20
}
```

`task_type` MAY be omitted when conservative classification can identify a source;
an explicit `source_override` is allowed for compatibility/debugging and is recorded
as an override in the Route Decision.

## Search response

```json
{
  "world": "my-project",
  "route_decision": {
    "selected": ["animus"],
    "skipped": {"archive": "not durable-knowledge task", "atlas": "not structural task"}
  },
  "results": [
    {
      "source": "animus",
      "source_term": "MemPalace",
      "record_kind": "memory_shard",
      "record_id": "...",
      "source_ref": {"path": "...", "world": "my-project", "sector": "debugging"},
      "content": "...",
      "provenance": {"transformations": []}
    }
  ]
}
```

## Safety and exit behavior

- `init`, `update`, `mine`, and `promote` MUST report a dry-run or effect summary
  before/after mutation as appropriate.
- Conflicts, ambiguous paths, unsupported operations, and missing required sources
  return a non-zero exit status with a corrective action.
- `status` MAY return warnings for optional semantic enrichment while remaining
  successful if the local/keyless baseline is usable.
- JSON output MUST remain machine-readable; diagnostic text goes to the documented
  diagnostic stream and MUST NOT contain credentials.
