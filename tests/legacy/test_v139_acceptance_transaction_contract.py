from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_acceptance_projection_transaction_contract, check_prototype_contract
from beacon.main import app
from beacon.utils.doctor_orchestrator import run_delivery_verify
from beacon.utils.release_scorecard import build_release_scorecard
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import write_json
from beacon.utils.writeback import (
    acceptance_projection_transaction_contract,
    record_acceptance_writeback,
    record_implementation_writeback,
    record_verification_writeback,
)


VERSION = "v1.3.9"
FEATURE = "Beacon v1.3.9 execution projection convergence and QA acceptance dual-write"
SLUG = "beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write"
runner = CliRunner()


def _seed_docs(root: Path) -> None:
    docs = root / "docs" / "beacon" / VERSION
    (docs / "execution").mkdir(parents=True, exist_ok=True)
    (docs / ".machine" / "change").mkdir(parents=True, exist_ok=True)
    (docs / "change").mkdir(parents=True, exist_ok=True)
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    (docs / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (docs / "execution" / "index.md").write_text("# Execution Index\n", encoding="utf-8")
    (docs / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (docs / "change" / f"{VERSION}.md").write_text("# Version Change\n", encoding="utf-8")
    write_json(
        docs / ".machine" / "change" / f"{VERSION}.json",
        {"version": VERSION, "feature_count": 1, "features": [{"feature_slug": SLUG}]},
    )
    (docs / "user-story" / f"{SLUG}.md").write_text(
        "# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Acceptance | transaction converges |\n",
        encoding="utf-8",
    )
    (docs / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (docs / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")


def _seed_acceptance_success(root: Path) -> dict[str, str]:
    _seed_docs(root)
    (root / ".beacon" / "state").mkdir(parents=True, exist_ok=True)
    write_json(root / ".beacon" / "gate-report.json", {"status": "Pass", "version": VERSION, "issues": []})
    write_json(
        root / ".beacon" / "qa" / "status.json",
        {
            "feature": FEATURE,
            "version": VERSION,
            "status": "passed",
            "evidence_done": True,
            "execution_mode": "feature-aware",
            "release_ready": True,
        },
    )
    freeze_revision_state(root, version=VERSION, feature=FEATURE)
    record_implementation_writeback(
        root,
        version=VERSION,
        feature=FEATURE,
        run_id="run-impl",
        implemented_item_ids=["AC-001", "TEST-001"],
        changed_files=["beacon/utils/writeback.py"],
    )
    record_verification_writeback(
        root,
        version=VERSION,
        feature=FEATURE,
        run_id="run-qa",
        verified_item_ids=["AC-001", "TEST-001"],
        failed_item_ids=[],
        evidence_ref=[".beacon/qa/status.json"],
    )
    run_dir = root / ".beacon" / "runs" / "run-qa"
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "state.json", {"workflow": "workflow.start", "run_id": "run-qa", "version": VERSION, "feature": FEATURE})
    result = record_acceptance_writeback(
        root,
        version=VERSION,
        feature=FEATURE,
        accepted_by="qa",
        verdict="passed",
        run_id="run-qa",
        evidence_ref=[".beacon/qa/status.json"],
        source_command=f'beacon qa run "{FEATURE}" --project-root . --version {VERSION}',
        accepted_ac_ids=["AC-001"],
        accepted_test_ids=["TEST-001"],
    )
    return {
        "machine_path": str(result["machine_path"]),
        "markdown_path": str(result["markdown_path"]),
        "runtime_path": str(result["runtime_path"]),
    }


def test_v139_release_scorecard_should_expose_acceptance_transaction_contract(tmp_path: Path) -> None:
    _seed_acceptance_success(tmp_path)

    payload = build_release_scorecard(tmp_path, version=VERSION)

    assert payload["acceptance"]["source"] == "qa_acceptance_envelope"
    assert payload["acceptance_transaction"]["status"] == "pass"
    assert payload["qa"]["acceptance_transaction_status"] == "pass"


def test_v139_gate_should_block_when_acceptance_runtime_projection_is_missing(tmp_path: Path) -> None:
    refs = _seed_acceptance_success(tmp_path)
    (tmp_path / refs["runtime_path"]).unlink()

    contract = acceptance_projection_transaction_contract(tmp_path, version=VERSION, feature=FEATURE)
    assert contract["status"] == "warn"
    assert contract["reason_code"] == "acceptance_projection_missing"

    issues = check_acceptance_projection_transaction_contract(
        tmp_path,
        GateMode.STRICT,
        "release",
        VERSION,
    )
    assert issues
    assert issues[0]["blocked"] is True
    assert issues[0]["reason_code"] == "acceptance_projection_missing"


def test_v139_doctor_delivery_verify_should_surface_acceptance_transaction_check(tmp_path: Path) -> None:
    refs = _seed_acceptance_success(tmp_path)
    (tmp_path / refs["runtime_path"]).unlink()

    result = run_delivery_verify(
        project_root=str(tmp_path),
        version=VERSION,
        strict=False,
    )
    checks = result.payload["result"]["checks"]
    acceptance_check = next(item for item in checks if item["name"] == "acceptance_projection_transaction_contract")
    assert acceptance_check["status"] == "warn"


def test_v139_prototype_auto_mode_should_not_silently_pass_when_it_falls_back_to_rule(tmp_path: Path, monkeypatch) -> None:
    _seed_docs(tmp_path)
    story_path = tmp_path / "docs" / "beacon" / VERSION / "user-story" / f"{SLUG}.md"
    story_path.write_text(
        "# User Story\n\nprototype visualization required\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Prototype | must not silently downgrade |\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("BEACON_LLM_API_KEY", raising=False)
    monkeypatch.delenv("BEACON_PROTOTYPE_DISABLE_LLM", raising=False)

    create = runner.invoke(app, ["prototype", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert create.exit_code == 0, create.stdout
    review = runner.invoke(app, ["prototype", "review", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert review.exit_code == 0, review.stdout
    freeze = runner.invoke(app, ["prototype", "freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "release", version=VERSION)
    assert any(item["reason_code"] == "prototype_auto_template_downgrade_blocked" for item in issues)
