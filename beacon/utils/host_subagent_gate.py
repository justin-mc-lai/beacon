"""Host subagent keyword gate (v1.6.8+ spawn budget).

Default single-thread: no host agent spawn unless global keyword or --subagent.
"并行" alone enables satellite fan-out (existing), NOT host agents (UD-SA-001).

Spawn budget (v1.6.10 D-VA-CNT):
- Catalog may install up to 10 plan-review roles.
- Default spawn plan is 3 roles (architect / code-review / knowledge-synth).
- User may raise count via utterance, explicit param, or CLI; hard-capped.
"""

from __future__ import annotations

import os
import re
from typing import Any

REASON_DEFAULT_OFF = "subagent_default_off"
REASON_NEGATED = "subagent_negated"
REASON_FLAG_OFF = "subagent_flag_off"
REASON_GATE_ON = "subagent_gate_on"
REASON_FLAG_ON = "subagent_flag_on"

# Spawn budget
DEFAULT_SPAWN_MAX = 3
SPAWN_HARD_MAX = 10
ENV_SUBAGENT_MAX = "BEACON_SUBAGENT_MAX"

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

# Default triangle when pack-review opens without a higher user count
PLAN_REVIEW_CORE_ROLES = (
    "architect-reviewer",
    "code-reviewer",
    "knowledge-synthesizer",
)

PLAN_REVIEW_CONDITIONAL_ROLES = (
    "multi-agent-coordinator",
    "security-auditor",
    "performance-engineer",
    "api-designer",
    "qa-expert",
    "docs-researcher",
    "search-specialist",
)

PLAN_REVIEW_TEN_ROLES = PLAN_REVIEW_CORE_ROLES + PLAN_REVIEW_CONDITIONAL_ROLES

# Global spawn priority: prefer triangle, then remaining catalog order
SPAWN_PRIORITY = PLAN_REVIEW_TEN_ROLES + (
    "backend-developer",
)

