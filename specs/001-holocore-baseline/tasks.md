---

description: "Dependency-ordered implementation tasks for the HoloCore baseline coordinator"

---

# Tasks: HoloCore Baseline Coordinator

**Input**: Design documents from `specs/001-holocore-baseline/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), and [quickstart.md](quickstart.md)

**Tests**: Required by the feature specification for capability preservation, routing,
keyless operation, and non-destructive writes.

**Organization**: Tasks are grouped by user story. Setup and Foundational tasks are
shared; each story phase has an independent test criterion.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the installable package, test layout, and deterministic fixture
without touching the delegated source copies or `graphify-out`.

- [ ] T001 Create the installable project metadata and `holocore` console entry point in `pyproject.toml`
- [ ] T002 [P] Create the coordinator package skeleton in `src/holocore/__init__.py`
- [ ] T003 [P] Create the adapter package skeleton in `src/holocore/adapters/__init__.py`
- [ ] T004 [P] Create unit, contract, integration, and fixture directories under `tests/`
- [ ] T005 [P] Create the baseline fixture inputs under `tests/fixtures/holocore-baseline/archive/`, `tests/fixtures/holocore-baseline/world/`, `tests/fixtures/holocore-baseline/episode/`, and `tests/fixtures/holocore-baseline/unrelated.txt`
- [ ] T006 Configure pytest markers and no-network/no-external-key defaults in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the HoloCore-owned data, configuration, manifest, adapter, routing,
health, and lifecycle boundaries before story-specific commands are implemented.

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete.

- [ ] T007 [P] Define validated World configuration and Windows path handling in `src/holocore/config.py`
- [ ] T008 [P] Define normalized entities, Adapter Result, Route Decision, Health Report, and Promotion Request in `src/holocore/models.py`
- [ ] T009 [P] Define source-manifest loading, validation, capability inventory, and alias mapping in `src/holocore/manifest.py`
- [ ] T010 [P] Define the HoloCore adapter protocol, structured errors, and provenance envelope in `src/holocore/adapters/base.py`
- [ ] T011 Define task-type classification, source ownership rules, and relevance-gated dispatch interfaces in `src/holocore/router.py`
- [ ] T012 Define read-only dependency/path/version checks and keyless readiness reporting in `src/holocore/health.py`
- [ ] T013 Define explicit update/mine/promote orchestration interfaces and effect summaries in `src/holocore/lifecycle.py`
- [ ] T014 Define human-readable and JSON diagnostic output conventions in `src/holocore/cli.py`
- [ ] T015 [P] Add contract fixtures for source identity, provenance, confidence, declared transformations, and structured errors in `tests/contract/fixtures/adapter_results.json`

**Checkpoint**: Foundation ready; story work can proceed in priority order, with US2
adapter work parallelizable by source after the shared protocol exists.

---

## Phase 3: User Story 1 - Install and inspect a local World (Priority: P1) 🎯 MVP

**Goal**: Initialize a World safely and report local/keyless readiness through
`init`, `status`, and `doctor`.

**Independent Test**: Run the Scenario 1 commands from [quickstart.md](quickstart.md)
against the baseline fixture with external LLM credentials absent; confirm only
missing configuration is created, the three sources are identified, and diagnostics
are actionable.

### Tests for User Story 1

- [ ] T016 [P] [US1] Add config creation, existing-file preservation, and Windows path contract tests in `tests/contract/test_init_contract.py`
- [ ] T017 [P] [US1] Add World path and keyless readiness unit tests in `tests/unit/test_config.py`
- [ ] T018 [US1] Add end-to-end `init`, `status`, and `doctor` fixture tests in `tests/integration/test_keyless_setup.py`

### Implementation for User Story 1

- [ ] T019 [US1] Implement non-destructive initialization and dependency detection in `src/holocore/install.py`
- [ ] T020 [US1] Implement source-root, executable, graph-freshness, and optional-credential checks in `src/holocore/health.py`
- [ ] T021 [US1] Implement `init`, `status`, and `doctor` command parsing and output in `src/holocore/cli.py`
- [ ] T022 [US1] Persist validated World configuration and source manifest without overwriting user files in `src/holocore/config.py`
- [ ] T023 [US1] Add PowerShell smoke invocation coverage for absolute paths and spaces in `tests/integration/test_powershell_setup.ps1`

**Checkpoint**: A clean local fixture can be initialized and diagnosed without an
external LLM API key; no source file or existing configuration is overwritten.

---

## Phase 4: User Story 2 - Retrieve targeted knowledge across the three sources (Priority: P1)

**Goal**: Search one World through relevance-gated Archive, Atlas, and Animus
adapters with source labels, provenance, and route explanations.

**Independent Test**: Run the three targeted search scenarios from [quickstart.md](quickstart.md)
and assert correct source selection, result metadata, confidence preservation, and
exclusion of `tests/fixtures/holocore-baseline/unrelated.txt`.

### Tests for User Story 2

- [ ] T024 [P] [US2] Add route-selection, skipped-source, and explicit-override contract tests in `tests/contract/test_routing_contract.py`
- [ ] T025 [P] [US2] Add task classification and relevance-gate unit tests in `tests/unit/test_router.py`
- [ ] T026 [P] [US2] Add Archive result normalization tests in `tests/unit/test_archive_adapter.py`
- [ ] T027 [P] [US2] Add Atlas confidence and graph-boundary normalization tests in `tests/unit/test_atlas_adapter.py`
- [ ] T028 [P] [US2] Add Animus scope, route-hint, and transformation-preservation tests in `tests/unit/test_animus_adapter.py`
- [ ] T029 [US2] Add Library/Map/Timeline routing acceptance tests using the fixture in `tests/integration/test_routing_acceptance.py`

### Implementation for User Story 2

- [ ] T030 [P] [US2] Implement Obsidian Archive search and AI-first provenance mapping in `src/holocore/adapters/archive.py`
- [ ] T031 [P] [US2] Implement Graphify Atlas command construction, AST-only default, freshness lookup, and confidence mapping in `src/holocore/adapters/atlas.py`
- [ ] T032 [P] [US2] Implement MemPalace Animus scoped search, route hints, and declared-transformation mapping in `src/holocore/adapters/animus.py`
- [ ] T033 [US2] Implement source-owned relevance routing and Route Decision recording in `src/holocore/router.py`
- [ ] T034 [US2] Implement `search` response formatting with source labels, provenance, and skipped-source reasons in `src/holocore/cli.py`
- [ ] T035 [US2] Reject unscoped broad-vault searches and unrelated-only results in `src/holocore/router.py`

**Checkpoint**: Archive, Atlas, and Animus each return their own source-shaped result
through one HoloCore search command, while unnecessary backends are skipped.

---

## Phase 5: User Story 3 - Refresh, capture, and promote knowledge safely (Priority: P2)

**Goal**: Add explicit, scoped, provenance-preserving update, mine, and promote
operations with conflict handling and idempotence.

**Independent Test**: Run Scenario 4 from [quickstart.md](quickstart.md), repeat
unchanged operations, and verify no duplicate Archive Entry, no unscoped Animus
capture, and no write outside the declared Atlas output boundary.

### Tests for User Story 3

- [ ] T036 [P] [US3] Add explicit-write scope and conflict contract tests in `tests/contract/test_lifecycle_contract.py`
- [ ] T037 [P] [US3] Add promotion state-transition and duplicate-avoidance unit tests in `tests/unit/test_lifecycle.py`
- [ ] T038 [US3] Add update/mine/promote idempotence and provenance integration tests in `tests/integration/test_safe_writes.py`

### Implementation for User Story 3

- [ ] T039 [US3] Implement scoped Atlas refresh and graph-output boundary enforcement in `src/holocore/lifecycle.py`
- [ ] T040 [US3] Implement scoped Animus mining with required World/Sector and no automatic Archive promotion in `src/holocore/lifecycle.py`
- [ ] T041 [US3] Implement Archive search-before-create, explicit update, and conflict stop behavior in `src/holocore/lifecycle.py`
- [ ] T042 [US3] Implement `update`, `mine`, and `promote` CLI commands with dry-run/effect summaries in `src/holocore/cli.py`
- [ ] T043 [US3] Record declared transformations, source references, and promotion outcomes in `src/holocore/models.py`

**Checkpoint**: All writes are explicit, scoped, provenance-preserving, and safe to
repeat on unchanged input.

---

## Phase 6: User Story 4 - Keep upstream workflows available through HoloCore (Priority: P2)

**Goal**: Preserve representative upstream behavior and expose compatibility aliases
while keeping HoloCore vocabulary and lifecycle distinct.

**Independent Test**: Run one representative preserved capability and one alias per
source, then verify source semantics, manifest identity, and HoloCore terminology.

### Tests for User Story 4

- [ ] T044 [P] [US4] Add Archive AI-first write and compatibility-alias acceptance tests in `tests/contract/test_archive_compatibility.py`
- [ ] T045 [P] [US4] Add Atlas pipeline, confidence, and alias acceptance tests in `tests/contract/test_atlas_compatibility.py`
- [ ] T046 [P] [US4] Add Animus scoped/verbatim-or-declared-transformation and alias acceptance tests in `tests/contract/test_animus_compatibility.py`
- [ ] T047 [US4] Add cross-source preservation regression fixture tests in `tests/integration/test_upstream_preservation.py`

### Implementation for User Story 4

- [ ] T048 [US4] Implement HoloCore-to-upstream command and vocabulary aliases in `src/holocore/compatibility.py`
- [ ] T049 [US4] Register preserved capabilities, source roots, adapter status, and aliases in `src/holocore/manifest.py`
- [ ] T050 [US4] Add compatibility help/diagnostic output showing HoloCore and upstream terms in `src/holocore/cli.py`
- [ ] T051 [US4] Add adapter lifecycle checks proving existing CLI/MCP/file-format paths remain callable in `src/holocore/health.py`

**Checkpoint**: Users can reach representative Archive, Atlas, and Animus workflows
through HoloCore without losing upstream semantics or HoloCore distinctness.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete baseline, improve diagnostics, and keep the
implementation aligned with the design artifacts.

- [ ] T052 [P] Add complete quickstart command coverage in `tests/integration/test_quickstart.py`
- [ ] T053 [P] Add secret/path-redaction and actionable-error tests in `tests/unit/test_diagnostics.py`
- [ ] T054 [P] Add schema validation coverage for `specs/001-holocore-baseline/contracts/source-manifest.schema.json` in `tests/contract/test_manifest_schema.py`
- [ ] T055 Run the full unit, contract, integration, and acceptance suite with no external LLM credentials in `tests/`
- [ ] T056 Run every PowerShell scenario in `specs/001-holocore-baseline/quickstart.md` and record pass/fail evidence in `tests/integration/test_quickstart.py`
- [ ] T057 Verify no implementation task modifies delegated source review directories or `graphify-out` in `tests/integration/test_scope_guard.py`
- [ ] T058 Reconcile implementation behavior against `specs/001-holocore-baseline/spec.md`, `plan.md`, `data-model.md`, and `contracts/` in `tests/integration/test_spec_alignment.py`
- [ ] T059 Measure the 95% unnecessary-source avoidance outcome for User Story 2 across the routing acceptance suite in `tests/integration/test_routing_acceptance.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; T002–T005 can run in parallel after the
  repository root is confirmed, while T001 and T006 both touch `pyproject.toml` and
  run sequentially.
