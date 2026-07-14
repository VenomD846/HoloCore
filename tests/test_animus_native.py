import ast
from pathlib import Path

import pytest

from holocore.animus import Animus, ShardInput


def store(tmp_path):
    animus = Animus(tmp_path)
    animus.create_world("demo", "Demo World")
    animus.create_sector("demo", "debugging")
    animus.create_sector("demo", "decisions")
    return animus


def test_scoped_ingest_search_and_provenance(tmp_path):
    animus = store(tmp_path)
    shard = animus.ingest("The cache failure was fixed by invalidation.", world="demo",
                          sector="debugging", source_ref="session://one", version_token="v1",
                          route_hint="history", transformations=("none",),
                          privacy={"scope": "project"})
    animus.ingest("Cache is an architecture decision.", world="demo", sector="decisions",
                  source_ref="session://two")
    found = animus.search("cache failure", world="demo", sector="debugging")
    assert [item.id for item in found] == [shard.id]
    assert found[0].provenance[0].source_ref == "session://one"
    assert found[0].route_hint == "history"
    assert found[0].transformations == ("none",)


def test_content_hash_deduplicates_and_source_update_replaces_stale_shard(tmp_path):
    animus = store(tmp_path)
    first = animus.ingest("same verbatim memory", world="demo", sector="debugging", source_ref="a")
    duplicate = animus.ingest("same verbatim memory", world="demo", sector="debugging", source_ref="b")
    assert duplicate.id == first.id
    assert duplicate.action == "deduplicated"
    assert {p.source_ref for p in duplicate.provenance} == {"a", "b"}

    updated = animus.update("new memory text", world="demo", sector="debugging", source_ref="a", version_token="v2")
    assert updated.action == "updated"
    assert animus.status("demo")["memory_shards"] == 2  # old content remains for source b
    assert animus.search("new memory", world="demo", sector="debugging")[0].provenance[0].version_token == "v2"


def test_sync_is_idempotent_and_prunes_only_its_scope(tmp_path):
    animus = store(tmp_path)
    records = [ShardInput("current episode", "file://current", sector="debugging")]
    first = animus.sync("demo", records, sector="debugging")
    second = animus.sync("demo", records, sector="debugging")
    assert first.inserted == 1
    assert second.unchanged == 1

    animus.ingest("durable episode", world="demo", sector="decisions", source_ref="file://decision")
    report = animus.sync("demo", [], sector="debugging")
    assert report.removed_shards == 1
    assert animus.status("demo")["memory_shards"] == 1


def test_requires_declared_world_and_sector(tmp_path):
    animus = Animus(tmp_path)
    with pytest.raises(KeyError):
        animus.ingest("memory", world="missing", source_ref="source")
    animus.create_world("demo")
    with pytest.raises(KeyError):
        animus.search("memory", world="demo", sector="missing")


def test_rename_world_preserves_scoped_memory_and_provenance(tmp_path):
    animus = store(tmp_path)
    shard = animus.ingest(
        "A retained memory shard.",
        world="demo",
        sector="debugging",
        source_ref="session://rename",
    )

    assert animus.rename_world("demo", "Demo Project", "Demo Project") is True

    assert animus.get_world("Demo Project").display_name == "Demo Project"
    with pytest.raises(KeyError):
        animus.get_world("demo")
    renamed = animus.search("retained", world="Demo Project", sector="debugging")
    assert [item.id for item in renamed] == [shard.id]
    assert renamed[0].provenance[0].source_ref == "session://rename"


def test_rename_world_merges_empty_legacy_scope_into_existing_world(tmp_path):
    animus = Animus(tmp_path)
    animus.create_world("legacy-hash", "Demo Project")
    animus.create_sector("legacy-hash", "extra")
    animus.create_world("Demo Project", "Demo Project")

    assert animus.rename_world("legacy-hash", "Demo Project", "Demo Project") is True

    assert animus.get_sector("Demo Project", "extra").display_name == "extra"
    with pytest.raises(KeyError):
        animus.get_world("legacy-hash")


def test_native_module_has_no_external_engine_or_subprocess_imports():
    path = Path(__file__).parents[1] / "src" / "holocore" / "animus.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = {alias.name.split(".")[0] for node in ast.walk(tree)
               if isinstance(node, (ast.Import, ast.ImportFrom))
               for alias in (node.names if isinstance(node, ast.Import) else [ast.alias(node.module or "")])}
    assert "subprocess" not in imports
    assert "mempalace" not in imports