# Roles for pack-default when only global on
DEFAULT_ROLES = ("search-specialist",)
PACK_ROLES: dict[str, tuple[str, ...]] = {
    "pack-research": ("search-specialist", "docs-researcher"),
    "pack-review": PLAN_REVIEW_TEN_ROLES,
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

_COUNT_PATTERNS = (
    re.compile(r"subagent[_-]?count\s*[=:]\s*(\d+)", re.I),
    re.compile(r"spawn[_-]?count\s*[=:]\s*(\d+)", re.I),
    re.compile(r"max[_-]?subagents?\s*[=:]\s*(\d+)", re.I),
    re.compile(r"--subagent-count\s*[=:]?\s*(\d+)", re.I),
    re.compile(r"开\s*(\d+)\s*个子代理"),
    re.compile(r"启动\s*(\d+)\s*个子代理"),
    re.compile(r"(\d+)\s*个子代理"),
    re.compile(r"(\d+)\s*subagents?\b", re.I),
    re.compile(r"spawn\s+(\d+)\s+subagents?\b", re.I),
)


def _norm(text: str) -> str:
    return str(text or "").strip().lower()


def _find_tokens(text: str, tokens: tuple[str, ...]) -> list[str]:
    raw = str(text or "")
    raw_lower = raw.lower()
    found: list[str] = []
    for tok in tokens:
        t = str(tok)
        if not t:
            continue
        if t.lower() in raw_lower or t in raw:
            found.append(t)
    return found


def parse_subagent_count(utterance: str = "") -> int | None:
    """Extract user-requested spawn count from utterance; None if not stated."""
    text = str(utterance or "").strip()
    if not text:
        return None
    for pattern in _COUNT_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                value = int(match.group(1))
            except (TypeError, ValueError):
                continue
            if value > 0:
                return value
    return None


def _env_spawn_cap() -> int | None:
    raw = str(os.environ.get(ENV_SUBAGENT_MAX) or "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    if value <= 0:
        return None
    return value


def resolve_spawn_count(
    *,
    catalog_size: int,
    utterance: str = "",
    subagent_count: int | None = None,
) -> dict[str, Any]:
    """Resolve how many host roles to plan (not how many files to install).

    Precedence: explicit param > utterance parse > DEFAULT_SPAWN_MAX(3).
    Hard caps: min(catalog_size, SPAWN_HARD_MAX, BEACON_SUBAGENT_MAX env if set).
    """
    catalog_n = max(0, int(catalog_size or 0))
    env_cap = _env_spawn_cap()
    hard = SPAWN_HARD_MAX
    if env_cap is not None:
        hard = min(hard, env_cap)
    if catalog_n > 0:
        hard = min(hard, catalog_n)
    else:
        hard = 0

    source = "default"
    requested: int | None = None
    if subagent_count is not None:
        try:
            requested = int(subagent_count)
            source = "param"
        except (TypeError, ValueError):
            requested = None
    if requested is None:
        parsed = parse_subagent_count(utterance)
        if parsed is not None:
            requested = parsed
            source = "utterance"
    if requested is None:
        requested = DEFAULT_SPAWN_MAX
        source = "default"

    if requested < 1:
        requested = 1
        source = f"{source}_clamped_min"
    spawn_n = min(int(requested), hard) if hard > 0 else 0
    if spawn_n != int(requested) and hard > 0:
        source = f"{source}_clamped_max"

    return {
        "spawn_count": spawn_n,
        "spawn_count_requested": int(requested),
        "spawn_count_source": source,
        "spawn_count_default": DEFAULT_SPAWN_MAX,
        "spawn_count_hard_max": SPAWN_HARD_MAX,
        "spawn_count_env_cap": env_cap,
        "spawn_count_catalog_size": catalog_n,
        "spawn_count_effective_cap": hard,
    }


def _order_roles(roles: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for name in SPAWN_PRIORITY:
        if name in roles and name not in seen:
            ordered.append(name)
            seen.add(name)
    for name in roles:
        if name not in seen:
            ordered.append(name)
            seen.add(name)
    return ordered


def evaluate_host_subagent_gate(
    utterance: str = "",
    *,
    flag: bool | None = None,
    subagent_count: int | None = None,
) -> dict[str, Any]:
    """Evaluate whether host agents may be planned.

    Priority: flag False / negate tokens > flag True / global ON > default off.
    When on, roles_catalog holds full pack catalog; roles is budget-sliced spawn plan.
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
    catalog: list[str] = []
    for pack_id, tokens in STAGE_PACKS.items():
        hits = _find_tokens(text, tokens)
        if hits:
            packs.append(pack_id)
            pack_tokens[pack_id] = hits
            for role in PACK_ROLES.get(pack_id, ()):
                if role not in catalog:
                    catalog.append(role)

    if not packs:
        packs = ["pack-default"]
        catalog = list(DEFAULT_ROLES)
        pack_tokens["pack-default"] = on_hits or ["--subagent"]

    roles_catalog = _order_roles(catalog)
    budget = resolve_spawn_count(
        catalog_size=len(roles_catalog),
        utterance=text,
        subagent_count=subagent_count,
    )
    roles = roles_catalog[: int(budget["spawn_count"])]

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
        "roles_catalog": roles_catalog,
        "spawn_count": budget["spawn_count"],
        "spawn_count_requested": budget["spawn_count_requested"],
        "spawn_count_source": budget["spawn_count_source"],
        "spawn_count_default": budget["spawn_count_default"],
        "spawn_count_hard_max": budget["spawn_count_hard_max"],
        "spawn_count_env_cap": budget["spawn_count_env_cap"],
        "spawn_count_catalog_size": budget["spawn_count_catalog_size"],
        "spawn_count_effective_cap": budget["spawn_count_effective_cap"],
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
        "roles_catalog": [],
        "spawn_count": 0,
        "spawn_count_requested": 0,
        "spawn_count_source": "off",
        "spawn_count_default": DEFAULT_SPAWN_MAX,
        "spawn_count_hard_max": SPAWN_HARD_MAX,
        "spawn_count_env_cap": _env_spawn_cap(),
        "spawn_count_catalog_size": 0,
        "spawn_count_effective_cap": 0,
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
        "subagent_keyword_precision": 0.22,
        "subagent_keyword_recall": 0.13,
        "single_thread_preservation": 0.18,
        "host_pack_readiness": 0.13,
        "boundary_no_self_complete": 0.14,
        "fallback_honesty": 0.10,
        "spawn_budget_control": 0.10,
    }
