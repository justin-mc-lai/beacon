"""CAP-3 canary: concrete user gate cards (AC-003)."""

from __future__ import annotations

from beacon.utils.goal_gates import assert_gate_resolved, build_gate_card, resolve_gate


def test_gate_card_has_question_context_and_resume_action() -> None:
    result = build_gate_card(
        {},
        "scope_v1612",
        "是否接受单 feature 合并？",
        context="5 个能力组合并为一个 truth 包",
        resume_action="load_next_skill",
    )
    assert result["duplicate"] is False
    card = result["card"]
    assert card["question"] == "是否接受单 feature 合并？"
    assert card["context"] == "5 个能力组合并为一个 truth 包"
    assert card["resume_action"] == "load_next_skill"
    assert card["status"] == "open"


def test_same_decision_key_is_not_asked_twice() -> None:
    state: dict = {}
    first = build_gate_card(state, "key1", "问题A")
    card = first["card"]
    resolved = resolve_gate(state, "key1", "yes")
    state["decision_cache"] = resolved["decision_cache"]
    second = build_gate_card(state, "key1", "问题A")
    assert second["duplicate"] is True
    assert second["cached_answer"] == {"answer": "yes", "at": resolved["decision_cache"]["key1"]["at"]}


def test_unresolved_gate_blocks_next_stage() -> None:
    guard = assert_gate_resolved({}, "key2")
    assert guard["blocked"] is True
    assert guard["reason_code"] == "gate_unresolved"


def test_resolved_gate_allows_next_stage() -> None:
    state: dict = {}
    resolved = resolve_gate(state, "key3", "go")
    state["decision_cache"] = resolved["decision_cache"]
    assert assert_gate_resolved(state, "key3")["ok"] is True


def test_re_resolve_same_key_rejected() -> None:
    state: dict = {}
    resolved = resolve_gate(state, "key4", "a")
    state["decision_cache"] = resolved["decision_cache"]
    again = resolve_gate(state, "key4", "b")
    assert again["reason_code"] == "already_resolved"
