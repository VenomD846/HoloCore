import json

from holocore.capture import (
    CaptureStateStore,
    capture_hook,
    commit_capture,
    parse_transcript_jsonl,
)
from holocore.capture_hook import run as run_capture_hook
from holocore.config import Config
from holocore.install import bootstrap_project


def jsonl(*records):
    return "".join(json.dumps(record) + "\n" for record in records)


def test_parses_claude_and_codex_shapes_and_skips_non_message_content():
    transcript = jsonl(
        {"type": "session_meta", "payload": {"cwd": "/private"}},
        {"role": "system", "message": {"role": "user", "content": "nested metadata"}},
        {"type": "user", "message": {"role": "user", "content": "Plan it"}},
        {"type": "user", "message": {"role": "user", "content": "Plan it"}},
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "text": "private reasoning"},
                    {"type": "text", "text": "Done"},
                    {"type": "tool_use", "name": "shell", "input": {"command": "secret"}},
                    {"type": "web_search_tool_result", "content": "search output"},
                ],
            },
        },
        {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "tool output"}]}},
        {
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": {"value": "Ship it"}}],
            },
        },
        {"type": "event_msg", "payload": {"type": "user_message", "message": "Thanks"}},
        {"role": "assistant", "message": {"content": {"text": "Nested text"}}},
    )
    assert parse_transcript_jsonl(transcript) == [
        {"role": "user", "content": "Plan it"},
        {"role": "assistant", "content": "Done"},
        {"role": "assistant", "content": "Ship it"},
        {"role": "user", "content": "Thanks"},
        {"role": "assistant", "content": "Nested text"},
    ]


def test_capture_is_incremental_and_commits_only_explicitly(tmp_path):
    transcript = tmp_path / "session.jsonl"
    state_path = tmp_path / "capture-state.json"
    transcript.write_text(
        jsonl({"message": {"role": "user", "content": {"text": "hello"}}}),
        encoding="utf-8",
    )
    payload = {"transcript_path": transcript.name, "cwd": str(tmp_path)}

    first = capture_hook(payload, "codex", state_path)
    assert first.messages == [{"role": "user", "content": "hello"}]
    assert first.offset == 0
    assert first.new_offset == transcript.stat().st_size
    assert not state_path.exists()

    # A failed ingestion can retry because capture itself never advances state.
    assert capture_hook(payload, "codex", state_path).messages == first.messages
    assert commit_capture(first)
    assert capture_hook(payload, "codex", state_path).reason == "no-new-bytes"

    # Dedupe remains adjacent across the committed byte boundary.
    with transcript.open("a", encoding="utf-8") as handle:
        handle.write(jsonl(
            {"role": "user", "content": "hello"},
            {"payload": {"type": "agent_message", "content": "welcome"}},
        ))
    second = capture_hook(payload, "codex", state_path)
    assert second.messages == [{"role": "assistant", "content": "welcome"}]
    assert second.commit()

    stored = json.loads(state_path.read_text(encoding="utf-8"))
    key = CaptureStateStore.key("codex", transcript)
    assert stored[key]["offset"] == transcript.stat().st_size
    assert len(stored[key]["hash"]) == 64
    assert not list(tmp_path.glob(".capture-state.json.*.tmp"))


def test_partial_final_line_is_retried_from_its_byte_boundary(tmp_path):
    transcript = tmp_path / "claude.jsonl"
    state_path = tmp_path / "state.json"
    complete = jsonl({"role": "user", "content": "first"}).encode()
    partial = b'{"role":"assistant","content":"sec'
    transcript.write_bytes(complete + partial)

    first = capture_hook({"transcript_path": str(transcript), "cwd": str(tmp_path)}, "claude", state_path)
    assert first.messages == [{"role": "user", "content": "first"}]
    assert first.new_offset == len(complete)
    assert first.commit()

    with transcript.open("ab") as handle:
        handle.write(b'ond"}\n')
    second = capture_hook({"transcript_path": str(transcript), "cwd": str(tmp_path)}, "claude", state_path)
    assert second.messages == [{"role": "assistant", "content": "second"}]
    assert second.offset == len(complete)


