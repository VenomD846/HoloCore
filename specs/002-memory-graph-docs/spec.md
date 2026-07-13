# Feature Specification: Memory, Graph, and Documentation Experience

**Feature Branch**: `002-memory-graph-docs`

**Created**: 2026-07-13

**Status**: Validated; ready for planning

**Input**: User description: "Custom LLM memory refinement, native graph HTML, slash commands, portable installation, and complete documentation, with current and planned capabilities distinguished and no original-app runtime dependency."

## User Scenarios & Testing

### User Story 1 - Install a self-contained HoloCore (Priority: P1)

As a local user, I can install HoloCore on a supported machine, initialize a project, and connect an AI client without installing or running the three applications used as design references.

**Why this priority**: Every other workflow depends on a trustworthy, portable, self-contained installation.

**Independent Test**: Starting from a clean supported environment, follow the installation guide and reach a healthy initialized World using only HoloCore and declared platform prerequisites.

**Acceptance Scenarios**:

1. **Given** a clean supported environment, **When** the user follows the documented install and initialization flow, **Then** HoloCore reports Archive, Atlas, and Animus status without an external LLM key.
2. **Given** none of the original reference applications are installed, **When** HoloCore runs, **Then** all implemented native baseline capabilities remain available.
3. **Given** an existing client configuration, **When** initialization runs, **Then** existing files are preserved and skipped files are reported.

---

### User Story 2 - Refine memories with a chosen LLM (Priority: P1)

As a user, I can optionally configure an LLM to refine candidate episodic material into useful memory while retaining the original content, provenance, scope, and an auditable record of transformation.

**Why this priority**: Refinement is the requested quality improvement, but it must not weaken the local, keyless baseline or memory trustworthiness.

**Independent Test**: Submit the same candidate with refinement disabled and enabled; verify the keyless path stores the original and the refined path records both source and transformation without silently changing scope.

**Acceptance Scenarios**:

1. **Given** no provider is configured, **When** a user remembers or mines content, **Then** HoloCore uses the implemented deterministic path and does not fail for lack of an LLM key.
2. **Given** a supported provider is explicitly configured, **When** refinement is requested, **Then** the resulting memory identifies the original, refined representation, provider/model identity, transformation, and provenance.
3. **Given** refinement fails or returns unusable output, **When** the operation completes, **Then** the original remains available and the failure is reported without data loss.

---

### User Story 3 - Explore the native graph in HTML (Priority: P1)

As a user, I can generate and open a standalone HTML view of the current Atlas graph, search and inspect nodes and relationships, and trace every displayed element back to native graph data.

**Why this priority**: A portable visual map makes structural knowledge usable without a separate graph application.

**Independent Test**: Generate HTML from a fixture graph, open it without a server or network connection, and inspect nodes, edges, metadata, and freshness information.

**Acceptance Scenarios**:

1. **Given** a current native graph, **When** HTML export is requested, **Then** HoloCore writes a self-contained view that works locally without the original Graphify application.
2. **Given** an absent or stale graph, **When** export is requested, **Then** the user receives a clear refresh or missing-data diagnostic rather than a misleading visualization.
3. **Given** a large graph, **When** the view opens, **Then** users can filter, search, inspect provenance, and distinguish node and relationship kinds.

---

### User Story 4 - Use consistent slash commands (Priority: P2)

As an AI-client user, I can invoke documented HoloCore workflows through portable slash-command prompts with equivalent intent and safe-write rules across supported clients.

**Why this priority**: Commands reduce prompt variation and make safe workflows repeatable across clients.

**Independent Test**: Install the command bundle for each supported client and compare the generated workflow intent, arguments, read/write boundary, and fallback CLI instructions.

**Acceptance Scenarios**:

1. **Given** a supported AI client, **When** integration is installed, **Then** documented HoloCore command prompts are placed only in that client's supported project location without overwriting files.
2. **Given** a client without native slash-command support, **When** the user follows the portability guide, **Then** an equivalent reusable prompt or MCP/CLI flow is available.
3. **Given** a command can write data, **When** invoked, **Then** scope and user intent are explicit before mutation.

