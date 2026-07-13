# HoloCore Tasks

## Foundation

- [ ] Create `pyproject.toml` and `src/holocore/` package.
- [ ] Add typed configuration with safe path validation and non-destructive defaults.
- [ ] Add `sources.yml`/JSON manifest for the three embedded upstream projects.
- [ ] Move/copy the three engine packages into a HoloCore-owned vendored monorepo layout with provenance metadata.
- [ ] Define adapter protocols and labelled result models.

## Core commands

- [ ] Implement `holocore init`.
- [ ] Implement `holocore status`.
- [ ] Implement `holocore doctor`.
- [ ] Implement `holocore search <query>` with relevance gates.
- [ ] Implement `holocore update <world>` for Atlas refresh.
- [ ] Implement `holocore mine <world>` for scoped Animus capture.
- [ ] Implement `holocore promote <record>` for verified Archive promotion.

## Integration

- [ ] Add Obsidian Archive adapter.
- [ ] Add Graphify Atlas adapter and graph freshness checks.
- [ ] Add MemPalace Animus adapter and scoped wing/sector handling.
- [ ] Remove runtime dependence on separately installed Graphify and MemPalace commands.
- [ ] Add reviewed upstream sync endpoint/command that imports new upstream commits into staging only.
- [ ] Add compatibility aliases for the original unified-brain command names.
- [ ] Add installer with dependency detection and safe MCP registration.

## Verification

- [ ] Add unit tests for config, vault search, command construction, and doctor.
- [ ] Add acceptance fixture for Library, Timeline, Map, and irrelevant-file routing.
- [ ] Prove baseline operation without an LLM API key.
- [ ] Prove existing capabilities remain available after integration.
- [ ] Add regression checks for non-destructive install and promotion behavior.
