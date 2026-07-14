from pathlib import Path
from datetime import date

import pytest

from holocore.archive import (
    Archive,
    ArchiveConflictError,
    ArchiveValidationError,
    PathTraversalError,
)


def _body(name: str = "Archive") -> str:
    return f"## For future Claude\nThis note preserves verified context about [[{name}]].\n\n## Details\nNative and local."


def test_init_search_read_and_provenance(tmp_path: Path) -> None:
    archive = Archive(tmp_path / "vault")
    initialized = archive.init_vault()
    assert initialized["initialized"] is True
    assert (archive.vault / "system" / "index.md").exists()

    created = archive.create(
        "wiki/native.md",
        _body(),
        frontmatter={
            "type": "decision",
            "date": "2026-07-13",
            "tags": ["decision"],
            "ai-first": True,
        },
        provenance={"source": "spec.md", "line": 120},
    )
    assert created["provenance"] == {"source": "spec.md", "line": 120}
    assert archive.search("Native")[0]["source_id"] == "archive"
    note = archive.read("wiki/native.md")
    assert note["frontmatter"]["type"] == "decision"
    assert note["provenance"] == {"source": "spec.md", "line": 120}


def test_create_update_validate_and_conflict(tmp_path: Path) -> None:
    archive = Archive(tmp_path / "vault")
    archive.init_vault()
    archive.create("wiki/entry.md", _body(), provenance="fixture")
    before = archive.read("wiki/entry.md")["content"]

    archive.update("wiki/entry.md", append="A preserved addition.", set_fields={"status": "active"})
    updated = archive.read("wiki/entry.md")
    assert "A preserved addition." in updated["content"]
    assert updated["provenance"] == "fixture"
    assert updated["frontmatter"]["updated"] == date.today().isoformat()
    assert archive.validate("wiki/entry.md")["ok"] is True

    with pytest.raises(ArchiveConflictError):
        archive.create("wiki/entry.md", _body())
    with pytest.raises(ArchiveConflictError):
        archive.update("wiki/entry.md", append="stale", expected_content=before)
    with pytest.raises(ArchiveValidationError):
        archive.create("wiki/invalid.md", "---\ntype: note\n---\n\nNo preamble")


@pytest.mark.parametrize("path", ["../escape.md", "../../escape.md", ".obsidian/private.md"])
def test_path_traversal_and_protected_paths_are_rejected(tmp_path: Path, path: str) -> None:
    archive = Archive(tmp_path / "vault")
    archive.init_vault()
    with pytest.raises(PathTraversalError):
        archive.create(path, _body())


def test_backlinks_health_and_bounded_scan(tmp_path: Path) -> None:
    archive = Archive(tmp_path / "vault", max_files=3)
    archive.init_vault()
    archive.create("wiki/target.md", _body("Source"), provenance="fixture")
    archive.create("wiki/ref.md", _body("target"), provenance="fixture")
    backlinks = archive.backlinks("wiki/target.md")
    assert backlinks["backlinks"] == ["wiki/ref.md"]

    (archive.vault / "wiki" / "legacy.md").write_text("legacy [[Missing]]", encoding="utf-8")
    health = archive.health()
    assert health["notes_scanned"] == 3
    assert health["capped"] is True
    assert health["invalid_ai_first"]["count"] >= 1
    assert health["wanted_notes"]["count"] >= 1


def test_bom_frontmatter_is_valid(tmp_path: Path) -> None:
    archive = Archive(tmp_path / "vault")
    archive.init_vault()
    text = "\ufeff---\ntype: note\ndate: 2026-07-13\ntags: [note]\nai-first: true\n---\n\n" + _body()
    (archive.vault / "bom.md").write_text(text, encoding="utf-8")
    assert archive.validate("bom.md")["ok"] is True


def test_plain_create_adds_ai_preamble_and_search_preserves_provenance(tmp_path: Path) -> None:
    archive = Archive(tmp_path / "vault")
    archive.init_vault()
    archive.create("wiki/plain.md", "A durable native decision.", provenance="spec:FR-009")
    note = archive.read("wiki/plain.md")
    assert "## For future Claude" in note["content"]
    result = archive.search("durable")[0]
    assert result["provenance"] == "spec:FR-009"
    assert result["ai_first"] is True


@pytest.mark.parametrize("path", ["raw/source.md", ".OBSIDIAN/private.md"])
def test_writes_reject_immutable_or_case_varied_protected_paths(tmp_path: Path, path: str) -> None:
    archive = Archive(tmp_path / "vault")
    archive.init_vault()
    with pytest.raises(PathTraversalError):
        archive.create(path, _body())


def test_read_returns_a_bounded_prefix_and_health_reports_missing_frontmatter(tmp_path: Path) -> None:
    archive = Archive(tmp_path / "vault", read_cap=80)
    archive.init_vault()
    archive.create("wiki/long.md", _body() + (" x" * 200), provenance="fixture")
    note = archive.read("wiki/long.md")
    assert len(note["content"]) == 80
    assert note["truncated"] is True

    (archive.vault / "wiki" / "legacy.md").write_text("legacy", encoding="utf-8")
    health = archive.health()
    assert health["missing_frontmatter"]["sample"] == ["wiki/legacy.md"]