---

### User Story 5 - Operate from complete, honest documentation (Priority: P2)

As a user or maintainer, I can find task-oriented documentation for installation, workflows, commands, configuration, MCP, architecture, troubleshooting, and client portability, with every capability labelled implemented or planned.

**Why this priority**: Documentation is part of the product contract and prevents planned designs from being mistaken for current behavior.

**Independent Test**: Use only the documentation index to complete setup, search, graph refresh, memory capture, MCP connection, and troubleshooting, and identify unavailable planned features before attempting them.

**Acceptance Scenarios**:

1. **Given** a reader starts at the README, **When** they choose a task, **Then** they reach the relevant guide through a valid link.
2. **Given** a planned feature is described, **When** the reader encounters it, **Then** it is visibly labelled planned and not shown as an executable current command.
3. **Given** a current command or MCP tool is documented, **When** compared with the installed interface, **Then** its name, required inputs, effects, and limitations match.

### Edge Cases

- Provider credentials are missing, invalid, or accidentally included in diagnostics.
- Refinement changes meaning, invents facts, expands scope, or produces empty output.
- Identical source content is refined repeatedly or with a different provider/model.
- A graph contains no nodes, unresolved relationships, syntax-error file signals, Unicode paths, or enough data to stress browser responsiveness.
- HTML is moved away from the project, opened offline, or generated over an existing export.
- A client changes command-directory conventions or supports MCP but not slash commands.
- Initialization encounters existing, partially configured, read-only, or space-containing paths.
- Documentation and runtime versions drift.

## Requirements

### Capability Status

- **Implemented baseline**: native Archive operations; native Atlas JSON and self-contained HTML; native SQLite Animus plus raw-chat audits and deterministic local or OpenAI-compatible distillation; unified CLI; eleven MCP tools; non-destructive client configuration and generated command definitions; local keyless operation.
- **Planned hardening in this feature**: provider/model shard provenance and graceful remote failure behavior; explicit graph freshness/overwrite controls and edge inspection; release-grade portable installation verification; client compatibility checks; and automated documentation/interface drift checks.
- **Documentation delivered with this feature**: the complete guide and reference set described in User Story 5.

### Functional Requirements

- **FR-001**: HoloCore MUST remain fully usable for its baseline workflows without an external LLM provider.
- **FR-002**: HoloCore MUST NOT require any original Archive, Graphify, or MemPalace application at runtime; reference source trees MUST remain non-runtime evidence only.
- **FR-003**: Optional memory refinement MUST require explicit configuration and explicit invocation or an explicitly enabled scoped policy.
- **FR-004**: Refinement MUST retain original content, World, Sector, source reference, transformation history, and provider/model identity.
- **FR-005**: Refinement MUST reject or quarantine empty, structurally invalid, or scope-changing output and preserve the original on every failure.
- **FR-006**: Repeated refinement MUST define deterministic duplicate and version behavior, including provider/model changes.
- **FR-007**: Sensitive provider credentials MUST be obtained from protected configuration inputs and MUST NOT appear in stored memories, generated HTML, logs, or diagnostics.
- **FR-008**: Native graph HTML MUST derive from HoloCore's Atlas graph contract and MUST NOT depend on an original Graphify runtime.
- **FR-009**: The HTML output MUST be viewable offline and expose search, filtering, node/edge inspection, provenance, graph generation metadata, and freshness state.
- **FR-010**: HTML generation MUST handle missing, stale, empty, malformed, and large graphs with explicit diagnostics or bounded degradation.
- **FR-011**: HTML export MUST use explicit overwrite behavior and MUST avoid embedding secrets or unrelated source content.
- **FR-012**: Slash commands MUST cover status/diagnosis, unified search, Atlas refresh/search/export, memory capture/recall/refinement, Archive search/create, and help.
- **FR-013**: Every write-capable slash command MUST state its target scope and require explicit write intent.
- **FR-014**: Client integrations MUST be non-destructive, report created/skipped files, and provide equivalent prompt/MCP/CLI fallbacks where native slash commands are unavailable.
- **FR-015**: Portable installation MUST document supported prerequisites, package installation, clean-project bootstrap, upgrade/uninstall, offline limitations, and verification.
- **FR-016**: Installation verification MUST prove the runtime imports only HoloCore-owned modules for native Archive, Atlas, and Animus behavior.
- **FR-017**: README MUST serve as the documentation index and quick start.
- **FR-018**: Documentation MUST include user, installation, workflow, slash-command, configuration, MCP, architecture/technical, troubleshooting, and portability/AI-client guides.
- **FR-019**: Every guide MUST visibly distinguish implemented behavior from planned behavior and avoid presenting planned command syntax as currently executable.
- **FR-020**: CLI and MCP references MUST identify inputs, outputs, read/write effects, scope, error behavior, and current limitations.
- **FR-021**: Documentation links and referenced local files MUST be automatically checkable for validity.
- **FR-022**: The feature MUST preserve non-destructive writes, provenance, Windows-first commands, path-with-spaces support, and the local keyless baseline required by the constitution.

