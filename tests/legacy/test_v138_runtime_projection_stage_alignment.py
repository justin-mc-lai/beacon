from __future__ import annotations

from beacon.utils import runtime_projection as runtime_projection_module


def test_v138_runtime_projection_should_preserve_canonical_release_stage() -> None:
    assert runtime_projection_module._derive_stage({"current_stage": "release"}) == "release"
    assert runtime_projection_module._derive_stage({"current_stage": "qa"}) == "qa"
    assert runtime_projection_module._derive_stage({"current_stage": "implement"}) == "implement"
