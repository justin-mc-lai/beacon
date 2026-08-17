from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _ask_payload(tmp_path: Path, goal: str = "做一次环境诊断") -> dict:
    result = runner.invoke(app, ["ask", goal, "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0
    return json.loads(result.stdout)


def test_reuse_existing_learning_kernel(tmp_path: Path):
    payload = _ask_payload(tmp_path)
    disclosure = payload.get("learning_disclosure", {})
    assert disclosure.get("source") == "existing_learning_plane_contract"
    assert disclosure.get("contract_ref") == ".beacon/state/evo/decision-engine.json"


def test_progressive_disclosure_order(tmp_path: Path):
    payload = _ask_payload(tmp_path)
    disclosure = payload.get("learning_disclosure", {})
    assert disclosure.get("disclosure_order") == ["feature", "host", "runner", "domain"]


def test_learning_is_hint_not_truth(tmp_path: Path):
    payload = _ask_payload(tmp_path)
    disclosure = payload.get("learning_disclosure", {})
    assert disclosure.get("truth_role") == "hint_only"
    assert disclosure.get("cannot_override") == ["frozen_truth", "gate_verdict", "release_ready"]


def test_stale_and_superseded_learning_downgrade(tmp_path: Path):
    payload = _ask_payload(tmp_path)
    policy = payload.get("learning_disclosure", {}).get("freshness_policy", {})
    assert policy.get("stale") == "downgrade"
    assert policy.get("superseded") == "downgrade"
