import json

from holocore.conversation_import import ConversationImporter


def test_importer_normalizes_slack_and_chatgpt_exports(tmp_path):
    slack = tmp_path / "slack.json"
    slack.write_text(json.dumps([{"user_name": "Ada", "text": "Decision recorded", "ts": "1"}]), encoding="utf-8")
    result = ConversationImporter().import_file(slack)
    assert result["provider"] == "slack"
    assert result["messages"][0]["content"] == "Decision recorded"

    chatgpt = tmp_path / "chatgpt.json"
    chatgpt.write_text(json.dumps([{"conversation_id": "c1", "mapping": {"m": {"message": {"author": {"role": "user"}, "content": {"parts": ["Hello"]}}}}}]), encoding="utf-8")
    result = ConversationImporter().import_file(chatgpt)
    assert result["provider"] == "chatgpt"
    assert result["messages"][0]["role"] == "user"
