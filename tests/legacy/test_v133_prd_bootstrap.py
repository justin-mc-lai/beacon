from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.context_files import setup_context_files


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / "v1.3.3"
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# v1.3.3\n", encoding="utf-8")


def _seed_context(root: Path) -> None:
    setup_context_files(
        project_root=root,
        runtime_version="v1.3.3",
        dry_run=False,
        force=False,
        with_claude=True,
        with_agents=True,
    )


def _extract_ac_ids(text: str) -> list[str]:
    return sorted(set(match.group(0).upper() for match in re.finditer(r"\bAC-\d{3}\b", text, flags=re.IGNORECASE)))


def _init_git_repo(root: Path, *, version: str = "v1.3.3") -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    (root / ".gitkeep").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "switch", "-c", f"beacon/{version}"], cwd=root, check=True, capture_output=True, text=True)


def _write_runner_script(path: Path) -> None:
    path.write_text(
        (
            "import json, pathlib, sys\n"
            "request_file = pathlib.Path(sys.argv[1])\n"
            "result_file = pathlib.Path(sys.argv[2])\n"
            "payload = json.loads(request_file.read_text())\n"
            "result_file.parent.mkdir(parents=True, exist_ok=True)\n"
            "result_file.write_text(json.dumps({\n"
            "  'schema_version': '1.0',\n"
            "  'run_id': payload['run_id'],\n"
            "  'status': 'completed',\n"
            "  'summary': 'fake runner completed',\n"
            "  'changed_files': ['beacon/utils/requirement_parsing.py'],\n"
            "  'verification': [{'command': 'pytest -q', 'status': 'passed'}],\n"
            "  'artifact_updates': {'prd': {'required': False}}\n"
            "}, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')\n"
        ),
        encoding="utf-8",
    )


