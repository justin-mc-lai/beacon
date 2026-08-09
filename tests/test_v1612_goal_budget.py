"""CAP-4 canary: bounded turn budget (AC-004)."""

from __future__ import annotations

from beacon.utils.goal_budget import (
    HANDOFF_MAX_CHARS,
    HANDOFF_MAX_LINES,
    enforce_handoff_budget,
    spend_guard,
    turn_contract,
)


def test_turn_contract_is_bounded_delivery() -> None:
    contract = turn_contract()
    assert contract["mode"] == "bounded_delivery"
    assert contract["steps"] == ["choose", "deliver", "validate", "writeback", "spend"]
    assert contract["spend_after_writeback"] is True


def test_handoff_budget_truncates_long_text() -> None:
    long_text = "\n".join(f"line {i}" for i in range(30))
    result = enforce_handoff_budget(long_text)
    assert result["truncated"] is True
    assert result["lines"] == HANDOFF_MAX_LINES


def test_handoff_budget_truncates_by_chars() -> None:
    result = enforce_handoff_budget("x" * (HANDOFF_MAX_CHARS + 100))
    assert result["truncated"] is True
    assert result["chars"] == HANDOFF_MAX_CHARS


def test_handoff_budget_passes_compact_text() -> None:
    result = enforce_handoff_budget("ok\nnext: claim t1")
    assert result["truncated"] is False
    assert result["text"] == "ok\nnext: claim t1"


def test_spend_guard_requires_validated_writeback() -> None:
    assert spend_guard(False)["blocked"] is True
    assert spend_guard(True)["ok"] is True
