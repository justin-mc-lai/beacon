from __future__ import annotations

import runpy
from pathlib import Path


def _core():
    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_browser_admission_and_evidence_participate_in_lane_reasoning(tmp_path: Path) -> None:
    _core()["test_browser_runtime_admission_lane_is_classified_and_release_blocking"](tmp_path)
