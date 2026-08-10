from __future__ import annotations

import runpy
from pathlib import Path


def _core():
    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_canonical_lanes(tmp_path: Path) -> None:
    _core()["test_index_shape_and_canonical_lanes_from_frozen_truth"](tmp_path)
