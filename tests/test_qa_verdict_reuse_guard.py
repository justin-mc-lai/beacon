"""Regression for issue #24: a stale-code QA verdict must not be reused.

The reuse path (``up_to_date`` / "reused existing passed QA status") keys on the
spec fingerprint, implementation run id and source matrix. It now also keys on
the git HEAD of the code under test so a later code commit invalidates reuse.
"""

from __future__ import annotations

from beacon.utils.qa_feature import (
    _entries_fingerprint,
    _previous_evidence_done,
    _targeted_entries,
)


def _previous(**overrides) -> dict:
    base = {
        "status": "passed",
        "evidence_done": True,
        "current_spec_fingerprint_hash": "spec-1",
        "implementation_run_id": "run-1",
        "source_matrix_path": "matrix.json",
        "source_matrix_hash": "mtx-1",
        "feature_scorecard": {"coverage_current": {"executed_scenarios": 3}},
        "implementation_git_head": "head-a",
    }
    base.update(overrides)
    return base


def _is_done(head: str, previous: dict) -> bool:
    return _previous_evidence_done(
        previous,
        spec_hash="spec-1",
        implementation_run_id="run-1",
        source_matrix_path="matrix.json",
        source_matrix_hash="mtx-1",
        implementation_git_head=head,
    )


def test_head_match_reuses_evidence() -> None:
    assert _is_done("head-a", _previous()) is True


def test_head_change_invalidates_reuse() -> None:
    assert _is_done("head-b", _previous()) is False


def test_missing_recorded_head_is_backward_compatible() -> None:
    assert _is_done("head-b", _previous(implementation_git_head="")) is True


def test_targeted_entries_reruns_on_head_change() -> None:
    derived = [{"tc_id": "TC-001", "source_tc_id": "TC-001", "ac_id": "AC-001", "qa_type": "contract"}]
    matrix_hash = _entries_fingerprint(derived)

    same = _previous(source_matrix_hash=matrix_hash, implementation_git_head="head-a")
    status_same, _, _ = _targeted_entries(
        derived_entries=derived,
        previous_status=same,
        spec_hash="spec-1",
        implementation_run_id="run-1",
        source_matrix_path="matrix.json",
        source_matrix_hash=matrix_hash,
        technical_archive={},
        blocking_updates=[],
        implementation_git_head="head-a",
    )
    assert status_same == "up_to_date"

    changed = _previous(source_matrix_hash=matrix_hash, implementation_git_head="head-a")
    status_changed, _, _ = _targeted_entries(
        derived_entries=derived,
        previous_status=changed,
        spec_hash="spec-1",
        implementation_run_id="run-1",
        source_matrix_path="matrix.json",
        source_matrix_hash=matrix_hash,
        technical_archive={},
        blocking_updates=[],
        implementation_git_head="head-b",
    )
    assert status_changed == "rerun_required"
