"""Tests for PTK-aligned memory envelope behavior."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_remember_add_should_write_envelope_fields(tmp_path: Path):
    result = _invoke(
        [
            "remember",
            "add",
            "Scope guard confirms A/B/C before high-risk changes",
            "--type",
            "decision",
            "--source-session-id",
            "session-001",
            "--source",
            "workflow",
            "--evidence-ref",
            "docs/product/v1.0.0/execution/terminal.json",
            "--tag",
            "ptk",
            "--tag",
            "memory",
            "--project",
            str(tmp_path),
        ]
    )
    assert result.exit_code == 0

    path = tmp_path / ".beacon" / "memory" / "decisions.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("schema_version") == "3.0"
    assert isinstance(data.get("decisions"), list) and len(data["decisions"]) == 1

    row = data["decisions"][0]
    for key in (
        "memory_id",
        "type",
        "source_session_id",
        "source",
        "evidence_ref",
        "confidence",
        "tags",
        "created_at",
        "updated_at",
        "decision",
        "content",
    ):
        assert key in row
    assert row["type"] == "decision"
    assert row["source_session_id"] == "session-001"
    assert row["source"] == "workflow"
    assert row["decision"] == row["content"]


def test_recall_memory_should_filter_by_type(tmp_path: Path):
    _invoke(
        [
            "remember",
            "add",
            "Gate must check evidence chain",
            "--type",
            "insight",
            "--project",
            str(tmp_path),
        ]
    )
    _invoke(
        [
            "remember",
            "add",
            "Use A confirmation for high-risk scope deviation",
            "--type",
            "decision",
            "--project",
            str(tmp_path),
        ]
    )

    result = _invoke(
        [
            "recall",
            "memory",
            "--type",
            "decision",
            "--json",
            "--project",
            str(tmp_path),
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert len(payload) == 1
    assert payload[0]["type"] == "decision"

