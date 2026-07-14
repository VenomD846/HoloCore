"""Non-blocking Claude/Codex hook entrypoint for automatic conversation capture."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from .capture import capture_hook
from .engine import HoloCoreEngine


def _fallback_messages(payload: Mapping[str, Any]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for key in ("prompt", "user_message"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            messages.append({"role": "user", "content": value.strip()})
            break
    value = payload.get("last_assistant_message")
    if isinstance(value, str) and value.strip():
        messages.append({"role": "assistant", "content": value.strip()})
    return messages


def run(payload: Mapping[str, Any], client: str) -> dict[str, Any]:
    root = Path(str(payload.get("cwd") or Path.cwd())).expanduser().resolve(strict=False)
    state = root / ".holocore" / "capture-state.json"
    report = capture_hook(payload, client, state)
    messages = list(report.get("messages", [])) or _fallback_messages(payload)
    if not messages:
        return {"captured": False, "reason": report.get("reason", "no-messages")}
    engine = HoloCoreEngine(root)
    result = engine.ingest_chat(messages, source=f"{client}:{report.get('source') or 'hook'}")
    # Advance the transcript cursor immediately after successful ingestion so
    # an unrelated Atlas refresh failure cannot cause duplicate LLM calls.
    committed = report.commit()
    try:
        inbox = engine.sync_inbox()
        atlas = inbox.get("atlas") or engine.ensure_atlas()
    except Exception as exc:  # Capture must never break the parent AI client.
        inbox = {"synced": False, "warning": type(exc).__name__}
        atlas = {"refreshed": False, "warning": type(exc).__name__}
    return {
        "captured": True,
        "messages": len(messages),
        "committed": committed,
        "archive_entry": result.get("archive_entry"),
        "inbox": inbox,
        "atlas": atlas,
    }


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--client", choices=("claude", "codex"), required=True)
    args = parser.parse_args()
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        result = run(payload if isinstance(payload, dict) else {}, args.client)
    except Exception as exc:
        result = {"captured": False, "reason": f"hook-error:{type(exc).__name__}"}
    print(json.dumps(result, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
