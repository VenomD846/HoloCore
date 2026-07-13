# Feature Specification: HoloCore Baseline Coordinator

**Feature Branch**: `001-holocore-baseline`

**Created**: 2026-07-13

**Status**: Ready for planning

**Input**: User description: "Define the HoloCore baseline coordinator that preserves all three upstream capabilities through local keyless adapters and relevance-gated routing."

## User Scenarios & Testing

### User Story 1 - Install and inspect a local World (Priority: P1)

As a Windows user, I can initialize HoloCore for a World, point it at my existing
Archive, Atlas, and Animus sources, and see whether the local prerequisites are
available without providing an external LLM API key.

**Why this priority**: A safe, local, keyless baseline is the entry point for every
other workflow and prevents users from making changes before dependencies are known.

**Independent Test**: On a clean fixture World with local source paths, initialize
HoloCore, run `status` and `doctor`, and confirm that the configuration is created
without overwriting pre-existing files and that the keyless baseline is reported as
ready or with actionable diagnostics.

**Acceptance Scenarios**:

1. **Given** a World with valid local source paths, **When** the user runs the
   initialization command, **Then** HoloCore creates only missing configuration and
   source-manifest files and reports the selected World and source roots.
2. **Given** the fixture has no external LLM API key, **When** the user runs
   `status` and `doctor`, **Then** AST-only Atlas mapping and local Archive/Animus
   checks pass without treating optional semantic enrichment as a failure.
3. **Given** a source path is missing or incompatible, **When** the user runs
   `doctor`, **Then** the result names the source, failed check, and corrective action
   without modifying the source.

---

### User Story 2 - Retrieve targeted knowledge across the three sources (Priority: P1)

As a user working on a World, I can submit one search request and receive compact,
source-labelled context from the relevant Archive, Atlas, and/or Animus layer while
unrelated sources and unrelated fixture files are excluded.

**Why this priority**: Unified, relevance-gated retrieval is HoloCore's primary user
value and the clearest proof that the three engines work together without becoming a
single undifferentiated store.

**Independent Test**: Use one fixture containing a curated decision, a structural
code dependency, a prior project episode, and an unrelated file. Run one query per
information need and verify the expected source is selected, the result is labelled,
and the unrelated file is not returned as targeted context.

**Acceptance Scenarios**:

1. **Given** a query about a durable architecture decision, **When** the user
   searches the World, **Then** Archive returns the curated entry with provenance.
2. **Given** a query about a code dependency or relationship, **When** the user
   searches the World, **Then** Atlas returns the relevant Signals/Constellation and
   distinguishes extracted relationships from inferred or ambiguous relationships.
3. **Given** a query that continues a prior attempt or debugging episode, **When**
   the user searches the World, **Then** Animus returns scoped episodic Memory Shards
   with their World/Sector context.
4. **Given** a query that does not require one of the sources, **When** the user
   searches, **Then** the router does not query that source and reports the routing
   reason in the diagnostic metadata.

---

### User Story 3 - Refresh, capture, and promote knowledge safely (Priority: P2)

As a user, I can explicitly refresh Atlas, capture meaningful project history in
Animus, and promote only verified durable knowledge into Archive without duplicate
notes or destructive overwrites.

**Why this priority**: The system must compound over time, but writes need stronger
guardrails than reads because the three upstream stores have different ownership and
retention semantics.

**Independent Test**: Change the fixture's source, run the explicit refresh/capture/
promotion operations, and verify the structural graph updates, episodic record stays
scoped, an existing Archive entry is updated or reused rather than duplicated, and
all writes report provenance and effects.

**Acceptance Scenarios**:

1. **Given** a changed World source, **When** the user explicitly refreshes Atlas,
   **Then** the graph output is updated using the local default mode and existing
   user files outside the graph output are untouched.
2. **Given** meaningful project work, **When** the user explicitly mines it into
   Animus, **Then** the capture is scoped to the declared World/Sector and is not
   automatically copied into Archive.
3. **Given** a verified durable decision, **When** the user explicitly promotes it,
   **Then** HoloCore searches for an existing Archive entry first, preserves
   provenance, and creates or updates one entry without duplicating it.
4. **Given** a write target is ambiguous, **When** the user requests the operation,
   **Then** HoloCore stops with an actionable conflict instead of guessing or
   overwriting content.

