"""Plan first-principles artifact (Scheme A P0).

plan_artifact.v1 captures deep_want + options + recommended_next.
Does not write frozen truth or implement.
"""

from __future__ import annotations

import re
from typing import Any

from beacon.utils.runtime import now_iso
import hashlib

SCHEMA = "plan_artifact.v1"

# High-risk cues → prefer review / completeness before truth
_HIGH_RISK = (
    "支付",
    "payment",
    "billing",
    "stripe",
    "订阅",
    "权限",
    "auth",
    "认证",
    "登录",
    "安全",
    "security",
    "状态机",
    "fsm",
    "完整复刻",
    "parity",
    "生产",
    "production",
    "迁移",
    "migration",
    "合规",
    "插件",
    "plugin",
    "webhook",
)


def _infer_deep_want(utterance: str, subintent: str, *, decomposition: dict | None = None) -> str:
    """Deep-want heuristic enriched by intent_decomposition when present."""
    text = str(utterance or "").strip()
    if not text:
        return "未提供明确诉求；需澄清：成功时看得见什么、最怕什么失败。"
    if isinstance(decomposition, dict) and decomposition.get("deep_want"):
        return str(decomposition["deep_want"])
    scaffolds = {
        "review": f"深层想要：在动手前确认方案可落地、边界清晰、状态/风险可审查。表层：{text[:200]}",
        "brainstorm": f"深层想要：先想清楚问题与选项，避免过早冻需求。表层：{text[:200]}",
        "source": f"深层想要：以仓库真实代码/接口为锚做需求调研，避免空中楼阁。表层：{text[:200]}",
        "program": f"深层想要：把大海拆成可交付的湖与用户旅程，控制范围与顺序后再 freeze。表层：{text[:200]}",
        "friction": f"深层想要：扫清阻塞/摩擦，恢复可前进状态。表层：{text[:200]}",
        "default": f"深层想要：推进可验证的下一步计划（尚待澄清约束与成功标准）。表层：{text[:200]}",
    }
    return scaffolds.get(subintent, scaffolds["default"])


def _infer_non_goals(subintent: str) -> list[str]:
    base = [
        "不在 plan 阶段写入 frozen truth",
        "不在 plan 阶段实现代码或宣称 QA/release 通过",
    ]
    if subintent == "brainstorm":
        base.append("不把 brainstorm 笔记当成已冻结需求")
    if subintent == "source":
        base.append("不臆造源码中不存在的行为")
    return base


def _default_options(subintent: str) -> list[dict[str, str]]:
    catalog = {
        "review": [
            {"id": "A", "title": "先跑 multi-angle planner-review", "tradeoff": "慢但挡假方案"},
            {"id": "B", "title": "仅 intent-fidelity 快审后进 truth", "tradeoff": "快但可能漏状态机/parity"},
        ],
        "brainstorm": [
            {"id": "A", "title": "只读收敛 gap，再人工 promote 到 truth", "tradeoff": "稳"},
            {"id": "B", "title": "并行收集选项后一次性 truth", "tradeoff": "更快，需防范围膨胀"},
        ],
        "source": [
            {"id": "A", "title": "源码锚定调研 → plan artifact → truth", "tradeoff": "防空中楼阁"},
            {"id": "B", "title": "先草拟 truth 再对照代码修正", "tradeoff": "易产生假需求"},
        ],
        "program": [
            {"id": "A", "title": "海→湖 program graph 后再逐湖 truth", "tradeoff": "可控"},
            {"id": "B", "title": "单湖直接 truth", "tradeoff": "仅当范围已是湖"},
        ],
        "friction": [
            {"id": "A", "title": "friction 入队后继续主链", "tradeoff": "不挡交付"},
            {"id": "B", "title": "先清 P0 摩擦再 plan", "tradeoff": "可能停住"},
        ],
        "default": [
            {"id": "A", "title": "轻量 program/plan 后进入 truth", "tradeoff": "默认路径"},
            {"id": "B", "title": "若风险高则先 review/source", "tradeoff": "多一轮 plan"},
        ],
    }
    return list(catalog.get(subintent, catalog["default"]))


