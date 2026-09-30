"""Intent decomposition for product goals (v1.6.9+).

Turns a one-shot utterance into structured intents + user-journey seeds
before truth freeze. Does not write frozen truth itself.
"""

from __future__ import annotations

import re
from typing import Any

from beacon.utils.runtime import now_iso

SCHEMA = "intent_decomposition.v1"

# Host-fill markers appended by the task-closure advisory below. They are
# ADVISORY at plan stage: fill+freeze is hard-enforced at truth stage exit
# (scaffold/draft/freeze-ack), so plan_to_truth_gate must not block on them.
ADVISORY_FILL_PENDING_KEYS: tuple[str, ...] = (
    "host_llm_full_package_fill_pending",
    "host_agent_skill_authored_fill_pending",
)

# Capability / product surface cues
_CAPABILITY = (
    "认证",
    "登录",
    "注册",
    "auth",
    "支付",
    "billing",
    "订阅",
    "stripe",
    "多语言",
    "i18n",
    "插件",
    "plugin",
    "skill",
    "agent skill",
    "dashboard",
    "控制台",
    "部署",
    "deploy",
    "seo",
    "后台",
    "admin",
    "邮件",
    "email",
    "resend",
)

_PLATFORM = (
    "cloudflare",
    "d1",
    "postgres",
    "postgresql",
    "vercel",
    "better auth",
    "nextauth",
    "drizzle",
    "tanstack",
)

_OCEAN = (
    "拆海",
    "海级",
    "整包",
    "完整复刻",
    "parity",
    "底座",
    "foundation",
    "开源底座",
    "多模块",
    "多湖",
    "蒸干",
    "l0",
    "l1",
    "l2",
    "l3",
    "l4",
    "l5",
    "l6",
    "oss parity",
    "全功能",
)

_SOURCE = (
    "github.com",
    "对着代码",
    "源码",
    "对照",
    "参考",
    "get-saas",
    "别瞎编",
    "仓库",
)

_JOURNEY_HINTS: list[tuple[str, str, tuple[str, ...], list[str]]] = [
    (
        "J-deploy",
        "冷启动与部署",
        ("部署", "deploy", "cloudflare", "pages", "d1", "wrangler"),
        ["可按文档在目标平台拉起环境", "密钥与绑定清单完整"],
    ),
    (
        "J-identity",
        "注册登录与会话",
        ("认证", "登录", "注册", "auth", "better auth", "session"),
        ["用户可注册/登录", "会话可校验", "用户数据在自有存储"],
    ),
    (
        "J-billing",
        "订阅支付与权益",
        ("支付", "billing", "订阅", "stripe", "权益", "entitlement", "webhook"),
        ["可发起 checkout", "webhook 幂等开通权益", "无密钥泄漏到插件"],
    ),
    (
        "J-shell",
        "产品壳与多语言",
        ("dashboard", "控制台", "i18n", "多语言", "landing", "壳"),
        ["双语言壳可访问", "登录后可见账户/权益状态"],
    ),
    (
        "J-plugin",
        "插件化新产品",
        ("插件", "plugin", "多产品", "plugin-v0", "扩展"),
        ["manifest 可挂载路由/导航", "插件不直连支付密钥"],
    ),
    (
        "J-agent",
        "Agent skill 操作面",
        ("skill", "agent", "orient", "smoke", "子代理"),
        ["orient/add-plugin/smoke 技能可用", "冒烟有证据路径"],
    ),
    (
        "J-qa-release",
        "验收与发布门",
        ("验收", "qa", "release", "发布", "smoke"),
        ["旅程有测试或清单证据", "release 需人工门"],
    ),
]


def _has_any(text: str, tokens: tuple[str, ...]) -> list[str]:
    raw = str(text or "")
    low = raw.lower()
    hits: list[str] = []
    for tok in tokens:
        if tok.lower() in low or tok in raw:
            hits.append(tok)
    return hits


def _split_clauses(utterance: str) -> list[str]:
    parts = re.split(r"[。；;\n]|→|->", str(utterance or ""))
    out: list[str] = []
    for p in parts:
        p = p.strip(" ：:，,")
        if len(p) >= 4:
            out.append(p)
    return out


