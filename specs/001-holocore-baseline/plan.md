# Implementation Plan: HoloCore Baseline Coordinator

**Branch**: `001-holocore-baseline` (Git branch: N/A; workspace is not a Git repository) | **Date**: 2026-07-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-holocore-baseline/spec.md`

## Summary

Build HoloCore as a local Python engine with three internal subsystems. Archive
contains curated Markdown and AI-first vault workflows; Atlas contains deterministic
graph lifecycle and queries; Animus contains scoped episodic mining and retrieval.
A HoloCore-owned
configuration, source manifest, router, lifecycle, health model, compatibility
alias layer, and PowerShell-friendly CLI compose the sources without merging their
codebases. The baseline is local and keyless: AST-only Atlas processing is the
default and optional semantic providers are not required for initialization,
health checks, retrieval, or acceptance.

## Technical Context

**Language/Version**: Python 3.11+ for the coordinator CLI/package; the adapter
boundary tolerates Graphify's Python 3.10+ and MemPalace's Python 3.9+ runtimes.

**Primary Dependencies**: Python standard library for the HoloCore engine and its
MCP/CLI surfaces; vendored engine source is called in-process where practical.
Legacy CLI/MCP interfaces remain compatibility shims. `pytest` is development-only.

**Storage**: A user-owned local JSON configuration and source manifest; existing
Obsidian Markdown vault; project-local `graphify-out/graph.json` and related Atlas
outputs; user-selected local MemPalace storage. HoloCore MUST NOT relocate or
rewrite these stores in the baseline.

**Testing**: `pytest` unit, contract, integration, and acceptance-fixture tests;
PowerShell quickstart smoke checks; subprocess command-construction tests with
mocked executables; no network or external LLM calls in baseline tests.

**Target Platform**: Windows-first local workstation with PowerShell; paths must
also remain representable as platform-neutral path values for future clients.

**Project Type**: Installable local CLI, MCP server, and unified Python engine package.

**Performance Goals**: `status` and `doctor` return a useful dependency report in
under 5 seconds on a configured local World; relevance gates prevent at least 95%
of clearly unnecessary source invocations in the acceptance suite.

**Constraints**: No external LLM API key for baseline operation; no premature source
code merge; explicit writes only; no broad-vault Animus mining; no blind overwrites;
source-labelled and provenance-preserving results; compatible Windows quoting and
long-path handling.

**Scale/Scope**: One local user, multiple configured Worlds, three upstream source
adapters, one baseline fixture, and the initial commands `init`, `status`, `doctor`,
`search`, `update`, `mine`, and `promote` plus compatibility aliases.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Evidence |
|---|---|---|
| Capability preservation | PASS | Three explicit adapters, preservation scenarios, and contracts cover Archive, Atlas, and Animus. |
| Additive evolution | PASS | Compatibility aliases, idempotent writes, and regression acceptance are in scope. |
| HoloCore ownership | PASS | Configuration, manifest, router, lifecycle, health, vocabulary, and installer are HoloCore-owned. |
| Source ownership and relevance gates | PASS | Archive/Atlas/Animus ownership and route decisions are modelled and contracted. |
| Local/keyless baseline | PASS | Standard-library coordinator, AST-only Atlas default, and no-key quickstart are required. |
| Safe scoped writes | PASS | Explicit update/mine/promote contracts, conflict behavior, and non-destructive tests are required. |
| Windows compatibility | PASS | PowerShell commands, path validation, quoting, spaces, Unicode, and long paths are acceptance concerns. |
| Evidence-based verification | PASS | Source manifest, delegated-review evidence, contracts, fixture, and quickstart are included. |

**Gate result**: PASS. No constitution violation or complexity exception is needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-holocore-baseline/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── adapter-contract.md
│   ├── cli-contract.md
│   └── source-manifest.schema.json
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
pyproject.toml
src/holocore/
├── __init__.py
├── cli.py                 # command parsing and human/JSON output
├── config.py              # World config and safe path handling
├── manifest.py            # source manifest and capability inventory
├── models.py              # normalized records, route decisions, health results
├── router.py              # task classification and relevance-gated dispatch
├── lifecycle.py           # explicit update, mine, promote orchestration
├── health.py              # status/doctor checks and diagnostics
├── install.py             # non-destructive bootstrap and dependency detection
├── adapters/
│   ├── base.py            # HoloCore adapter protocol
│   ├── archive.py         # Obsidian Second Brain adapter
│   ├── atlas.py           # Graphify adapter
│   └── animus.py          # MemPalace adapter
└── compatibility.py       # upstream aliases and vocabulary mapping
tests/
├── unit/
├── contract/
├── integration/
└── fixtures/holocore-baseline/
    ├── archive/
    ├── world/
    ├── episode/
    └── unrelated.txt
```

**Structure Decision**: Use one installable `holocore` package with small owned
coordination modules and adapters that call or read the existing upstream surfaces.
Keep each adapter independently testable and keep source-specific semantics inside
the adapter. The fixture and tests are separate so the baseline can be run without
mutating any of the delegated source review copies or the existing graph output.

## Phase 0: Research Summary

Phase 0 decisions are recorded in [research.md](research.md). They resolve the
runtime boundary, source ownership, local/keyless baseline, routing policy, write
safety, and Windows operational constraints before implementation tasks begin.

## Phase 1: Design Summary

- [data-model.md](data-model.md) defines World, Source Manifest, source-owned
  records, normalized Adapter Result, Route Decision, Health Report, and Promotion
  Request.
- [contracts/adapter-contract.md](contracts/adapter-contract.md) defines identity,
  capabilities, lifecycle, provenance, errors, and compatibility behavior.
- [contracts/cli-contract.md](contracts/cli-contract.md) defines the baseline
  commands, safe write boundaries, diagnostics, and compatibility aliases.
- [contracts/source-manifest.schema.json](contracts/source-manifest.schema.json)
  defines the machine-readable manifest shape.
- [quickstart.md](quickstart.md) defines runnable PowerShell validation scenarios
  for keyless setup, routing, preserved capabilities, and safe writes.

## Post-Design Constitution Check

**Result**: PASS. The design retains all three adapter boundaries, keeps HoloCore's
owned routing/configuration/lifecycle surface distinct, and makes no write or
semantic-enrichment requirement that conflicts with the constitution. The design
also makes the source manifest and acceptance fixture first-class evidence rather
than relying on implementation claims.

## Complexity Tracking

No constitution violations are present. The three adapters are required boundaries,
not additional projects: they isolate independently upgradeable upstream systems
behind one HoloCore-owned contract and allow preserved-capability acceptance tests.
