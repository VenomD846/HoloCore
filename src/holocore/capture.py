"""Local, incremental capture of Claude and Codex JSONL transcripts.

Capture and ingestion are intentionally separate operations.  A caller captures
new messages, ingests them, and only then commits the returned report.  Failed
ingestion therefore leaves the byte cursor unchanged for a later retry.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


_ROLE_ALIASES = {
    "user": "user",
    "human": "user",
    "user_message": "user",
    "assistant": "assistant",
    "ai": "assistant",
    "agent": "assistant",
    "model": "assistant",
    "agent_message": "assistant",
}
_WRAPPER_KEYS = ("message", "payload", "item", "data", "event", "record")
_NON_TEXT_TYPES = {
    "analysis",
    "computer_initialize_state",
    "function_call",
    "function_call_output",
    "image",
    "input_image",
    "metadata",
    "reasoning",
    "thinking",
    "tool",
    "tool_call",
    "tool_result",
    "tool_use",
}
_NON_MESSAGE_RECORD_TYPES = {
    "developer",
    "file_history_snapshot",
    "metadata",
    "progress",
    "queue_operation",
    "session_meta",
    "summary",
    "system",
    "token_count",
    "turn_context",
}
_ANCHOR_BYTES = 4096


def _kind(value: Mapping[str, Any]) -> str:
    raw = value.get("type", value.get("kind", ""))
    return str(raw).strip().lower().replace("-", "_")


def _is_non_text_kind(kind: str) -> bool:
    return (
        kind in _NON_TEXT_TYPES
        or "tool" in kind
        or kind.startswith(("analysis", "function_", "reasoning", "thinking"))
        or kind.endswith(("_call", "_result"))
    )


def _role(value: Mapping[str, Any]) -> str | None:
    raw: Any = value.get("role")
    if raw is None:
        for key in ("author", "sender"):
            nested = value.get(key)
            if isinstance(nested, Mapping) and nested.get("role") is not None:
                raw = nested.get("role")
                break
    if raw is not None:
        return _ROLE_ALIASES.get(str(raw).strip().lower().replace("-", "_"))
    return _ROLE_ALIASES.get(_kind(value))


def _text(value: Any) -> str:
    """Extract visible message text without walking tool or metadata payloads."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        parts = [_text(item) for item in value]
        return "\n".join(part for part in parts if part).strip()
    if not isinstance(value, Mapping):
        return ""
    if _is_non_text_kind(_kind(value)):
        return ""
    for key in ("text", "content", "parts", "value"):
        if key in value:
            found = _text(value[key])
            if found:
                return found
    return ""


def _content(value: Mapping[str, Any]) -> str:
    for key in ("content", "text", "parts", "value"):
        if key in value:
            found = _text(value[key])
            if found:
                return found
    message = value.get("message")
    return _text(message)


def _has_explicit_role(value: Mapping[str, Any]) -> bool:
    if value.get("role") is not None:
        return True
    return any(
        isinstance(value.get(key), Mapping) and value[key].get("role") is not None
        for key in ("author", "sender")
    )


def _message_candidates(value: Any) -> Iterable[dict[str, str]]:
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from _message_candidates(item)
        return
    if not isinstance(value, Mapping):
        return

    kind = _kind(value)
    if kind in _NON_MESSAGE_RECORD_TYPES or _is_non_text_kind(kind):
        return
    role = _role(value)
    if role:
        # Claude often puts the real role/content object under ``message``.
        nested = value.get("message")
        if isinstance(nested, Mapping):
            nested_messages = list(_message_candidates(nested))
            if nested_messages:
                yield from nested_messages
                return
        content = _content(value)
        if content:
            yield {"role": role, "content": content}
        return

    # Never reinterpret an explicitly non-chat role (tool, system, developer)
    # or a metadata envelope by descending into strings nested below it.
    if _has_explicit_role(value):
        return

    # Codex wraps messages in response_item.payload; Claude has similar
    # envelope records.  Restrict recursion to known wrappers so arbitrary
    # metadata strings can never become chat content.
    for key in _WRAPPER_KEYS:
        nested = value.get(key)
        if isinstance(nested, (Mapping, list, tuple)):
            yield from _message_candidates(nested)


def _message_hash(message: Mapping[str, str]) -> str:
    canonical = f"{message['role']}\0{message['content']}".encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def normalize_transcript(records: Iterable[Any]) -> list[dict[str, str]]:
    """Normalize transcript records and remove adjacent duplicate messages."""
    messages: list[dict[str, str]] = []
    previous = ""
    for record in records:
        for message in _message_candidates(record):
            digest = _message_hash(message)
            if digest == previous:
                continue
            messages.append(message)
            previous = digest
    return messages


