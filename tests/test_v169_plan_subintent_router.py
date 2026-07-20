"""Plan subintent router — strong intent → primary methodology (AC-PSI)."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.plan_subintent import detect_plan_subintent, plan_progressive_loads_for_utterance
from beacon.utils.product_goal_runtime import build_stage_plan, progressive_skills_for_stage

ROOT = Path(__file__).resolve().parents[1]


def test_ac_psi_001_review() -> None:
    d = detect_plan_subintent("对方案做全面审查，检查状态机与 source parity")
    assert d["subintent"] == "review"
    assert d["primary"] == "beacon-pln-review"
    assert d["writes_truth"] is False


def test_ac_psi_002_brainstorm() -> None:
    d = detect_plan_subintent("先 brainstorm 想清楚，先别写需求、先别冻")
    assert d["subintent"] == "brainstorm"
    assert d["primary"] == "beacon-pln-brainstorm"


def test_ac_psi_003_source() -> None:
    d = detect_plan_subintent("对着代码和现有接口调研需求，别瞎编")
    assert d["subintent"] == "source"
    assert d["primary"] == "beacon-pln-source"
    assert "beacon-pln-review" in d["secondary"]


def test_ac_psi_004_default_program() -> None:
    d = detect_plan_subintent("帮我规划一下下一步")
    assert d["subintent"] == "default"
    assert d["primary"] == "beacon-pln-program"


def test_ac_psi_005_primary_first_full_set() -> None:
    r = plan_progressive_loads_for_utterance("多角度 review 一下")
    loads = r["progressive_loads"]
    assert loads[0] == "beacon-plan"
    assert loads[1] == "beacon-pln-review"
    assert "beacon-pln-brainstorm" in loads
    assert "beacon-pln-source" in loads


def test_ac_psi_006_stage_plan_attaches() -> None:
    stages = build_stage_plan(utterance="对着仓库源码做需求调研")
    plan = next(s for s in stages if s["stage"] == "plan")
    assert plan.get("plan_subintent", {}).get("subintent") == "source"
    skills = progressive_skills_for_stage("plan", "全面审查 parity")
    assert "beacon-pln-review" in skills[:4]


def test_ac_psi_007_examples() -> None:
    ex = ROOT / "skills/beacon/examples"
    for name in (
        "surface-plan-review-30s.md",
        "surface-plan-brainstorm-30s.md",
        "surface-plan-source-research-30s.md",
    ):
        assert (ex / name).is_file()


def test_ac_psi_008_rust_plan_loads() -> None:
    text = (ROOT / "packages/beacon-rs/beacon-orchestrator/src/skill_load.rs").read_text(encoding="utf-8")
    for name in (
        "beacon-pln-review",
        "beacon-pln-brainstorm",
        "beacon-pln-source",
        "beacon-pln-friction",
    ):
        assert name in text


def test_ac_psi_009_hard_gate_flags() -> None:
    for utt in ("审查", "brainstorm", "对着代码", "拆海", ""):
        d = detect_plan_subintent(utt)
        assert d["writes_truth"] is False
        assert d["may_implement"] is False
        assert d["may_qa_verdict"] is False


def test_plan_skill_description_triggers() -> None:
    text = (ROOT / "skills/beacon/beacon-plan/SKILL.md").read_text(encoding="utf-8")
    assert "brainstorm" in text.lower()
    assert "review" in text.lower()
    assert "源码" in text or "代码" in text