def test_missing_corrupt_and_invalid_inputs_return_safe_skipped_reports(tmp_path):
    state_path = tmp_path / "state.json"
    state_path.write_text("not json", encoding="utf-8")

    missing_path = capture_hook({"cwd": str(tmp_path)}, "claude", state_path)
    assert missing_path.skipped and missing_path.reason == "missing-transcript-path"
    assert not missing_path.commit()

    missing_file = capture_hook(
        {"cwd": str(tmp_path), "transcript_path": "missing.jsonl"}, "claude", state_path
    )
    assert missing_file.skipped and missing_file.reason == "missing-transcript"

    invalid = tmp_path / "invalid.jsonl"
    invalid.write_text("{unfinished", encoding="utf-8")
    report = capture_hook(
        {"cwd": str(tmp_path), "transcript_path": invalid.name}, "claude", state_path
    )
    assert report.skipped and report.reason == "incomplete-transcript"
    assert report.new_offset == 0

    assert capture_hook(None, "claude", state_path).reason == "invalid-payload"


def test_state_is_scoped_by_client_and_resolved_transcript(tmp_path):
    transcript = tmp_path / "shared.jsonl"
    transcript.write_text(jsonl({"role": "human", "content": "same file"}), encoding="utf-8")
    state_path = tmp_path / "state.json"
    payload = {"cwd": str(tmp_path), "transcript_path": transcript.name}

    codex = capture_hook(payload, "codex", state_path)
    assert codex.commit()
    claude = capture_hook(payload, "claude", state_path)
    assert claude.messages == [{"role": "user", "content": "same file"}]
    assert claude.commit()

    stored = json.loads(state_path.read_text(encoding="utf-8"))
    assert set(stored) == {
        CaptureStateStore.key("codex", transcript),
        CaptureStateStore.key("claude", transcript),
    }


def test_capture_hook_end_to_end_is_incremental_without_duplicate_ingestion(
    tmp_path, isolated_holocore_home
):
    world = tmp_path / "captured-world"
    bootstrap_project(world, init_git=False, platforms=[], home=isolated_holocore_home)
    transcript = world / "session.jsonl"
    transcript.write_text(
        jsonl({"role": "user", "content": "First captured statement."}),
        encoding="utf-8",
    )
    payload = {"cwd": str(world), "transcript_path": str(transcript)}

    first = run_capture_hook(payload, "codex")
    assert first["captured"] is True
    assert first["messages"] == 1
    assert first["committed"] is True
    config = Config.load(root=world)
    assert len(list(config.raw_chats_path.glob("*.json"))) == 1
    assert len(list(config.vault.glob("wiki/memory/*.md"))) == 1

    second = run_capture_hook(payload, "codex")
    assert second == {"captured": False, "reason": "no-new-bytes"}
    assert len(list(config.raw_chats_path.glob("*.json"))) == 1
    assert len(list(config.vault.glob("wiki/memory/*.md"))) == 1

    with transcript.open("a", encoding="utf-8") as handle:
        handle.write(
            jsonl(
                {"role": "user", "content": "First captured statement."},
                {"role": "assistant", "content": "Second captured statement."},
            )
        )
    third = run_capture_hook(payload, "codex")
    assert third["captured"] is True
    assert third["messages"] == 1
    assert third["committed"] is True
    assert len(list(config.raw_chats_path.glob("*.json"))) == 2
    assert len(list(config.vault.glob("wiki/memory/*.md"))) == 2
    assert run_capture_hook(payload, "codex") == {
        "captured": False,
        "reason": "no-new-bytes",
    }

    state = json.loads((world / ".holocore/capture-state.json").read_text(encoding="utf-8"))
    key = CaptureStateStore.key("codex", transcript)
    assert state[key]["offset"] == transcript.stat().st_size
