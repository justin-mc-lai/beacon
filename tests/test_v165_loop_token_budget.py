from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from beacon.utils.loop_budget import (
    append_budget_record,
    build_loop_budget_status,
    budget_ledger_path,
    daily_totals,
    registry_budget_caps,
    unattended_loop_preflight,
)


def _write_registry(root: Path) -> None:
    path = root / "docs/beacon/v1.6.5/loop-patterns/registry.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """
patterns:
  -
    id: ralph
    cadence: iterative
    risk: medium
    harness_skills: [generator]
    state_surface: .beacon/ralph
    phases: [run]
    human_gates: [qa]
    token_cost: 10
    daily_cap: 100
    safety: {}
""",
        encoding="utf-8",
    )


def test_registry_token_cost_fields_are_consumed(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    assert registry_budget_caps(tmp_path, version="v1.6.5") == {"ralph": 100}


def test_budget_ledger_appends_run_record(tmp_path: Path) -> None:
    record = append_budget_record(tmp_path, pattern_id="ralph", run_id="run-1", estimated_tokens=10, actual_tokens=8, date="2026-07-09", source="test")
    assert record["pattern_id"] == "ralph"
    payload = json.loads(budget_ledger_path(tmp_path).read_text(encoding="utf-8"))
    assert payload["records"][0]["actual_tokens"] == 8


def test_daily_totals_per_pattern_and_project() -> None:
    totals = daily_totals(
        [
            {"pattern_id": "ralph", "estimated_tokens": 10, "date": "2026-07-09"},
            {"pattern_id": "team", "actual_tokens": 5, "date": "2026-07-09"},
            {"pattern_id": "ralph", "estimated_tokens": 99, "date": "2026-07-08"},
        ],
        date="2026-07-09",
    )
    assert totals["per_pattern"] == {"ralph": 10, "team": 5}
    assert totals["project_total"] == 15


def test_status_loop_budget_json(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    append_budget_record(tmp_path, pattern_id="ralph", run_id="run-1", estimated_tokens=25, date="2026-07-09")
    proc = subprocess.run(
        [sys.executable, "-m", "beacon", "status", "loop-budget", "--project-root", str(tmp_path), "--version", "v1.6.5", "--date", "2026-07-09", "--json"],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["totals"]["project_total"] == 25
    assert payload["caps"]["ralph"] == 100
    assert payload["remaining"]["ralph"] == 75


def test_unattended_preflight_blocks_when_cap_exceeded(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    append_budget_record(tmp_path, pattern_id="ralph", run_id="run-1", estimated_tokens=95, date="2026-07-09")
    payload = unattended_loop_preflight(tmp_path, version="v1.6.5", pattern_id="ralph", estimated_tokens=10, date="2026-07-09")
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "loop_budget_exceeded"


def test_kill_switch_blocks_automated_loops(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    pause = tmp_path / ".beacon/loop/pause-all"
    pause.parent.mkdir(parents=True, exist_ok=True)
    pause.write_text("pause\n", encoding="utf-8")
    payload = unattended_loop_preflight(tmp_path, version="v1.6.5", pattern_id="ralph", estimated_tokens=1)
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "loop_kill_switch_active"
