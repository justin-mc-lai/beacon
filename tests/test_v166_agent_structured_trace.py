from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.utils.agent_trace import (
    REASON_INVALID_EVENT_TYPE,
    REASON_INVALID_LOOP_LAYER,
    REASON_MISSING,
    SCHEMA_VERSION,
    agent_trace_coverage_signal,
    append_event,
    build_event,
    normalize_trace_lines,
    preflight_governed_trace,
    read_trace_events,
    record_governed_iteration,
    trace_path,
    validate_event,
)
from beacon.utils.loop_audit import run_loop_audit


def _valid_event(**overrides) -> dict:
    base = build_event(
        run_id="run-test",
        event_type="decision",
        summary="test decision",
        iteration=1,
        payload={"step": "plan"},
        loop_layer="coding",
    )
    base.update(overrides)
    return base


def test_schema_accepts_valid_event() -> None:
    result = validate_event(_valid_event())
    assert result["status"] == "pass"


def test_schema_rejects_invalid_event_type() -> None:
    result = validate_event(_valid_event(event_type="not-a-real-type"))
    assert result["status"] == "fail"
    assert result["reason_code"] == REASON_INVALID_EVENT_TYPE


def test_loop_layer_optional_field() -> None:
    for layer in ("coding", "developer", "realworld"):
        assert validate_event(_valid_event(loop_layer=layer))["status"] == "pass"
    bad = validate_event(_valid_event(loop_layer="plateau"))
    assert bad["status"] == "fail"
    assert bad["reason_code"] == REASON_INVALID_LOOP_LAYER


def test_append_events_on_governed_run(tmp_path: Path) -> None:
    run_id = "run-append-001"
    result = record_governed_iteration(
        tmp_path,
        run_id=run_id,
        event_type="decision",
        summary="iteration start",
        iteration=1,
    )
    assert result["status"] == "pass"
    events = read_trace_events(tmp_path, run_id)
    assert len(events) >= 1
    assert events[0]["event_type"] in {"decision", "failure", "retry", "output"}
    assert trace_path(tmp_path, run_id).is_file()


def test_fail_closed_when_trace_missing(tmp_path: Path) -> None:
    blocked_file = tmp_path / ".beacon" / "traces"
    blocked_file.parent.mkdir(parents=True, exist_ok=True)
    blocked_file.write_text("not-a-directory", encoding="utf-8")
    result = append_event(tmp_path, _valid_event(run_id="run-blocked"))
    assert result["status"] == "blocked"
    assert result["reason_code"] in {REASON_MISSING, "agent_trace_append_failed"}


def test_lifecycle_index_records_trace_pointer(tmp_path: Path) -> None:
    run_id = "run-index-001"
    record_governed_iteration(tmp_path, run_id=run_id, summary="indexed", event_type="output")
    from beacon.utils.agent_trace import get_run_trace_index

    entry = get_run_trace_index(tmp_path, run_id)
    assert entry is not None
    assert entry["trace_path"] == f".beacon/traces/{run_id}.jsonl"
    assert entry["trace_event_count"] >= 1


def test_loop_audit_agent_trace_coverage_signal(tmp_path: Path) -> None:
    missing = run_loop_audit(tmp_path, version="v1.6.6")
    assert missing["agent_trace_coverage"]["status"] == "missing"
    record_governed_iteration(tmp_path, run_id="run-audit", summary="audit pass", event_type="output")
    passed = run_loop_audit(tmp_path, version="v1.6.6")
    assert passed["agent_trace_coverage"]["status"] == "pass"
    assert passed["agent_trace_coverage"]["signal"] == "agent_trace_coverage"


def test_golden_trace_normalization() -> None:
    fixture = Path("tests/fixtures/agent_trace/golden-run.jsonl")
    reference = Path("tests/fixtures/agent_trace/golden-normalized.json")
    lines = fixture.read_text(encoding="utf-8").splitlines()
    normalized = normalize_trace_lines(lines)
    expected = json.loads(reference.read_text(encoding="utf-8"))
    assert normalized == expected


def test_preflight_governed_trace_creates_traces_dir(tmp_path: Path) -> None:
    result = preflight_governed_trace(tmp_path, run_id="run-preflight")
    assert result["status"] == "pass"
    assert (tmp_path / ".beacon" / "traces").is_dir()
