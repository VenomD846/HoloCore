from holocore.engine import HoloCoreEngine


def test_engine_reuses_search_result(tmp_path, monkeypatch):
    engine = HoloCoreEngine(tmp_path)
    calls = []
    monkeypatch.setattr(engine.router, "search", lambda query, world=None: calls.append(query) or [])
    engine.search("decision", "demo")
    engine.search("decision", "demo")
    assert calls == ["decision"]
