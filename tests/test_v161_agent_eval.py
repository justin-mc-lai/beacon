from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from beacon.utils.agent_surface import v160_skill_package_projection


def _invoke(args: list[str], *, cwd: Path) -> dict:
    env = {"BEACON_ALLOW_CONTEXT_VERSION_DRIFT": "1", **dict(__import__("os").environ)}
    proc = subprocess.run(
        [sys.executable, "-m", "beacon", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )
    payload = {}
    if proc.stdout.strip():
        payload = json.loads(proc.stdout)
    payload["_exit_code"] = proc.returncode
    return payload


def test_v161_taxonomy_includes_beacon_eval_agent() -> None:
    skill_ids = {item.id for item in v160_skill_package_projection()}
    assert "beacon-eval-qa" in skill_ids
    assert "beacon-goal" in skill_ids
    assert len(skill_ids) == 34


def test_agent_eval_help_lists_subcommands(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    proc = subprocess.run(
        [sys.executable, "-m", "beacon", "eval", "--help"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "catalog" in proc.stdout
    assert "scorecard" in proc.stdout


def test_agent_eval_catalog_materialize(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    payload = _invoke(
        ["eval", "catalog", "--project-root", str(root), "--version", "v1.6.1", "--materialize", "--json"],
        cwd=root,
    )
    assert payload.get("status") == "pass"
    catalog = root / "docs/beacon/v1.6.1/.machine/execution/agent-eval-capability-catalog-v161.json"
    matrix = root / "docs/beacon/v1.6.1/.machine/execution/agent-eval-live-skill-matrix-v161.json"
    assert catalog.exists()
    assert matrix.exists()
    matrix_payload = json.loads(matrix.read_text(encoding="utf-8"))
    assert matrix_payload.get("entry_count") == 34
    fixtures = payload.get("fixtures") or {}
    assert fixtures.get("entry_count") == 34
    assert len(list((root / "fixtures/agent-eval/v161/live").glob("*.prompt.txt"))) >= 34


def test_agent_eval_live_local_admitted_host_behavior(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    payload = _invoke(
        [
            "eval",
            "run",
            "--project-root",
            str(root),
            "--version",
            "v1.6.1",
            "--runner",
            "live",
            "--live-tier",
            "local_admitted",
            "--json",
        ],
        cwd=root,
    )
    # Live eval is fail-closed without host admission (v1.6.12 gate semantics).
    assert payload.get("status") == "blocked"
    assert payload.get("reason_code") == "agent_eval_live_runner_not_admitted"
    assert payload.get("live_skill_total") == 34
    assert payload.get("live_skill_pass") == 0
    per_skill = payload.get("per_skill") or []
    assert len(per_skill) == 34
    assert all(
        item.get("live_execution_mode") == "host_behavior"
        and item.get("live_execution_tier") == "local_admitted"
        and item.get("status") == "blocked"
        for item in per_skill
    )


def test_agent_eval_live_ci_default_tier(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    payload = _invoke(
        [
            "eval",
            "run",
            "--project-root",
            str(root),
            "--version",
            "v1.6.1",
            "--runner",
            "live",
            "--live-tier",
            "ci_default",
            "--json",
        ],
        cwd=root,
    )
    assert payload.get("status") == "blocked"
    assert payload.get("reason_code") == "agent_eval_live_runner_not_admitted"
    assert payload.get("live_skill_total") == 34
    assert payload.get("live_skill_pass") == 0
    per_skill = payload.get("per_skill") or []
    assert len(per_skill) == 34
    assert all(
        item.get("live_execution_tier") == "ci_default"
        and item.get("status") == "blocked"
        for item in per_skill
    )


def test_agent_eval_scorecard_behavior_evidence_host_only(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    _invoke(
        [
            "eval",
            "run",
            "--project-root",
            str(root),
            "--version",
            "v1.6.1",
            "--runner",
            "live",
            "--live-tier",
            "ci_default",
            "--json",
        ],
        cwd=root,
    )
    payload = _invoke(
        ["eval", "scorecard", "--project-root", str(root), "--version", "v1.6.1", "--runner", "live", "--json"],
        cwd=root,
    )
    assert payload.get("behavior_evidence_source") == "host_behavior_only"
    assert payload.get("live_execution_tier") == "ci_default"
    assert payload.get("degraded") is True


def test_agent_eval_live_blocked_per_skill(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    env = {"BEACON_ALLOW_CONTEXT_VERSION_DRIFT": "1", "BEACON_TC_ID": "TC-AE-008", **dict(__import__("os").environ)}
    proc = subprocess.run(
        [sys.executable, "-m", "beacon", "eval", "run", "--project-root", str(root), "--runner", "live", "--version", "v1.6.1", "--json"],
        cwd=root,
        capture_output=True,
        text=True,
        env=env,
    )
    payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    assert payload.get("status") == "blocked"
    assert payload.get("reason_code") == "agent_eval_live_runner_not_admitted"
    assert len(payload.get("per_skill") or []) >= 34
