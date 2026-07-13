# Research: HoloCore Baseline Coordinator

## Research scope

This research uses the HoloCore root briefs and the delegated local source reviews,
not network assumptions. The relevant evidence is:

- `speckit.constitution.md`, `speckit.plan.md`, `unified-brain-project-handover.md`,
  `unified-knowledge-system-proposal.md`, and `knowledge-retrieval-workflow.md`.
- `graphify-8 (1)\graphify-8\ARCHITECTURE.md` and its README.
- `mempalace-develop\mempalace-develop\README.md` and
  `docs\rfcs\002-source-adapter-plugin-spec.md`.
- `obsidian-second-brain-main\obsidian-second-brain-main\architecture.md` and
  its README/FORK_INSIGHTS.md.

## Decision 1: Keep upstream systems separate behind HoloCore adapters

**Decision**: HoloCore owns a stable adapter protocol and delegates to the existing
Obsidian, Graphify, and MemPalace surfaces. It does not merge their codebases for the
baseline.

**Rationale**: The handover explicitly calls for a compatibility-first coordinator.
The source reviews show three different primary surfaces: Obsidian compiles one
platform-neutral command source through adapters; Graphify exposes a staged pipeline
and standalone CLI; MemPalace exposes a local CLI/MCP system with a pluggable source
adapter contract. Delegation preserves upgradeability and makes compatibility
failures visible at one boundary.

**Alternatives considered**:

- Merge all source code into one package: rejected because it would create a large,
  tightly coupled fork before contracts and ownership are stable.
- Treat the three sources as opaque search providers: rejected because lifecycle,
  safe writes, capability preservation, and provenance would be untestable.

## Decision 2: Use a normalized, source-labelled result model

**Decision**: Every routed result is normalized to a HoloCore Adapter Result while
retaining source-specific provenance, confidence, and transformation metadata.

**Rationale**: Graphify labels relationships as EXTRACTED, INFERRED, or AMBIGUOUS;
MemPalace's adapter RFC requires source references, declared transformations, typed
records, and route hints; Obsidian's AI-first rules require durable note provenance
and duplicate avoidance. A normalized envelope can carry these without flattening
source semantics.

**Alternatives considered**:

- Return raw upstream output only: rejected because the router cannot consistently
  label, explain, or test cross-source results.
- Convert all sources to one common content type: rejected because it would lose
  structural graph edges and episodic/durable ownership distinctions.

## Decision 3: Relevance gates are explicit and task-driven

**Decision**: The router accepts a World plus a task type or conservative task
classification. It selects Archive for durable knowledge, Atlas for structure and
relationships, Animus for prior episodes, and multiple sources only when the task
requires them. It records selected and skipped sources with reasons.

**Rationale**: The root retrieval workflow says not to query every source for every
task. Source ownership also provides the default routing policy and reduces leakage
of episodic content into durable retrieval.

**Alternatives considered**:

- Fan out every query to all sources: rejected for unnecessary latency, cost, and
  context exposure.
- Require users to name a source every time: rejected because it defeats the value
  of one unified workflow; explicit source selection remains an override.

## Decision 4: Baseline is local and keyless

**Decision**: Use Python 3.11+ for HoloCore, standard-library coordination logic,
existing local executables/file formats, and AST-only Atlas refresh by default. Keep
semantic provider integrations optional.

**Rationale**: Graphify supports AST extraction without LLM credits; MemPalace
describes local-first retrieval with zero API calls; Obsidian documents a keyless
research fallback and optional semantic search. The common local baseline avoids
making external credentials a prerequisite.

**Alternatives considered**:

- Require a hosted embedding or LLM service: rejected because it conflicts with the
  local/keyless requirement and makes acceptance non-deterministic.
- Reimplement semantic search in HoloCore: rejected because it duplicates upstream
  functionality and expands the baseline beyond coordination.

## Decision 5: Explicit writes and source ownership are mandatory

**Decision**: `update`, `mine`, and `promote` are explicit operations. Animus captures
  remain episodic unless explicitly promoted. Archive promotion searches before
  writing and stops on ambiguity. Atlas updates are scoped to the World and preserve
  user-owned files outside graph outputs.

**Rationale**: The root proposal separates durable Library, structural Map, and
  episodic Timeline responsibilities. Obsidian's architecture requires search-before-
  create and additive/sentinel-style writes; MemPalace stores verbatim history; the
  handover warns against mining the entire vault or overwriting user files.

**Alternatives considered**:

- Auto-promote every captured record: rejected because transient debugging history
  and curated durable knowledge have different ownership and retention semantics.
- Let every adapter write freely: rejected because the coordinator could not provide
  safe conflict handling or provenance.

## Decision 6: PowerShell is a first-class validation path

**Decision**: The CLI and quickstart use PowerShell commands with absolute paths,
  literal path handling, and clear diagnostics for spaces, Unicode, and long paths.

**Rationale**: HoloCore is being planned and operated on Windows. The user-facing
  workflow must prove the same baseline through the shell used for installation and
  verification.

**Alternatives considered**:

- Document Bash only: rejected because it would make the baseline unverifiable in
  the target environment.
- Hide path quoting inside a separate installer: rejected because command construction
  and diagnostics are themselves compatibility behavior.

## Open questions resolved for baseline

- **Branch**: no Git branch is available in this workspace; the feature directory
  remains `001-holocore-baseline` and the plan records branch as N/A.
- **Tests**: contract, integration, and acceptance tests are required because the
  feature specification explicitly makes preservation and routing measurable.
- **Contracts**: external CLI/MCP/file-format boundaries exist, so adapter, CLI, and
  source-manifest contracts are included.
