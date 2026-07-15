"""Non-blocking Claude/Codex hook entrypoint for automatic conversation capture."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from .capture import capture_hook
from .engine import HoloCoreEngine
from .config import Config


def _world_root(cwd: Path) -> Path:
    """Resolve a hook cwd inside the registered World that owns it."""
    try:
        home = Config._selected_home()
        if home:
            for item in __import__("holocore.home", fromlist=["HomeManager"]).HomeManager(home).list_worlds().get("worlds", []):
                candidate = Path(str(item.get("root", ""))).resolve()
                if candidate and (cwd == candidate or candidate in cwd.parents):
                    return candidate
    except Exception:
        pass
    return cwd


def _diagnostic(root: Path, payload: Mapping[str, Any], result: Mapping[str, Any]) -> None:
    path = Config.load(root=root).state_dir / "capture-diagnostics.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "event": payload.get("hook_event_name", "unknown"), "session_id": payload.get("session_id"), "turn_id": payload.get("turn_id"), "cwd": str(root), "transcript_path": payload.get("transcript_path"), "captured": result.get("captured", False), "reason": result.get("reason"), "messages": result.get("messages", 0), "committed": result.get("committed", False), "archive_entry": result.get("archive_entry")}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")


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
    root = _world_root(Path(str(payload.get("cwd") or Path.cwd())).expanduser().resolve(strict=False))
    state = root / ".holocore" / "capture-state.json"
    report = capture_hook(payload, client, state)
    messages = list(report.get("messages", [])) or _fallback_messages(payload)
    if not messages:
        result = {"captured": False, "reason": report.get("reason", "no-messages")}; _diagnostic(root, payload, result); return result
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
    result = {
        "captured": True,
        "messages": len(messages),
        "committed": committed,
        "archive_entry": result.get("archive_entry"),
        "inbox": inbox,
        "atlas": atlas,
    }; _diagnostic(root, payload, result); return result


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
    # Hook response schemas differ across clients. Keep the rich capture
    # result in capture-diagnostics.jsonl and emit no stdout so Codex, Claude,
    # and future clients cannot reject an otherwise successful capture.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
