from __future__ import annotations

import runpy
from pathlib import Path


def _core():
    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_v142_does_not_promote_runtime(tmp_path: Path) -> None:
    _core()["test_planning_line_safety_keeps_v142_out_of_runtime"](tmp_path)
