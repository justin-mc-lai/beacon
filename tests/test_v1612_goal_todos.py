"""CAP-2 canary: goal todo ownership (AC-002)."""

from __future__ import annotations

from beacon.utils.goal_todos import claim_todo, next_open_todo, new_todo, release_todo, supersede_todo


def _state() -> dict:
    return {"todos": [new_todo("t1", "fix batch 1", capability_gate="workspace_admission")]}


def test_double_claim_is_rejected() -> None:
    state = _state()
    first = claim_todo(state, "t1", "agent-a", lease="lease-1")
    assert first["ok"] is True
    second = claim_todo(state, "t1", "agent-b")
    assert second["ok"] is False
    assert second["reason_code"] == "double_claim"
    assert second["owner"] == "agent-a"


def test_release_requires_owner() -> None:
    state = _state()
    claim_todo(state, "t1", "agent-a")
    wrong = release_todo(state, "t1", agent_id="agent-b")
    assert wrong["reason_code"] == "not_owner"
    ok = release_todo(state, "t1", agent_id="agent-a")
    assert ok["ok"] is True
    assert next_open_todo(state)["id"] == "t1"


def test_supersede_keeps_history_and_next_action() -> None:
    state = _state()
    claim_todo(state, "t1", "agent-a")
    result = supersede_todo(state, "t1", "t2", "fix batch 1 v2")
    assert result["ok"] is True
    assert result["superseded"]["status"] == "superseded"
    assert result["superseded"]["successor"] == "t2"
    assert next_open_todo(state)["id"] == "t2"


def test_unclaimed_todo_is_next_action() -> None:
    state = _state()
    assert next_open_todo(state)["id"] == "t1"


def test_missing_todo_claim_blocked() -> None:
    state = _state()
    result = claim_todo(state, "nope", "agent-a")
    assert result["reason_code"] == "todo_missing"
