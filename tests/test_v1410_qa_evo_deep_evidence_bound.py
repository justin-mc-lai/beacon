from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.qa_evo_deep import (
    build_deep_absorption_status,
    run_qa_evo_deep,
    validate_qa_evo_deep_payload,
)
from beacon.utils.qa_feature import build_feature_qa_precision_artifacts
from beacon.utils.release_scorecard import summarize_release_scorecard
from beacon.utils import release_scorecard as release_scorecard_module
from beacon.utils.runtime import write_json
from beacon.utils.skill_eval_kit import replay_eval_case, run_skill_eval
from beacon.utils.story_state import feature_slug


VERSION = "v1.4.10"
FEATURE = "qa-evo-deep-evidence-bound-ac-aware-closure"


def seed_truth_and_qa(root: Path, *, feature: str = FEATURE, ac_status: str = "accepted") -> None:
    slug = feature_slug(feature)
    base = root / "docs" / "beacon" / VERSION
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "prd" / f"{slug}.md").write_text("# PRD\n\n- AC-001: Source evidence ready\n", encoding="utf-8")
    (base / "user-story" / f"{slug}.md").write_text(
        "# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | source | QA evo-deep reads evidence. |\n",
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / f"{slug}.md").write_text(
        "# Test Cases\n\n| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |\n| --- | --- | --- | --- | --- | --- |\n| AC-001 | TC-001 | contract | `pytest` | passes | `.beacon/evidence/TC-001.json` |\n",
        encoding="utf-8",
    )
    qa_root = root / ".beacon" / "qa" / "features" / slug
    qa_root.mkdir(parents=True, exist_ok=True)
    write_json(
        qa_root / "scorecard.json",
        {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slug,
            "release_ready": ac_status == "accepted",
            "continue_decision": "ready_for_release" if ac_status == "accepted" else "continue",
        },
    )
    write_json(
        qa_root / "ac-closure.json",
        {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slug,
            "reports": [{"ac_id": "AC-001", "closure_status": ac_status}],
        },
    )


def test_required_source_materials_are_loaded(tmp_path: Path) -> None:
    seed_truth_and_qa(tmp_path)

    payload = run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["status"] == "ready"
    assert payload["source_materials"]["status"] == "ready"
    assert payload["validation"]["status"] == "pass"
    assert payload["findings"][0]["affected_ac_ids"] == ["AC-001"]
    assert payload["findings"][0]["current_evidence_refs"]


def test_missing_source_material_blocks_ready_report(tmp_path: Path) -> None:
    payload = run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["status"] == "blocked"
    assert payload["validation"]["blocked"] is True
    assert any(issue["reason_code"] == "qa_evo_deep_source_evidence_missing" for issue in payload["validation"]["issues"])
    assert payload["findings"][0]["finding_family"] == "blocked_admission"


def test_ready_findings_require_ac_and_evidence_refs(tmp_path: Path) -> None:
    seed_truth_and_qa(tmp_path)
    payload = run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)

    validation = validate_qa_evo_deep_payload(payload)

    assert validation["status"] == "pass"
    assert all(item["affected_ac_ids"] for item in payload["findings"])
    assert all(item["current_evidence_refs"] for item in payload["findings"])


def test_empty_skeleton_findings_fail_closed(tmp_path: Path) -> None:
    seed_truth_and_qa(tmp_path)
    payload = run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)
    payload["findings"][0]["affected_ac_ids"] = []

    validation = validate_qa_evo_deep_payload(payload)

    assert validation["blocked"] is True
    assert validation["issues"][0]["reason_code"] == "qa_evo_deep_empty_skeleton_finding"


def test_blocked_admission_can_explain_source_gap(tmp_path: Path) -> None:
    payload = run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)
    admission = payload["findings"][0]["blocked_admissions"][0]

    assert admission["reason_code"] == "qa_evo_deep_source_evidence_missing"
    assert admission["missing_sources"]
    assert admission["route_recommendation"] == "beacon qa supplement"


def test_skill_eval_replays_route_boundary_and_source_anchor(tmp_path: Path) -> None:
    payload = run_skill_eval(tmp_path)
    traces = sorted((tmp_path / payload["traces_path"]).glob("*.json"))
    trace = json.loads(traces[0].read_text(encoding="utf-8"))

    assert trace["route_decision_replayed"] is True
    assert trace["route_decision_matched"] is True
    assert trace["boundary_preservation_replayed"] is True
    assert trace["boundary_preserved"] is True
    assert trace["source_anchor_replayed"] is True
    assert trace["source_anchor_covered"] is True


