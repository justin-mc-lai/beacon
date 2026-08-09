"""CAP-1 canary: goal compute quota kernel (AC-001)."""

from __future__ import annotations

from beacon.utils.goal_quota import normalize_quota_config, quota_should_run, record_spend, spent_slots


def test_quota_should_run_orders_gates_before_quota() -> None:
    state = {"focus_wait": True, "quota_ledger": []}
    result = quota_should_run(state, config={"compute": 1.0, "window_hours": 24, "slot_minutes": 1})
    assert result["should_run"] is False
    assert result["decision"] == "skip"
    assert result["state"] == "focus_wait"


def test_focus_wait_does_not_spend_and_recovery_is_separate_boolean() -> None:
    state = {"focus_wait": True, "recovery_action": True, "recovery_kind": "outcome_floor_recovery"}
    result = quota_should_run(state)
    assert result["should_run"] is False
    assert result["recovery_action"] is True
    assert result["recovery_kind"] == "outcome_floor_recovery"
    # A skip must never look like a run, and a recovery must never look like a quiet skip.
    assert result["decision"] == "skip"


def test_spend_refused_without_validated_writeback() -> None:
    state = {"quota_ledger": []}
    result = record_spend(state, slots=1, writeback_validated=False)
    assert result["ok"] is False
    assert result["reason_code"] == "spend_without_validated_writeback"
    assert spent_slots(state) == 0


def test_spend_exactly_once_after_validated_writeback() -> None:
    state = {"quota_ledger": []}
    first = record_spend(state, slots=1, writeback_validated=True)
    assert first["ok"] is True
    state["quota_ledger"] = first["ledger"]
    second = record_spend(state, slots=1, writeback_validated=True)
    assert second["spent_slots"] == 2


def test_quota_zero_is_visible_but_not_runnable() -> None:
    state = {"quota_ledger": [{"slots": 1440}]}
    result = quota_should_run(state, config={"compute": 1.0, "window_hours": 24, "slot_minutes": 1})
    assert result["should_run"] is False
    assert result["state"] == "quota_exhausted"
    assert result["spent_slots"] == 1440


def test_quota_default_config_full_duty_cycle() -> None:
    cfg = normalize_quota_config(None)
    assert cfg["allowed_slots"] == 1440
