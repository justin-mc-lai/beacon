from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.automation_capabilities import build_automation_capabilities_payload
from beacon.utils.automation_feedback import refresh_qa_feedback_ledger, update_automation_queue_from_feedback


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed_feature_status(root: Path, *, feature: str, status: str, continue_decision: str = "continue", stop_reasons: list[str] | None = None) -> None:
    slug = feature.replace(" ", "-").replace("_", "-").lower()
    _write_json(
        root / ".beacon" / "qa" / "features" / slug / "status.json",
        {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slug,
            "version": "v1.4.6",
            "run_id": f"run-{slug}",
            "status": status,
            "evidence_done": status == "passed",
            "release_ready": status == "passed",
            "targeted_rerun": {"targeted_layers": ["functional"], "targeted_tc_ids": ["TC-001"], "targeted_scenario_ids": ["SC-001"]},
            "feature_scorecard": {
                "continue_decision": continue_decision,
                "stop_reasons": stop_reasons or [],
                "resume_command": f'beacon qa run "{feature}" --project-root . --version v1.4.6',
                "repair_handoff": {
                    "action": "implement-repair" if continue_decision == "stop_for_repair" else "",
                    "command": f'beacon implement run "{feature}" --project . --version v1.4.6 --runner native-single' if continue_decision == "stop_for_repair" else "",
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
            "resume_command": f'beacon qa run "{feature}" --project-root . --version v1.4.6',
            "repair_handoff": {
                "action": "implement-repair" if continue_decision == "stop_for_repair" else "",
                "command": f'beacon implement run "{feature}" --project . --version v1.4.6 --runner native-single' if continue_decision == "stop_for_repair" else "",
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


def test_qa_feedback_ledger_contract_is_frozen(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature pass", status="passed")
    payload = refresh_qa_feedback_ledger(tmp_path, features=["feature pass"])
    assert payload["entry_count"] == 1
    entry = payload["entries"][0]
    assert entry["feature"] == "feature pass"
    assert entry["status"] == "passed"
    assert "continue_decision" in entry
    assert "repair_command" in entry


def test_automation_cli_exposes_summarize_qa(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature pass", status="passed")
    result = runner.invoke(app, ["automation", "summarize-qa", "--project-root", str(tmp_path), "--feature", "feature pass", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["entry_count"] == 1


def test_automation_cli_exposes_update_queue(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature pass", status="passed")
    _seed_queue(tmp_path)
    refresh_qa_feedback_ledger(tmp_path, features=["feature pass"])
    result = runner.invoke(app, ["automation", "update-queue", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "updated"


def test_queue_update_is_explicit_and_governed(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature pass", status="passed")
    _seed_feature_status(tmp_path, feature="feature repair", status="blocked", continue_decision="stop_for_repair", stop_reasons=["implementation_reopened"])
    _seed_queue(tmp_path)
    refresh_qa_feedback_ledger(tmp_path, features=["feature pass", "feature repair"])
    payload = update_automation_queue_from_feedback(tmp_path)
    updated = json.loads((tmp_path / "automation" / "beacon-automation-queue.json").read_text(encoding="utf-8"))
    qa_features = updated["jobs"][0]["feature_selector"]["features"]
    implement_features = updated["jobs"][1]["feature_selector"]["features"]
    assert "feature pass" not in qa_features
    assert "feature repair" in qa_features
    assert "feature repair" in implement_features
    assert any(item["action"] == "removed_from_qa_queue" for item in payload["updates"])
    assert any(item["action"] == "added_to_implement_queue" for item in payload["updates"])


def test_queue_update_keeps_passed_but_repair_needed_feature_in_repair_loop(tmp_path: Path) -> None:
    _seed_feature_status(tmp_path, feature="feature pass", status="passed")
    _seed_feature_status(
        tmp_path,
        feature="feature qa repair",
        status="passed",
        continue_decision="stop_for_repair",
        stop_reasons=["assertion_count_zero_pass"],
    )
    _seed_queue(tmp_path)
    queue_path = tmp_path / "automation" / "beacon-automation-queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    queue["jobs"][0]["feature_selector"]["features"] = ["feature pass", "feature qa repair"]
    queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    refresh_qa_feedback_ledger(tmp_path, features=["feature pass", "feature qa repair"])
    payload = update_automation_queue_from_feedback(tmp_path)

    updated = json.loads(queue_path.read_text(encoding="utf-8"))
    qa_features = updated["jobs"][0]["feature_selector"]["features"]
    implement_features = updated["jobs"][1]["feature_selector"]["features"]
    assert "feature pass" not in qa_features
    assert "feature qa repair" in qa_features
    assert "feature qa repair" in implement_features
    assert any(item["feature"] == "feature qa repair" and item["action"] == "added_to_implement_queue" for item in payload["updates"])


def test_nightly_qa_wrapper_refreshes_feedback_loop() -> None:
    text = (ROOT / "automation" / "jobs" / "beacon-qa-job.sh").read_text(encoding="utf-8")
    assert 'automation summarize-qa' in text
    assert 'automation build-summary' in text
    assert 'automation update-queue' in text
    assert '.beacon/automation/qa-feedback-ledger.json' in text
    assert 'cp "${LEDGER_ARTIFACT_PATH}" "${CANONICAL_LEDGER_PATH}"' in text
    assert 'AUTOMATION_FEISHU_WEBHOOK' in text
    assert 'beacon-notify-feishu-post.py' in text
    assert 'send_summary_notification "${SUMMARY_PATH}" "Beacon nightly QA"' in text
    assert "nightly QA window closed, skipping" in text


def test_hourly_qa_wrapper_refreshes_feedback_loop() -> None:
    text = (ROOT / "automation" / "jobs" / "beacon-hourly-qa-job.sh").read_text(encoding="utf-8")
    assert "qa-global.lock" in text
    assert 'automation summarize-qa' in text
    assert 'automation build-summary' in text
    assert 'automation update-queue' in text
    assert '.beacon/automation/qa-feedback-ledger.json' in text
    assert '--summary-kind hourly' in text
    assert 'send_summary_notification "${SUMMARY_PATH}" "Beacon hourly QA"' in text
    assert "hourly QA window closed, skipping" in text


def test_gated_implement_wrapper_refreshes_queue() -> None:
    text = (ROOT / "automation" / "jobs" / "beacon-gated-implement-job.sh").read_text(encoding="utf-8")
    assert "implement run" in text
    assert "implement dev-run" not in text
    assert "--auto-qa" in text
    assert 'automation summarize-qa' in text
    assert 'automation build-summary' in text
    assert 'automation update-queue' in text


def test_repair_window_wrapper_is_controlled_and_refreshes_queue() -> None:
    text = (ROOT / "automation" / "jobs" / "beacon-repair-window-job.sh").read_text(encoding="utf-8")
    assert "Repair window requires exactly one enabled implement feature" in text
    assert "Refusing repair window on dirty worktree" in text
    assert "--allow-dirty" in text
    assert "implement run" in text
    assert "qa run" in text
    assert 'automation summarize-qa' in text
    assert 'automation update-queue' in text
    assert 'send_summary_notification "${SUMMARY_PATH}" "Beacon repair window"' in text


def test_automation_capabilities_report_feedback_loop_surface() -> None:
    payload = build_automation_capabilities_payload(ROOT)
    feedback_loop = payload["feedback_loop"]
    assert feedback_loop["qa_feedback_ledger"] == ".beacon/automation/qa-feedback-ledger.json"
    assert "summarize-qa" in feedback_loop["qa_summary_entrypoint"]
    assert "build-summary" in feedback_loop["shared_summary_entrypoint"]
    assert "update-queue" in feedback_loop["queue_update_entrypoint"]
    assert "hourly-qa" in payload["supported_job_patterns"]
    assert "repair-window" in payload["supported_job_patterns"]
    assert any(item["executor"] == "codex" and item["beacon_runtime_execution"] is True for item in payload["executor_matrix"])


def test_automation_jobs_feedback_loop_preserves_core_lifecycle_boundary() -> None:
    prd = (ROOT / "docs" / "beacon" / "v1.4.6" / "prd" / "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md").read_text(encoding="utf-8")
    story = (ROOT / "docs" / "beacon" / "v1.4.6" / "user-story" / "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md").read_text(encoding="utf-8")
    assert "not a new lifecycle stage" in prd
    assert "does not create a new Beacon lifecycle stage" in story


def test_automation_jobs_feedback_loop_is_registered_in_machine_change_and_blueprint() -> None:
    machine_change = json.loads(
        (ROOT / "docs" / "beacon" / "v1.4.6" / ".machine" / "change" / "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.json").read_text(encoding="utf-8")
    )
    version_change = json.loads(
        (ROOT / "docs" / "beacon" / "v1.4.6" / ".machine" / "change" / "v1.4.6.json").read_text(encoding="utf-8")
    )
    blueprint = (ROOT / "docs" / "beacon" / "v1.4.6" / "execution" / "architecture-blueprint.md").read_text(encoding="utf-8")

    assert machine_change["feature_slug"] == "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance"
    assert ".beacon/automation/qa-feedback-ledger.json" == machine_change["artifacts"]["feedback_ledger"]
    assert version_change["feature_count"] == 3
    assert any(
        item["feature_slug"] == "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance"
        for item in version_change["features"]
    )
    assert "Automation Jobs Feedback Loop" in blueprint


def test_automation_jobs_feedback_loop_is_exposed_in_runbook_and_release_docs() -> None:
    runbook = (ROOT / "docs" / "beacon" / "v1.4.6" / "execution" / "automation-jobs-runbook.md").read_text(encoding="utf-8")
    release = (ROOT / "docs" / "beacon" / "v1.4.6" / "release" / "v1.4.6.md").read_text(encoding="utf-8")
    checklist = (ROOT / "docs" / "beacon" / "v1.4.6" / "release" / "checklist-v1.4.6.md").read_text(encoding="utf-8")

    assert "beacon automation summarize-qa --project-root ." in runbook
    assert "beacon automation update-queue --project-root ." in runbook
    assert "project-local automation/jobs feedback loop" in release
    assert "Automation jobs operator runbook generated" in checklist
