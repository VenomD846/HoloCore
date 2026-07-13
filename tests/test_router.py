from pathlib import Path

from holocore.router import Router


def test_router_does_not_activate_animus_for_code_query(tmp_path, monkeypatch):
    router = Router(tmp_path)
    calls = []
    monkeypatch.setattr(router.archive, "search", lambda q: calls.append("archive") or [])
    monkeypatch.setattr(router.atlas, "search", lambda q: calls.append("atlas") or [])
    monkeypatch.setattr(router.animus, "search", lambda q, wing=None: calls.append("animus") or [])
    router.search("dependency path")
    assert calls == ["archive", "atlas"]
