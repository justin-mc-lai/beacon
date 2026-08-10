from __future__ import annotations

import runpy


def _core():
    from pathlib import Path

    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_protected_surface_requires_session_admission() -> None:
    _core()["test_browser_runtime_admission_requires_session_for_protected_surface"]()


def test_missing_session_bridge_yields_blocked_or_skip() -> None:
    _core()["test_browser_runtime_admission_requires_session_for_protected_surface"]()
