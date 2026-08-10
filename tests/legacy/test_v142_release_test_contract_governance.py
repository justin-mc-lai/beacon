from __future__ import annotations

import runpy
from pathlib import Path


def _core():
    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_release_consumes_lane_status(tmp_path: Path) -> None:
    _core()["test_release_consumes_lane_status_and_reason_codes"](tmp_path)