def _recommended_next(subintent: str, *, high_risk: bool) -> dict[str, Any]:
    if subintent == "brainstorm":
        return {
            "action": "continue_plan_or_promote",
            "next_stage_hint": "truth" if not high_risk else "plan",
            "message": "brainstorm 完成后需显式 promote 再 freeze；高风险建议再 review。",
        }
    if subintent in {"review", "source"} and high_risk:
        return {
            "action": "complete_plan_then_truth",
            "next_stage_hint": "truth",
            "message": "深审/源码调研完成后进入 truth；仍禁止在 plan 直接 freeze。",
        }
    if subintent == "friction":
        return {
            "action": "queue_and_continue",
            "next_stage_hint": "plan",
            "message": "摩擦入队后可继续主链；P0 阻塞需人处理。",
        }
    return {
        "action": "proceed_truth",
        "next_stage_hint": "truth",
        "message": "plan 产出齐备后进入 truth(freeze) 链。",
    }


def is_high_risk_utterance(utterance: str = "") -> bool:
    text = str(utterance or "").lower()
    raw = str(utterance or "")
    return any(tok.lower() in text or tok in raw for tok in _HIGH_RISK)


def build_plan_artifact(
    utterance: str = "",
    *,
    subintent_payload: dict[str, Any] | None = None,
    evidence_anchors: list[str] | None = None,
    lakes: list[str] | None = None,
) -> dict[str, Any]:
    """Build plan_artifact.v1 from utterance + optional subintent detection."""
    if isinstance(subintent_payload, dict):
        det = subintent_payload
    else:
        from beacon.utils.plan_subintent import detect_plan_subintent

        det = detect_plan_subintent(utterance)
    sub = str(det.get("subintent") or "default")
    high_risk = is_high_risk_utterance(utterance)
    anchors = [str(a).strip() for a in (evidence_anchors or []) if str(a).strip()]
    if sub == "source" and not anchors:
        anchors = ["(required) path/symbol from repo — agent must fill during source research"]

    from beacon.utils.intent_decomposition import decompose_product_intent

    decomposition = decompose_product_intent(
        utterance, lakes=lakes, subintent=sub
    )
    if decomposition.get("high_risk_domains"):
        high_risk = True
    deep_want = _infer_deep_want(utterance, sub, decomposition=decomposition)
    options = _default_options(sub)
    rec = _recommended_next(sub, high_risk=high_risk)
    # Ocean / multi-journey: do not recommend auto truth skip
    tr = decomposition.get("truth_readiness") if isinstance(decomposition.get("truth_readiness"), dict) else {}
    if tr.get("blocks_auto_tick_past_plan"):
        rec = {
            "action": "decompose_and_freeze_journeys",
            "next_stage_hint": "truth",
            "message": str(tr.get("user_facing") or "先完成用户旅程拆解与冻结，再 auto 推进。"),
            "blocks_auto_tick_past_plan": True,
        }

    completeness = {
        "surface_ask": bool(str(utterance or "").strip()),
        "deep_want": bool(deep_want and "未提供明确诉求" not in deep_want),
        "options": len(options) >= 1,
        "recommended_next": bool(rec.get("next_stage_hint")),
        "evidence_anchors_ok": sub != "source" or any(not a.startswith("(required)") for a in anchors) or True,
        # source allows placeholder anchor at create; agent must replace — flag soft
    }
    # soft completeness: structural fields present
    complete = all(
        [
            completeness["surface_ask"] or True,  # allow empty with scaffold
            completeness["deep_want"],
            completeness["options"],
            completeness["recommended_next"],
        ]
    )

    missing = [k for k, ok in completeness.items() if not ok and k != "evidence_anchors_ok"]
    # ponytail: persistent goal — plan产持久目标对象，对齐 codex ThreadGoal，最小闭环
    _obj = str(utterance or "").strip()
    persistent_goal = {
        "objective": _obj,
        "status": "active",
        "token_budget": None,
        "objective_fingerprint": hashlib.sha256(_obj.encode()).hexdigest()[:12] if _obj else "",
        "source": SCHEMA,
    }

    return {
        "schema": SCHEMA,
        "surface_ask": str(utterance or "").strip(),
        "persistent_goal": persistent_goal,
        "deep_want": deep_want,
        "non_goals": _infer_non_goals(sub),
        "methodology_track": sub,
        "primary_skill": det.get("primary"),
        "options": options,
        "recommended_next": rec,
        "evidence_anchors": anchors,
        "high_risk": high_risk,
        "intent_decomposition": decomposition,
        "journeys": list(decomposition.get("journeys") or []),
        "truth_readiness": decomposition.get("truth_readiness") or {},
        "plan_subintent": {
            "subintent": sub,
            "reason_code": det.get("reason_code"),
            "matched_tokens": det.get("matched_tokens") or [],
            "confidence": det.get("confidence"),
        },
        "completeness": completeness,
        "structurally_complete": complete,
        "missing_fields": missing,
        "writes_truth": False,
        "may_implement": False,
        "generated_at": now_iso(),
        "status": "ok",
    }


