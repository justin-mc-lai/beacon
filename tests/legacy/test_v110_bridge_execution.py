"""v1.1.0 workflow bridge execution contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.memory import load_memory_entries

runner = CliRunner()
VERIFY_PASS_ARGS = [
    "--implementation-command",
    "python3 -c \"print('impl')\"",
    "--verify-scope",
    "unit",
    "--verify-unit-command",
    "python3 -c \"print('ok')\"",
]


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _extract_run_id(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("Run ID:"):
            return line.split(":", 1)[1].strip()
    return ""


def test_bridge_should_be_hint_only_by_default(tmp_path: Path):
    result = _invoke([
        "workflow",
        "start",
        "Bridge Feature",
        "--project",
        str(tmp_path),
            "--version",
            "v1.1.0",
            "--auto",
            "--confirm-execute",
            "--confirm-execute-second",
            *VERIFY_PASS_ARGS,
        ])
    assert result.exit_code == 0

    run_id = _extract_run_id(result.stdout)
    assert run_id

    bridge_path = tmp_path / ".beacon" / "bridge" / run_id / "bridge-execution.json"
    assert not bridge_path.exists()


def test_bridge_should_execute_when_flag_enabled(tmp_path: Path):
    result = _invoke([
        "workflow",
        "start",
        "Bridge Feature",
        "--project",
        str(tmp_path),
            "--version",
            "v1.1.0",
            "--auto",
            "--confirm-execute",
            "--confirm-execute-second",
            "--bridge-execute",
            "--bridge-targets",
            "team",
        "--bridge-timeout",
        "60",
        *VERIFY_PASS_ARGS,
    ])
    assert result.exit_code == 0

    run_id = _extract_run_id(result.stdout)
    assert run_id

    bridge_path = tmp_path / ".beacon" / "bridge" / run_id / "bridge-execution.json"
    assert bridge_path.exists()

    payload = json.loads(bridge_path.read_text(encoding="utf-8"))
    assert payload.get("run_id") == run_id
    assert payload.get("summary", {}).get("executed") == 1
    results = payload.get("results", [])
    assert isinstance(results, list) and results
    assert results[0].get("target") == "team"

    lifecycle_path = tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json"
    assert lifecycle_path.exists()
    payload = json.loads(lifecycle_path.read_text(encoding="utf-8"))
    items = payload.get("items", []) if isinstance(payload, dict) else []
    assert any(str(item.get("event", "")) == "bridge_execution_recorded" for item in items if isinstance(item, dict))


def test_bridge_result_should_be_written_to_memory_and_lifecycle(tmp_path: Path):
    result = _invoke([
        "workflow",
        "start",
        "Bridge Feature",
        "--project",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "--auto",
        "--confirm-execute",
        "--confirm-execute-second",
        "--bridge-execute",
        "--bridge-targets",
        "team",
        "--bridge-timeout",
        "60",
        *VERIFY_PASS_ARGS,
    ])
    assert result.exit_code == 0
    run_id = _extract_run_id(result.stdout)
    assert run_id

    entries = load_memory_entries(tmp_path)
    assert any(
        str(item.get("source", "")) == "workflow.bridge.execute"
        and str(item.get("source_session_id", "")) == run_id
        for item in entries
        if isinstance(item, dict)
    )

    lifecycle_path = tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json"
    payload = json.loads(lifecycle_path.read_text(encoding="utf-8"))
    items = payload.get("items", []) if isinstance(payload, dict) else []
    assert any(
        str(item.get("event", "")) == "bridge_execution_recorded"
        and str(item.get("run_id", "")) == run_id
        for item in items
        if isinstance(item, dict)
    )
