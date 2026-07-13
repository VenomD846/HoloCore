import json

from holocore.animus import Animus
from holocore.llm import LocalMemoryProvider
from holocore.memory_pipeline import MemoryRefinementPipeline


class FakeProvider:
    def __init__(self):
        self.calls = []

    def extract(self, messages, *, instructions=""):
        self.calls.append((messages, instructions))
        return {"summary": "Cache policy chosen.", "facts": ["Redis is used."],
                "decisions": ["Use a five minute TTL."], "preferences": ["Prefer local fallback."],
                "entities": ["Redis"]}


def pipeline(tmp_path, provider):
    animus = Animus(tmp_path / "state")
    animus.create_world("demo")
    animus.create_sector("demo", "sessions")
    return animus, MemoryRefinementPipeline(animus, tmp_path / "raw-chat", provider)


def test_refines_in_one_call_audits_raw_chat_and_distills_shards(tmp_path):
    provider = FakeProvider()
    animus, memory = pipeline(tmp_path, provider)
    result = memory.refine([{"role": "user", "content": "raw secret conversation"}], world="demo",
                           sector="sessions", source_ref="chat://1", instructions="Keep architecture decisions")
    assert len(provider.calls) == 1
    assert provider.calls[0][1] == "Keep architecture decisions"
    assert result.extraction.entities == ("Redis",)
    assert len(result.shards) == 5
    assert all(shard.metadata["memory_kind"] for shard in result.shards)
    assert all("raw secret conversation" not in shard.content for shard in result.shards)
    audit = json.loads(result.audit_path.read_text(encoding="utf-8"))
    assert audit["messages"][0]["content"] == "raw secret conversation"
    assert animus.status("demo")["memory_shards"] == 5


def test_existing_animus_deduplicates_distilled_content(tmp_path):
    provider = FakeProvider()
    animus, memory = pipeline(tmp_path, provider)
    first = memory.refine("one", world="demo", sector="sessions", source_ref="chat://1")
    second = memory.refine("two", world="demo", sector="sessions", source_ref="chat://2")
    assert [item.id for item in first.shards] == [item.id for item in second.shards]
    assert all(item.action == "deduplicated" for item in second.shards)
    assert animus.status("demo")["memory_shards"] == 5


def test_local_provider_is_deterministic_and_keyless():
    provider = LocalMemoryProvider()
    messages = [{"role": "user", "content": "We decided to use SQLite. I prefer local tools."}]
    assert provider.extract(messages) == provider.extract(messages)
    result = provider.extract(messages)
    assert result["decisions"] == ["We decided to use SQLite."]
    assert result["preferences"] == ["I prefer local tools."]
