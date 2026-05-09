from __future__ import annotations

import runpy


def _core():
    from pathlib import Path

    return runpy.run_path(str(Path(__file__).with_name("test_v142_test_contract_governance.py")))


def test_skill_guides_contract_lane_verification() -> None:
    _core()["test_skill_guidance_mentions_contract_lanes_and_unclassified_full_suite"]()
