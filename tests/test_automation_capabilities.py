from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.automation_capabilities import (
    build_automation_capabilities_payload,
    render_automation_capabilities_markdown,
)
from beacon.utils.automation_feedback import refresh_qa_feedback_ledger
from beacon.utils.automation_queue import validate_automation_queue


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def test_automation_capabilities_payload_should_report_boundary_and_assets():
    payload = build_automation_capabilities_payload(ROOT)

    assert payload["boundary"]["scheduler_owner"] == "codex_automations_or_host_scheduler"
    assert payload["boundary"]["truth_owner"] == "beacon"
    assert "nightly-qa" in payload["supported_job_patterns"]
    assert payload["assets"]["docs"] == "docs/analysis/codex-automations-and-beacon-capability-guide.md"
    assert payload["assets"]["queue_path"] == "automation/beacon-automation-queue.json"
    assert "automation/codex/nightly-qa.md" in payload["assets"]["codex_specs"]
    assert "automation/jobs/beacon-qa-job.sh" in payload["assets"]["job_wrappers"]
    assert payload["queue_contract"]["status"] == "valid"
    assert payload["bootstrap"]["init_entrypoint"] == "beacon automation init --project-root ."
    assert payload["bootstrap"]["toolkit_skill"] == "beacon-toolkit-automation"
    assert "shared_summary_entrypoint" in payload["feedback_loop"]
    assert any(item["executor"] == "cursor" for item in payload["executor_matrix"])


def test_automation_capabilities_markdown_should_render_human_sections():
    payload = build_automation_capabilities_payload(ROOT)
    text = render_automation_capabilities_markdown(payload)

    assert "# Beacon Automation Capabilities" in text
    assert "## Boundary" in text
    assert "## Supported Job Patterns" in text
    assert "## Codex Prompt Specs" in text
    assert "## Host Scheduler Assets" in text
    assert "## Feedback Loop" in text
    assert "## Bootstrap" in text
    assert "## Executor Matrix" in text


def test_automation_capabilities_cli_should_support_json_and_human_output():
    human = runner.invoke(app, ["automation", "capabilities", "--project-root", str(ROOT)])
    assert human.exit_code == 0, human.stdout
    assert "Beacon Automation Capabilities" in human.stdout
    assert "nightly-qa" in human.stdout

    machine = runner.invoke(app, ["automation", "capabilities", "--project-root", str(ROOT), "--json"])
    assert machine.exit_code == 0, machine.stdout
    payload = json.loads(machine.stdout)
    assert payload["assets"]["automation_root"] == "automation"
    assert "gated-implement" in payload["supported_job_patterns"]
    assert payload["queue_contract"]["status"] == "valid"
    assert payload["feedback_loop"]["qa_feedback_ledger"] == ".beacon/automation/qa-feedback-ledger.json"
    assert "build-summary" in payload["feedback_loop"]["shared_summary_entrypoint"]
    assert payload["bootstrap"]["ownership"] == "project_local_scaffold_generation"
    assert any(item["executor"] == "trae" and item["tier"] == "experimental" for item in payload["executor_matrix"])


def test_automation_validate_queue_should_accept_current_contract():
    result = runner.invoke(app, ["automation", "validate-queue", "--project-root", str(ROOT), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "valid"
    assert payload["queue_path"].endswith("automation/beacon-automation-queue.json")
    assert payload["error_count"] == 0


def test_automation_summarize_and_update_queue_cli_should_exist():
    summarize = runner.invoke(app, ["automation", "summarize-qa", "--project-root", str(ROOT), "--json"])
    assert summarize.exit_code == 0, summarize.stdout
    payload = json.loads(summarize.stdout)
    assert "entries" in payload

    update = runner.invoke(app, ["automation", "update-queue", "--project-root", str(ROOT), "--json"])
    assert update.exit_code == 0, update.stdout
    payload = json.loads(update.stdout)
    assert payload["status"] == "updated"


def test_automation_build_summary_cli_should_emit_shared_schema():
    result = runner.invoke(
        app,
        [
            "automation",
            "build-summary",
            "--project-root",
            str(ROOT),
            "--summary-kind",
            "functional",
            "--job",
            "demo-functional-qa",
            "--layer",
            "functional",
            "--status",
            "passed",
            "--tests",
            "6",
            "--failures",
            "0",
            "--artifact",
            "junit=/tmp/demo.junit.xml",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["summary_kind"] == "functional"
    assert payload["job"] == "demo-functional-qa"
    assert payload["layer"] == "functional"
    assert payload["status"] == "passed"
    assert payload["metrics"]["tests"] == 6
    assert payload["artifacts"]["junit"] == "/tmp/demo.junit.xml"
    assert payload["notification"]["lines"][0]
    assert "reconciliation" in payload


def test_automation_queue_validator_should_reject_invalid_implement_shape():
    payload = {
        "version": "v0",
        "project_root": "/tmp/demo",
        "default_workspace_mode": "worktree",
        "jobs": [
            {
                "job_id": "bad-implement",
                "job_kind": "implement",
                "target_agent": "codex",
                "enabled": True,
                "feature_selector": {"mode": "all_active"},
                "preconditions": ["truth_frozen"],
                "workspace_mode": "worktree",
                "risk_level": "medium",
                "on_blocked": "report_only",
                "on_success": "report_only",
                "notes": "bad",
            }
        ],
    }
    errors = validate_automation_queue(payload)
    assert any("all_active is supported only for status jobs" in item for item in errors)
    assert any("implement jobs must declare risk_level=high" in item for item in errors)
    assert any("implement jobs must declare on_success=trigger_qa" in item for item in errors)


def test_v145_docs_should_link_codex_automations_capability_surfaces():
    summary = (ROOT / "docs" / "beacon" / "v1.4.5" / "SUMMARY.md").read_text(encoding="utf-8")
    index_doc = (ROOT / "docs" / "beacon" / "v1.4.5" / "execution" / "index.md").read_text(encoding="utf-8")

    assert "docs/analysis/codex-automations-and-beacon-capability-guide.md" in summary
    assert "automation/README.md" in summary
    assert "beacon automation capabilities --project-root ." in summary
    assert "beacon automation validate-queue --project-root ." in summary

    assert "Codex Automations is supported as a host-scheduled capability plane" in index_doc
    assert "docs/analysis/codex-automations-and-beacon-capability-guide.md" in index_doc
    assert "beacon automation capabilities --project-root ." in index_doc
    assert "beacon automation validate-queue --project-root ." in index_doc
