from __future__ import annotations

import runpy
from pathlib import Path


def _core():
    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_qa_first_principles_order(tmp_path: Path) -> None:
    _core()["test_qa_order_and_deep_delta_policy_are_indexed"](tmp_path)
