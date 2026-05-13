"""v1.4.5 guidance-family contract helpers."""

from __future__ import annotations

from typing import Any


GUIDANCE_SURFACE_FAMILY = (
    "ceo-review",
    "brainstorm",
    "design-review",
    "deep",
)

SHARED_DECISION_LOOP = (
    "define",
    "challenge",
    "freeze",
    "execute",
    "verify",
    "learn",
)

GUIDANCE_SKILL_PHILOSOPHY = (
    "strategy_philosophy",
    "minimum_complete_tools",
    "necessary_factual_grounding",
)

_ALIASES = {
    "beacon-ceo-review": "ceo-review",
    "ceo-review": "ceo-review",
    "beacon-brainstorm": "brainstorm",
    "brainstorm": "brainstorm",
    "beacon-design-review": "design-review",
    "design-review": "design-review",
    "beacon-deep": "deep",
    "deep": "deep",
}


def normalize_guidance_surface(surface: str | None) -> str:
    text = str(surface or "").strip()
    return _ALIASES.get(text, text)


def guidance_surface_family_members() -> list[str]:
    return list(GUIDANCE_SURFACE_FAMILY)


def build_guidance_family_contract() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "family": "guidance-surface-family",
        "members": guidance_surface_family_members(),
        "shared_decision_loop": list(SHARED_DECISION_LOOP),
        "boundaries": {
            "not_truth_source": True,
            "not_gate_source": True,
            "not_new_lifecycle_stage": True,
            "must_route_back_to": ["change", "prd", "user-story", "test-case", "implement", "qa"],
        },
        "software_lifecycle_materialization": {
            "type": "domain_materialization",
            "loop_projection": {
                "define": ["prd", "user-story", "test-case"],
                "challenge": ["ceo-review", "brainstorm", "design-review", "deep"],
                "freeze": ["change", "prototype"],
                "execute": ["implement"],
                "verify": ["qa", "release"],
                "learn": ["beacon-learn", "learning-loop"],
            },
        },
        "skill_philosophy_priority": list(GUIDANCE_SKILL_PHILOSOPHY),
    }


def build_guidance_surface_projection(
    surface: str,
    *,
    current_loop_layer: str = "challenge",
    missing_evidence: list[str] | None = None,
    target_surface: str = "",
    recommended_route: str = "",
) -> dict[str, Any]:
    normalized = normalize_guidance_surface(surface)
    contract = build_guidance_family_contract()
    return {
        "surface": normalized,
        "family": contract["family"],
        "family_member": normalized in GUIDANCE_SURFACE_FAMILY,
        "shared_decision_loop": contract["shared_decision_loop"],
        "current_loop_layer": current_loop_layer,
        "missing_evidence": [str(item).strip() for item in (missing_evidence or []) if str(item).strip()],
        "target_truth_or_delivery_surface": str(target_surface or "").strip(),
        "recommended_route": str(recommended_route or "").strip(),
        "boundaries": dict(contract["boundaries"]),
        "skill_philosophy_priority": list(contract["skill_philosophy_priority"]),
    }


def route_non_software_guidance(goal: str, *, output_shape: str = "") -> dict[str, str]:
    text = " ".join([str(goal or ""), str(output_shape or "")]).lower()
    if any(token in text for token in ("article", "post", "wechat", "weibo", "xhs", "content", "newsletter", "outline")):
        return {
            "surface": "brainstorm",
            "current_loop_layer": "challenge",
            "recommended_route": "beacon-brainstorm",
            "reason": "content-style business goals should converge through guidance before any truth or delivery route is chosen",
        }
    if any(token in text for token in ("strategy", "pricing", "market", "industry", "positioning", "analysis")):
        return {
            "surface": "ceo-review",
            "current_loop_layer": "challenge",
            "recommended_route": "beacon-ceo-review",
            "reason": "strategy-style business goals should challenge framing before they are materialized into delivery truth",
        }
    return {
        "surface": "brainstorm",
        "current_loop_layer": "challenge",
        "recommended_route": "beacon-brainstorm",
        "reason": "cross-domain goals default to the guidance family instead of forcing a coding-first lifecycle declaration",
    }
