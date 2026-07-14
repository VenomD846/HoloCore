# HoloCore Knowledge Policy

This project uses HoloCore through `AI client`. HoloCore is local-first and uses one
check-first, non-recursive route for each request.

## Start of a project session

1. Read the project instruction file once.
2. Run `holocore status` before broad orientation.
3. Check Atlas freshness before using structural results. HoloCore refreshes a
   missing or stale Atlas once before search; do not trigger a duplicate refresh.
4. Do not repeat the full bootstrap sequence during the same session.

## Retrieval order

1. **Atlas first:** use the project graph to identify relevant files, symbols, and
   relationships.
2. **Archive second:** search the corresponding index and linked durable notes for
   verified rules, decisions, and guidance.
3. **Animus third, only when relevant:** recall prior work, errors, attempts,
   decisions, or conversations from the current World and Sector.
4. **Exact sources last:** open only the project files identified by the preceding
   checks.

Build one route plan and execute it once. Never route a HoloCore search back into itself.
Each selected subsystem may run at most once per request.

## Knowledge ownership

- Archive owns verified, durable, reusable knowledge.
- Atlas owns rebuildable structural facts from project files.
- Animus owns episodic history and refined conversation memory.
- Project files remain the source of truth for exact implementation details.
- Do not copy the same raw content into every store.

## Simple distinction

- **Archive** = verified knowledge.
- **Atlas** = structural map.
- **Animus** = remembered history.
- **World** = project.
- **Sector** = area inside a project.
- **Memory Shard** = raw remembered fragment.
- **Archive Entry** = polished durable note.
- **Signal** = one mapped thing.
- **Constellation** = group of related mapped things.
- **Deck** = bounded context inside a World.
- **Signal** = a named concept or entity tracked by Animus.
- **Chronicle** = the temporal history of a Signal.

## Writing and certainty

- Setup is explicit authorization for local conversation capture, deduplicated
  memory promotion, and one stale-Atlas refresh. Other writes remain explicit.
- Update an existing Archive Entry before creating a duplicate.
- Automatically promote only durable-looking summaries, facts, and decisions,
  retaining transcript provenance so they can be reviewed.
- Record uncertain claims as open questions, never as settled facts.
- Refresh Atlas after meaningful source changes.
- Store meaningful project history in Animus; do not mine the entire Archive.