def test_skill_eval_replay_failure_blocks_case() -> None:
    case = {
        "case_id": "route-fail",
        "expected_route": "beacon-deep",
        "actual_route": "beacon-qa",
    }

    replay = replay_eval_case(case)

    assert replay["status"] == "fail"
    assert replay["failures"][0]["reason_code"] == "skill_eval_route_replay_failed"


def test_qa_scorecard_records_deep_absorption_status(tmp_path: Path) -> None:
    seed_truth_and_qa(tmp_path)
    run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)
    _, _, scorecard, _, _ = build_feature_qa_precision_artifacts(
        tmp_path,
        feature=FEATURE,
        run_id="run-test",
        plan={"version": VERSION, "required_scenario_families": []},
        per_item_results=[
            {
                "ac_id": "AC-001",
                "tc_id": "TC-001",
                "source_tc_id": "TC-001",
                "scenario_id": "TC-001",
                "scenario_family": "primary",
                "status": "passed",
                "evidence_ref": [".beacon/evidence/TC-001.json"],
            }
        ],
    )

    assert scorecard["deep_absorption"]["status"] == "absorbed"
    assert scorecard["deep_absorption"]["absorbed_count"] >= 1
    assert scorecard["release_supplement_input"]["deep_findings_absorbed"] is True


def test_release_uses_only_absorbed_deep_findings(tmp_path: Path) -> None:
    seed_truth_and_qa(tmp_path)
    run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)
    absorption = build_deep_absorption_status(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        ac_closure={"reports": [{"ac_id": "AC-001", "closure_status": "accepted"}]},
    )
    summary = summarize_release_scorecard(
        {
            "feature_qa_scorecard": {
                "deep_absorption": absorption,
                "release_supplement_input": {
                    "deep_findings_absorbed": absorption["eligible_for_release_supplement"],
                    "policy": "absorbed_deep_findings_only",
                },
            }
        }
    )

    assert summary["qa_evo_deep_release_supplement_eligible"] is True
    assert summary["qa_evo_deep_release_supplement_policy"] == "absorbed_deep_findings_only"


def test_release_bridge_accepts_absorbed_qa_evo_deep_supplement_only() -> None:
    absorbed_scorecard = {
        "deep_absorption": {
            "status": "absorbed",
            "eligible_for_release_supplement": True,
            "absorbed_count": 7,
        },
        "release_supplement_input": {
            "deep_findings_absorbed": True,
            "policy": "absorbed_deep_findings_only",
        },
    }

    bridged = release_scorecard_module._apply_qa_evo_deep_release_supplement_bridge(
        {
            "status": "blocked",
            "blocked": True,
            "reason_codes": ["deep_loop_unclosed"],
        },
        feature_scorecard=absorbed_scorecard,
    )

    assert bridged["blocked"] is False
    assert bridged["qa_evo_deep_release_supplement_bridge"]["status"] == "applied"


def test_release_bridge_does_not_hide_other_deep_blockers() -> None:
    absorbed_scorecard = {
        "deep_absorption": {
            "status": "absorbed",
            "eligible_for_release_supplement": True,
            "absorbed_count": 7,
        },
        "release_supplement_input": {
            "deep_findings_absorbed": True,
            "policy": "absorbed_deep_findings_only",
        },
    }

    bridged = release_scorecard_module._apply_qa_evo_deep_release_supplement_bridge(
        {
            "status": "blocked",
            "blocked": True,
            "reason_codes": ["deep_loop_unclosed", "deep_release_blocking_finding_open"],
        },
        feature_scorecard=absorbed_scorecard,
    )

    assert bridged["blocked"] is True
    assert "deep_release_blocking_finding_open" in bridged["reason_codes"]


def test_authority_bypass_still_fails_closed(tmp_path: Path) -> None:
    seed_truth_and_qa(tmp_path)
    payload = run_qa_evo_deep(tmp_path, version=VERSION, feature=FEATURE)
    payload["findings"][0]["authority_boundary"] = "gate_verdict"

    validation = validate_qa_evo_deep_payload(payload)

    assert validation["blocked"] is True
    assert validation["issues"][0]["reason_code"] == "qa_evo_deep_authority_bypass"
