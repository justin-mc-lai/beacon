"""Plan harness subintent router (Scheme A).

Maps user utterance → primary progressive skill under public surface `plan`.
Does not write truth, implement, or issue QA/release verdicts.
"""

from __future__ import annotations

from typing import Any

# plan_artifact imported lazily to avoid cycles

# Primary internal skills (must remain planner HARD GATE)
PRIMARY_REVIEW = "beacon-pln-review"
PRIMARY_BRAINSTORM = "beacon-pln-brainstorm"
PRIMARY_SOURCE = "beacon-pln-source"
PRIMARY_PROGRAM = "beacon-pln-program"
PRIMARY_FRICTION = "beacon-pln-friction"
PRIMARY_DEFAULT = "beacon-pln-program"

# Full progressive set for plan (capability non-regression)
PLAN_ALL_LOADS = [
    "beacon-plan",
    "beacon-pln-program",
    "beacon-pln-program-auto",
    "beacon-pln-program-interactive",
    "beacon-pln-review",
    "beacon-pln-friction",
    "beacon-pln-brainstorm",
    "beacon-pln-source",
]

# subintent → (primary, secondary list, reason_code)
# Order matters: first match wins (more specific before default).
_RULES: list[tuple[str, tuple[str, ...], str, list[str]]] = [
    (
        "friction",
        (
            "摩擦",
            "卡点",
            "吐槽",
            "阻塞",
            "blocker",
            "friction",
            "一直过不去",
            "烦死了",
        ),
        PRIMARY_FRICTION,
        [],
    ),
    (
        "source",
        (
            "对着代码",
            "源码",
            "代码里",
            "接口",
            "别瞎编",
            "不要瞎编",
            "锚定代码",
            "source-driven",
            "source driven",
            "read the code",
            "based on code",
            "仓库现状",
            "现有实现",
            "github.com",
            "对照",
            "参考这个",
            "参考文章",
            "get-saas",
            "能力对照",
            "oss-sync",
        ),
        PRIMARY_SOURCE,
        [PRIMARY_REVIEW],
    ),
    (
        "review",
        (
            "全面审查",
            "多角度",
            "pln-review",
            "review",
            "审查",
            "状态机",
            "parity",
            "完整复刻",
            "做全",
            "source parity",
            "intent fidelity",
            "对抗",
            "challenge plan",
            "评审方案",
            "方案有问题",
            "是否可 implement",
            "freeze 前",
            "冻之前",
        ),
        PRIMARY_REVIEW,
        [PRIMARY_SOURCE],
    ),
    (
        "brainstorm",
        (
            "brainstorm",
            "头脑风暴",
            "先想清楚",
            "先别写需求",
            "先别冻",
            "先不写 truth",
            "只是 challenge",
            "挑战假设",
            "收敛 gap",
            "还没想清楚",
            "探索一下",
            "discuss first",
            "don't freeze yet",
            "only brainstorm",
        ),
        PRIMARY_BRAINSTORM,
        [],
    ),
    (
        "program",
        (
            "拆海",
            "海级",
            "多模块",
            "program",
            "feature graph",
            "程序规划",
            "整包复刻",
            "oss parity",
            "版本级规划",
            "多湖",
            "program plan",
            "蒸干",
            "底座",
            "开源底座",
            "foundation",
            "全功能",
            "插件化",
            "多产品",
            "l0",
            "l1",
            "l2",
            "l3",
            "l4",
            "l5",
            "l6",
            "能力对照",
            "saas",
        ),
        PRIMARY_PROGRAM,
        ["beacon-pln-program-auto", "beacon-pln-program-interactive"],
    ),
]