def _extract_lakes(utterance: str, lakes: list[str] | None = None) -> list[str]:
    found: list[str] = []
    if lakes:
        found.extend([str(x).strip() for x in lakes if str(x).strip()])
    raw = str(utterance or "")
    # L0-name / L0 name / L0: name
    for m in re.finditer(r"\bL([0-9]+)\s*[-:.]?\s*([A-Za-z0-9_-]+)?", raw, flags=re.I):
        n = m.group(1)
        slug = (m.group(2) or "").strip("-_ ")
        label = f"l{n}-{slug}".lower() if slug else f"l{n}"
        if label not in found:
            found.append(label)
    for m in re.finditer(r"湖\s*([0-9]+)", raw):
        label = f"lake-{m.group(1)}"
        if label not in found:
            found.append(label)
    return found


def _build_intents(utterance: str) -> list[dict[str, Any]]:
    intents: list[dict[str, Any]] = []
    clauses = _split_clauses(utterance)
    if not clauses and utterance.strip():
        clauses = [utterance.strip()]
    for idx, clause in enumerate(clauses, start=1):
        kinds: list[str] = []
        if _has_any(clause, _PLATFORM):
            kinds.append("platform")
        if _has_any(clause, _CAPABILITY):
            kinds.append("capability")
        if _has_any(clause, _OCEAN):
            kinds.append("scope")
        if _has_any(clause, _SOURCE):
            kinds.append("source")
        if not kinds:
            kinds = ["delivery"]
        intents.append(
            {
                "id": f"I{idx:02d}",
                "text": clause[:300],
                "kinds": kinds,
                "source_ref": f"utterance_clause_{idx}",
            }
        )
    return intents


def _build_journeys(utterance: str, lakes: list[str]) -> list[dict[str, Any]]:
    journeys: list[dict[str, Any]] = []
    for jid, name, tokens, ac_seeds in _JOURNEY_HINTS:
        hits = _has_any(utterance, tokens)
        # always include if lakes imply
        lake_force = False
        for lake in lakes:
            low = lake.lower()
            if jid == "J-identity" and "identity" in low:
                lake_force = True
            if jid == "J-billing" and "billing" in low:
                lake_force = True
            if jid == "J-shell" and "shell" in low:
                lake_force = True
            if jid == "J-plugin" and "plugin" in low:
                lake_force = True
            if jid == "J-deploy" and "deploy" in low:
                lake_force = True
            if jid == "J-qa-release" and ("smoke" in low or "qa" in low):
                lake_force = True
            if jid == "J-agent" and ("skill" in low or "smoke" in low):
                lake_force = True
        if hits or lake_force:
            journeys.append(
                {
                    "id": jid,
                    "name": name,
                    "matched_tokens": hits,
                    "actors": ["end_user", "builder", "agent"] if jid.startswith("J-agent") else ["end_user", "builder"],
                    "steps_seed": [
                        f"前置：满足 {name} 的环境/账户条件",
                        f"主路径：完成 {name}",
                        "失败路径：记录可恢复错误与权限拒绝",
                        "证据：测试、清单或日志路径可引用",
                    ],
                    "acceptance_seeds": list(ac_seeds),
                    "detail_level": "seed",  # seed ≠ frozen journey
                    "requires_freeze": True,
                }
            )
    # ocean with few matches → force core SaaS journeys
    if len(journeys) < 3 and (_has_any(utterance, _OCEAN) or len(lakes) >= 3):
        forced_ids = {"J-identity", "J-billing", "J-plugin", "J-agent"}
        have = {j["id"] for j in journeys}
        for jid, name, tokens, ac_seeds in _JOURNEY_HINTS:
            if jid in forced_ids and jid not in have:
                journeys.append(
                    {
                        "id": jid,
                        "name": name,
                        "matched_tokens": [],
                        "actors": ["end_user", "builder"],
                        "steps_seed": [
                            f"前置：满足 {name} 的环境/账户条件",
                            f"主路径：完成 {name}",
                            "失败路径：记录可恢复错误与权限拒绝",
                            "证据：测试、清单或日志路径可引用",
                        ],
                        "acceptance_seeds": list(ac_seeds),
                        "detail_level": "seed",
                        "requires_freeze": True,
                        "forced_by": "ocean_minimum",
                    }
                )
    return journeys


