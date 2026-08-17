"""Tests for beacon-harness-remediation-sandbox-v166 (Phase 3)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.utils.remediation_sandbox import (
    SCHEMA_VERSION,
    OVERLAY_TYPES,
    apply_overlay,
    build_remediation_report,
    create_sandbox,
    eval_overlay,
    rollback_overlay,
    remediation_signal,
)


@pytest.fixture
def sandbox_project(tmp_path: Path) -> Path:
    """Create a project root with canonical truth files for no-write checking."""
    root = tmp_path
    # Create canonical truth files
    truth_dir = root / "docs" / "beacon" / "v1.6.6" / "features" / "test-feature"
    truth_dir.mkdir(parents=True, exist_ok=True)
    (truth_dir / "truth.md").write_text("# Truth\nstatus: frozen\n", encoding="utf-8")
    (truth_dir / "tests.md").write_text("# Tests\n", encoding="utf-8")
    (truth_dir / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    (truth_dir / "evidence.md").write_text("# Evidence\n", encoding="utf-8")
    return root


class TestSandboxCreate:
    """AC-001: create_sandbox creates isolated directory in governed worktree."""

    def test_create_sandbox(self, sandbox_project: Path):
        result = create_sandbox(sandbox_project, run_id="test-rm-001", stagnation_ref="stag-001")
        assert result["status"] == "pass"
        sandbox_path = Path(result["sandbox_path"])
        assert sandbox_path.is_dir()
        assert (sandbox_path / "overlay").is_dir()
        assert (sandbox_path / "eval").is_dir()
        assert (sandbox_path / "sandbox-state.json").is_file()


class TestOverlayApply:
    """AC-002: apply_overlay writes runtime patch, doesn't modify canonical skill."""

    def test_apply_overlay(self, sandbox_project: Path):
        create_result = create_sandbox(sandbox_project, run_id="test-rm-002")
        sandbox_path = create_result["sandbox_path"]
        result = apply_overlay(
            sandbox_project,
            sandbox_path=sandbox_path,
            overlay_type="retry-with-backoff",
            overlay_content="# retry patch",
        )
        assert result["status"] == "pass"
        overlay_file = Path(result["overlay_file"])
        assert overlay_file.is_file()
        assert overlay_file.read_text() == "# retry patch"

    def test_apply_overlay_rejects_invalid_type(self, sandbox_project: Path):
        create_result = create_sandbox(sandbox_project, run_id="test-rm-002b")
        result = apply_overlay(
            sandbox_project,
            sandbox_path=create_result["sandbox_path"],
            overlay_type="invalid-type",
        )
        assert result["status"] == "blocked"
        assert result["reason_code"] == "invalid_overlay_type"


class TestEvalPass:
    """AC-003: valid overlay → status=remediated, all checks pass."""

    def test_eval_pass(self, sandbox_project: Path):
        stagnation_report = {
            "findings": [{"recommendation": "retry-with-backoff"}],
        }
        create_result = create_sandbox(sandbox_project, run_id="test-rm-003")
        sandbox_path = create_result["sandbox_path"]
        apply_overlay(
            sandbox_project,
            sandbox_path=sandbox_path,
            overlay_type="retry-with-backoff",
            overlay_content="# valid patch",
        )
        eval_result = eval_overlay(
            sandbox_project,
            sandbox_path=sandbox_path,
            stagnation_report=stagnation_report,
        )
        assert eval_result["status"] == "remediated"
        assert eval_result["eval"]["smoke_test_pass"] is True
        assert eval_result["eval"]["no_truth_write"] is True
        assert eval_result["eval"]["stagnation_resolved"] is True
        assert eval_result["human_review_required"] is True


