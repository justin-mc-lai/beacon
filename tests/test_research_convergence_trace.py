from __future__ import annotations

from pathlib import Path


def test_prd_and_user_story_should_reference_research_convergence(tmp_path: Path):
    prd_path = tmp_path / "docs" / "beacon" / "v1.1.1" / "prd" / "beacon-strict-config-governance.md"
    us_path = tmp_path / "docs" / "beacon" / "v1.1.1" / "user-story" / "beacon-strict-config-governance.md"
    prd_path.parent.mkdir(parents=True, exist_ok=True)
    us_path.parent.mkdir(parents=True, exist_ok=True)
    prd_path.write_text("research -> user-story / prd -> test-case\n", encoding="utf-8")
    us_path.write_text("完成 research 后再进入 `test-case`。\n", encoding="utf-8")

    prd = prd_path.read_text(encoding="utf-8")
    us = us_path.read_text(encoding="utf-8")
    assert "research -> user-story / prd -> test-case" in prd
    assert "再进入 `test-case`" in us