---

### User Story 4 - Keep upstream workflows available through HoloCore (Priority: P2)

As an existing user of any of the three upstream tools, I can continue using the
documented source capability through HoloCore adapters and compatibility aliases,
while HoloCore presents its own unified vocabulary and lifecycle.

**Why this priority**: Adoption depends on trust that integration adds a coordinator
without removing the workflows that already work independently.

**Independent Test**: For each upstream source, invoke one representative preserved
capability through its adapter and one compatibility alias, then verify the original
source semantics remain available and the HoloCore result identifies the adapter and
source manifest entry.

**Acceptance Scenarios**:

1. **Given** an Archive workflow that writes AI-first notes, **When** it is invoked
   through the Archive adapter, **Then** the existing note-writing rules and
   provenance behavior remain available.
2. **Given** an Atlas workflow that builds and queries a graph, **When** it is
   invoked through the Atlas adapter, **Then** AST-only mapping, graph freshness,
   confidence labels, and graph output semantics remain available.
3. **Given** an Animus workflow that mines or searches episodic content, **When** it
   is invoked through the Animus adapter, **Then** verbatim storage, scoped World /
   Sector retrieval, and local backend behavior remain available.
4. **Given** a HoloCore command name differs from an upstream command name, **When**
   the user uses the compatibility alias, **Then** the same upstream capability is
   reachable and the public HoloCore term is shown alongside the compatibility term.

## Edge Cases

- A source executable is present but returns an incompatible version or unsupported
  command; `doctor` reports the mismatch and routing marks that source unavailable.
- The Archive, Atlas, or Animus path contains spaces, Unicode, or a Windows long-path
  prefix; path validation preserves the exact path and diagnostics remain readable.
- The Atlas graph is absent or stale; status distinguishes missing from stale and
  refresh is available as an explicit operation.
- The same fact appears in a durable Archive entry and an episodic Animus record;
  search labels both and promotion does not merge them silently.
- Animus capture is requested without a declared World or with a broad vault root;
  HoloCore rejects unscoped capture rather than mining the entire Archive.
- Optional semantic enrichment is configured without credentials; the baseline still
  operates locally and reports enrichment as unavailable rather than failing all work.
- A promotion target already contains user edits or conflicting provenance; HoloCore
  reports a conflict and requires an explicit resolution.
- A query matches only the unrelated fixture file; targeted retrieval returns no
  source result and explains why no backend was selected.

## Requirements

### Functional Requirements

- **FR-001**: HoloCore MUST initialize one World configuration that records the
  Archive, Atlas, and Animus roots without overwriting existing user files.
- **FR-002**: HoloCore MUST maintain a source manifest containing exact upstream
  roots, adapter identity, preserved capabilities, compatibility aliases, and
  adapter status.
- **FR-003**: HoloCore MUST provide `init`, `status`, and `doctor` workflows that
  work with local Windows paths and produce actionable diagnostics.
- **FR-004**: HoloCore MUST complete its baseline initialization, health checks,
  local retrieval, and acceptance fixture without an external LLM API key.
- **FR-005**: Atlas MUST default to deterministic AST-only mapping for the baseline;
  semantic enrichment MUST be optional and explicitly configured.
- **FR-006**: HoloCore MUST expose an adapter contract for each of Archive, Atlas,
  and Animus that identifies capabilities, source references, lifecycle operations,
  errors, and compatibility behavior.
- **FR-007**: HoloCore MUST route a search request using the active World, task type,
  and relevance gates instead of querying every backend by default.
- **FR-008**: Every routed result MUST include a source label, source reference,
  confidence or provenance metadata where supplied, and the reason for routing.
- **FR-009**: The Archive adapter MUST preserve curated Markdown retrieval,
  AI-first note-writing rules, duplicate avoidance, and explicit promotion behavior.
- **FR-010**: The Atlas adapter MUST preserve graph build/query behavior, graph
  freshness checks, confidence labels, and the project-local graph output contract.
- **FR-011**: The Animus adapter MUST preserve scoped episodic mining and search,
  verbatim or declared-transformation semantics, local retrieval, and backend
  selection behavior.
- **FR-012**: HoloCore MUST provide explicit refresh, mine, and promote operations
  with clear scope and reported effects.
- **FR-013**: HoloCore MUST keep transient episodic captures in Animus unless a user
  explicitly promotes verified durable knowledge into Archive.
