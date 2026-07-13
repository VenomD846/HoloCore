# HoloCore Implementation Plan

## Scope

Build a distinct, installable local super-app that vendors the three source applications in one distribution, while keeping their engine boundaries internally clear.

## Architecture

- `holocore` orchestration package: configuration, lifecycle, routing, health, and compatibility commands.
- Vendored engine packages ship with HoloCore; users do not install Graphify or MemPalace separately.
- Archive adapter: Obsidian vault index/search and promotion workflow.
- Atlas adapter: Graphify CLI and project-local `graphify-out\graph.json` lifecycle.
- Animus adapter: MemPalace CLI/MCP/hooks and scoped episodic mining/search.
- Source manifest: exact upstream roots, preserved capabilities, versions, sync policy, and adapter status.
- Acceptance fixture: one code dependency, one durable decision, one prior episode, and one unrelated file.

## Phases

1. Establish contracts, vendoring layout, and source manifest.
2. Create package/config/CLI skeleton with `init`, `status`, and `doctor`.
3. Implement Archive, Atlas, and Animus adapters with source-labelled routing.
4. Implement explicit update, mine, and promote writes.
5. Add installer and project bootstrap commands.
6. Run acceptance, compatibility, and regression tests.

## Constraints

- Preserve all documented source functionality inside the HoloCore distribution.
- Keep HoloCore code materially different: unified config, router, contracts, lifecycle, and vocabulary.
- AST-only Graphify is the default.
- Do not mine the entire Obsidian vault into MemPalace.
- Do not overwrite existing user files during install.
- Upstream feature sync is review-then-merge; it cannot overwrite HoloCore-owned orchestration or contracts.
