# Workflow guide

## Orient before broad work

1. Run `status`.
2. Search Archive for durable decisions.
3. Use Atlas only for code/file structure.
4. Use Animus only for previous work or errors.
5. Make writes explicit and scoped.

```powershell
holocore --root "C:\work\project" archive-search "architecture decision"
holocore --root "C:\work\project" atlas-search "Router dependency"
holocore --root "C:\work\project" recall "previous Router error" --sector project
```

## Refresh structural knowledge

Run `atlas-refresh` after source changes. It writes the configured native Atlas JSON atomically and reports node/edge totals. Use `status` to inspect freshness first.

## Capture episodic knowledge

Use `remember` for a concise explicit event. Use `mine` only when whole-file capture of an understood directory is intended. Animus deduplicates identical content in the same scope and records source provenance.

## Curate durable knowledge

The CLI currently exposes `archive-init` and `archive-search`. Archive create/read/update/validate/backlink operations exist in the native Python and MCP surfaces, but CLI coverage is incomplete. Do not treat Animus capture as automatic Archive promotion.

## Refined-memory workflow

Use `ingest-chat` with a JSON message list or an object containing `messages`. HoloCore writes a raw-chat audit, then uses deterministic local extraction or an explicitly configured OpenAI-compatible provider and stores distilled summary/fact/decision/preference/entity shards. There is no separate `refine` command. Provider/model identity on each shard and graceful remote-provider fallback remain planned hardening.

## Graph-view workflow

Run `atlas-refresh`, then `atlas-html` or `atlas-view`. HoloCore writes a self-contained offline HTML file beside Atlas JSON with search and filters. Current limitations: it does not launch a browser, does not ask before replacing the default HTML path, and does not independently reject stale JSON.
