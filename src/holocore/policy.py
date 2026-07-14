"""Portable, client-neutral HoloCore knowledge workflow policy."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable, Mapping


@dataclass(frozen=True)
class PrivacyPolicy:
    """Explicit local/provider policy for content sent to optional LLMs."""

    allow_remote: bool = False
    consent: bool = False
    redact_patterns: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_config(cls, config: Mapping[str, object] | None = None) -> "PrivacyPolicy":
        values = dict(config or {})
        return cls(
            allow_remote=bool(values.get("allow_remote", False)),
            consent=bool(values.get("consent", False)),
            redact_patterns=tuple(str(item) for item in values.get("redact_patterns", ()) if str(item)),
        )

    @property
    def remote_allowed(self) -> bool:
        return self.allow_remote and self.consent

    def redact(self, text: str) -> str:
        result = text
        for pattern in self.redact_patterns:
            result = re.sub(pattern, "[REDACTED]", result, flags=re.I)
        return result

    def redact_messages(self, messages: Iterable[Mapping[str, str]]) -> list[dict[str, str]]:
        return [{"role": str(item.get("role", "user")), "content": self.redact(str(item.get("content", "")))} for item in messages]


def render_policy(client: str = "AI client") -> str:
    """Return the policy installed for every supported AI client."""
    return f"""# HoloCore Knowledge Policy

This project uses HoloCore through `{client}`. HoloCore is local-first and uses one
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

## Source coordination

- HoloCore is the single routing layer for project context.
- The central Second Brain is a curated Archive source, not a second automatic
  conversation-capture engine. Read its indexed, linked notes when the Archive
  route selects them; do not mine the whole vault.
- Legacy Graphify outputs and MemPalace remain compatibility or migration sources.
  Query them only when HoloCore explicitly identifies a gap or the user asks for
  historical compatibility. Do not fan out to Graphify, MemPalace, Atlas, Archive,
  and Animus independently for the same request.
- Treat generated files and databases as non-source artifacts: `holocore-out`,
  `graphify-out`, `.holocore`, `.git`, MCP logs, caches, and imported copies must
  not be ingested as new knowledge.
- Never write the same conversation or fact to both MemPalace and Animus. HoloCore
  Animus is the default destination for new episodic history.

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

## Writing and certainty

- Setup is explicit authorization for local conversation capture, deduplicated
  memory promotion, and one stale-Atlas refresh. Other writes remain explicit.
- Update an existing Archive Entry before creating a duplicate.
- Automatically promote only durable-looking summaries, facts, and decisions,
  retaining transcript provenance so they can be reviewed.
- Record uncertain claims as open questions, never as settled facts.
- Refresh Atlas after meaningful source changes.
- Store meaningful project history in Animus; do not mine the entire Archive.
- Promote verified durable knowledge into the central Archive only once, updating
  an existing note before creating a new one.
- If a route result points to another HoloCore command, do not execute it
  automatically unless the user explicitly requested that write or refresh.
"""


__all__ = ["PrivacyPolicy", "render_policy"]
