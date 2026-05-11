from __future__ import annotations

import runpy
from pathlib import Path


def _core():
    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_legacy_snapshot_not_release_blocker_by_default(tmp_path: Path) -> None:
    _core()["test_legacy_snapshot_not_release_blocker_by_default"](tmp_path)