def decompose_product_intent(
    utterance: str = "",
    *,
    lakes: list[str] | None = None,
    subintent: str | None = None,
) -> dict[str, Any]:
    """Decompose utterance into intents + journey seeds + truth readiness."""
    text = str(utterance or "").strip()
    lake_list = _extract_lakes(text, lakes)
    intents = _build_intents(text)
    journeys = _build_journeys(text, lake_list)
    ocean_hits = _has_any(text, _OCEAN)
    source_hits = _has_any(text, _SOURCE)
    capability_hits = _has_any(text, _CAPABILITY)
    platform_hits = _has_any(text, _PLATFORM)
    scope_mode = "ocean" if ocean_hits or len(lake_list) >= 3 else "lake"

    # Journey freeze readiness: seeds alone are NEVER enough for ocean
    missing: list[str] = []
    if not text:
        missing.append("empty_utterance")
    if scope_mode == "ocean" and len(journeys) < 3:
        missing.append("insufficient_journey_seeds")
    if scope_mode == "ocean":
        missing.append("journey_detail_not_frozen")  # seeds require human/agent freeze pass
        missing.append("ac_matrix_not_materialized")
    if source_hits and not any("github.com" in text.lower() or "get-saas" in text.lower() or "源码" in text or "对照" in text for _ in [1]):
        pass
    if source_hits:
        # need explicit source anchors later
        missing.append("source_anchors_pending")
    if any(k in text for k in ("支付", "billing", "stripe", "auth", "认证", "权限")) or _has_any(
        text, ("支付", "stripe", "auth", "认证")
    ):
        # high-risk domains present → require domain FSM notes before truth auto
        if "domain_fsm_notes_missing" not in missing and scope_mode == "ocean":
            missing.append("domain_fsm_notes_missing")

    # Lake-only simple delivery can be ready sooner
    ready = False
    if scope_mode == "lake" and len(intents) >= 1 and len(missing) == 0:
        ready = True
    if scope_mode == "lake" and not ocean_hits and len(lake_list) <= 1:
        # drop ocean-only missing
        missing = [m for m in missing if m not in {"journey_detail_not_frozen", "ac_matrix_not_materialized", "domain_fsm_notes_missing"}]
        ready = len(intents) >= 1 and not missing

    blocks_auto = scope_mode == "ocean" or bool(missing)

    deep_want_bits = []
    if platform_hits:
        deep_want_bits.append(f"平台约束：{', '.join(platform_hits[:6])}")
    if capability_hits:
        deep_want_bits.append(f"能力面：{', '.join(capability_hits[:8])}")
    if ocean_hits:
        deep_want_bits.append("范围：海级/多湖，需拆旅程后 freeze")
    if source_hits:
        deep_want_bits.append(f"源码锚定：{', '.join(source_hits[:5])}")
    deep_want = (
        "；".join(deep_want_bits)
        if deep_want_bits
        else "推进可验证交付；需补齐成功标准与失败边界。"
    )
    if text:
        deep_want = f"{deep_want}｜表层：{text[:240]}"

    methodology_secondary: list[str] = []
    primary = subintent or "default"
    if ocean_hits or len(lake_list) >= 2:
        methodology_secondary.append("program")
    if source_hits:
        methodology_secondary.append("source")
    if _has_any(text, ("支付", "auth", "安全", "状态机", "parity", "完整复刻")):
        methodology_secondary.append("review")

    result = {
        "schema": SCHEMA,
        "generated_at": now_iso(),
        "surface_ask": text,
        "deep_want": deep_want,
        "intents": intents,
        "journeys": journeys,
        "scope": {
            "mode": scope_mode,
            "lakes": lake_list,
            "ocean_tokens": ocean_hits,
        },
        "methodology": {
            "declared_subintent": subintent,
            "secondary_tracks": methodology_secondary,
        },
        "signals": {
            "platform": platform_hits,
            "capability": capability_hits,
            "source": source_hits,
            "ocean": ocean_hits,
        },
        "high_risk_domains": sorted(
            {
                *(["payment"] if _has_any(text, ("支付", "stripe", "billing", "订阅")) else []),
                *(["auth"] if _has_any(text, ("认证", "auth", "登录", "权限")) else []),
                *(["plugin_isolation"] if _has_any(text, ("插件", "plugin")) else []),
            }
        ),
        "truth_readiness": {
            "ready": ready and not blocks_auto if scope_mode == "ocean" else ready,
            "missing": missing,
            "blocks_auto_tick_past_plan": blocks_auto,
            "requires_journey_freeze": scope_mode == "ocean" or len(journeys) >= 2,
            "user_facing": (
                "海级/多旅程诉求：已生成 journey seeds，但尚未冻结用户旅程与 AC 矩阵；禁止 auto_tick 跳过 truth。"
                if blocks_auto
                else "意图拆解可进入 truth 细化。"
            ),
        },
        "recommended_truth_artifacts": [
            "docs/beacon/<ver>/user-story/*-journeys.md",
            "docs/beacon/<ver>/features/<lake>/truth.md (per lake)",
            "docs/beacon/<ver>/.machine/user-story/*.json",
            "domain FSM notes for payment/auth if high_risk",
        ],
        "status": "ok",
    }
    try:
        from beacon.utils.plan_goal_task_closure import (
            INTENT_DIMENSIONS,
            INHERITED_MUST_INTENTS,
            evaluate_intent_dimensions,
            evaluate_inherited_must_intents,
            evaluate_missing_must,
            version_requires_task_closure,
        )

        wants_closure = (
            "v1.6.11" in text
            or "task closure" in text.lower()
            or "任务闭环" in text
            or "大目标" in text
            or any("v1611" in str(x).lower() for x in lake_list)
            or version_requires_task_closure("v1.6.11", lake_list[0] if lake_list else "")
        )
        if wants_closure:
            dim_intents = []
            for n, i in enumerate(intents, 1):
                dim_intents.append(
                    {
                        "id": i.get("id") or f"I{n:02d}",
                        "text": i.get("text") or text,
                        "strength": "must",
                        "landing": "AC-pending",
                        "dimensions": list(INTENT_DIMENSIONS),
                    }
                )
            if not dim_intents:
                dim_intents = [
                    {
                        "id": "I01",
                        "text": text or "task closure",
                        "strength": "must",
                        "landing": "AC-pending",
                        "dimensions": list(INTENT_DIMENSIONS),
                    }
                ]
            landings = {k: f"AC-INH-{n:02d}" for n, k in enumerate(INHERITED_MUST_INTENTS, 1)}
            result["task_closure_intent"] = {
                "schema": "task-closure-intent-advisory.v1",
                "intent_dimensions": evaluate_intent_dimensions(dim_intents),
                "missing_must": evaluate_missing_must(dim_intents),
                "inherited_must_intents": evaluate_inherited_must_intents(landings),
                "recommended_fill": [
                    "beacon truth init -f <lake> -v v1.6.11",
                    "beacon truth fill-request -f <lake> -v v1.6.11 -u <utterance> --json",
                    "beacon truth fill-apply -f <lake> -v v1.6.11 --request-json <req> --response-json <resp> --json",
                ],
            }
            # surface fill requirement into truth readiness advisory
            tr = dict(result.get("truth_readiness") or {})
            miss = list(tr.get("missing") or [])
            if "host_llm_full_package_fill_pending" not in miss:
                miss.append("host_llm_full_package_fill_pending")
            if "host_agent_skill_authored_fill_pending" not in miss:
                miss.append("host_agent_skill_authored_fill_pending")
            tr["missing"] = miss
            tr["task_closure"] = True
            result["truth_readiness"] = tr
    except Exception:  # noqa: BLE001
        pass
    return result


