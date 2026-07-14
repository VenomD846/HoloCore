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
    home: Path | None = None
    world_id: str | None = None
    animus: Path | None = None
    raw_chats: Path | None = None
    shared_archive: Path | None = None

    @classmethod
    def for_world(cls, root: Path) -> "Config":
        root = root.resolve(); return cls(Path(os.getenv("HOLOCORE_VAULT", root / "Archive")), Path(os.getenv("HOLOCORE_STATE", root / ".holocore")), None)

    @classmethod
    def load(cls, path: Path | None = None, root: Path | None = None) -> "Config":
        root = (root or Path.cwd()).resolve(); default = cls.for_world(root); path = path or root / ".holocore" / "config.json"
        if not path.exists(): return default
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            Path(raw.get("archive", raw.get("vault", default.vault))),
            Path(raw.get("state_dir", path.parent)),
            raw.get("llm"),
            Path(raw["home"]) if raw.get("home") else None,
            str(raw.get("world_id")) if raw.get("world_id") else None,
            Path(raw["animus"]) if raw.get("animus") else None,
            Path(raw["raw_chats"]) if raw.get("raw_chats") else None,
            Path(raw["shared_archive"]) if raw.get("shared_archive") else None,
        )

    @property
    def atlas_path(self) -> Path: return self.state_dir / "atlas.json"

    @property
    def animus_path(self) -> Path: return self.animus or self.state_dir / "animus.db"

    @property
    def raw_chats_path(self) -> Path: return self.raw_chats or self.state_dir / "raw-chats"

    def save(self, path: Path | None = None) -> Path:
        path = path or self.state_dir / "world.json"; path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists(): path.write_text(json.dumps({"version": 2, "archive": str(self.vault), "shared_archive": str(self.shared_archive) if self.shared_archive else None, "state_dir": str(self.state_dir), "home": str(self.home) if self.home else None, "world_id": self.world_id, "animus": str(self.animus) if self.animus else None, "raw_chats": str(self.raw_chats) if self.raw_chats else None, "llm": self.llm or {"provider": "local"}}, indent=2), encoding="utf-8")
        return path
