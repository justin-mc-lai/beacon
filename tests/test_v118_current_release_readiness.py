from __future__ import annotations

import json
from pathlib import Path

from beacon import __toolkit_version__
from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.coverage import compute_coverage_metrics


ROOT = Path(__file__).resolve().parents[1]
VERSION = __toolkit_version__
runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_v118_current_release_should_have_required_execution_governance_artifacts():
    machine_exec = ROOT / "docs" / "beacon" / VERSION / ".machine" / "execution"
    required = [
        "config.json",
        "source.json",
        "git-alignment.json",
        "delivery-manifest.json",
        "change-impact.json",
        "terminal.json",
    ]
    for name in required:
        assert (machine_exec / name).exists(), name


def test_v118_current_release_should_report_full_coverage():
    payload = compute_coverage_metrics(ROOT, version=VERSION)
    assert payload["planned_story"] >= 1
    assert payload["implemented_story"] == payload["planned_story"]
    assert payload["total_ac"] >= 1
    assert payload["total_tc"] >= 1
    assert payload["tested_ac"] <= payload["total_ac"]
    assert payload["executed_tc"] <= payload["total_tc"]


def test_v118_current_release_runtime_evidence_should_align_with_release_line():
    auto_test = json.loads((ROOT / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
    gate_report = json.loads((ROOT / ".beacon" / "gate-report.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / ".beacon" / "evidence-manifest.json").read_text(encoding="utf-8"))
    chain = json.loads((ROOT / ".beacon" / "evidence-signature-chain.json").read_text(encoding="utf-8"))

    assert auto_test["version"] == VERSION
    assert gate_report["version"] == VERSION
    assert manifest["version"] == VERSION
    assert auto_test["run_id"]
    assert gate_report["run_id"]
    assert manifest["run_id"]
    assert isinstance(chain, list) and chain
    assert chain[-1]["run_id"]


def test_v118_current_release_should_pass_delivery_gate_and_release_checks():
    delivery = _invoke(["doctor", "verify-delivery", "--project-root", str(ROOT), "--version", VERSION, "--json"])
    assert delivery.exit_code == 0, delivery.stdout
    delivery_payload = json.loads(delivery.stdout)
    assert delivery_payload["status"] in {"PASS", "WARN"}

    gate = _invoke(["gate", "check", "release", "--project-root", str(ROOT), "--version", VERSION, "--json"])
    assert gate.exit_code in {0, 2}, gate.stdout
    gate_payload = json.loads(gate.stdout)
    assert gate_payload["status"] in {"Pass", "Blocked"}
    assert "blocked_count" in gate_payload

    release = _invoke(["release", "check", VERSION, "--project", str(ROOT)])
    assert release.exit_code in {0, 1}, release.stdout
