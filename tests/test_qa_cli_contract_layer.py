"""Regression: CLI contract layers must not fail QA for lacking junit.

A frozen TC can legitimately be "run this CLI and expect exit 0"
(e.g. ``wrangler deploy --dry-run``). Demanding junit/assertion counts from
those layers marked a green run as failed, and the stored failure then blocked
every later run through ``previous_feature_qa_not_passed``.
"""

from __future__ import annotations

from pathlib import Path

from beacon.commands.auto_test import _collect_required_file_issues, _layer_uses_test_runner


def _cli_layer(**overrides):
    layer = {
        "layer": "contract",
        "command": "npx wrangler deploy --dry-run --outdir .wrangler/dry",
        "status": "passed",
        "exit_code": 0,
        "assertion_count": 0,
        "junit_path": "",
        "junit_valid": False,
        "evidence_ref": [
            ".beacon/evidence/auto-test/run-x/contract/command.txt",
            ".beacon/evidence/auto-test/run-x/contract/stdout.log",
        ],
    }
    layer.update(overrides)
    return layer


def test_cli_contract_layer_needs_no_junit(tmp_path: Path):
    issues = _collect_required_file_issues(
        project_root=tmp_path,
        layer_results=[_cli_layer()],
        require_junit=True,
        require_assertion_count=True,
    )
    assert issues == []


def test_cli_contract_layer_still_needs_captured_evidence(tmp_path: Path):
    issues = _collect_required_file_issues(
        project_root=tmp_path,
        layer_results=[_cli_layer(evidence_ref=[])],
        require_junit=True,
        require_assertion_count=True,
    )
    assert [item["reason_code"] for item in issues] == ["command_evidence_missing"]


def test_real_test_runner_layer_still_requires_junit(tmp_path: Path):
    issues = _collect_required_file_issues(
        project_root=tmp_path,
        layer_results=[
            _cli_layer(command="python3 -m pytest -q tests/", assertion_count=0),
        ],
        require_junit=True,
        require_assertion_count=True,
    )
    codes = [item["reason_code"] for item in issues]
    assert "assertion_count_zero_pass" in codes
    assert "junit_missing_or_invalid" in codes


def test_unknown_command_stays_strict():
    assert _layer_uses_test_runner({"layer": "unit", "status": "passed"}) is True


def test_wrangler_and_tsc_are_not_test_runners():
    assert _layer_uses_test_runner(_cli_layer()) is False
    assert _layer_uses_test_runner(_cli_layer(command="npx tsc --noEmit")) is False
    assert _layer_uses_test_runner(_cli_layer(command="npx vitest run")) is True
