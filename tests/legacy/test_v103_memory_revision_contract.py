"""v1.0.3 Memory v1 revision/search contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _extract_memory_id(output: str) -> str:
    for line in output.splitlines():
        if "memory_id:" in line:
            return line.split(":", 1)[1].strip()
    return ""


def _load_memory_v1(project_root: Path) -> dict:
    path = project_root / ".beacon" / "memory" / "memory-v1.json"
    assert path.exists()
    return json.loads(path.read_text(encoding="utf-8"))


def test_memory_revision_should_mark_previous_as_superseded(tmp_path: Path):
    first = _invoke(
        [
            "remember",
            "add",
            "Initial rollout decision",
            "--type",
            "decision",
            "--source-session-id",
            "run-a",
            "--source",
            "workflow.verify",
            "--reason-code",
            "verify_failed",
            "--project",
            str(tmp_path),
        ]
    )
    assert first.exit_code == 0
    first_id = _extract_memory_id(first.stdout)
    assert first_id

    second = _invoke(
        [
            "remember",
            "add",
            "Revised rollout decision after fix",
            "--type",
            "decision",
            "--revision-of",
            first_id,
            "--reason-code",
            "verify_recovered",
            "--project",
            str(tmp_path),
        ]
    )
    assert second.exit_code == 0
    second_id = _extract_memory_id(second.stdout)
    assert second_id

    payload = _load_memory_v1(tmp_path)
    items = payload.get("items", [])
    old_row = next(item for item in items if item.get("memory_id") == first_id)
    new_row = next(item for item in items if item.get("memory_id") == second_id)

    assert old_row.get("status") == "superseded"
    assert old_row.get("superseded_by") == second_id
    assert new_row.get("revision_of") == first_id
    assert str(old_row.get("content_hash", "")).startswith("sha256:")
    assert str(new_row.get("content_hash", "")).startswith("sha256:")
    assert "verify_recovered" in (new_row.get("reason_codes") or [])


def test_memory_upsert_should_dedupe_by_content_hash(tmp_path: Path):
    args = [
        "remember",
        "add",
        "Scope rule: no hidden requirement changes",
        "--type",
        "insight",
        "--source-session-id",
        "run-b",
        "--source",
        "feedback.sync",
        "--upsert",
        "--project",
        str(tmp_path),
    ]
    first = _invoke([*args, "--reason-code", "scope_deviation"])
    second = _invoke([*args, "--reason-code", "scope_deviation_confirmed"])
    assert first.exit_code == 0
    assert second.exit_code == 0

    payload = _load_memory_v1(tmp_path)
    rows = [
        item
        for item in payload.get("items", [])
        if item.get("type") == "insight"
        and item.get("source_session_id") == "run-b"
        and item.get("source") == "feedback.sync"
    ]
    assert len(rows) == 1
    assert set(rows[0].get("reason_codes") or []) >= {"scope_deviation", "scope_deviation_confirmed"}


def test_remember_search_should_support_mode_and_layer(tmp_path: Path):
    seeded = _invoke(
        [
            "remember",
            "add",
            "OAuth token refresh should happen every 24h",
            "--type",
            "insight",
            "--tag",
            "auth",
            "--project",
            str(tmp_path),
        ]
    )
    assert seeded.exit_code == 0

    result = _invoke(
        [
            "remember",
            "search",
            "token refresh",
            "--mode",
            "hybrid",
            "--layer",
            "index",
            "--json",
            "--project",
            str(tmp_path),
        ]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload
    first = payload[0]
    assert "memory_id" in first
    assert "summary" in first
    assert "reason_codes" in first
    assert "content" not in first


def test_recall_memory_should_support_layer_and_ids(tmp_path: Path):
    first = _invoke(["remember", "add", "Alpha memory", "--project", str(tmp_path)])
    second = _invoke(["remember", "add", "Beta memory", "--project", str(tmp_path)])
    assert first.exit_code == 0
    assert second.exit_code == 0

    first_id = _extract_memory_id(first.stdout)
    second_id = _extract_memory_id(second.stdout)
    assert first_id and second_id and first_id != second_id

    detail = _invoke(
        [
            "recall",
            "memory",
            "--layer",
            "detail",
            "--ids",
            first_id,
            "--json",
            "--project",
            str(tmp_path),
        ]
    )
    assert detail.exit_code == 0
    detail_payload = json.loads(detail.stdout)
    assert len(detail_payload) == 1
    assert detail_payload[0]["memory_id"] == first_id

    timeline = _invoke(
        [
            "recall",
            "memory",
            "--layer",
            "timeline",
            "--ids",
            ",".join([first_id, second_id]),
            "--json",
            "--project",
            str(tmp_path),
        ]
    )
    assert timeline.exit_code == 0
    timeline_payload = json.loads(timeline.stdout)
    assert {item.get("memory_id") for item in timeline_payload} == {first_id, second_id}
    assert all("source_session_id" in item for item in timeline_payload)
