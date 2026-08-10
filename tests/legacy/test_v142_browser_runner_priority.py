from __future__ import annotations

import runpy


def _core():
    from pathlib import Path

    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_protected_surface_runner_priority() -> None:
    _core()["test_browser_runtime_admission_prefers_attached_session_runner"]()
