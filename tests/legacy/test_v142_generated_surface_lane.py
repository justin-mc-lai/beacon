from __future__ import annotations

import runpy
from pathlib import Path


def _core():
    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_generated_surface_sync_blocks_drift(tmp_path: Path) -> None:
    _core()["test_generated_surface_sync_lane_blocks_failed_evidence"](tmp_path)
