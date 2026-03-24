from nemoclaw_control.orchestrator.parsers import parse_json_or_empty, parse_ollama_models


def test_parse_ollama_models_table_output():
    output = "NAME SIZE MODIFIED\nnemotron-3-nano:30b 20 GB now\nqwen3.5:27b 16 GB yesterday"
    assert parse_ollama_models(output) == ["nemotron-3-nano:30b", "qwen3.5:27b"]


def test_parse_json_or_empty_handles_bad_json():
    assert parse_json_or_empty("not json") == {}
    assert parse_json_or_empty("") == {}
    assert parse_json_or_empty('{"ok": true}') == {"ok": True}