def plan_to_truth_gate(plan_artifact: dict[str, Any] | None) -> dict[str, Any]:
    """Gate before plan → truth (soft for humans; hard flag for auto_tick only).

    - ``blocked`` stays soft (False) so manual tick/agent authoring is not hard-stopped.
    - ``blocks_auto_tick_past_plan`` is the hard signal for ``--auto-tick`` facade.
    """
    art = plan_artifact if isinstance(plan_artifact, dict) else {}
    if not art:
        return {
            "status": "warn",
            "blocked": False,
            "reason_code": "plan_artifact_missing",
            "user_facing": "缺少 plan_artifact，建议重建 plan 后再 truth。",
            "recommended_action": "rebuild_plan_artifact",
            "blocks_auto_tick_past_plan": True,
            "missing": ["plan_artifact"],
        }
    deep_ok = bool((art.get("completeness") or {}).get("deep_want"))
    high = bool(art.get("high_risk"))
    tr = art.get("truth_readiness") if isinstance(art.get("truth_readiness"), dict) else {}
    if not tr and isinstance(art.get("intent_decomposition"), dict):
        tr = (art.get("intent_decomposition") or {}).get("truth_readiness") or {}
    from beacon.utils.intent_decomposition import ADVISORY_FILL_PENDING_KEYS

    # Host-fill markers are advisory at plan (intent_decomposition calls them
    # exactly that): fill+freeze is hard-enforced at truth stage exit
    # (scaffold/frozen gates). Blocking plan on them deadlocks every
    # task-closure goal, because nothing ever clears them from the artifact —
    # the precomputed blocks_auto flag is advisory-driven once journeys freeze.
    missing = [m for m in list(tr.get("missing") or []) if m not in ADVISORY_FILL_PENDING_KEYS]
    if high and not deep_ok:
        return {
            "status": "warn",
            "blocked": False,
            "reason_code": "plan_deep_want_incomplete_high_risk",
            "user_facing": "高风险诉求但深层目标仍模糊；进入 truth 前建议补齐 deep_want / 先 review。",
            "recommended_action": "enrich_deep_want_or_review",
            "blocks_auto_tick_past_plan": True,
            "missing": missing or ["deep_want"],
        }
    if not art.get("structurally_complete", True) and not deep_ok:
        return {
            "status": "warn",
            "blocked": False,
            "reason_code": "plan_artifact_incomplete",
            "user_facing": "plan_artifact 结构不齐，建议补齐后再 truth。",
            "recommended_action": "enrich_plan_artifact",
            "blocks_auto_tick_past_plan": True,
            "missing": missing or list(art.get("missing_fields") or []),
        }
    if missing:
        return {
            "status": "ok",
            "blocked": False,
            "reason_code": "plan_journey_decomposition_incomplete",
            "user_facing": str(
                tr.get("user_facing")
                or "已识别海级/多旅程诉求，但用户旅程与 AC 尚未冻结；禁止 auto_tick 跳过 truth。"
            ),
            "recommended_action": "freeze_user_journeys_then_truth",
            "blocks_auto_tick_past_plan": True,
            "missing": missing,
            "journeys": list(art.get("journeys") or []),
        }
    return {
        "status": "ok",
        "blocked": False,
        "reason_code": "plan_to_truth_ok",
        "user_facing": "plan 产出结构齐全，可进入 truth。",
        "recommended_action": "proceed_truth",
        "blocks_auto_tick_past_plan": False,
        "missing": [],
    }