- **FR-014**: HoloCore MUST search for an existing Archive entry before promotion
  and MUST stop on ambiguous or conflicting write targets.
- **FR-015**: HoloCore MUST provide compatibility aliases for representative
  upstream workflows and document the mapping between upstream and HoloCore terms.
- **FR-016**: HoloCore MUST report missing, stale, incompatible, or unconfigured
  dependencies without modifying their source data.
- **FR-017**: HoloCore MUST validate Windows paths and preserve spaces, Unicode, and
  long-path prefixes through setup and adapter invocation.
- **FR-018**: HoloCore MUST include an acceptance fixture covering one structural
  dependency, one durable decision, one prior episode, and one unrelated file.
- **FR-019**: HoloCore MUST verify that a targeted query does not return the
  unrelated fixture file as relevant context.
- **FR-020**: HoloCore MUST prove that representative upstream capabilities remain
  available after adapter integration and that added routing does not remove them.

### Key Entities

- **World**: A project, repository, client, or knowledge domain with declared source
  roots and configuration.
- **Source Manifest**: The compatibility record for one World; it names upstream
  roots, adapters, capabilities, aliases, versions, and health status.
- **Archive Entry**: Curated durable Markdown knowledge owned by Archive.
- **Signal**: A structural node or relationship returned by Atlas, optionally grouped
  into a Constellation and labelled with extracted/inferred/ambiguous confidence.
- **Memory Shard**: A scoped episodic record owned by Animus, associated with a World
  and optional Sector.
- **Route Decision**: The source-selection explanation attached to a search request,
  including task type, selected source, skipped source, and reason.
- **Adapter Result**: A normalized source-labelled result that retains the upstream
  reference and any declared transformation or provenance metadata.
- **Promotion Request**: An explicit request to move verified durable knowledge from
  a source result into one Archive Entry without duplication or silent overwrite.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A new user can initialize a fixture World and obtain a readable
  `status`/`doctor` result in under 5 minutes without an external LLM API key.
- **SC-002**: In the acceptance fixture, 100% of the three targeted information
  needs resolve to the correct owning source with a source label and provenance.
- **SC-003**: At least 95% of targeted queries in the acceptance suite avoid querying
  sources that the task-type relevance gate marks unnecessary.
- **SC-004**: Zero unrelated fixture files are returned as relevant context in the
  targeted retrieval acceptance suite.
- **SC-005**: Repeating refresh, mine, or promotion operations on unchanged input is
  idempotent: it creates no duplicate Archive entry and no unscoped Animus capture.
- **SC-006**: 100% of representative preservation checks for Archive, Atlas, and
  Animus pass after adapter integration.
- **SC-007**: A user can identify the source, routing reason, and next action for
  every failed dependency check without reading implementation code.
- **SC-008**: A Windows path containing spaces is accepted by every documented
  baseline setup and validation scenario.

## Assumptions

- The three upstream source reviews and local source roots remain available as
  separately upgradeable dependencies; HoloCore does not vendor or merge them for
  the baseline.
- Users provide or accept local paths for the active Archive, Atlas output, and
  Animus storage; HoloCore validates them rather than discovering arbitrary sources.
- Existing upstream CLIs, MCP servers, hooks, and file formats remain the primary
  compatibility surface until HoloCore contracts are proven.
- The baseline uses a Python-based local CLI/package shape because the handover and
  prototype describe that shape; exact dependency versions are resolved in planning.
- Tests are required for this baseline because capability preservation, routing, and
  non-destructive writes are acceptance-critical, even though the generic Spec Kit
  template treats test tasks as optional.
- Hosted multi-user storage, mandatory web search, semantic provider orchestration,
  and complete source-code unification are out of scope for this baseline.

## Evidence

- Root project brief: `speckit.constitution.md`, `speckit.plan.md`,
  `unified-brain-project-handover.md`, and `unified-knowledge-system-proposal.md`.
- Workflow guidance: `knowledge-retrieval-workflow.md`.
- Delegated source reviews: `graphify-8 (1)\graphify-8\ARCHITECTURE.md`,
  `mempalace-develop\mempalace-develop\docs\rfcs\002-source-adapter-plugin-spec.md`,
  and `obsidian-second-brain-main\obsidian-second-brain-main\architecture.md`.
