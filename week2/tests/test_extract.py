from types import SimpleNamespace

import pytest

from ..app.services.extract import (
    extract_action_items,
    extract_action_items_llm,
)


def _mock_response(payload: str) -> SimpleNamespace:
    return SimpleNamespace(message=SimpleNamespace(content=payload))


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_action_items_llm_handles_bullet_list(monkeypatch):
    text = "- finalize slides for demo\n- email pilot customers"

    def fake_chat(**kwargs):
        assert "finalize slides" in kwargs["messages"][1]["content"]
        return _mock_response('{"action_items":["Finalize slide deck","Email pilot customers"]}')

    monkeypatch.setattr("week2.app.services.extract.ollama_chat", fake_chat)

    items = extract_action_items_llm(text)
    assert items == ["Finalize slide deck", "Email pilot customers"]


def test_extract_action_items_llm_falls_back_to_heuristics(monkeypatch):
    text = "Action: refresh metrics dashboard"

    def fake_chat(**kwargs):
        return _mock_response("[]")

    monkeypatch.setattr("week2.app.services.extract.ollama_chat", fake_chat)

    items = extract_action_items_llm(text)
    assert "Action: refresh metrics dashboard" in items


def test_extract_action_items_llm_empty_input_skips_model(monkeypatch):
    def fake_chat(**kwargs):  # pragma: no cover - should not run
        raise AssertionError("LLM should not be called for empty input")

    monkeypatch.setattr("week2.app.services.extract.ollama_chat", fake_chat)

    assert extract_action_items_llm("   \n\t") == []


def test_extract_action_items_llm_missing_dependency(monkeypatch):
    monkeypatch.setattr("week2.app.services.extract.ollama_chat", None)
    text = "Action: refresh metrics dashboard"
    items = extract_action_items_llm(text)
    assert "refresh metrics dashboard" in items[0].lower()


def test_extract_action_items_llm_handles_runtime_errors(monkeypatch):
    def fake_chat(**kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("week2.app.services.extract.ollama_chat", fake_chat)

    text = "- [ ] Update onboarding doc"
    items = extract_action_items_llm(text)
    assert "update onboarding doc" in [item.lower() for item in items]
