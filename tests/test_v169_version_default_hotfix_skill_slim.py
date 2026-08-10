"""version-default + hotfix-mainline + skill-slim (v1.6.9)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.prod_ops_v168 import build_hotfix_plan
from beacon.utils.version_defaults import (
    bump_patch,
    default_hotfix_baseline,
    default_target_version,
    hotfix_branch_name,
    resolve_goal_version,
)

ROOT = Path(__file__).resolve().parents[1]


def test_bump_patch_only() -> None:
    assert bump_patch("v1.6.8") == "v1.6.9"
    assert bump_patch("1.6.8") == "v1.6.9"


def test_ac_vd_default_target_on_real_repo() -> None:
    r = default_target_version(ROOT)
    assert r["version"].startswith("v")
    assert r["source"] in {
        "planning_or_docs_higher_than_runtime",
        "patch_bump",
        "beacon_self_planning_or_docs_higher_than_runtime",
        "beacon_self_patch_bump_of_runtime_release",
    }
    assert r.get("project_kind") == "beacon_self"
    # must not be major jump from runtime without planning
    assert r.get("runtime_baseline")


def test_ac_vd_resolve_goal_auto() -> None:
    r = resolve_goal_version(ROOT, "auto", goal_mode="normal")
    assert r["version"]
    assert r["source"] != "explicit"


def test_ac_hf_baseline_default() -> None:
    b = default_hotfix_baseline(ROOT)
    assert b["baseline"]
    assert b["bump"] is False
    plan = build_hotfix_plan(
        utterance="生产：事故",
        project_root=ROOT,
        auto_defaults=True,
        rollback_notes="revert x",
    )
    assert plan["baseline_ref"]
    assert plan.get("blocked") is False  # baseline filled
    assert plan.get("hotfix_branch", "").startswith("hotfix/")
    assert plan.get("not_feature_worktree") is True
    assert plan.get("forward_port_target") == "main"
    # release_ready needs rollback - we provided
    assert plan.get("release_ready") is True


def test_ac_hf_branch_name() -> None:
    name = hotfix_branch_name("v1.6.8", "生产：支付重复扣款")
    assert name.startswith("hotfix/v1.6.8-")


def test_ac_hf_resolve_goal_no_bump() -> None:
    r = resolve_goal_version(ROOT, "auto", goal_mode="hotfix")
    b = default_hotfix_baseline(ROOT)
    assert r["version"] == b["baseline"]


def test_ac_ss_skill_slim() -> None:
    goal = (ROOT / "skills/beacon/beacon-goal/SKILL.md").read_text(encoding="utf-8")
    lines = goal.count("\n") + (0 if goal.endswith("\n") else 1)
    # allow small margin for frontmatter
    assert lines <= 90, lines
    # slim SKILL.md delegates operational detail to shared references
    assert "goal" in goal.lower()
    assert (ROOT / "skills/beacon/references/hotfix-prod-incident.md").is_file()
    assert (ROOT / "skills/beacon/references/version-default.md").is_file()
    loom = (ROOT / "skills/loom/loom-goal/SKILL.md").read_text(encoding="utf-8")
    assert len(loom.splitlines()) <= 90


def test_feature_packages_exist() -> None:
    assert (ROOT / "docs/beacon/v1.6.9/features/beacon-version-default-hotfix-mainline-skill-slim-v169/truth.md").is_file()
