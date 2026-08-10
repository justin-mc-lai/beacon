from __future__ import annotations

import runpy
from pathlib import Path


def _core():
    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_blocked_governance_has_repair_route(tmp_path: Path) -> None:
    _core()["test_verify_missing_index_has_repair_route"](tmp_path)
