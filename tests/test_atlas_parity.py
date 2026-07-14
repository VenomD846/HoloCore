from pathlib import Path

from holocore.atlas import Atlas
from holocore.atlas_exports import export_atlas


def test_constellations_audit_and_queries_are_deterministic(tmp_path: Path):
    (tmp_path / "a.py").write_text("from b import run\ndef start():\n    return run()\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("def run():\n    return 1\n", encoding="utf-8")
    atlas = Atlas(tmp_path); atlas.refresh()
    first = atlas.constellations(); second = atlas.constellations()
    assert first == second and first[0]["id"].startswith("constellation:")
    assert atlas.explain("run")["resolved"]
    assert atlas.neighborhood("run")["nodes"]
    audit = atlas.audit()
    assert audit["source_coverage"]["files"] == 2


def test_graphify_style_exports_write_manifest(tmp_path: Path):
    (tmp_path / "main.py").write_text("def main():\n    return True\n", encoding="utf-8")
    atlas = Atlas(tmp_path); atlas.refresh()
    result = export_atlas(atlas, tmp_path / "exports")
    assert set(result["formats"]) == {"json", "html", "markdown", "manifest"}
    assert (tmp_path / "exports" / "graph.json").is_file()
    assert (tmp_path / "exports" / "graph.html").is_file()
