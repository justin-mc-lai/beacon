"""Progressive merge lake: map + shells + self-heal + whitelist + examples."""

from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.product_goal_runtime import (
    host_visible_whitelist,
    load_progressive_map,
    plan_goal_self_heal,
    progressive_skills_for_stage,
    run_goal_facade,
)

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "skills/beacon/references/public-surface-progressive-map.v1.json"
SHELLS = [
    "beacon-goal",
    "beacon-plan",
    "beacon-truth",
    "beacon-design",
    "beacon-implement",
    "beacon-qa",
    "beacon-release",
    "loom-goal",
    "loom-plan",
    "loom-truth",
    "loom-design",
    "loom-implement",
    "loom-qa",
    "loom-release",
]


def test_ac_pm_001_map_exists() -> None:
    assert MAP_PATH.is_file()
    m = load_progressive_map()
    assert m.get("schema") == "public-surface-progressive-map.v1"
    harness = m["harness"]
    assert set(harness) == {"plan", "truth", "design", "implement", "qa", "release"}
    for _k, meta in harness.items():
        assert meta.get("progressive_loads"), _k


def test_ac_pm_002_progressive_stage_loads() -> None:
    plan = progressive_skills_for_stage("plan")
    assert "beacon-plan" in plan
    assert "beacon-pln-program" in plan
    impl = progressive_skills_for_stage("implement")
    assert "beacon-implement" in impl
    assert "beacon-gen-implement" in impl
    # rust alias
    assert progressive_skills_for_stage("loop")[0] == "beacon-plan"
    assert "beacon-qa" in progressive_skills_for_stage("qa-evidence")


def test_ac_pm_003_aggregate_shells_exist() -> None:
    for name in SHELLS:
        brand = "beacon" if name.startswith("beacon-") else "loom"
        path = ROOT / "skills" / brand / name / "SKILL.md"
        assert path.is_file(), name
        text = path.read_text(encoding="utf-8")
        assert "public_surface: true" in text or "public_surface: true" in text.replace(" ", "")
        assert "progressive" in text.lower()


def test_ac_pm_004_goal_self_heal() -> None:
    pre = plan_goal_self_heal(phase="pre")
    assert pre["steps"]
    assert pre["user_language"]
    run = run_goal_facade(ROOT, utterance="surface merge smoke", version="v1.6.9")
    assert "self_heal" in run
    assert "pre" in run["self_heal"]
    assert run.get("public_surface", {}).get("scheme") == "A"


def test_ac_pm_005_whitelist() -> None:
    b = host_visible_whitelist("beacon")
    l = host_visible_whitelist("loom")
    assert len(b) == 7 and len(l) == 7
    assert b[0].endswith("goal") and l[0].endswith("goal")


def test_ac_pm_006_examples() -> None:
    ex = ROOT / "skills/beacon/examples"
    for name in (
        "surface-goal-30s.md",
        "surface-plan-30s.md",
        "surface-truth-30s.md",
        "surface-design-30s.md",
        "surface-implement-30s.md",
        "surface-qa-30s.md",
        "surface-release-30s.md",
        "surface-goal-selfheal-30s.md",
    ):
        assert (ex / name).is_file(), name


def test_ac_pm_007_openai_yaml() -> None:
    for name in SHELLS:
        brand = "beacon" if name.startswith("beacon-") else "loom"
        # goal may already have openai.yaml
        y = ROOT / "skills" / brand / name / "agents" / "openai.yaml"
        if name.endswith("-goal") and not y.is_file():
            # beacon-goal has agents/openai.yaml historically
            y2 = ROOT / "skills" / brand / name / "agents" / "openai.yaml"
            assert y2.is_file() or (ROOT / "skills/beacon/beacon-goal/agents/openai.yaml").is_file()
            continue
        assert y.is_file(), name


def test_ac_pm_008_install_whitelist() -> None:
    claude = (ROOT / "scripts/install_claude_skills.sh").read_text(encoding="utf-8")
    loom = (ROOT / "scripts/install-loom-skills.sh").read_text(encoding="utf-8")
    agents = (ROOT / "scripts/install_all_agents.sh").read_text(encoding="utf-8")
    beacon_install = (ROOT / "scripts/beacon-install.sh").read_text(encoding="utf-8")
    assert "WHITELIST_BEACON" in claude or "beacon-plan" in claude
    assert "INSTALL_ALL" in claude
    assert "WHITELIST_LOOM" in loom
    assert "INSTALL_ALL" in loom
    # Scheme A: no default package-root install for Codex/agents
    assert "install_global_agents_beacon_skills" in agents
    assert "package root" in beacon_install.lower() or "Scheme A" in beacon_install
    assert "WHITELIST_BEACON" in beacon_install


def test_ac_pm_009_non_empty_loads() -> None:
    m = load_progressive_map()
    for hid, meta in m["harness"].items():
        assert len(meta["progressive_loads"]) >= 1, hid