- **Foundational (Phase 2)**: Depends on Setup; T007–T010 can run in parallel, then
  T011–T014 consume the shared models/config/adapter boundaries.
- **User Story 1 (Phase 3)**: Depends on T007–T014; it is the first independently
  usable increment.
- **User Story 2 (Phase 4)**: Depends on the foundational adapter protocol and US1
  World configuration; the three adapter implementations T030–T032 can run in
  parallel.
- **User Story 3 (Phase 5)**: Depends on US2 adapter results and routing; its tests
  and lifecycle operations can then proceed in the listed order.
- **User Story 4 (Phase 6)**: Depends on all adapters and the manifest; preservation
  tests can run in parallel by source.
- **Polish (Phase 7)**: Depends on all desired stories being complete.

### User Story Dependencies

- **US1 (P1)**: Depends only on Foundational; no dependency on another user story.
- **US2 (P1)**: Uses US1's World configuration but remains independently testable
  with a fixture manifest and adapters.
- **US3 (P2)**: Uses US2's source references and normalized results.
- **US4 (P2)**: Uses the three adapter implementations and manifest from US2; it
  verifies preservation rather than adding a new source.

### Parallel Opportunities

- Setup package, adapter directory, test directories, and fixture inputs (T002–T005).
- Foundational configuration, models, manifest, adapter protocol, and contract fixture
  work (T007–T010 and T015).