def detect_plan_subintent(utterance: str = "") -> dict[str, Any]:
    """Detect plan subintent from utterance.

    Multi-signal scoring: collects all matching tracks, then picks primary by
    priority (friction > source/review/brainstorm/program). Ocean/source can
    attach as secondary tracks so program+source is not collapsed to default.
    Default = light program only when nothing matches.
    """
    text = str(utterance or "")
    raw = text
    low = text.lower()
    scored: list[tuple[int, str, str, list[str], list[str]]] = []
    for subintent, tokens, primary, secondary in _RULES:
        hits: list[str] = []
        for tok in tokens:
            if tok.lower() in low or tok in raw:
                hits.append(tok)
        if hits:
            score = len(hits) * 10
            # boost program when lake markers present
            if subintent == "program" and any(
                x in low for x in ("l0", "l1", "l2", "l3", "l4", "l5", "l6", "多湖", "底座")
            ):
                score += 15
            if subintent == "source" and any(x in low for x in ("github.com", "get-saas", "对照")):
                score += 10
            scored.append((score, subintent, primary, list(secondary), hits))

    if not scored:
        return {
            "schema": "plan-subintent.v1",
            "subintent": "default",
            "primary": PRIMARY_DEFAULT,
            "secondary": [],
            "ordered_focus": [PRIMARY_DEFAULT],
            "matched_tokens": [],
            "confidence": 50,
            "reason_code": "plan_subintent_default",
            "writes_truth": False,
            "may_implement": False,
            "may_qa_verdict": False,
            "artifact_kind": "plan_note",
            "secondary_tracks": [],
            "status": "ok",
        }

    # priority for primary selection when scores close
    priority = {"friction": 100, "brainstorm": 90, "source": 80, "review": 70, "program": 60}
    scored.sort(key=lambda x: (x[0], priority.get(x[1], 0)), reverse=True)
    best_score, subintent, primary, secondary, matched = scored[0]
    secondary_tracks = [s[1] for s in scored[1:] if s[1] != subintent]
    # merge skill secondaries
    secondaries = [s for s in secondary if s != primary]
    for _sc, si, pr, sec, _h in scored[1:]:
        if pr not in secondaries and pr != primary:
            secondaries.append(pr)
        for s in sec:
            if s not in secondaries and s != primary:
                secondaries.append(s)
    # program+source common case: keep source research under program primary
    if subintent == "program" and "source" in secondary_tracks and PRIMARY_SOURCE not in secondaries:
        secondaries.insert(0, PRIMARY_SOURCE)
    if subintent == "source" and "program" in secondary_tracks and PRIMARY_PROGRAM not in secondaries:
        secondaries.insert(0, PRIMARY_PROGRAM)

    ordered = [primary, *secondaries]
    conf = 100 if best_score >= 20 else 75 if best_score >= 10 else 60
    return {
        "schema": "plan-subintent.v1",
        "subintent": subintent,
        "primary": primary,
        "secondary": secondaries,
        "ordered_focus": ordered,
        "matched_tokens": matched,
        "confidence": conf,
        "reason_code": f"plan_subintent_{subintent}",
        "writes_truth": False,
        "may_implement": False,
        "may_qa_verdict": False,
        "artifact_kind": {
            "review": "planner_review",
            "brainstorm": "brainstorm_note",
            "source": "source_research",
            "program": "program_plan",
            "friction": "friction_queue_item",
        }.get(subintent, "plan_note"),
        "secondary_tracks": secondary_tracks,
        "status": "ok",
    }



def plan_progressive_loads_for_utterance(utterance: str = "", *, brand: str = "beacon") -> dict[str, Any]:
    """Build progressive load list: public shell + primary/secondary first, then rest for non-regression."""
    det = detect_plan_subintent(utterance)
    shell = "beacon-plan" if brand != "loom" else "loom-plan"
    focus = list(det.get("ordered_focus") or [])
    # map to loom-* if brand loom and file naming
    if brand == "loom":
        focus = [x.replace("beacon-", "loom-", 1) for x in focus]
        all_loads = [x.replace("beacon-", "loom-", 1) if x.startswith("beacon-") else x for x in PLAN_ALL_LOADS]
        all_loads = ["loom-plan" if x == "beacon-plan" else x for x in all_loads]
    else:
        all_loads = list(PLAN_ALL_LOADS)

    # shell first, then focus, then remaining (capability non-regression)
    ordered: list[str] = []
    for x in [shell, *focus, *all_loads]:
        if x not in ordered:
            ordered.append(x)

    # default: do not force-load every heavy skill body — primary first, rest available
    # For default subintent, keep list shorter primary path but retain full set after
    from beacon.utils.plan_artifact import build_plan_artifact

    artifact = build_plan_artifact(utterance, subintent_payload=det)
    return {
        **det,
        "brand": brand,
        "public_shell": shell,
        "progressive_loads": ordered,
        "primary_load": ordered[1] if len(ordered) > 1 else ordered[0],
        "load_policy": "primary_first_then_full_set_for_non_regression",
        "plan_artifact": artifact,
    }
