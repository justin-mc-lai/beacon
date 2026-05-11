from __future__ import annotations

import runpy


def _core():
    from pathlib import Path

    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_placeholder_transcript_is_not_browser_closure() -> None:
    _core()["test_browser_evidence_authenticity_marks_placeholder_runner_statuses"]()


def test_placeholder_browser_evidence_forces_needs_more_evidence() -> None:
    _core()["test_placeholder_browser_evidence_forces_needs_more_evidence"]()
