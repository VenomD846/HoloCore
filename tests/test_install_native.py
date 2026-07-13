from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from holocore.install import bootstrap_project


def test_bootstrap_creates_native_files_for_all_clients(tmp_path: Path) -> None:
    root = tmp_path / "World with spaces"
    report = bootstrap_project(root)

    expected = {
        ".holocore/config.json",
        ".holocore/instructions.md",
        ".holocore/mcp.json",
        ".codex/config.toml",
        ".mcp.json",
        ".gemini/settings.json",
        ".cursor/mcp.json",
        ".cursor/rules/holocore.mdc",
        "opencode.json",
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        "HOLOCORE.md",
    }
    assert expected <= {path.relative_to(root).as_posix() for path in report.created}
    assert json.loads((root / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["holocore"]["cwd"] == str(root.resolve())
    assert json.loads((root / "opencode.json").read_text(encoding="utf-8"))["mcp"]["holocore"]["type"] == "local"


def test_bootstrap_never_overwrites_and_reports_skips(tmp_path: Path) -> None:
    root = tmp_path / "world"
    root.mkdir()
    agents = root / "AGENTS.md"
    agents.write_text("user owned\n", encoding="utf-8")

    first = bootstrap_project(root, platforms=["codex", "opencode"])
    config_before = (root / ".holocore/config.json").read_bytes()
    second = bootstrap_project(root, platforms=["codex", "opencode"])

    assert agents.read_text(encoding="utf-8") == "user owned\n"
    assert (root / ".holocore/config.json").read_bytes() == config_before
    assert agents in first.skipped
    assert agents in second.skipped
    assert root / ".holocore/config.json" in second.skipped


def test_git_is_initialized_only_when_requested(tmp_path: Path) -> None:
    root = tmp_path / "world"
    with patch("holocore.install.subprocess.run") as run:
        bootstrap_project(root, platforms=[], init_git=False)
        run.assert_not_called()

        bootstrap_project(root, platforms=[], init_git=True)
        run.assert_called_once()
        assert run.call_args.args[0][:2] == ["git", "init"]
