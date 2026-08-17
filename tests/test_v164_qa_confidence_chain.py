"""Tests for beacon-qa-coverage-confidence-chain-v164."""

from __future__ import annotations

from beacon.utils.coverage import project_qa_layer_confidence
from beacon.utils.qa_acceptance import BROWSER_RUNNER_REGISTRY, build_qa_profile_completeness
from beacon.utils.qa_confidence_chain import CONFIDENCE_CHAIN_LAYERS, build_confidence_chain


def test_chain_model_bottom_up() -> None:
    chain = build_confidence_chain(
        executed_layers=["unit", "interface", "contract", "integration", "smoke", "functional", "regression", "exception", "compatibility", "browser_e2e"],
    )
    assert chain["chain_direction"] == "unit_to_browser_e2e"
    assert chain["layers"][0]["layer"] == "unit"
    assert chain["layers"][-1]["layer"] == "browser_e2e"
    assert chain["layers"][-1]["confidence"] == 1.0


def test_gap_detection() -> None:
    chain = build_confidence_chain(executed_layers=["unit"], skipped_layers=["interface"])
    interface = next(item for item in chain["layers"] if item["layer"] == "interface")
    contract = next(item for item in chain["layers"] if item["layer"] == "contract")
    assert interface["status"] == "skipped"
    assert "downstream_gap" in contract["gap_markers"]
    assert "interface" in chain["downstream_gap_layers"]


def test_confidence_chain_field() -> None:
    profile = build_qa_profile_completeness(
        profile="browser",
        browser_required=True,
        executed_layers=["unit", "interface"],
    )
    assert "confidence_chain" in profile
    assert isinstance(profile["confidence_chain"], dict)
    projection = project_qa_layer_confidence(profile)
    assert projection["confidence_chain"] == profile["confidence_chain"]


def test_break_chain_blocks() -> None:
    profile = build_qa_profile_completeness(
        profile="browser",
        browser_required=True,
        executed_layers=["unit"],
        skipped_layers=["browser_e2e"],
    )
    assert profile["partial"] is True
    assert profile["status"] == "partial"
    assert profile["is_complete"] is False
    assert profile["confidence_chain"]["chain_broken"] is True


def test_browser_e2e_chain_terminal() -> None:
    assert "playwright-extension" in BROWSER_RUNNER_REGISTRY
    assert CONFIDENCE_CHAIN_LAYERS[-1] == "browser_e2e"
    chain = build_confidence_chain(executed_layers=list(CONFIDENCE_CHAIN_LAYERS))
    assert chain["terminal_layer"] == "browser_e2e"
    assert chain["chain_broken"] is False
