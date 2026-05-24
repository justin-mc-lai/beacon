"""Human-facing implement mode playbooks and route recommendations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PUBLIC_IMPLEMENT_SKILL = "beacon-implement"
FORBIDDEN_PUBLIC_IMPLEMENT_MODE_SKILLS = (
    "beacon-implement-single",
    "beacon-implement-team",
    "beacon-implement-ralph",
)

IMPLEMENT_MODE_PLAYBOOKS: dict[str, dict[str, Any]] = {
    "single": {
        "mode": "single",
        "title": "Single Mode",
        "purpose": "Small, low-risk, clearly scoped implementation through the single public implement surface.",
        "admission_conditions": [
            "change scope is narrow",
            "frozen requirement truth is stable",
            "role separation is not needed",
            "multi-round closure control is not needed",
        ],
        "expected_evidence": [
            "implementation summary",
            "changed file list",
            "handoff to QA when implementation evidence is ready",
        ],
        "boundary": "Single mode cannot rewrite frozen truth or claim QA, release, or gate verdicts.",
        "non_goals": [
            "parallel role execution",
            "Ralph repair loop control",
            "QA or release verdict",
        ],
    },
    "team": {
        "mode": "team",
        "title": "Team Mode",
        "purpose": "Complex implementation with role separation, subagent lanes, or parallel evidence needs.",
        "admission_conditions": [
            "implementation spans multiple modules or concerns",
            "planner / implementer / reviewer / tester separation is useful",
            "subagent or team evidence is required",
            "QA handoff must preserve role-specific context",
        ],
        "expected_evidence": [
            "team plan and role evidence",
            "implementation handoff",
            "review or QA readiness notes",
        ],
        "boundary": "Team mode remains internal runtime behavior under beacon-implement and is not a public lifecycle skill.",
        "non_goals": [
            "new public team skill",
            "automatic QA pass",
            "automatic release pass",
        ],
    },
    "ralph": {
        "mode": "ralph",
        "title": "Ralph Mode",
        "purpose": "Closure controller for multi-round repair routing after team or complex implementation evidence.",
        "admission_conditions": [
            "team implementation finished but closure is not authoritative",
            "review quality, QA, or release next action must be routed",
            "multi-round repair needs a controlled loop",
            "Ralph state can record blocker, next action, and evidence references",
        ],
        "expected_evidence": [
            "Ralph round trace",
            "current blocker and next action",
            "recommended command for implement repair, QA, or release",
        ],
        "boundary": "Ralph routes next action and evidence only; it never replaces QA, release, gate, or frozen truth.",
        "non_goals": [
            "formal QA verdict",
            "release verdict",
            "full checkpoint/recovery controller in this feature",
        ],
    },
}


def canonical_implement_mode_command(*, feature: str, project_root: Path | str, version: str, mode: str) -> str:
    quoted_feature = json.dumps(str(feature or ""), ensure_ascii=False)
    return f"beacon implement run {quoted_feature} --project {project_root} --version {version} --mode {mode}"


def playbook_refs() -> dict[str, str]:
    return {
        mode: f"skills/beacon/beacon-implement/references/implement-{mode}.md"
        for mode in IMPLEMENT_MODE_PLAYBOOKS
    }


def validate_public_implement_route(route: str) -> dict[str, Any]:
    text = str(route or "").strip()
    if text in FORBIDDEN_PUBLIC_IMPLEMENT_MODE_SKILLS:
        mode = text.removeprefix("beacon-implement-")
        return {
            "status": "blocked",
            "blocked": True,
            "reason_code": "forbidden_public_implement_mode_skill",
            "forbidden_route": text,
            "redirect_skill": PUBLIC_IMPLEMENT_SKILL,
            "mode": mode if mode in IMPLEMENT_MODE_PLAYBOOKS else "",
        }
    return {"status": "pass", "blocked": False, "reason_code": ""}


def recommend_implement_mode(
    *,
    feature: str,
    project_root: Path,
    version: str,
    next_step: dict[str, Any] | None = None,
    execution_surface: dict[str, Any] | None = None,
    prompt: str = "",
) -> dict[str, Any]:
    next_payload = next_step or {}
    execution = execution_surface or {}
    prompt_text = str(prompt or "").lower()
    next_action = str(next_payload.get("action") or "").lower()
    next_command = str(next_payload.get("command") or "").lower()
    active_mode = str(execution.get("implement_mode") or "").strip().lower()
    team_phase = str(execution.get("team_phase") or "").strip().lower()
    ralph_status = str(execution.get("ralph_status") or "").strip().lower()

    mode = "single"
    reason = "default implementation path for a frozen, clearly scoped feature"

    if (
        active_mode == "ralph"
        or ralph_status in {"active", "pending"}
        or next_action == "ralph"
        or "--mode ralph" in next_command
        or any(token in prompt_text for token in ("ralph", "closure", "repair loop", "qa release", "multi-round"))
    ):
        mode = "ralph"
        reason = "closure control is needed after team or complex implementation evidence"
    elif (
        active_mode == "team"
        or team_phase in {"running", "completed", "passed"}
        or "--mode team" in next_command
        or any(token in prompt_text for token in ("team", "subagent", "parallel", "multi role", "multi-role", "complex"))
    ):
        mode = "team"
        reason = "implementation needs role separation, subagent lanes, or complex-work evidence"
    elif active_mode == "single" or "--mode single" in next_command:
        mode = "single"
        reason = "single mode is already selected for this implementation evidence"

    playbook = IMPLEMENT_MODE_PLAYBOOKS[mode]
    return {
        "schema_version": "1.0",
        "public_skill": PUBLIC_IMPLEMENT_SKILL,
        "recommended_mode": mode,
        "reason": reason,
        "canonical_command": canonical_implement_mode_command(
            feature=feature,
            project_root=project_root,
            version=version,
            mode=mode,
        ),
        "playbook_ref": playbook_refs()[mode],
        "playbook": playbook,
        "forbidden_public_skills": list(FORBIDDEN_PUBLIC_IMPLEMENT_MODE_SKILLS),
        "authority_boundary": playbook["boundary"],
    }
