from __future__ import annotations

import runpy


def _core():
    from pathlib import Path

    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_runner_learning_note_contract() -> None:
    _core()["test_browser_runner_learning_reason_code_is_frozen"]()


def test_runner_learning_note_is_written(tmp_path) -> None:
    _core()["test_browser_runner_learning_note_is_written"](tmp_path)
