"""Intent decomposition hardening — ocean journeys + auto_tick block."""

from __future__ import annotations

import tempfile
from pathlib import Path

from beacon.utils.intent_decomposition import decompose_product_intent, mark_journeys_frozen
from beacon.utils.plan_artifact import build_plan_artifact, plan_to_truth_gate
from beacon.utils.plan_subintent import detect_plan_subintent
from beacon.utils.product_goal_runtime import create_goal_run, run_goal_facade


OPEN_SAAS_UTT = (
    "交付 open-saas-base 开源 SaaS 底座：主平台 Cloudflare Pages + D1；"
    "能力对照 get-saas；插件化多产品；完善 agent skills。"
    "并行子代理海湖蒸干 L0 skeleton → L1 Identity → L2 Billing → L3 Shell → "
    "L4 Plugin v0 → L5 Deploy → L6 Smoke QA，作为自研产品底座。"
)


def test_open_saas_not_default_subintent() -> None:
    d = detect_plan_subintent(OPEN_SAAS_UTT)
    assert d["subintent"] != "default"
    assert d["subintent"] in {"program", "source", "review"}
    assert d["confidence"] >= 60


def test_decompose_ocean_journeys_and_block_auto() -> None:
    dec = decompose_product_intent(
        OPEN_SAAS_UTT,
        lakes=["l0-skeleton", "l1-identity", "l2-billing", "l3-shell", "l4-plugin-v0", "l5-deploy", "l6-smoke-qa"],
    )
    assert dec["scope"]["mode"] == "ocean"
    assert len(dec["journeys"]) >= 3
    assert len(dec["intents"]) >= 2
    tr = dec["truth_readiness"]
    assert tr["blocks_auto_tick_past_plan"] is True
    assert tr["ready"] is False
    assert "journey_detail_not_frozen" in tr["missing"]


def test_plan_artifact_carries_decomposition() -> None:
    art = build_plan_artifact(OPEN_SAAS_UTT, lakes=["l0-skeleton", "l1-identity", "l2-billing"])
    assert art["intent_decomposition"]["schema"] == "intent_decomposition.v1"
    assert art["journeys"]
    assert art["high_risk"] is True
    gate = plan_to_truth_gate(art)
    assert gate["blocks_auto_tick_past_plan"] is True
    assert gate["reason_code"] == "plan_journey_decomposition_incomplete"


def test_mark_journeys_frozen_clears_block_but_keeps_host_fill_advisory() -> None:
    dec = decompose_product_intent(OPEN_SAAS_UTT, lakes=["l1-identity", "l2-billing", "l4-plugin-v0"])
    ids = [j["id"] for j in dec["journeys"]]
    frozen = mark_journeys_frozen(
        dec,
        frozen_journey_ids=ids,
        ac_matrix_present=True,
        domain_fsm_present=True,
        source_anchors=["oss-sync/saas/templates/get-saas"],
    )
    # journey/AC/FSM/source items are cleared, but host LLM full-package fill and
    # host agent skill authored advisory remain before truth readiness.
    missing = frozen["truth_readiness"]["missing"]
    assert "journey_detail_not_frozen" not in missing
    assert "ac_matrix_not_materialized" not in missing
    assert "domain_fsm_notes_missing" not in missing
    assert "source_anchors_pending" not in missing
    assert "host_llm_full_package_fill_pending" in missing
    assert "host_agent_skill_authored_fill_pending" in missing
    assert frozen["truth_readiness"]["ready"] is False
    assert frozen["truth_readiness"]["blocks_auto_tick_past_plan"] is True


def test_auto_tick_stops_at_plan_for_ocean() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs" / "beacon").mkdir(parents=True)
        out = run_goal_facade(
            root,
            utterance=OPEN_SAAS_UTT,
            version="v0.0.1",
            lakes=["l0-skeleton", "l1-identity", "l2-billing", "l3-shell", "l4-plugin-v0", "l5-deploy", "l6-smoke-qa"],
            auto_tick=True,
            longrun=False,
            driver_start=False,
        )
        assert out["current_stage"] == "plan"
        assert out.get("plan_to_truth_hint", {}).get("blocks_auto_tick_past_plan") is True
        stages = {s["stage"]: s["status"] for s in out.get("stages") or []}
        assert stages.get("plan") in {"planned", "done", "active"}  # blocked before plan marked done
        # truth must NOT be done via auto_tick
        assert stages.get("truth") != "done"
        assert stages.get("implement") != "done"


def test_host_subagent_on_for_parallel_zi_daili() -> None:
    from beacon.utils.host_subagent_gate import evaluate_host_subagent_gate

    g = evaluate_host_subagent_gate(OPEN_SAAS_UTT)
    assert g["gate_on"] is True
    assert g["spawn"] is True


def test_simple_plan_still_auto_ticks() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs" / "beacon").mkdir(parents=True)
        out = run_goal_facade(
            root,
            utterance="帮我规划一下下一步小改动",
            version="v0.0.1",
            auto_tick=True,
            longrun=False,
            driver_start=False,
        )
        # light plan may advance; at least not crash
        assert out.get("run_id")
        assert out.get("plan_artifact", {}).get("schema") == "plan_artifact.v1"
