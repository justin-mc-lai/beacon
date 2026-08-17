from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TRUTH = ROOT / "docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md"


def test_truth_integrity_not_blocked() -> None:
    proc = subprocess.run(
        [
            "beacon",
            "doctor",
            "verify-truth-integrity",
            "beacon-test-modernization-v1612",
            "--project-root",
            str(ROOT),
            "--version",
            "v1.6.12",
            "--mode",
            "block",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    payload = json.loads(proc.stdout)
    blocked = payload.get("result", {}).get("blocked")
    assert blocked is False
    # archived v1.6.1 package is intentionally fail-closed under current validation
    archived = subprocess.run(
        [
            "beacon",
            "doctor",
            "verify-truth-integrity",
            "beacon-harness-program-plan-v161",
            "--project-root",
            str(ROOT),
            "--version",
            "v1.6.1",
            "--mode",
            "block",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    archived_payload = json.loads(archived.stdout)
    assert archived_payload.get("result", {}).get("blocked") is True
    assert archived_payload.get("result", {}).get("reason_code") == "feature_package_validation_failed"


def test_program_plan_contract_defines_graph_and_fsm() -> None:
    contract = ROOT / "docs/beacon/archive/v1.6.1/execution/program-plan-contract.md"
    assert contract.is_file()
    text = contract.read_text(encoding="utf-8")
    assert "feature-graph.json" in text
    assert "truth-promotion" in text or "program" in text.lower()


def test_operator_guide_declares_goal_primary_entry() -> None:
    guide = ROOT / "docs/beacon/archive/v1.6.1/execution/long-task-operator-guide.md"
    assert guide.is_file()
    text = guide.read_text(encoding="utf-8")
    assert "beacon-loop goal" in text
    assert "scaffold" in text.lower()
    assert "beacon plan start" in text


def test_truth_declares_goal_entry_and_program_fsm() -> None:
    text = TRUTH.read_text(encoding="utf-8")
    assert "beacon-loop goal" in text
    assert "program-run-state" in text
    assert "beacon-loop-goal-closed-loop-orchestrator-v161" in text
