# Data Model: HoloCore Baseline Coordinator

## Entity: World

Represents one project, repository, client, or knowledge domain.

| Field | Type | Rules |
|---|---|---|
| `id` | string | Stable, user-readable identifier; required and unique within configuration. |
| `display_name` | string | Human-facing name; required and not used as a path without validation. |
| `archive_root` | path | Existing or explicitly creatable Archive root; must be absolute and validated. |
| `atlas_root` | path | World/project root whose structure Atlas maps; must be declared. |
| `atlas_output` | path | Expected project-local graph output; must remain inside the World or configured output boundary. |
| `animus_root` | path | Local Animus storage or configured palace root; must be explicit. |
| `default_task_type` | enum | `durable`, `structure`, `history`, `mixed`, or `unknown`. |
| `created_at` | datetime | Set once on initialization. |
| `updated_at` | datetime | Changes when configuration changes. |

Relationships: one World owns one Source Manifest and many Route Decisions,
Health Reports, Memory Shards, Signals, and Promotion Requests.

Validation: path fields preserve spaces, Unicode, and long-path prefixes; missing
paths are reported by `doctor` and are not silently substituted.

## Entity: Source Manifest

The compatibility inventory for a World.

| Field | Type | Rules |
|---|---|---|
| `schema_version` | integer | Required; begins at `1`. |
| `world_id` | string | Foreign key to World. |
| `sources` | list | Exactly three baseline entries: `archive`, `atlas`, `animus`. |
| `aliases` | map | HoloCore command/vocabulary term to upstream-compatible term. |
| `manifest_updated_at` | datetime | Changes when source identity or capabilities change. |

Each source entry contains `id`, `holo_term`, `upstream_name`, `root`, `adapter`,
`capabilities`, `compatibility_aliases`, `version_hint`, `status`, and
`last_checked_at`. Capabilities are declarative and acceptance-tested.

## Entity: Archive Entry

Curated durable knowledge stored as a user-authored or promoted Markdown note.

Required metadata: stable source reference, title or note identity, provenance,
content state, and whether the entry is AI-first compliant. Promotion MUST search
by identity/content before create and MUST preserve existing user edits on conflict.

## Entity: Signal

A structural Atlas node or relationship.

Fields include stable `id`, label, source file, source location, relation, confidence
(`EXTRACTED`, `INFERRED`, or `AMBIGUOUS`), and optional Constellation identifier.
Atlas graph output remains owned by Graphify; HoloCore stores only the normalized
reference needed for routing and presentation.

## Entity: Memory Shard

An episodic Animus record.

Fields include content, source reference, World, optional Sector, version token,
chunk index, route hint, declared transformations, and privacy/scope metadata.
Raw or transformed content remains governed by Animus; HoloCore MUST NOT promote it
automatically.

## Entity: Adapter Result

The normalized envelope returned by any adapter.

| Field | Type | Rules |
|---|---|---|
| `source_id` | enum | `archive`, `atlas`, or `animus`; required. |
| `source_term` | string | Upstream identity, e.g. Obsidian, Graphify, MemPalace. |
| `record_kind` | enum | `archive_entry`, `signal`, `memory_shard`, or `health`. |
| `record_id` | string | Stable upstream or derived identity. |
| `title` | string | Optional display title. |
| `content` | string/object | Source-shaped payload; never silently flattened. |
| `source_ref` | object | Path/URI and location/provenance fields. |
| `confidence` | enum/string | Required when source supplies it; otherwise `not-provided`. |
| `transformations` | list | Declared transformations only. |
| `route_decision_id` | string | Foreign key to the Route Decision that selected it. |

## Entity: Route Decision

Explains how a query was routed.

Fields: `id`, World, query/task type, selected sources, skipped sources, reason per
source, explicit override flag, started/finished timestamps, and result count.
The decision is diagnostic metadata and MUST NOT contain secrets.

## Entity: Health Report

The result of `status` or `doctor`.

Fields: World, source checks, executable/version check, path check, graph freshness,
keyless baseline check, severity (`ok`, `warning`, `error`), corrective action, and
timestamp. A Health Report is read-only output and does not modify sources.

## Entity: Promotion Request

An explicit request to move verified durable knowledge into Archive.

Fields: request id, source result id, World, target identity, verification note,
existing-match result, conflict state, requested action (`create`, `update`, `cancel`),
provenance, and outcome. State transitions are:

```text
requested -> matched | no-match | conflict
matched -> updated | cancelled
no-match -> created | cancelled
conflict -> resolved | cancelled
```

No transition may overwrite an Archive entry without an explicit, recorded action.

## Cross-entity invariants

1. Every Adapter Result belongs to one declared source and one Route Decision.
2. Every source write is scoped to a World and preserves an upstream reference.
3. Animus Memory Shards are not Archive Entries unless a Promotion Request succeeds.
4. Missing optional semantic credentials never change a keyless Health Report from
   usable to unusable when the local baseline checks pass.
5. A stale or missing Atlas output is a health state, not permission to write outside
   the declared Atlas output boundary.
