from __future__ import annotations

import json
import re
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