### Key Entities

- **Refinement Policy**: Whether refinement is disabled, manually requested, or enabled for a declared scope, plus provider/model and safety limits.
- **Refinement Record**: Original content reference, refined representation, transformation metadata, provider/model identity, timestamps, validation outcome, and provenance.
- **Graph Export**: A standalone visual artifact tied to a graph version, source digest, generation time, filters, and safe overwrite decision.
- **Slash Command Definition**: Portable command intent, arguments, read/write classification, scope rules, and client-specific installation target.
- **Client Integration**: A non-destructive set of MCP, instructions, and command artifacts for one AI client.
- **Capability Status**: An implemented or planned label associated with a documented command, tool, workflow, or limitation.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A new user can install, initialize, and obtain healthy status in under 10 minutes on a supported clean environment without an external LLM key or original-app runtime.
- **SC-002**: 100% of refinement outcomes preserve a retrievable original and complete provenance; failed refinement causes zero original-data loss.
- **SC-003**: A generated graph view opens offline and lets a user find and inspect a known fixture relationship in under 60 seconds.
- **SC-004**: 100% of write-capable slash commands declare scope and write intent; installation overwrites zero existing client files by default.
- **SC-005**: Every implemented CLI command and MCP tool is represented accurately in the reference docs, and every planned capability is visibly labelled planned.
- **SC-006**: Automated documentation validation reports zero broken local links and zero undocumented current public commands/tools.
- **SC-007**: Clean-runtime verification passes with all three original reference applications absent.

## Assumptions

- Python 3.11+ and PowerShell are the supported baseline described by the current package metadata and constitution.
- The current remote refinement adapter is OpenAI-compatible; additional provider contracts remain a planning decision.
- HTML is a generated standalone artifact, not a hosted multi-user web application.
- Existing CLI and MCP names remain compatible; new interfaces are additive.
- Native slash-command locations vary by client, so one portable definition may generate multiple client artifacts.
- Packaging may use standard Python distribution formats, but exact release infrastructure is a planning decision.

## Out of Scope

- Mandatory cloud services or mandatory semantic enrichment.
- Hosted multi-user graph or memory services.
- Silent autonomous promotion of refined episodic content into Archive.
- Runtime delegation to, import from, or subprocess invocation of the original reference applications.
- Replacing AI-client vendors' own command systems or guaranteeing undocumented client behavior.

## Evidence

- Project constitution: `.specify/memory/constitution.md`.
- Current package and interfaces: `pyproject.toml`, `src/holocore/cli.py`, `src/holocore/mcp_server.py`.
- Native engines: `src/holocore/archive.py`, `src/holocore/atlas.py`, `src/holocore/animus.py`.
- Runtime boundary: `holocore.sources.json` and native-runtime tests.
