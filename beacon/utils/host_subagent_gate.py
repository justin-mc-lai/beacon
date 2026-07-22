"""Host subagent keyword gate (v1.6.8).

Default single-thread: no host agent spawn unless global keyword or --subagent.
"并行" alone enables satellite fan-out (existing), NOT host agents (UD-SA-001).
"""

from __future__ import annotations

from typing import Any

REASON_DEFAULT_OFF = "subagent_default_off"
REASON_NEGATED = "subagent_negated"
REASON_FLAG_OFF = "subagent_flag_off"
REASON_GATE_ON = "subagent_gate_on"
REASON_FLAG_ON = "subagent_flag_on"

# Global ON — host agents allowed only after these (or --subagent)
GLOBAL_ON = (
    "subagent",
    "sub-agents",
    "sub agents",
    "with agents",
    "子代理",
    "多代理",
    "开子代理",
    "启用子代理",
    "并行子代理",
    "satellite agent",
    "host agents",
)

# Global OFF — wins over ON tokens when present in utterance
GLOBAL_OFF = (
    "no subagent",
    "without subagent",
    "without subagents",
    "disable subagent",
    "不要子代理",
    "禁用子代理",
    "关闭子代理",
)

# Stage packs (matched after gate is on)
STAGE_PACKS: dict[str, tuple[str, ...]] = {
    "pack-research": ("调研", "搜索", "search", "竞品", "先搜", "docs-researcher", "search-specialist"),
    "pack-review": (
        "全面审查",
        "多角度",
        "oracle",
        "challenge",
        "pln-review",
        "architect-reviewer",
        "架构",
        "架构设计",
        "架构审查",
        "代码审查",
        "code review",
        "软件工程",
        "全面分析",
        "plan review",
        "需求分析",
        "设计审查",
    ),
    "pack-implement": ("并行实现", "worker", "team implement", "backend-developer", "蒸干", "多湖", "l0", "l1", "实现湖"),
    "pack-qa": ("并行验收", "reviewer", "qa subagent", "correctness", "qa-expert", "验收子代理"),
}

# Roles for pack-default when only global on
DEFAULT_ROLES = ("search-specialist",)
PACK_ROLES: dict[str, tuple[str, ...]] = {
    "pack-research": ("search-specialist", "docs-researcher"),
    "pack-review": (
        "multi-agent-coordinator",
        "architect-reviewer",
        "code-reviewer",
        "knowledge-synthesizer",
        "security-auditor",
        "performance-engineer",
        "api-designer",
        "qa-expert",
        "docs-researcher",
        "search-specialist",
    ),
    "pack-implement": ("backend-developer",),
    "pack-qa": ("code-reviewer", "qa-expert"),
    "pack-default": DEFAULT_ROLES,
    "pack-coord": ("multi-agent-coordinator",),
}

# Six curated roles (UD-SA-002)
MINIMAL_SIX_ROLES = (
    "search-specialist",
    "docs-researcher",
    "multi-agent-coordinator",
    "code-reviewer",
    "backend-developer",
    "qa-expert",
)

PLAN_REVIEW_CORE_ROLES = (
    "multi-agent-coordinator",
    "architect-reviewer",
    "code-reviewer",
    "knowledge-synthesizer",
)

PLAN_REVIEW_CONDITIONAL_ROLES = (
    "security-auditor",
    "performance-engineer",
    "api-designer",
    "qa-expert",
    "docs-researcher",
    "search-specialist",
)

PLAN_REVIEW_TEN_ROLES = PLAN_REVIEW_CORE_ROLES + PLAN_REVIEW_CONDITIONAL_ROLES


def _norm(text: str) -> str:
    return str(text or "").strip().lower()


def _find_tokens(text: str, tokens: tuple[str, ...]) -> list[str]:
    hay = _norm(text)
    # keep original for CJK match
    raw = str(text or "")
    raw_lower = raw.lower()
    found: list[str] = []
    for tok in tokens:
        t = str(tok)
        if not t:
            continue
        # CJK / mixed: substring on original + lower
        if t.lower() in raw_lower or t in raw:
            found.append(t)
    return found


def evaluate_host_subagent_gate(
    utterance: str = "",
    *,
    flag: bool | None = None,
) -> dict[str, Any]:
    """Evaluate whether host agents may be planned.

    Priority: flag False / negate tokens > flag True / global ON > default off.
    """
    text = str(utterance or "")
    off_hits = _find_tokens(text, GLOBAL_OFF)
    on_hits = _find_tokens(text, GLOBAL_ON)

    if flag is False:
        return _off_payload(reason=REASON_FLAG_OFF, matched_off=["--no-subagent"], matched_on=on_hits)

    if off_hits:
        return _off_payload(reason=REASON_NEGATED, matched_off=off_hits, matched_on=on_hits)

    gate_on = bool(flag is True) or bool(on_hits)
    if not gate_on:
        # UD-SA-001: parallel/satellite words alone do NOT open host agents
        return _off_payload(reason=REASON_DEFAULT_OFF, matched_off=[], matched_on=[])

    packs: list[str] = []
    pack_tokens: dict[str, list[str]] = {}
    roles: list[str] = []
    for pack_id, tokens in STAGE_PACKS.items():
        hits = _find_tokens(text, tokens)
        if hits:
            packs.append(pack_id)
            pack_tokens[pack_id] = hits
            for role in PACK_ROLES.get(pack_id, ()):
                if role not in roles:
                    roles.append(role)

    if not packs:
        packs = ["pack-default"]
        roles = list(DEFAULT_ROLES)
        pack_tokens["pack-default"] = on_hits or ["--subagent"]

    reason = REASON_FLAG_ON if flag is True else REASON_GATE_ON
    return {
        "schema": "host-subagent-gate.v1",
        "host_agents": True,
        "spawn": True,
        "single_thread": False,
        "gate_on": True,
        "reason_code": reason,
        "matched_global_on": on_hits if flag is not True else on_hits + ["--subagent"],
        "matched_global_off": [],
        "packs": packs,
        "pack_tokens": pack_tokens,
        "roles": roles,
        "cannot_complete_goal": True,
        "cannot_auto_release": True,
        "satellite_parallel_independent": True,
        "status": "ok",
    }


def _off_payload(
    *,
    reason: str,
    matched_off: list[str],
    matched_on: list[str],
) -> dict[str, Any]:
    return {
        "schema": "host-subagent-gate.v1",
        "host_agents": False,
        "spawn": False,
        "single_thread": True,
        "gate_on": False,
        "reason_code": reason,
        "matched_global_on": matched_on,
        "matched_global_off": matched_off,
        "packs": [],
        "pack_tokens": {},
        "roles": [],
        "cannot_complete_goal": True,
        "cannot_auto_release": True,
        "satellite_parallel_independent": True,
        "status": "ok",
    }


def detect_satellite_parallel_intent(utterance: str = "") -> bool:
    """Satellite/worktree parallel — independent of host agents (UD-SA-001)."""
    text = str(utterance or "").lower()
    markers = ("并行", "多湖", "satellite", "fan-out", "fanout", "主星", "卫星", "parallel lakes")
    return any(m in text or m in str(utterance or "") for m in markers)


def score_overlay_dimensions() -> dict[str, float]:
    """L3 Agent Eval overlay weights (runtime_evidence_only; not formal QA)."""
    return {
        "subagent_keyword_precision": 0.25,
        "subagent_keyword_recall": 0.15,
        "single_thread_preservation": 0.20,
        "host_pack_readiness": 0.15,
        "boundary_no_self_complete": 0.15,
        "fallback_honesty": 0.10,
    }
