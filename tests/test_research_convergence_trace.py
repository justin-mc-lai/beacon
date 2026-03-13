from __future__ import annotations

from pathlib import Path


def test_prd_and_user_story_should_reference_research_convergence():
    prd = Path("/Users/apple/Developer/Personal/my_skill/beacon/docs/beacon/v1.1.1/prd/beacon-strict-config-governance.md").read_text(encoding="utf-8")
    us = Path("/Users/apple/Developer/Personal/my_skill/beacon/docs/beacon/v1.1.1/user-story/beacon-strict-config-governance.md").read_text(encoding="utf-8")
    assert "research -> user-story / prd -> test-case" in prd
    assert "再进入 `test-case`" in us
