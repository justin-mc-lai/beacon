"""P0 plan_artifact + P1 goal host_subagent/stage_trace/plan_to_truth + P2 checklists."""

from __future__ import annotations

import tempfile
from pathlib import Path

from beacon.utils.plan_artifact import build_plan_artifact, plan_to_truth_gate
from beacon.utils.plan_subintent import plan_progressive_loads_for_utterance
from beacon.utils.product_goal_runtime import (
    build_stage_plan,
    create_goal_run,
    tick_goal_run,
)
from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate

ROOT = Path(__file__).resolve().parents[1]


def test_ac_pa_001_schema_and_deep_want() -> None:
    art = build_plan_artifact("对着代码审查支付状态机完整复刻")
    assert art["schema"] == "plan_artifact.v1"
    assert art["methodology_track"] in {"review", "source"}
    assert art["deep_want"]
    assert "未提供明确诉求" not in art["deep_want"]
    assert len(art["options"]) >= 1
    assert art["recommended_next"]["next_stage_hint"]
    assert art["writes_truth"] is False
    assert art["may_implement"] is False
    assert art["high_risk"] is True


def test_ac_pa_002_attached_to_subintent_loads() -> None:
    r = plan_progressive_loads_for_utterance("先 brainstorm 想清楚，先别冻")
    assert r["subintent"] == "brainstorm"
    art = r["plan_artifact"]
    assert art["methodology_track"] == "brainstorm"
    assert art["schema"] == "plan_artifact.v1"


def test_ac_pa_003_stage_plan_hoists_artifact() -> None:
    stages = build_stage_plan(utterance="全面审查 parity 与状态机")
    plan = next(s for s in stages if s["stage"] == "plan")
    assert plan.get("plan_artifact", {}).get("schema") == "plan_artifact.v1"
    assert plan["plan_subintent"]["plan_artifact"]["methodology_track"] == "review"


def test_ac_pa_004_soft_gate_high_risk_incomplete() -> None:
    emptyish = build_plan_artifact("")
    g = plan_to_truth_gate(emptyish)
    assert g["blocked"] is False
    assert g["status"] in {"warn", "ok"}
    missing = plan_to_truth_gate(None)
    assert missing["reason_code"] == "plan_artifact_missing"
    assert missing["blocked"] is False


def test_ac_pa_005_soft_gate_ok_path() -> None:
    art = build_plan_artifact("拆海做多模块 program 规划")
    g = plan_to_truth_gate(art)
    assert g["blocked"] is False
    assert g["reason_code"] in {"plan_to_truth_ok", "plan_artifact_incomplete", "plan_journey_decomposition_incomplete"}


def test_ac_p1_001_create_host_subagent_default_off() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs" / "beacon" / "v1.6.9").mkdir(parents=True)
        run = create_goal_run(root, utterance="实现登录并验收", version="v1.6.9")
        hs = run.get("host_subagent") or {}
        assert hs.get("gate_on") is False
        assert hs.get("spawn") is False
        assert hs.get("single_thread") is True
        assert run.get("plan_artifact", {}).get("schema") == "plan_artifact.v1"
        st = run.get("stage_trace") or {}
        assert st.get("schema") == "goal-stage-trace.v1"
        assert "per_stage" in st
        assert run.get("plan_to_truth_hint", {}).get("blocked") is False


def test_ac_p1_002_create_host_subagent_keyword_on() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs" / "beacon" / "v1.6.9").mkdir(parents=True)
        run = create_goal_run(
            root,
            utterance="启用子代理做调研搜索竞品",
            version="v1.6.9",
        )
        hs = run["host_subagent"]
        assert hs["gate_on"] is True
        assert hs["spawn"] is True
        assert "pack-research" in (hs.get("packs") or [])
        # gate evaluates but goal runtime does not auto-spawn workers
        assert hs.get("cannot_complete_goal") is True


def test_ac_p1_003_tick_plan_to_truth_hint() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs" / "beacon" / "v1.6.9").mkdir(parents=True)
        run = create_goal_run(
            root,
            utterance="对着代码审查支付权限",
            version="v1.6.9",
        )
        # first stage should be plan (or discover support)
        # advance until leaving plan
        rid = run["run_id"]
        cur = run["current_stage"]
        # force current to plan for deterministic AC
        state_path = root / ".beacon" / "state" / "product-goal" / f"{rid}.json"
        import json

        data = json.loads(state_path.read_text(encoding="utf-8"))
        data["current_stage"] = "plan"
        for s in data.get("stages") or []:
            if s.get("stage") == "plan":
                s["status"] = "active"
        state_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        out = tick_goal_run(root, rid, note="p1-ac")
        assert out.get("plan_to_truth_hint") is not None
        assert out["plan_to_truth_hint"].get("blocked") is False
        st = out.get("stage_trace") or {}
        assert "plan" in (st.get("per_stage") or {}) or out.get("current_stage")


def test_ac_p2_001_checklist_files() -> None:
    assert (ROOT / "skills/beacon/references/design-philosophy-checklist.md").is_file()
    assert (ROOT / "skills/beacon/references/domain-fsm-truth-checklist.md").is_file()


def test_ac_p2_002_stage_plan_refs() -> None:
    stages = build_stage_plan(utterance="做带 UI 的登录页设计系统", lakes=["login-ui"])
    design = next((s for s in stages if s["stage"] == "design"), None)
    truth = next(s for s in stages if s["stage"] == "truth")
    assert design is not None, "ux intent should include design"
    refs_d = design.get("references") or []
    refs_t = truth.get("references") or []
    assert any("design-philosophy-checklist" in r for r in refs_d)
    assert any("domain-fsm-truth-checklist" in r for r in refs_t)


def test_ac_p2_003_skill_mentions() -> None:
    plan = (ROOT / "skills/beacon/beacon-plan/SKILL.md").read_text(encoding="utf-8")
    assert "plan_artifact" in plan or "plan artifact" in plan.lower()
    truth = (ROOT / "skills/beacon/references/domain-fsm-truth-checklist.md").read_text(encoding="utf-8")
    assert "domain_fsm" in truth
    design = (ROOT / "skills/beacon/references/design-philosophy-checklist.md").read_text(encoding="utf-8")
    assert "design" in design.lower()


def test_gate_parity_standalone() -> None:
    assert evaluate_host_subagent_gate("普通").get("gate_on") is False
    assert evaluate_host_subagent_gate("子代理").get("gate_on") is True
