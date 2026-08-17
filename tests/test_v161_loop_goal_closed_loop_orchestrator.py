from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TRUTH = ROOT / "docs/beacon/archive/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md"
BEACON_RUN = ROOT / "packages/beacon-run"
BEACON_LOOP = ROOT / "packages/beacon-loop"


def test_truth_ac072_unified_goal_and_scope() -> None:
    text = TRUTH.read_text(encoding="utf-8")
    assert "AC-072" in text
    assert "beacon-loop goal" in text
    assert "湖" in text or "lake" in text.lower()
    assert "海" in text or "program" in text.lower()


def test_truth_ac074_eval_supplement_contract() -> None:
    text = TRUTH.read_text(encoding="utf-8")
    assert "eval-matrix" in text or "eval_matrix" in text
    assert "formal_verdict_authority=false" in text


def test_beacon_loop_delegate_sources_present() -> None:
    assert (BEACON_LOOP / "src/beacon-run-delegate.ts").exists()
    assert (BEACON_LOOP / "src/intent/scope-classify.ts").exists()


def test_beacon_run_program_outer_fsm_sources_present() -> None:
    assert (BEACON_RUN / "src/beacon/program-outer-fsm.ts").exists()
    assert (BEACON_RUN / "src/beacon/program-mode.ts").exists()
    assert (BEACON_RUN / "src/beacon/eval-supplement.ts").exists()


def _run_beacon_run_vitest(*, filter_name: str, extra_env: dict[str, str] | None = None) -> None:
    env = {**os.environ, **(extra_env or {})}
    build = subprocess.run(
        ["pnpm", "run", "build"],
        cwd=BEACON_RUN,
        capture_output=True,
        text=True,
        env=env,
    )
    assert build.returncode == 0, build.stderr or build.stdout
    proc = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "-t", filter_name],
        cwd=BEACON_RUN,
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_program_outer_fsm_vitest_gate() -> None:
    _run_beacon_run_vitest(filter_name="program-outer-fsm")


def test_e2e_program_sea_vitest_gate() -> None:
    _run_beacon_run_vitest(
        filter_name="e2e-program-sea",
        extra_env={"BEACON_RUN_E2E_PROGRAM": "1"},
    )


def test_beacon_loop_dry_run_sea_program_delegate() -> None:
    cli = BEACON_LOOP / "dist/cli.js"
    assert cli.exists(), "beacon-loop dist missing; run npm run build in packages/beacon-loop"
    proc = subprocess.run(
        [
            "node",
            str(cli),
            "goal",
            "复刻全站海级 program",
            "--project",
            str(ROOT),
            "--version",
            "v1.6.1",
            "--feature",
            "demo-sea",
            "--lake-or-ocean",
            "海",
            "--mode",
            "program",
            "--dry-run",
            "--json",
        ],
        cwd=BEACON_LOOP,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    payload = json.loads(proc.stdout)
    assert payload.get("status") == "dry_run"
    assert payload.get("delivery_mode") == "program"
    assert "--mode program" in str(payload.get("beacon_run_command", ""))