class TestEvalFailRollback:
    """AC-004: invalid overlay → status=rollback, sandbox restored."""

    def test_eval_fail_rollback(self, sandbox_project: Path):
        # Use an overlay type that doesn't match stagnation recommendation
        stagnation_report = {
            "findings": [{"recommendation": "break-on-plateau"}],
        }
        create_result = create_sandbox(sandbox_project, run_id="test-rm-004")
        sandbox_path = create_result["sandbox_path"]
        apply_overlay(
            sandbox_project,
            sandbox_path=sandbox_path,
            overlay_type="retry-with-backoff",  # mismatched
            overlay_content="# patch",
        )
        eval_result = eval_overlay(
            sandbox_project,
            sandbox_path=sandbox_path,
            stagnation_report=stagnation_report,
        )
        assert eval_result["status"] == "rollback"
        assert eval_result["eval"]["stagnation_resolved"] is False
        assert "rollback_result" in eval_result


class TestNoTruthWrite:
    """AC-005: canonical truth files not modified after overlay."""

    def test_canonical_truth_unchanged(self, sandbox_project: Path):
        truth_path = sandbox_project / "docs" / "beacon" / "v1.6.6" / "features" / "test-feature" / "truth.md"
        original_content = truth_path.read_text(encoding="utf-8")
        create_result = create_sandbox(sandbox_project, run_id="test-rm-005")
        apply_overlay(
            sandbox_project,
            sandbox_path=create_result["sandbox_path"],
            overlay_type="skip-and-continue",
            overlay_content="# skip patch",
        )
        eval_overlay(
            sandbox_project,
            sandbox_path=create_result["sandbox_path"],
            stagnation_report={"findings": [{"recommendation": "skip-and-continue"}]},
        )
        assert truth_path.read_text(encoding="utf-8") == original_content


class TestStagnationConsumed:
    """AC-006: sandbox consumes Phase 2 stagnation report as trigger."""

    def test_stagnation_ref_stored(self, sandbox_project: Path):
        result = create_sandbox(sandbox_project, run_id="test-rm-006", stagnation_ref="stag-run-006")
        assert result["stagnation_ref"] == "stag-run-006"
        state = json.loads(
            (Path(result["sandbox_path"]) / "sandbox-state.json").read_text(encoding="utf-8")
        )
        assert state["stagnation_ref"] == "stag-run-006"


class TestReportSchema:
    """AC-007: remediation report conforms to remediation-report.v1 schema."""

    def test_report_schema(self, sandbox_project: Path):
        create_result = create_sandbox(sandbox_project, run_id="test-rm-007", stagnation_ref="stag-007")
        sandbox_path = create_result["sandbox_path"]
        apply_overlay(
            sandbox_project,
            sandbox_path=sandbox_path,
            overlay_type="break-on-plateau",
            overlay_content="# break patch",
        )
        eval_result = eval_overlay(
            sandbox_project,
            sandbox_path=sandbox_path,
            stagnation_report={"findings": [{"recommendation": "break-on-plateau"}]},
        )
        report = build_remediation_report(
            sandbox_project,
            run_id="test-rm-007",
            sandbox_path=sandbox_path,
            stagnation_ref="stag-007",
            eval_result=eval_result,
        )
        assert report["schema_version"] == "remediation-report.v1"
        assert report["run_id"] == "test-rm-007"
        assert report["stagnation_ref"] == "stag-007"
        assert report["overlay_type"] == "break-on-plateau"
        assert "eval" in report
        assert "smoke_test_pass" in report["eval"]
        assert "human_review_required" in report


class TestHumanReview:
    """AC-008: eval pass → human_review_required=true, not auto-release."""

    def test_human_review_required(self, sandbox_project: Path):
        create_result = create_sandbox(sandbox_project, run_id="test-rm-008")
        sandbox_path = create_result["sandbox_path"]
        apply_overlay(
            sandbox_project,
            sandbox_path=sandbox_path,
            overlay_type="retry-with-backoff",
            overlay_content="# patch",
        )
        eval_result = eval_overlay(
            sandbox_project,
            sandbox_path=sandbox_path,
            stagnation_report={"findings": [{"recommendation": "retry-with-backoff"}]},
        )
        assert eval_result["human_review_required"] is True
        assert eval_result["status"] == "remediated"
