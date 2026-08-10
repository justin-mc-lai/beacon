from __future__ import annotations

from beacon.utils.deep_loop import evaluate_deep_trigger, should_reopen_deep_from_qa


def test_high_risk_triggers_are_detected() -> None:
    payload = evaluate_deep_trigger(
        "payment order wallet ranking scoring identity binding invitation relationship chain reporting migration multi-role multi-state post-fact attribution"
    )

    assert payload["required"] is True
    categories = {item["category"] for item in payload["triggers"]}
    assert "financial_or_payment_flow" in categories
    assert "ranking_or_scoring_flow" in categories
    assert "identity_or_attribution_binding" in categories
    assert "relationship_or_invitation_chain" in categories


def test_low_risk_skip_reason_is_explicit() -> None:
    payload = evaluate_deep_trigger("static page visual-only copy change", skip_reason="visual-only low-risk update")

    assert payload["skipped"] is True
    assert payload["deep_requirement_state"] == "not_required"
    assert payload["reason_code"] == "deep_skip_reason_recorded"
    assert payload["skip_reason"] == "visual-only low-risk update"


def test_qa_structural_defect_reopens_deep() -> None:
    assert should_reopen_deep_from_qa("P2 defect exposes fact source consistency gap", severity="P2") is True
    payload = evaluate_deep_trigger("low risk text", qa_feedback="state machine consistency defect", qa_severity="P1")

    assert payload["required"] is True
    assert payload["qa_structural_reopen"] is True
    assert any(item["category"] == "qa_structural_defect_reopen" for item in payload["triggers"])
