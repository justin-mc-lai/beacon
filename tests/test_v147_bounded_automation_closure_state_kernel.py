from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.automation_feedback import refresh_qa_feedback_ledger, update_automation_queue_from_feedback
from beacon.utils.automation_queue import claim_feature_execution_lease
from beacon.utils.automation_runtime import (
    bounded_runtime_round_summary,
    derive_bounded_runtime_from_qa,
    load_feature_automation_runtime,
    record_implement_repair_round,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed_feature_status(
    root: Path,
    *,
    feature: str,
    status: str,
    continue_decision: str,
    stop_reasons: list[str] | None = None,
    run_id: str | None = None,
) -> None:
    slug = feature.replace(" ", "-").replace("_", "-").lower()
    _write_json(
        root / ".beacon" / "qa" / "features" / slug / "status.json",
        {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slug,
            "version": "v1.4.7",
            "run_id": run_id or f"run-{slug}",
            "status": status,
            "evidence_done": status == "passed",
            "release_ready": status == "passed",
            "truth_hash": f"truth-{slug}",
            "implementation_evidence_hash": f"impl-{slug}-{run_id or '1'}",
            "targeted_rerun": {
                "targeted_layers": ["functional"],
                "targeted_tc_ids": ["TC-001"],
                "targeted_scenario_ids": ["SC-001"],
            },
            "feature_scorecard": {
                "continue_decision": continue_decision,
                "stop_reasons": stop_reasons or [],
                "resume_command": f'beacon qa run "{feature}" --project-root . --version v1.4.7',
                "repair_handoff": {
                    "action": "implement-repair" if continue_decision == "stop_for_repair" else "",
                    "command": f'beacon implement run "{feature}" --project . --version v1.4.7 --runner native-single'
                    if continue_decision == "stop_for_repair"
                    else "",
                },
                "coverage_current": {"coverage_rate": 1.0 if status == "passed" else 0.5, "executed_scenarios": 1, "required_scenarios": 2},
            },
        },
    )
    _write_json(
        root / ".beacon" / "qa" / "features" / slug / "scorecard.json",
        {
            "continue_decision": continue_decision,
            "stop_reasons": stop_reasons or [],
            "resume_command": f'beacon qa run "{feature}" --project-root . --version v1.4.7',
            "repair_handoff": {
                "action": "implement-repair" if continue_decision == "stop_for_repair" else "",
                "command": f'beacon implement run "{feature}" --project . --version v1.4.7 --runner native-single'
                if continue_decision == "stop_for_repair"
                else "",
            },
            "coverage_current": {"coverage_rate": 1.0 if status == "passed" else 0.5, "executed_scenarios": 1, "required_scenarios": 2},
        },
    )


def _seed_queue(root: Path) -> None:
    _write_json(
        root / "automation" / "beacon-automation-queue.json",
        {
            "version": "v0",
            "project_root": str(root),
            "default_workspace_mode": "worktree",
            "queue_revision": 0,
            "feature_leases": {},
            "jobs": [
                {
                    "job_id": "beacon-nightly-qa",
                    "job_kind": "qa",
                    "target_agent": "codex",
                    "enabled": True,
                    "feature_selector": {"mode": "explicit_list", "features": ["feature pass", "feature repair"]},
                    "preconditions": ["implementation_evidence_present"],
                    "workspace_mode": "worktree",
                    "risk_level": "medium",
                    "on_blocked": "report_only",
                    "on_success": "report_only",
                    "notes": "",
                },
                {
                    "job_id": "beacon-gated-implement",
                    "job_kind": "implement",
                    "target_agent": "codex",
                    "enabled": False,
                    "feature_selector": {"mode": "explicit_list", "features": []},
                    "preconditions": ["truth_frozen"],
                    "workspace_mode": "worktree",
                    "risk_level": "high",
                    "on_blocked": "handoff_to_human",
                    "on_success": "trigger_qa",
                    "notes": "",
                },
            ],
        },
    )


def test_closure_state_envelope_is_emitted_with_required_fields(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature pass", status="passed", continue_decision="ready_for_release")
    payload = refresh_qa_feedback_ledger(tmp_path, features=["feature pass"])
    entry = payload["entries"][0]
    runtime = entry["bounded_runtime"]
    assert runtime["feature"] == "feature pass"
    assert runtime["version"] == "v1.4.7"
    assert runtime["closure_state"] == "release_ready"
    assert runtime["next_route"] == "release"
    assert runtime["terminal_signal"] == "qa_exit_ready_for_release"
    assert runtime["round_number"] == 0
    assert "previous_round_ref" in runtime


def test_bounded_closure_state_taxonomy_is_frozen(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature repair", status="blocked", continue_decision="stop_for_repair", stop_reasons=["needs_fix"])
    payload = refresh_qa_feedback_ledger(tmp_path, features=["feature repair"])
    runtime = payload["entries"][0]["bounded_runtime"]
    assert runtime["closure_state"] in {"active", "blocked", "release_ready", "closed", "human_escalation_required"}


def test_bounded_next_route_taxonomy_is_frozen_for_current_slice(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature repair", status="blocked", continue_decision="stop_for_repair", stop_reasons=["needs_fix"])
    payload = refresh_qa_feedback_ledger(tmp_path, features=["feature repair"])
    runtime = payload["entries"][0]["bounded_runtime"]
    assert runtime["next_route"] in {"qa", "implement", "release", "human"}
    assert runtime["next_route"] == "implement"


def test_active_issue_register_inherits_only_live_repair_context(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature repair", status="blocked", continue_decision="stop_for_repair", stop_reasons=["needs_fix"], run_id="run-1")
    status = json.loads((tmp_path / ".beacon" / "qa" / "features" / "feature-repair" / "status.json").read_text(encoding="utf-8"))
    scorecard = json.loads((tmp_path / ".beacon" / "qa" / "features" / "feature-repair" / "scorecard.json").read_text(encoding="utf-8"))
    derive_bounded_runtime_from_qa(tmp_path, feature="feature repair", status=status, scorecard=scorecard)
    payload = record_implement_repair_round(tmp_path, feature="feature repair", accepted_fixes=["fix-timeout"], outcome_ref="implement:round-1")
    register = payload["active_issue_register"]
    assert register["accepted_fixes"] == ["fix-timeout"]
    assert register["unresolved_stop_reasons"] == ["needs_fix"]
    assert register["latest_ref"] == "implement:round-1"
    assert "feature_scorecard" not in register
    assert "status" not in register


def test_qa_exit_predicates_drive_bounded_runtime_routes(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature pass", status="passed", continue_decision="ready_for_release")
    _seed_feature_status(tmp_path, feature="feature repair", status="blocked", continue_decision="stop_for_repair", stop_reasons=["needs_fix"])
    payload = refresh_qa_feedback_ledger(tmp_path, features=["feature pass", "feature repair"])
    by_feature = {entry["feature"]: entry["bounded_runtime"] for entry in payload["entries"]}
    assert by_feature["feature pass"]["terminal_signal"] == "qa_exit_ready_for_release"
    assert by_feature["feature pass"]["next_route"] == "release"
    assert by_feature["feature repair"]["terminal_signal"] == "qa_route_implement_repair"
    assert by_feature["feature repair"]["next_route"] == "implement"


def test_implement_exit_predicates_drive_return_to_qa_or_human(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature repair", status="blocked", continue_decision="stop_for_repair", stop_reasons=["needs_fix"])
    refresh_qa_feedback_ledger(tmp_path, features=["feature repair"])
    back_to_qa = record_implement_repair_round(tmp_path, feature="feature repair", accepted_fixes=["fix-a"])
    assert back_to_qa["terminal_signal"] == "implement_exit_to_qa"
    assert back_to_qa["next_route"] == "qa"
    escalated = record_implement_repair_round(tmp_path, feature="feature repair", human_escalation=True, outcome_ref="implement:round-escalate")
    assert escalated["terminal_signal"] == "implement_route_human_escalation"
    assert escalated["next_route"] == "human"


def test_stale_queue_writer_is_rejected_when_revision_mismatches(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature repair", status="blocked", continue_decision="stop_for_repair", stop_reasons=["needs_fix"])
    _seed_queue(tmp_path)
    refresh_qa_feedback_ledger(tmp_path, features=["feature repair"])
    payload = update_automation_queue_from_feedback(tmp_path, expected_revision=99)
    assert payload["status"] == "stale_writer_rejected"
    assert payload["queue_revision_before"] == 0
    current = json.loads((tmp_path / "automation" / "beacon-automation-queue.json").read_text(encoding="utf-8"))
    assert current["queue_revision"] == 0


def test_single_feature_execution_lease_prevents_double_claim(tmp_path: Path) -> None:
    _seed_queue(tmp_path)
    claimed = claim_feature_execution_lease(tmp_path / "automation" / "beacon-automation-queue.json", feature="feature repair", owner="worker-a")
    assert claimed["status"] == "claimed"
    rejected = claim_feature_execution_lease(
        tmp_path / "automation" / "beacon-automation-queue.json",
        feature="feature repair",
        owner="worker-b",
        expected_revision=claimed["queue_revision_after"],
    )
    assert rejected["status"] == "lease_conflict"
    assert rejected["active_lease"]["owner"] == "worker-a"


def test_bounded_runtime_round_summary_exposes_operator_visible_state(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature repair", status="blocked", continue_decision="stop_for_repair", stop_reasons=["needs_fix"])
    refresh_qa_feedback_ledger(tmp_path, features=["feature repair"])
    runtime = load_feature_automation_runtime(tmp_path, feature="feature repair")
    summary = bounded_runtime_round_summary(runtime)
    assert summary["round_number"] == 0
    assert summary["closure_state"] == "blocked"
    assert summary["terminal_signal"] == "qa_route_implement_repair"
    assert summary["next_route"] == "implement"
    assert summary["human_takeover_required"] is False


def test_automation_kernel_preserves_truth_boundary_and_rejects_full_loop_claims(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature pass", status="passed", continue_decision="ready_for_release")
    payload = refresh_qa_feedback_ledger(tmp_path, features=["feature pass"])
    runtime = payload["entries"][0]["bounded_runtime"]
    assert runtime["next_route"] == "release"
    assert runtime["truth_recompiled_pending"] is False
    assert runtime["support_review"] == {}
    assert runtime["human_takeover_required"] is False
