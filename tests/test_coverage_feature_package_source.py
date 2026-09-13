"""Regression for issue #23: report feature coverage even when not release_ready.

``compute_coverage_metrics`` used to discard a feature scorecard unless the
feature was ``release_ready`` / ``ready_for_release``, which coupled a reporting
signal to a release verdict and produced ``ac=0/1`` false negatives.
"""

from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.coverage import compute_coverage_metrics


def _seed_feature_scorecard(root: Path, *, release_ready: bool) -> None:
    (root / "docs" / "beacon" / "v1.0.0").mkdir(parents=True, exist_ok=True)
    qa = root / ".beacon" / "qa"
    (qa / "features" / "demo").mkdir(parents=True, exist_ok=True)
    (qa / "status.json").write_text(
        json.dumps({"version": "v1.0.0", "feature": "demo"}), encoding="utf-8"
    )
    (qa / "features" / "demo" / "scorecard.json").write_text(
        json.dumps(
            {
                "release_ready": release_ready,
                "continue_decision": "" if not release_ready else "ready_for_release",
                "ac_total": 26,
                "ac_accepted": 26,
                "coverage_current": {"required_scenarios": 30, "executed_scenarios": 30},
            }
        ),
        encoding="utf-8",
    )


def test_feature_coverage_reported_when_not_release_ready(tmp_path: Path) -> None:
    _seed_feature_scorecard(tmp_path, release_ready=False)

    metrics = compute_coverage_metrics(tmp_path, version="v1.0.0", feature="demo")

    assert metrics["source"] == "feature_qa_scorecard"
    assert metrics["total_ac"] == 26
    assert metrics["tested_ac"] == 26
    assert metrics["total_tc"] == 30
    assert metrics["executed_tc"] == 30
    assert metrics["release_ready"] is False
