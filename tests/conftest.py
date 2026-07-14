from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_holocore_home(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> Path:
    """Keep every test away from the real user-level Home pointer and Home."""
    user_root = tmp_path_factory.mktemp("holocore-user")
    config_home = user_root / "config"
    home = (user_root / "home").resolve()
    config_home.mkdir()
    (config_home / "home.json").write_text(
        json.dumps({"schema_version": 1, "home": str(home)}, indent=2) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("HOLOCORE_CONFIG_HOME", str(config_home))
    return home
