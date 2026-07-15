"""Tests for beacon-loop-stagnation-detector-v166 (Phase 2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.utils.agent_trace import append_event, build_event, preflight_governed_trace
from beacon.utils.stagnation_detector import (
    DEFAULT_PARAMS,
    SCHEMA_VERSION,
    _detect_plateau,
    _detect_repeat_failure,
    _detect_repeat_labor,
    _jaccard_similarity,
    detect_stagnation,
    stagnation_detection_signal,
)


@pytest.fixture
def trace_project(tmp_path: Path) -> Path:
    """Create a project root with traces directory."""
    (tmp_path / ".beacon" / "traces").mkdir(parents=True, exist_ok=True)
    return tmp_path


def _write_trace(project_root: Path, run_id: str, events: list[dict]) -> None:
    """Write events to a trace file."""
    preflight_governed_trace(project_root, run_id=run_id)
    for event in events:
        append_event(project_root, event)


class TestRepeatFailureDetection:
    """AC-001: repeat_failure detection."""

    def test_repeat_failure_detected(self, trace_project: Path):
        run_id = "test-rf-001"
        events = [
            build_event(run_id=run_id, event_type="failure", summary="fail 1", iteration=0, reason_code="truth-drift"),
            build_event(run_id=run_id, event_type="failure", summary="fail 2", iteration=1, reason_code="truth-drift"),
            build_event(run_id=run_id, event_type="failure", summary="fail 3", iteration=2, reason_code="truth-drift"),
        ]
        _write_trace(trace_project, run_id, events)
        report = detect_stagnation(trace_project, run_id=run_id)
        assert report["schema_version"] == SCHEMA_VERSION
        assert report["status"] == "stagnant"
        rf_findings = [f for f in report["findings"] if f["stagnation_type"] == "repeat_failure"]
        assert len(rf_findings) >= 1
        assert rf_findings[0]["reason_code"] == "truth-drift"
        assert rf_findings[0]["matched_count"] >= 3


class TestRepeatLaborDetection:
    """AC-002: repeat_labor detection."""

    def test_repeat_labor_detected(self, trace_project: Path):
        run_id = "test-rl-002"
        events = [
            build_event(run_id=run_id, event_type="decision", summary="analyzing feature scope", iteration=0, feature_slug="feat-x"),
            build_event(run_id=run_id, event_type="decision", summary="analyzing feature scope", iteration=1, feature_slug="feat-x"),
            build_event(run_id=run_id, event_type="decision", summary="analyzing feature scope", iteration=2, feature_slug="feat-x"),
        ]
        _write_trace(trace_project, run_id, events)
        report = detect_stagnation(trace_project, run_id=run_id)
        rl_findings = [f for f in report["findings"] if f["stagnation_type"] == "repeat_labor"]
        assert len(rl_findings) >= 1
        assert rl_findings[0]["matched_count"] >= 3


class TestPlateauDetection:
    """AC-003: plateau detection."""

    def test_plateau_detected(self, trace_project: Path):
        run_id = "test-pl-003"
        summary = "processing iteration step forward progress"
        events = [
            build_event(run_id=run_id, event_type="output", summary=summary, iteration=0),
            build_event(run_id=run_id, event_type="output", summary=summary, iteration=1),
            build_event(run_id=run_id, event_type="output", summary=summary, iteration=2),
        ]
        _write_trace(trace_project, run_id, events)
        report = detect_stagnation(trace_project, run_id=run_id)
        pl_findings = [f for f in report["findings"] if f["stagnation_type"] == "plateau"]
        assert len(pl_findings) >= 1
        assert pl_findings[0]["matched_count"] >= 3


class TestCleanTrace:
    """AC-004: clean trace returns no findings."""

    def test_clean_trace(self, trace_project: Path):
        run_id = "test-clean-004"
        events = [
            build_event(run_id=run_id, event_type="decision", summary="unique decision A", iteration=0),
            build_event(run_id=run_id, event_type="output", summary="unique output B", iteration=1, reason_code=""),
            build_event(run_id=run_id, event_type="decision", summary="unique decision C", iteration=2),
        ]
        _write_trace(trace_project, run_id, events)
        report = detect_stagnation(trace_project, run_id=run_id)
        assert report["status"] == "clean"
        assert report["findings"] == []


class TestUpstreamCorrelation:
    """AC-005: findings contain pattern_ref and failure_ref fields."""

    def test_findings_have_correlation_fields(self, trace_project: Path):
        run_id = "test-up-005"
        events = [
            build_event(run_id=run_id, event_type="failure", summary="fail 1", iteration=0, reason_code="truth-drift"),
            build_event(run_id=run_id, event_type="failure", summary="fail 2", iteration=1, reason_code="truth-drift"),
            build_event(run_id=run_id, event_type="failure", summary="fail 3", iteration=2, reason_code="truth-drift"),
        ]
        _write_trace(trace_project, run_id, events)
        report = detect_stagnation(trace_project, run_id=run_id)
        for finding in report["findings"]:
            assert "pattern_ref" in finding
            assert "failure_ref" in finding


class TestDeterminism:
    """AC-006: same input → same output."""

    def test_deterministic_output(self, trace_project: Path):
        run_id = "test-det-006"
        events = [
            build_event(run_id=run_id, event_type="failure", summary="fail 1", iteration=0, reason_code="truth-drift"),
            build_event(run_id=run_id, event_type="failure", summary="fail 2", iteration=1, reason_code="truth-drift"),
            build_event(run_id=run_id, event_type="failure", summary="fail 3", iteration=2, reason_code="truth-drift"),
        ]
        _write_trace(trace_project, run_id, events)
        report1 = detect_stagnation(trace_project, run_id=run_id)
        report2 = detect_stagnation(trace_project, run_id=run_id)
        # Findings should be identical (excluding detected_at timestamp)
        findings1 = [{k: v for k, v in f.items()} for f in report1["findings"]]
        findings2 = [{k: v for k, v in f.items()} for f in report2["findings"]]
        assert findings1 == findings2
        assert report1["status"] == report2["status"]


class TestDoctorSignal:
    """AC-007: doctor loop-audit includes stagnation_detection signal."""

    def test_stagnation_signal_in_loop_audit(self, trace_project: Path):
        from beacon.utils.loop_readiness import build_loop_readiness_audit
        # Create minimal project structure for audit
        (trace_project / "docs" / "beacon" / "v1.6.6" / "features").mkdir(parents=True, exist_ok=True)
        (trace_project / "docs" / "beacon" / "governance").mkdir(parents=True, exist_ok=True)
        (trace_project / "docs" / "beacon" / "governance" / "project-version-governance.md").write_text("# Governance")
        (trace_project / "docs" / "beacon" / "global-boundaries.md").write_text("# Boundaries")
        audit = build_loop_readiness_audit(trace_project, version="v1.6.6")
        signal_ids = [s["id"] for s in audit["signals"]]
        assert "stagnation_detection" in signal_ids


class TestReportSchema:
    """AC-008: report conforms to stagnation-report.v1 schema."""

    def test_schema_version(self, trace_project: Path):
        run_id = "test-schema-008"
        report = detect_stagnation(trace_project, run_id=run_id)
        assert report["schema_version"] == "stagnation-report.v1"
        assert "run_id" in report
        assert "detected_at" in report
        assert "status" in report
        assert "findings" in report
        assert "upstream_signals" in report
        assert "event_count" in report

    def test_empty_trace_returns_clean(self, trace_project: Path):
        run_id = "test-empty-008b"
        report = detect_stagnation(trace_project, run_id=run_id)
        assert report["status"] == "clean"
        assert report["findings"] == []
        assert report["event_count"] == 0
