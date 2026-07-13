<!--
Sync Impact Report
- Version change: template -> 1.0.0 (initial HoloCore constitution and ratification).
- Modified principles: all template placeholders replaced by eight HoloCore principles.
- Added sections: Product boundaries, Required quality gates, and explicit governance rules.
- Removed sections: none; all template sections are retained with concrete HoloCore content.
- Templates requiring updates: .specify/templates/plan-template.md (reviewed, compatible),
  .specify/templates/spec-template.md (reviewed, compatible),
  .specify/templates/tasks-template.md (reviewed, compatible),
  .specify/templates/commands/*.md (reviewed, generic references retained).
- Follow-up TODOs: none.
-->
# HoloCore Constitution

HoloCore is governed by this constitution. It defines the non-negotiable
constraints for planning and implementation of the local knowledge coordinator.

## Core Principles

### I. Capability Preservation Through Adapters

HoloCore MUST preserve the documented capabilities of Obsidian Second Brain,
Graphify, and MemPalace. Each upstream capability MUST be represented by an
explicit adapter contract, a source-labelled result path, and acceptance coverage.
An adapter MAY delegate to an upstream CLI, MCP server, hook, library, or file
format; it MUST NOT silently replace or weaken the upstream behavior.

Rationale: the product is a compatibility-first coordinator, so users retain the
tools they already rely on while gaining a unified workflow.

### II. Additive Evolution and No Silent Loss

New HoloCore behavior MUST be additive unless a documented compatibility decision
explicitly approves a breaking change. Existing command aliases, source ownership,
data semantics, and user-authored files MUST remain usable after an extension.
Regression checks MUST cover both the added behavior and the preserved behavior.

Rationale: integration work must increase capability without creating an accidental
fork that users cannot safely adopt.

### III. HoloCore Owns the Coordination Layer

HoloCore MUST remain materially distinct from every upstream project. Its owned
responsibilities are unified configuration, source manifest, lifecycle, routing,
health reporting, compatibility aliases, public vocabulary, and install/bootstrap
experience. HoloCore MUST NOT become a thin repackaging or a premature merge of the
three upstream codebases.

Rationale: independent upstream upgrades remain possible only when the coordination
boundary is explicit and owned by HoloCore.

### IV. Source Ownership and Relevance-Gated Routing

Archive (Obsidian) owns curated durable knowledge and user-authored notes. Atlas
(Graphify) owns structural signals, relationships, and graph freshness. Animus
(MemPalace) owns episodic history, prior attempts, and conversations. The router
MUST select sources from the active World and task type; it MUST NOT query every
backend by default. Every routed result MUST identify its source and the reason the
source was selected.

Rationale: clear ownership prevents duplication, while relevance gates preserve
local performance and reduce unnecessary exposure of sensitive context.

### V. Local and Keyless Baseline

The baseline install and acceptance fixture MUST work locally without an external
LLM API key. Atlas MUST default to AST-only graph processing. Archive retrieval,
local health checks, and Animus retrieval MUST remain usable without paid semantic
enrichment. Optional semantic providers MAY extend the system only when explicitly
configured and MUST NOT be required for baseline operation.

Rationale: the first release must be installable, testable, and useful on a local
Windows machine before optional enrichment is introduced.

### VI. Explicit, Safe, and Scoped Writes

Read and health operations MUST be safe by default. Update, mine, promote, install,
and registration operations MUST be explicit, scoped to a declared World or source,
and report their effects. HoloCore MUST NOT overwrite existing configuration,
curated Archive entries, or upstream-generated files blindly. Writes MUST be
atomic where practical, preserve provenance, and distinguish transient episodic
content from verified durable knowledge.

Rationale: the system handles personal knowledge and project history; reversibility
and provenance are more important than automation that cannot be audited.

### VII. Windows-First Operational Compatibility

PowerShell commands, absolute Windows paths, local executables, and path validation
MUST be first-class supported behavior. Every documented setup and validation path
MUST have a PowerShell-compatible form. Shell-specific failures MUST be reported as
actionable dependency or configuration diagnostics.

Rationale: HoloCore is being built and operated in a Windows environment where path
and shell behavior are part of the product contract.

### VIII. Evidence-Based Verification

Every feature plan MUST identify source evidence, contract coverage, independent
acceptance scenarios, and a quickstart validation path. `status` and `doctor` MUST
report missing, stale, incompatible, or unconfigured dependencies clearly. The
source manifest MUST record the exact upstream roots, preserved capabilities,
adapter status, and compatibility aliases. Unverified claims MUST remain marked as
open questions rather than being promoted to durable knowledge.

Rationale: a multi-source coordinator is trustworthy only when its routing,
provenance, and compatibility claims can be checked locally.

## Product Boundaries

The public product vocabulary is HoloCore, Archive, Atlas, Animus, World, Sector,
Memory Shard, Signal, and Constellation. Compatibility aliases MAY expose upstream
terms such as vault, wing, room, drawer, and graph.json where users need them.

The baseline scope is a local coordinator with one configuration, one source
manifest, adapter contracts, relevance-gated search, `init`/`status`/`doctor`,
explicit `update`/`mine`/`promote` operations, safe install/bootstrap behavior, and
an acceptance fixture proving Library/Timeline/Map routing plus irrelevant-file
exclusion. Merging upstream implementations, hosted multi-user operation, and
mandatory semantic enrichment are outside the baseline.

## Required Quality Gates

- Every adapter exposes identity, capabilities, source references, lifecycle,
  error, and compatibility behavior in a documented contract.
- Every routed result carries a source label and provenance sufficient to locate the
  originating Archive entry, Atlas signal, or Animus memory shard.
- The acceptance fixture covers one structural dependency, one durable decision,
  one prior episode, and one unrelated file.
- Baseline acceptance passes with no external LLM API key.
- Install and promotion checks prove non-destructive behavior and duplicate avoidance.
- Changes are validated against the constitution, the feature specification, the
  plan/design artifacts, and all preserved upstream capabilities in scope.

## Governance

This constitution supersedes conflicting planning guidance for HoloCore. Every
implementation plan MUST include a Constitution Check before research and after
design. Every task list MUST map work to user stories, contracts, data entities,
acceptance evidence, and exact file paths.

Amendments require a documented rationale, an updated Sync Impact Report, a semantic
version change, and review of dependent Spec Kit templates. A MAJOR version removes
or redefines a non-negotiable principle; a MINOR version adds or materially expands
a principle or governed section; a PATCH version clarifies wording without changing
the contract. The last amended date changes whenever the constitution changes.

Compliance is reviewed at planning, design, implementation, and acceptance gates.
Any justified exception MUST be recorded in the plan's Complexity Tracking section
with the rejected simpler alternative and the compatibility impact. No exception
may waive capability preservation, source ownership, safe writes, or the local and
keyless baseline without an explicit constitution amendment.

**Version**: 1.0.0 | **Ratified**: 2026-07-13 | **Last Amended**: 2026-07-13