def mark_journeys_frozen(
    decomposition: dict[str, Any],
    *,
    frozen_journey_ids: list[str] | None = None,
    ac_matrix_present: bool = False,
    domain_fsm_present: bool = False,
    source_anchors: list[str] | None = None,
) -> dict[str, Any]:
    """Return updated decomposition after a real freeze pass (agent/human)."""
    d = dict(decomposition or {})
    tr = dict(d.get("truth_readiness") or {})
    missing = [m for m in list(tr.get("missing") or []) if m != "empty_utterance"]
    fj = set(frozen_journey_ids or [])
    journeys = list(d.get("journeys") or [])
    if fj and all(j.get("id") in fj for j in journeys if j.get("requires_freeze")):
        missing = [m for m in missing if m != "journey_detail_not_frozen"]
        for j in journeys:
            if j.get("id") in fj:
                j = dict(j)
                j["detail_level"] = "frozen"
        d["journeys"] = [
            ({**j, "detail_level": "frozen"} if j.get("id") in fj else j) for j in journeys
        ]
    if ac_matrix_present:
        missing = [m for m in missing if m != "ac_matrix_not_materialized"]
    if domain_fsm_present:
        missing = [m for m in missing if m != "domain_fsm_notes_missing"]
    if source_anchors:
        d["source_anchors"] = list(source_anchors)
        missing = [m for m in missing if m != "source_anchors_pending"]
    ready = len(missing) == 0
    tr["missing"] = missing
    tr["ready"] = ready
    tr["blocks_auto_tick_past_plan"] = not ready
    tr["user_facing"] = (
        "旅程/AC 已标记冻结，可进入 truth 物化。"
        if ready
        else f"仍缺：{', '.join(missing)}"
    )
    d["truth_readiness"] = tr
    return d
