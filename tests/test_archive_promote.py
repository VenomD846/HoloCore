from __future__ import annotations

from pathlib import Path

from holocore.archive_promote import MANAGED, promote_sources


def test_promote_reasons_deduplicates_updates_and_indexes(tmp_path: Path) -> None:
    source = tmp_path / "project"
    docs = source / "docs"
    docs.mkdir(parents=True)
    decision = docs / "decision.md"
    decision.write_text("# Storage Decision\n\nWe decided all World data will live in HoloCore Home.\n", encoding="utf-8")
    (source / "src").mkdir()
    (source / "src" / "noise.txt").write_text("implementation noise", encoding="utf-8")
    vault = tmp_path / "world" / "Archive"

    first = promote_sources(source, vault, world="demo")
    second = promote_sources(source, vault, world="demo")
    decision.write_text("# Storage Decision\n\nWe decided all World data will live centrally in HoloCore Home.\n", encoding="utf-8")
    third = promote_sources(source, vault, world="demo")

    assert len(first["created"]) == 1
    note = vault / first["created"][0]
    content = note.read_text(encoding="utf-8")
    assert MANAGED in content
    assert "## Summary" in content
    assert "source_id:" in content and "source_hash:" in content
    assert second["unchanged"] == first["created"]
    assert third["updated"] == first["created"]
    assert "src/noise.txt" in first["excluded"]
    assert "[[wiki/storage-decision" in (vault / "system" / "index.md").read_text(encoding="utf-8")


def test_promote_dry_run_and_user_owned_conflict(tmp_path: Path) -> None:
    source = tmp_path / "docs"
    source.mkdir()
    (source / "guide.md").write_text("# Useful Guide\n\nPrefer local reasoning.\n", encoding="utf-8")
    vault = tmp_path / "Archive"

    planned = promote_sources(source, vault, scope="all", dry_run=True)
    assert planned["created"]
    assert not vault.exists()

    written = promote_sources(source, vault, scope="all")
    note = vault / written["created"][0]
    note.write_text("# User-owned replacement\n", encoding="utf-8")
    conflict = promote_sources(source, vault, scope="all")
    assert conflict["conflicts"] == written["created"]
    assert note.read_text(encoding="utf-8") == "# User-owned replacement\n"


def test_promote_excludes_generated_client_and_holocore_policy_files(tmp_path: Path) -> None:
    source = tmp_path / "project"
    source.mkdir()
    (source / "AGENTS.md").write_text(
        "# HoloCore Knowledge Policy\n\nGenerated client policy.\n", encoding="utf-8"
    )
    generated = source / ".claude"
    generated.mkdir()
    (generated / "notes.md").write_text("# Generated command\n", encoding="utf-8")
    docs = source / "docs"
    docs.mkdir()
    (docs / "product.md").write_text("# Product Concept\n\nA real project note.\n", encoding="utf-8")

    result = promote_sources(source, tmp_path / "Archive", scope="docs")

    assert len(result["created"]) == 1
    assert "AGENTS.md" in result["excluded"]
    assert ".claude/notes.md" in result["excluded"]
