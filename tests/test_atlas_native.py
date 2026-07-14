import json
from pathlib import Path
import shutil
import subprocess

import pytest

from holocore.atlas import Atlas, content_hash


def _project(tmp_path: Path) -> Path:
    (tmp_path / "service.py").write_text(
        "from util import helper\n\nclass Service:\n    def run(self):\n        return helper()\n",
        encoding="utf-8",
    )
    (tmp_path / "util.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Example\n", encoding="utf-8")
    return tmp_path


def test_native_refresh_writes_node_link_graph_and_queries(tmp_path):
    root = _project(tmp_path)
    atlas = Atlas(root)
    graph = atlas.refresh()

    assert graph["directed"] is True
    assert graph["multigraph"] is False
    assert graph["graph"]["generator"] == "holocore-atlas"
    assert graph["graph"]["extracted_files"] == 3
    assert json.loads(atlas.graph_path.read_text(encoding="utf-8"))["links"]
    assert any(n["label"] == "Example" and n["file_type"] == "generic" for n in graph["nodes"])
    assert len(content_hash(root / "util.py")) == 64

    assert atlas.search("Service")[0]["label"] == "Service"
    assert [node["label"] for node in atlas.path("run", "helper")] == ["run()", "helper()"]
    affected = atlas.affected("helper")
    assert affected[0]["label"] == "run()"
    assert affected[0]["via_relation"] == "calls"
    assert atlas.freshness()["fresh"] is True


def test_refresh_is_incremental_and_prunes_deleted_files(tmp_path):
    root = _project(tmp_path)
    atlas = Atlas(root)
    first = atlas.refresh()
    helper_id = next(n["id"] for n in first["nodes"] if n["label"] == "helper()")

    second = atlas.refresh()
    assert second["graph"]["extracted_files"] == 0
    assert second["graph"]["reused_files"] == 3

    (root / "util.py").write_text("def helper():\n    return 2\n", encoding="utf-8")
    assert atlas.freshness()["changed"] == ["util.py"]
    third = atlas.refresh()
    assert third["graph"]["extracted_files"] == 1
    assert next(n["id"] for n in third["nodes"] if n["label"] == "helper()") == helper_id

    (root / "README.md").unlink()
    fourth = atlas.refresh()
    assert fourth["graph"]["deleted_files"] == 1
    assert not any(n.get("source_file") == "README.md" for n in fourth["nodes"])


def test_syntax_error_keeps_file_signal(tmp_path):
    (tmp_path / "broken.py").write_text("def nope(:\n", encoding="utf-8")
    graph = Atlas(tmp_path).refresh()
    node = next(n for n in graph["nodes"] if n["label"] == "broken.py")
    assert "parse_error" in node


def test_refresh_excludes_generated_and_ai_client_directories(tmp_path):
    (tmp_path / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    for directory in (".next", ".obsidian", "node_modules", ".agents", ".claude", "graphify", "raw", "Imported", "holocore-out"):
        folder = tmp_path / directory
        folder.mkdir()
        (folder / "noise.js").write_text("export const noise = true;\n", encoding="utf-8")

    graph = Atlas(tmp_path).refresh()

    sources = {str(node.get("source_file")) for node in graph["nodes"]}
    assert sources == {"app.py"}


def test_archive_entries_are_semantic_signals_and_self_edges_are_removed(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "app.py").write_text("from pathlib import Path\n\ndef run():\n    return Path('.')\n", encoding="utf-8")
    archive = tmp_path / "Archive"
    (archive / "wiki").mkdir(parents=True)
    (archive / "wiki" / "opaque-hash.md").write_text("# Parking Revenue Reconciliation\n\n## Decisions\n- Use invoice date.\n\n## Entities\n- Parking Revenue\n", encoding="utf-8")

    graph = Atlas(root, knowledge_roots={"archive": archive}).refresh()

    assert any(node["label"] == "Parking Revenue Reconciliation" and node["kind"] == "archive_entry" for node in graph["nodes"])
    assert any(node["label"] == "Parking Revenue" and node["kind"] == "concept" for node in graph["nodes"])
    assert any(node["label"] == "Use invoice date." and node["kind"] == "decision" for node in graph["nodes"])
    assert all(link["source"] != link["target"] for link in graph["links"])
    assert len({(link["source"], link["target"], link["relation"]) for link in graph["links"]}) == len(graph["links"])


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is not installed")
def test_git_world_does_not_map_ignored_reference_sources(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("reference-apps/\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    ignored = tmp_path / "reference-apps"
    ignored.mkdir()
    (ignored / "noisy.py").write_text("def copied_engine():\n    pass\n", encoding="utf-8")

    graph = Atlas(tmp_path).refresh()

    sources = {node.get("source_file") for node in graph["nodes"]}
    assert "app.py" in sources
    assert not any(str(source).startswith("reference-apps/") for source in sources if source)
