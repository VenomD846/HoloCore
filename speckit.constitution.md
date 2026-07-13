# HoloCore Constitution

## Mission

HoloCore is one local knowledge super-app combining the best capabilities of Obsidian Second Brain, Graphify, and MemPalace while remaining a distinct product with a unified workflow.

## Non-negotiable principles

1. **Capability preservation:** Existing upstream capabilities remain available through compatible adapters and explicit acceptance tests.
2. **Additive evolution:** New functionality may extend behavior, but must not silently remove or weaken an existing capability.
3. **Distinct implementation:** HoloCore owns its orchestration, configuration, routing, naming, lifecycle, and user experience; it must not be a thin repackaging or identical fork.
4. **Source ownership:** Archive/Library owns curated durable knowledge; Atlas/Map owns structural relationships; Animus/Timeline owns episodic history.
5. **Relevance-gated retrieval:** Do not query every backend for every task.
6. **Local-first baseline:** AST mapping, local retrieval, and health checks work without an external LLM API key.
7. **Safe writes:** Writes are explicit, scoped, atomic where possible, and never overwrite user configuration or curated notes blindly.
8. **Windows compatibility:** PowerShell and Windows paths are first-class supported behavior.

## Quality gates

- Every merged capability has an adapter contract and an acceptance test.
- Upstream source copies remain traceable in a source manifest.
- `status` and `doctor` report missing or incompatible dependencies clearly.
- The router labels results by source and records why a source was queried.
- Changes are validated against both new HoloCore behavior and preserved upstream behavior.

## Vocabulary

Public terms are HoloCore, Archive, Atlas, Animus, World, Sector, Memory Shard, Signal, and Constellation. Compatibility aliases may expose upstream terms where required.
