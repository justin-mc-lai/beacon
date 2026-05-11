from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.deep_loop import build_deep_release_supplement, load_deep_artifact, run_deep_loop
from beacon.utils.release_scorecard import build_release_scorecard
from beacon.utils.runtime import write_json

from v141_deep_helpers import FEATURE, VERSION, seed_deep_project


def test_release_consumes_deep_evidence(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)

    supplement = build_deep_release_supplement(tmp_path, version=VERSION, feature=FEATURE)
    assert supplement["status"] == "pass"
    assert supplement["closure_verdict"] == "closed"
    assert supplement["artifact_refs"]["closure_brief"]["json"].endswith("deep-closure-brief.json")

    scorecard = build_release_scorecard(tmp_path, version=VERSION)
    assert scorecard["deep_release_supplement"]["status"] == "pass"


def test_blocking_findings_must_close_or_waive(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE, qa_feedback="state machine consistency gap", qa_severity="P1")

    supplement = build_deep_release_supplement(tmp_path, version=VERSION, feature=FEATURE)
    assert supplement["blocked"] is True
    assert "deep_release_blocking_finding_open" in supplement["reason_codes"]


def test_backlog_findings_require_explicit_decision(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)
    run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)

    risk = load_deep_artifact(tmp_path, version=VERSION, feature=FEATURE, artifact="risk_register")
    risk["findings"][0]["closure_decision"] = "accepted_backlog"
    risk["findings"][0]["backlog_decision"] = ""
    refs = risk.get("artifact_refs") or {}
    path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "deep" / FEATURE / "risk-register.json"
    write_json(path, risk)

    supplement = build_deep_release_supplement(tmp_path, version=VERSION, feature=FEATURE)
    assert supplement["blocked"] is True
    assert "deep_backlog_decision_missing" in supplement["reason_codes"]