def _parse_jsonl_bytes(data: bytes) -> tuple[list[dict[str, str]], int, int, int]:
    records: list[Any] = []
    consumed = valid = invalid = 0
    for raw_line in data.splitlines(keepends=True):
        complete = raw_line.endswith((b"\n", b"\r"))
        body = raw_line.rstrip(b"\r\n")
        if not body.strip():
            consumed += len(raw_line)
            continue
        try:
            record = json.loads(body.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            # Keep an unterminated final fragment for the next Stop hook.  A
            # malformed complete line cannot become valid later, so consume it.
            if not complete:
                break
            invalid += 1
            consumed += len(raw_line)
            continue
        valid += 1
        consumed += len(raw_line)
        records.extend(record if isinstance(record, list) else (record,))
    return normalize_transcript(records), consumed, valid, invalid


def parse_transcript_jsonl(data: str | bytes) -> list[dict[str, str]]:
    """Parse a complete or partial JSONL string into normalized messages."""
    raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    return _parse_jsonl_bytes(raw)[0]


class CaptureReport(dict[str, Any]):
    """Dictionary-compatible capture result with an explicit state commit."""

    def __init__(self, *args: Any, state_path: str | Path | None = None, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._state_path = Path(state_path).expanduser() if state_path is not None else None

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def commit(self) -> bool:
        """Atomically advance capture state; call only after ingestion succeeds."""
        if self._state_path is None:
            return False
        return CaptureStateStore(self._state_path).commit(self)


class CaptureStateStore:
    """Atomic JSON mapping of client/transcript keys to incremental cursors."""

    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser()

    @staticmethod
    def key(client: str, transcript_path: str | Path) -> str:
        source = Path(transcript_path).expanduser().resolve(strict=False)
        return f"{str(client).strip().lower()}::{os.path.normcase(str(source))}"

    def _read(self) -> dict[str, dict[str, Any]]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError):
            return {}
        if not isinstance(raw, dict):
            return {}
        result: dict[str, dict[str, Any]] = {}
        for key, value in raw.items():
            if not isinstance(key, str) or not isinstance(value, Mapping):
                continue
            try:
                offset = int(value.get("offset", 0))
            except (TypeError, ValueError):
                continue
            if offset < 0:
                continue
            result[key] = {
                "offset": offset,
                "hash": str(value.get("hash", "")),
                "last_message_hash": str(value.get("last_message_hash", "")),
            }
        return result

    def get(self, client: str, transcript_path: str | Path) -> dict[str, Any]:
        return dict(self._read().get(self.key(client, transcript_path), {}))

    def _write(self, state: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_name = ""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary_name = temporary.name
                json.dump(state, temporary, ensure_ascii=False, indent=2, sort_keys=True)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_name, self.path)
        finally:
            if temporary_name:
                try:
                    Path(temporary_name).unlink(missing_ok=True)
                except OSError:
                    pass

    def commit(self, report: Mapping[str, Any]) -> bool:
        if not report.get("committable"):
            return False
        client = str(report.get("client", "")).strip()
        source = str(report.get("source", "")).strip()
        if not client or not source:
            return False
        try:
            offset = int(report["new_offset"])
        except (KeyError, TypeError, ValueError):
            return False
        if offset < 0:
            return False
        # Reload immediately before writing so sequential store instances merge
        # rather than replacing unrelated client/transcript cursors.
        state = self._read()
        state[self.key(client, source)] = {
            "offset": offset,
            "hash": str(report.get("hash", "")),
            "last_message_hash": str(report.get("last_message_hash", "")),
        }
        self._write(state)
        return True


def _anchor_hash(data: bytes) -> str:
    """Fingerprint bytes immediately before an offset to detect file rotation."""
    return hashlib.sha256(data[-_ANCHOR_BYTES:]).hexdigest()


def _report(
    *,
    state_path: str | Path | None,
    client: str,
    source: str,
    cwd: str,
    offset: int = 0,
    new_offset: int = 0,
    messages: list[dict[str, str]] | None = None,
    content_hash: str = "",
    last_message_hash: str = "",
    committable: bool = False,
    reason: str = "",
) -> CaptureReport:
    messages = messages or []
    return CaptureReport(
        {
            "messages": messages,
            "source": source,
            "cwd": cwd,
            "client": client,
            "offset": offset,
            "new_offset": new_offset,
            "hash": content_hash,
            "last_message_hash": last_message_hash,
            "committable": committable,
            "skipped": not messages,
            "reason": reason,
        },
        state_path=state_path,
    )


def capture_hook(
    payload: Mapping[str, Any], client: str, state_path: str | Path
) -> CaptureReport:
    """Capture only uncommitted transcript bytes without raising to a hook.

    The report's ``commit()`` method (or :func:`commit_capture`) must be called
    explicitly after the messages have been ingested successfully.
    """
    client_name = str(client).strip().lower() or "unknown"
    fallback_cwd = str(Path.cwd().resolve())
    source = ""
    cwd = fallback_cwd
    try:
        if not isinstance(payload, Mapping):
            return _report(state_path=state_path, client=client_name, source="", cwd=fallback_cwd, reason="invalid-payload")
        cwd_raw = payload.get("cwd")
        cwd_path = Path(str(cwd_raw)).expanduser() if cwd_raw else Path.cwd()
        cwd_path = cwd_path.resolve(strict=False)
        cwd = str(cwd_path)
        transcript_raw = payload.get("transcript_path")
        if not isinstance(transcript_raw, (str, os.PathLike)) or not str(transcript_raw).strip():
            return _report(state_path=state_path, client=client_name, source="", cwd=cwd, reason="missing-transcript-path")
        transcript = Path(transcript_raw).expanduser()
        if not transcript.is_absolute():
            transcript = cwd_path / transcript
        transcript = transcript.resolve(strict=False)
        source = str(transcript)
        if not transcript.is_file():
            return _report(state_path=state_path, client=client_name, source=source, cwd=cwd, reason="missing-transcript")

        state = CaptureStateStore(state_path).get(client_name, transcript)
        offset = int(state.get("offset", 0))
        previous_hash = str(state.get("hash", ""))
        previous_message_hash = str(state.get("last_message_hash", ""))
        anchor = b""
        with transcript.open("rb") as handle:
            size = os.fstat(handle.fileno()).st_size
            if offset > size:  # The append-only file was replaced or truncated.
                offset = 0
                previous_hash = ""
                previous_message_hash = ""
            elif offset:
                anchor_start = max(0, offset - _ANCHOR_BYTES)
                handle.seek(anchor_start)
                anchor = handle.read(offset - anchor_start)
                if previous_hash and _anchor_hash(anchor) != previous_hash:
                    # Same path, different transcript (rotation/rewrite).
                    offset = 0
                    previous_hash = ""
                    previous_message_hash = ""
                    anchor = b""
            handle.seek(offset)
            appended = handle.read()
        if not appended:
            return _report(
                state_path=state_path, client=client_name, source=source, cwd=cwd,
                offset=offset, new_offset=offset, content_hash=previous_hash,
                last_message_hash=previous_message_hash, reason="no-new-bytes",
            )

        parsed, consumed, valid, invalid = _parse_jsonl_bytes(appended)
        if consumed == 0:
            reason = "invalid-transcript" if invalid else "incomplete-transcript"
            return _report(
                state_path=state_path, client=client_name, source=source, cwd=cwd,
                offset=offset, new_offset=offset, content_hash=previous_hash,
                last_message_hash=previous_message_hash, reason=reason,
            )

        messages: list[dict[str, str]] = []
        last_hash = previous_message_hash
        for message in parsed:
            digest = _message_hash(message)
            if digest == last_hash:
                continue
            messages.append(message)
            last_hash = digest
        new_offset = offset + consumed
        content_hash = _anchor_hash(anchor + appended[:consumed])
        if messages:
            reason = ""
        elif valid == 0 and invalid:
            reason = "invalid-transcript"
        elif parsed:
            reason = "duplicate-messages"
        else:
            reason = "no-messages"
        return _report(
            state_path=state_path, client=client_name, source=source, cwd=cwd,
            offset=offset, new_offset=new_offset, messages=messages,
            content_hash=content_hash, last_message_hash=last_hash,
            committable=valid > 0, reason=reason,
        )
    except Exception as exc:  # Hook entrypoints must never break the AI client.
        return _report(
            state_path=state_path, client=client_name, source=source, cwd=cwd,
            reason=f"capture-error:{type(exc).__name__}",
        )


def commit_capture(report: Mapping[str, Any], state_path: str | Path | None = None) -> bool:
    """Explicitly commit a capture report after successful downstream ingestion."""
    if isinstance(report, CaptureReport) and state_path is None:
        return report.commit()
    if state_path is None:
        return False
    return CaptureStateStore(state_path).commit(report)


# Descriptive aliases retained for hook installers and direct library callers.
capture_from_hook = capture_hook
capture_transcript = capture_hook


__all__ = [
    "CaptureReport",
    "CaptureStateStore",
    "capture_from_hook",
    "capture_hook",
    "capture_transcript",
    "commit_capture",
    "normalize_transcript",
    "parse_transcript_jsonl",
]
