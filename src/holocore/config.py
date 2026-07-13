from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Config:
    vault: Path
    state_dir: Path
    llm: dict | None = None

    @classmethod
    def for_world(cls, root: Path) -> "Config":
        root = root.resolve(); return cls(Path(os.getenv("HOLOCORE_VAULT", root / "Archive")), Path(os.getenv("HOLOCORE_STATE", root / ".holocore")), None)

    @classmethod
    def load(cls, path: Path | None = None, root: Path | None = None) -> "Config":
        root = (root or Path.cwd()).resolve(); default = cls.for_world(root); path = path or root / ".holocore" / "config.json"
        if not path.exists(): return default
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(Path(raw.get("archive", raw.get("vault", default.vault))), Path(raw.get("state_dir", path.parent)), raw.get("llm"))

    @property
    def atlas_path(self) -> Path: return self.state_dir / "atlas.json"

    @property
    def animus_path(self) -> Path: return self.state_dir / "animus.db"

    def save(self, path: Path | None = None) -> Path:
        path = path or self.state_dir / "world.json"; path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists(): path.write_text(json.dumps({"version": 1, "archive": str(self.vault), "state_dir": str(self.state_dir), "llm": self.llm or {"provider": "local"}}, indent=2), encoding="utf-8")
        return path
