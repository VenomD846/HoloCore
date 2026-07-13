# Adapter Contract: Archive, Atlas, and Animus

## Purpose

This contract is owned by HoloCore and implemented independently by the three
source adapters. It preserves upstream behavior while giving the router one
source-labelled lifecycle surface.

## Adapter identity

Each adapter MUST expose:

- `id`: `archive`, `atlas`, or `animus`.
- `holo_term`: Archive, Atlas, or Animus.
- `upstream_name`: Obsidian Second Brain, Graphify, or MemPalace.
- `adapter_version` and a source-compatible version hint.
- `capabilities`: a stable list used by `status`, `doctor`, routing, and acceptance.
- `source_root` and any output/storage roots after path validation.

## Required operations

The conceptual operations are:

| Operation | Required behavior |
|---|---|
| `check()` | Read-only dependency, path, version, and compatibility check. |
| `describe()` | Return identity, capabilities, source references, and limitations. |
| `search(request)` | Return source-shaped records normalized as Adapter Results. |
| `update(request)` | Perform only the source-specific explicit refresh/capture operation allowed by the adapter. |
| `close()` | Release subprocess, MCP, or file resources; safe to call repeatedly. |

Optional operations MAY include `mine`, `promote`, `is_current`, `source_summary`,
or `alias`, but an adapter MUST report unsupported operations clearly rather than
silently emulate them.

## Source-specific preservation

### Archive adapter

- Preserves Markdown vault search and AI-first write rules.
- Exposes duplicate search before promotion and provenance on Archive Entries.
- Keeps HoloCore's Archive term alongside upstream vault/note terminology.
- Does not convert an Animus Memory Shard into an Archive Entry automatically.

### Atlas adapter

- Preserves the Graphify detect → extract → build → cluster → analyze → report →
  export lifecycle and project-local graph output boundary.
- Defaults to AST-only mode and does not require an LLM API key.
- Preserves `EXTRACTED`, `INFERRED`, and `AMBIGUOUS` relationship confidence.
- Reports missing/stale graph output without writing outside the declared boundary.

### Animus adapter

- Preserves scoped World/Sector retrieval, verbatim storage or declared
  transformations, and local backend selection.
- Carries source references, version tokens, route hints, and privacy/scope metadata.
- Rejects unscoped broad-vault capture in the baseline.
- Preserves the existing CLI/MCP/hook path where configured instead of reimplementing
  episodic storage in HoloCore.

## Result and provenance rules

Every result MUST include `source_id`, `source_term`, `record_kind`, `record_id`,
`source_ref`, and the Route Decision id. Source-specific confidence and declared
transformations MUST be preserved. Adapters MUST NOT silently change content beyond
their declared transformation set.

## Error behavior

Errors are structured as `source_id`, `operation`, `code`, `message`, `retryable`,
`corrective_action`, and optional upstream exit/status details. Secrets MUST NOT
appear in errors. Missing optional semantic providers are warnings when the local
baseline remains usable.

## Compatibility acceptance

For each adapter, acceptance MUST prove one representative upstream capability,
one HoloCore route, one compatibility alias, one missing-dependency diagnostic, and
one preserved source/provenance reference.