def _write_passing_layer_script(path: Path) -> None:
    path.write_text(
        (
            "#!/bin/sh\n"
            "set -eu\n"
            "mkdir -p \"$(dirname \"$BEACON_JUNIT_PATH\")\"\n"
            "cat > \"$BEACON_JUNIT_PATH\" <<'XML'\n"
            "<testsuite tests=\"1\"><testcase classname=\"qa\" name=\"ok\"/></testsuite>\n"
            "XML\n"
            "echo 'BEACON_ASSERTIONS: 1'\n"
        ),
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_v133_prd_bootstrap_should_default_to_safe_dry_run(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_context(tmp_path)
    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Checkout Reliability",
            "--desc",
            "提升支付确认链路可靠性",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "planned"
    assert payload["dry_run"] is True
    assert payload["strict_context_verify"] is True
    assert payload["no_overwrite"] is True
    assert (tmp_path / payload["state_path"]).exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.3.3" / "prd" / "checkout-reliability.md").exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.3.3" / "user-story" / "checkout-reliability.md").exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.3.3" / "qa" / "test-cases" / "checkout-reliability.md").exists()


def test_v133_prd_bootstrap_apply_should_write_three_docs_and_state(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_context(tmp_path)
    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Checkout Reliability",
            "--desc",
            "提升支付确认链路可靠性",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--apply",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "applied"
    assert payload["dry_run"] is False
    assert payload["rollback_plan"]
    assert (tmp_path / payload["state_path"]).exists()
    assert not (tmp_path / payload["lock_path"]).exists()

    prd_path = tmp_path / "docs" / "beacon" / "v1.3.3" / "prd" / "checkout-reliability.md"
    us_path = tmp_path / "docs" / "beacon" / "v1.3.3" / "user-story" / "checkout-reliability.md"
    tc_path = tmp_path / "docs" / "beacon" / "v1.3.3" / "qa" / "test-cases" / "checkout-reliability.md"
    assert prd_path.exists()
    assert us_path.exists()
    assert tc_path.exists()

    ac_story = _extract_ac_ids(us_path.read_text(encoding="utf-8"))
    ac_test = _extract_ac_ids(tc_path.read_text(encoding="utf-8"))
    assert ac_story
    assert ac_story == ac_test


def test_v133_prd_bootstrap_payment_flow_should_keep_ac_count_stable_through_sync_and_qa(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_context(tmp_path)

    bootstrap = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Checkout Reliability",
            "--desc",
            "提升支付确认链路可靠性",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--apply",
            "--json",
        ]
    )
    assert bootstrap.exit_code == 0, bootstrap.stdout

    sync = _invoke(
        [
            "doctor",
            "sync-materials",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--feature",
            "checkout-reliability",
            "--json",
        ]
    )
    assert sync.exit_code == 0, sync.stdout
    sync_payload = json.loads(sync.stdout)
    result = sync_payload["result"]["results"][0]
    assert result["story_sync"]["ac_count"] == 5
    assert result["story_sync"]["test_count"] == 5

    story = json.loads((tmp_path / "docs" / "beacon" / "v1.3.3" / ".machine" / "user-story" / "checkout-reliability.json").read_text(encoding="utf-8"))
    active_story = next(item for item in story["stories"] if item["revision_id"] == story["current_revision_id"])
    ac_items = [item for item in active_story["items"] if item["kind"] == "ac"]
    test_items = [item for item in active_story["items"] if item["kind"] == "test"]
    assert [item["id"] for item in ac_items] == ["AC-001", "AC-002", "AC-003", "AC-004", "AC-005"]
    assert [item["id"] for item in test_items] == ["TEST-001", "TEST-002", "TEST-003", "TEST-004", "TEST-005"]

    qa = _invoke(
        [
            "qa",
            "run",
            "Checkout Reliability",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--json",
        ]
    )
    assert qa.exit_code == 2, qa.stdout
    qa_payload = json.loads(qa.stdout)
    assert qa_payload["status"] == "blocked"
    assert qa_payload["reason_codes"] == ["implementation_not_recorded", "no_prior_feature_qa"]
    assert [item["ac_id"] for item in qa_payload["story_sequence"]] == ["AC-001", "AC-002", "AC-003", "AC-004", "AC-005"]


def test_v133_prd_bootstrap_payment_flow_should_close_after_freeze_review_implement_and_qa(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    _seed_docs(tmp_path)
    _seed_context(tmp_path)

    bootstrap = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Checkout Reliability",
            "--desc",
            "提升支付确认链路可靠性",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--apply",
            "--json",
        ]
    )
    assert bootstrap.exit_code == 0, bootstrap.stdout

    sync = _invoke(
        [
            "doctor",
            "sync-materials",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--feature",
            "checkout-reliability",
            "--json",
        ]
    )
    assert sync.exit_code == 0, sync.stdout

    freeze = _invoke(
        [
            "freeze",
            "Checkout Reliability",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--json",
        ]
    )
    assert freeze.exit_code == 0, freeze.stdout

    tech_review = _invoke(
        [
            "doctor",
            "sync-technical-review-contract",
            "Checkout Reliability",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--revision-id",
            "R1",
            "--review-status",
            "approved",
            "--approved-by",
            "qa-loop",
            "--reviewed-at",
            "2026-04-19T15:01:00+08:00",
            "--force-refresh",
            "--json",
        ]
    )
    assert tech_review.exit_code == 0, tech_review.stdout
    tech_review_payload = json.loads(tech_review.stdout)
    assert tech_review_payload["result"]["review_status"] == "approved"

    plan = _invoke(
        [
            "implement",
            "plan",
            "Checkout Reliability",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--json",
        ]
    )
    assert plan.exit_code == 0, plan.stdout
    assert json.loads(plan.stdout)["status"] == "planned"

    runner_script = tmp_path / "runner.py"
    _write_runner_script(runner_script)
    pass_layer = tmp_path / "pass-layer.sh"
    _write_passing_layer_script(pass_layer)
    (tmp_path / "beacon.config.yaml").write_text(
        (
            "skill:\n"
            "  adapters:\n"
            "    fake:\n"
            "      adapter_type: command\n"
            "      runtime_family: fake\n"
            "      command: python3\n"
            "      args:\n"
            "        - \"{project_root}/runner.py\"\n"
            "        - \"{request_file}\"\n"
            "        - \"{result_file}\"\n"
        ),
        encoding="utf-8",
    )

    implement = _invoke(
        [
            "implement",
            "run",
            "Checkout Reliability",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert implement.exit_code == 0, implement.stdout
    assert json.loads(implement.stdout)["status"] == "completed"
    assert (tmp_path / ".beacon" / "state" / "implementation-checkout-reliability.json").exists()

    qa = _invoke(
        [
            "qa",
            "run",
            "Checkout Reliability",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--layer-command",
            f"unit=sh {pass_layer}",
            "--layer-command",
            f"contract=sh {pass_layer}",
            "--layer-command",
            f"integration=sh {pass_layer}",
            "--layer-command",
            f"smoke=sh {pass_layer}",
            "--layer-command",
            f"regression=sh {pass_layer}",
            "--layer-command",
            f"exception=sh {pass_layer}",
            "--layer-command",
            f"interface=sh {pass_layer}",
            "--json",
        ]
    )
    assert qa.exit_code == 0, qa.stdout
    qa_payload = json.loads(qa.stdout)
    assert qa_payload["status"] == "passed"
    assert qa_payload["evidence_done"] is True
    assert qa_payload["feature_scorecard"]["continue_decision"] == "ready_for_release"
    assert qa_payload["feature_scorecard"]["release_ready"] is True
    assert qa_payload["failed_item_ids"] == []


def test_v133_prd_bootstrap_apply_should_block_when_target_exists_under_default_no_overwrite(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_context(tmp_path)
    target = tmp_path / "docs" / "beacon" / "v1.3.3" / "prd" / "checkout-reliability.md"
    target.write_text("existing\n", encoding="utf-8")

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Checkout Reliability",
            "--desc",
            "提升支付确认链路可靠性",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--apply",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "write_blocked"
    assert "--allow-overwrite" in payload["recommended_command"]
    assert target.read_text(encoding="utf-8") == "existing\n"
    assert not (tmp_path / payload["lock_path"]).exists()


def test_v133_prd_bootstrap_should_block_when_lock_already_active(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_context(tmp_path)
    lock = tmp_path / ".beacon" / "state" / "locks" / "prd-bootstrap.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text("run_id=locked\n", encoding="utf-8")

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Checkout Reliability",
            "--desc",
            "提升支付确认链路可靠性",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--apply",
            "--allow-overwrite",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "lock_active"
    assert "lock already active" in str(payload.get("error") or "")


def test_v133_prd_bootstrap_should_enforce_strict_context_verify_by_default(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Checkout Reliability",
            "--desc",
            "提升支付确认链路可靠性",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.3",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "context_verify_failed"
    assert "doctor setup-context" in payload["recommended_command"]
