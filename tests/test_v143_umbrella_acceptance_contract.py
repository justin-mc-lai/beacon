from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.4.3"
CEO_FEATURE = "beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface"
DESIGN_FEATURE = "beacon-v1.4.3-design-review-surface-and-prototype-governance"
LEARN_FEATURE = "beacon-v1.4.3-governed-learning-recall-and-route-explainability"
UMBRELLA_FEATURE = "beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation"


def _load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _acceptance_tx(feature: str) -> dict:
    return _load_json(f".beacon/transactions/qa-acceptance-{feature}.json")


def _scorecard(feature: str) -> dict:
    return _load_json(f".beacon/qa/features/{feature}/scorecard.json")


def test_ceo_subfeature_acceptance_passed() -> None:
    payload = _acceptance_tx(CEO_FEATURE)
    scorecard = _scorecard(CEO_FEATURE)
    assert payload["verdict"] == "passed"
    assert payload["write_status"] == "applied"
    assert scorecard["release_ready"] is True
    assert scorecard["ac_accepted"] == scorecard["ac_total"]


def test_design_subfeature_acceptance_passed() -> None:
    payload = _acceptance_tx(DESIGN_FEATURE)
    scorecard = _scorecard(DESIGN_FEATURE)
    assert payload["verdict"] == "passed"
    assert payload["write_status"] == "applied"
    assert scorecard["release_ready"] is True
    assert scorecard["ac_accepted"] == scorecard["ac_total"]


def test_learn_subfeature_acceptance_passed() -> None:
    payload = _acceptance_tx(LEARN_FEATURE)
    scorecard = _scorecard(LEARN_FEATURE)
    assert payload["verdict"] == "passed"
    assert payload["write_status"] == "applied"
    assert scorecard["release_ready"] is True
    assert scorecard["ac_accepted"] == scorecard["ac_total"]


def test_version_line_preserves_boundary_contract() -> None:
    execution_index = (ROOT / "docs" / "beacon" / VERSION / "execution" / "index.md").read_text(encoding="utf-8")
    assert "aggregation contract, not an implementation-owning feature" in execution_index
    assert "release/gate should consume accepted subfeature evidence" in execution_index
    assert "must not require a standalone `prototype`, `technical review`, or `implementation plan`" in execution_index


def test_umbrella_subfeatures_are_qa_closed() -> None:
    umbrella_story = (
        ROOT / "docs" / "beacon" / VERSION / "user-story" / f"{UMBRELLA_FEATURE}.md"
    ).read_text(encoding="utf-8")
    assert "QA-accepted" in umbrella_story
    for feature in (CEO_FEATURE, DESIGN_FEATURE, LEARN_FEATURE):
        payload = _acceptance_tx(feature)
        assert payload["verdict"] == "passed"
