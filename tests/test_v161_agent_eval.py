from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


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
    assert matrix_payload.get("entry_count") == 37


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
    assert len(payload.get("per_skill") or []) >= 37
