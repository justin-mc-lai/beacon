"""Loom slug alias display map + accurate skill scoring."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.loom_skill_score import score_all_loom_skills, score_loom_skill
from beacon.utils.loom_slug_alias import list_feature_aliases, resolve_feature_slug

ROOT = Path(__file__).resolve().parents[1]


def test_resolve_alias_to_canonical() -> None:
    r = resolve_feature_slug("loom-product-goal-orchestrator")
    assert r["ok"] is True
    assert r["canonical_slug"] == "beacon-v2-product-goal-orchestrator"
    assert "Loom" in r["display_name"]


def test_canonical_passthrough_display() -> None:
    r = resolve_feature_slug("beacon-v2-rust-kernel-redesign")
    assert r["canonical_slug"] == "beacon-v2-rust-kernel-redesign"
    assert r["display_name"] == "Loom Rust Kernel Redesign"


def test_list_aliases() -> None:
    m = list_feature_aliases()
    assert m["count"] >= 10
    assert m["policy"] == "identity_stays_canonical_display_is_loom"


def test_score_loom_gen_implement() -> None:
    r = score_loom_skill(ROOT, "loom-gen-implement")
    assert r["content_source_exists"] is True
    assert r["scores"]["composite"] >= 70


def test_score_loom_goal_public() -> None:
    r = score_loom_skill(ROOT, "loom-goal")
    assert r["ok"] is True
    assert r["scores"]["composite"] >= 55


def test_score_all_loom() -> None:
    allr = score_all_loom_skills(ROOT)
    assert allr["count"] >= 5
    assert allr["average_composite"] >= 60
    assert allr["ok"] is True, allr.get("failed")