- US2 Archive, Atlas, and Animus adapter implementations and their unit tests (T026–T032).
- US4 source-specific compatibility tests (T044–T046).
- Polish diagnostics, schema, quickstart, and scope-guard tests (T052–T054, T057).

## Parallel Example: User Story 2

```text
Task: "Implement Obsidian Archive adapter in src/holocore/adapters/archive.py"
Task: "Implement Graphify Atlas adapter in src/holocore/adapters/atlas.py"
Task: "Implement MemPalace Animus adapter in src/holocore/adapters/animus.py"
Task: "Add Archive normalization tests in tests/unit/test_archive_adapter.py"
Task: "Add Atlas normalization tests in tests/unit/test_atlas_adapter.py"
Task: "Add Animus normalization tests in tests/unit/test_animus_adapter.py"
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete US1 to prove safe local initialization and keyless health.
3. Complete US2 to prove the product's unified, relevance-gated retrieval value.
4. Stop and validate with the fixture and [quickstart.md](quickstart.md) before
   enabling write operations.

The smallest meaningful HoloCore demo is US1 + US2; US1 alone is the safe setup
checkpoint, not the complete product value.

### Incremental Delivery

1. Setup + Foundational → stable HoloCore contracts.
2. US1 → local/keyless World initialization and diagnosis.
3. US2 → source-labelled Archive/Atlas/Animus routing.
4. US3 → explicit safe writes and promotion.
5. US4 → compatibility aliases and preservation regression.
6. Polish → quickstart, schema, scope, and alignment validation.

Each increment preserves the previous stories and uses the same acceptance fixture.

### Format Validation

All 59 implementation tasks use the required checklist format: `- [ ]`, sequential
`T###` identifier, optional `[P]` marker only for parallel work, required `[US#]`
label in user-story phases, and an exact file path in every description.
