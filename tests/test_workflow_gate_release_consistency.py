"""Workflow terminal consistency contracts for strict release gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _extract_json(text: str) -> dict:
    start = text.find("{")
    assert start >= 0
    return json.loads(text[start:])


def test_workflow_auto_should_align_with_release_gate_strict(tmp_path: Path):
    start = _invoke(
        [
            "workflow",
            "start",
            "Release Consistency Feature",
            "--auto",
            "--project",
            str(tmp_path),
            "--implementation-command",
            "python3 -c \"print('impl')\"",
            "--verify-scope",
            "unit",
            "--verify-unit-command",
            "python3 -c \"print('ok')\"",
        ]
    )
    assert start.exit_code == 0

    gate = _invoke(
        [
            "gate",
            "check",
            "release",
            "--mode",
            "strict",
            "--json",
            "--project-root",
            str(tmp_path),
        ]
    )
    payload = _extract_json(gate.stdout)
    assert payload["status"] == "Pass"
    assert payload["blocked_count"] == 0

    lifecycle = json.loads((tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json").read_text(encoding="utf-8"))
    events = [i for i in lifecycle.get("items", []) if isinstance(i, dict)]
    assert any(
        i.get("stage") == "release" and i.get("event") == "release_decision_recorded"
        for i in events
    )

    manifest = json.loads((tmp_path / ".beacon" / "evidence-manifest.json").read_text(encoding="utf-8"))
    entries = [x for x in manifest.get("entries", []) if isinstance(x, dict)]
    raw_entry = next(x for x in entries if x.get("path") == ".beacon/raw-command-log.jsonl")
    raw_path = tmp_path / ".beacon" / "raw-command-log.jsonl"
    actual_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    assert raw_entry.get("sha256") == actual_hash
