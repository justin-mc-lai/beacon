"""Goal steering templates (Codex Goal distill → Loom InjectBundle).

Contract authority:
- docs/beacon/v2.0.0/fixtures/steering/*
- skills/beacon/references/goal-steering/MUST_SECTIONS.md
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

TEMPLATE_IDS = ("continuation", "budget_limit", "objective_updated")

# Must tags from MUST_SECTIONS.md — runtime must not strip these semantics
MUST_TAGS_CONTINUATION = (
    "OBJECTIVE_AS_DATA",
    "SCOPE_FIDELITY",
    "WORK_FROM_EVIDENCE",
    "COMPLETION_AUDIT",
    "NO_SELF_COMPLETE",
    "BLOCKED_AUDIT",
    "BUDGET_AWARE",
)

MUST_TAGS_BUDGET = (
    "BUDGET_EXHAUSTED",
    "WRAP_UP_ONLY",
    "NO_BUDGET_COMPLETE",
)

MUST_TAGS_OBJECTIVE = (
    "NEW_OBJECTIVE_SUPERSEDES",
    "OBJECTIVE_AS_DATA",
    "REDIRECT_TURN",
    "NO_SELF_COMPLETE",
)

# Phrases that would violate AC-V2-ST-004 / I-V2-ST-002
FORBIDDEN_SELF_COMPLETE = (
    "update_goal",
    "mark the goalrun complete without verifier",
    "self-certify goalrun complete",
)


def fixtures_dir(project_root: Path, version: str = "v2.0.0") -> Path:
    """Prefer project fixtures; fall back to Beacon package checkout fixtures."""
    rel = Path("docs") / "beacon" / version / "fixtures" / "steering"
    candidates = [
        Path(project_root) / rel,
        Path(__file__).resolve().parents[2] / rel,
    ]
    for cand in candidates:
        if cand.is_dir() and (cand / "continuation.md").is_file():
            return cand
    return candidates[0]


def must_sections_path(project_root: Path) -> Path:
    return project_root / "skills" / "beacon" / "references" / "goal-steering" / "MUST_SECTIONS.md"


def load_template(
    project_root: Path,
    template_id: str,
    *,
    version: str = "v2.0.0",
) -> str:
    if template_id not in TEMPLATE_IDS:
        raise ValueError(f"unknown steering template_id={template_id}")
    path = fixtures_dir(project_root, version) / f"{template_id}.md"
    if not path.is_file():
        raise FileNotFoundError(f"steering template missing: {path}")
    text = path.read_text(encoding="utf-8")
    # forbid private shortening: empty or truncated below hard floor
    if len(text.strip()) < 120:
        raise ValueError(f"steering template too short (must not shorten MUST sections): {template_id}")
    low = text.lower()
    for bad in FORBIDDEN_SELF_COMPLETE:
        if bad in low and "must not" not in low and "do not" not in low:
            # allow if only mentioned as prohibition; hard ban update_goal token always
            if bad == "update_goal":
                raise ValueError("steering template must not include update_goal")
    if "update_goal" in low:
        raise ValueError("steering template must not include update_goal")
    return text


def _render_placeholders(template: str, mapping: dict[str, str]) -> str:
    out = template
    for key, value in mapping.items():
        out = out.replace("{{ " + key + " }}", value)
        out = out.replace("{{" + key + "}}", value)
    # leave unknown placeholders empty rather than leaking braces
    out = re.sub(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", "", out)
    return out


def budget_fields(goal_payload: dict[str, Any], driver_state: dict[str, Any] | None = None) -> dict[str, str]:
    driver_state = driver_state or {}
    token_budget = goal_payload.get("token_budget")
    tokens_used = goal_payload.get("tokens_used")
    if tokens_used is None:
        tokens_used = driver_state.get("tokens_used", 0)
    max_turns = int(
        driver_state.get("max_agent_turns")
        or (goal_payload.get("budget") or {}).get("max_agent_turns")
        or 32
    )
    turns_used = int(driver_state.get("turn_n") or goal_payload.get("turns_used") or 0)
    time_used = int(goal_payload.get("time_used_seconds") or driver_state.get("time_used_seconds") or 0)

    def fmt(v: Any) -> str:
        if v is None or v == "":
            return "none"
        return str(v)

    remaining = "unbounded"
    if token_budget is not None:
        try:
            remaining = str(max(0, int(token_budget) - int(tokens_used or 0)))
        except (TypeError, ValueError):
            remaining = "unknown"

    return {
        "tokens_used": fmt(tokens_used if tokens_used is not None else 0),
        "token_budget": fmt(token_budget),
        "remaining_tokens": remaining,
        "turns_used": str(turns_used),
        "max_agent_turns": str(max_turns),
        "time_used_seconds": str(time_used),
    }


def render_steering(
    project_root: Path,
    template_id: str,
    goal_payload: dict[str, Any],
    *,
    version: str = "v2.0.0",
    driver_state: dict[str, Any] | None = None,
) -> str:
    raw = load_template(project_root, template_id, version=version)
    objective = str(goal_payload.get("utterance") or goal_payload.get("objective") or "").strip()
    mapping = budget_fields(goal_payload, driver_state)
    mapping["objective"] = objective or "(empty objective)"
    return _render_placeholders(raw, mapping)


def select_template_id(
    *,
    halt_budget: bool = False,
    objective_updated: bool = False,
) -> str:
    if halt_budget:
        return "budget_limit"
    if objective_updated:
        return "objective_updated"
    return "continuation"


def build_inject_bundle(
    project_root: Path,
    goal_payload: dict[str, Any],
    *,
    resume_pack: dict[str, Any],
    next_action: str,
    turn_n: int,
    version: str = "v2.0.0",
    driver_state: dict[str, Any] | None = None,
    halt_budget: bool = False,
    objective_updated: bool = False,
) -> dict[str, Any]:
    """Ordered InjectBundle: steering → resume-pack digest → next_action."""
    template_id = select_template_id(halt_budget=halt_budget, objective_updated=objective_updated)
    steering = render_steering(
        project_root,
        template_id,
        goal_payload,
        version=version,
        driver_state=driver_state,
    )
    digest_lines = [
        f"run_id: {resume_pack.get('run_id') or goal_payload.get('run_id')}",
        f"utterance: {resume_pack.get('utterance')}",
        f"current_stage: {resume_pack.get('current_stage')}",
        f"status: {resume_pack.get('status')}",
        f"last_substep: {resume_pack.get('last_substep')}",
        f"done_when: {resume_pack.get('done_when')}",
        f"open_blockers: {resume_pack.get('open_blockers')}",
        f"recent_heartbeats: {resume_pack.get('recent_heartbeats')}",
        f"authority_note: {resume_pack.get('authority_note')}",
    ]
    parts = {
        "order": ["steering", "resume_pack_digest", "next_action"],
        "template_id": template_id,
        "steering": steering,
        "resume_pack_digest": "\n".join(str(x) for x in digest_lines),
        "next_action": str(next_action or resume_pack.get("next_action") or ""),
        "turn_n": turn_n,
    }
    return parts


def render_inject_bundle_prompt(bundle: dict[str, Any]) -> str:
    """Serialize InjectBundle preserving authority order."""
    order = bundle.get("order") or ["steering", "resume_pack_digest", "next_action"]
    sections: list[str] = [
        f"# Beacon Goal Driver Turn {bundle.get('turn_n')}",
        f"template_id: {bundle.get('template_id')}",
        "inject_bundle_order: steering → resume_pack_digest → next_action",
        "",
    ]
    for key in order:
        if key == "steering":
            sections.extend(
                [
                    "## 1) Steering (behavioral contract)",
                    str(bundle.get("steering") or ""),
                    "",
                ]
            )
        elif key == "resume_pack_digest":
            sections.extend(
                [
                    "## 2) Resume-pack digest (progress authority)",
                    str(bundle.get("resume_pack_digest") or ""),
                    "",
                ]
            )
        elif key == "next_action":
            sections.extend(
                [
                    "## 3) next_action",
                    str(bundle.get("next_action") or ""),
                    "",
                ]
            )
    sections.extend(
        [
            "## Rules",
            "- Inject order is mandatory; do not treat full chat or execution.jsonl body as sole authority.",
            "- Complete only with verifier refs after awaiting_verifier; never self-certify; never auto-release.",
            "- On progress: `beacon goal heartbeat --run-id ... --summary ...`",
            "- On pause: `beacon goal checkpoint --run-id ... --next-action ...`",
            "",
        ]
    )
    body = "\n".join(sections)
    assert "execution_jsonl_body" not in body
    assert "full_chat" not in body
    assert "update_goal" not in body.lower()
    # order check: steering section before digest before next_action
    i1 = body.find("## 1) Steering")
    i2 = body.find("## 2) Resume-pack digest")
    i3 = body.find("## 3) next_action")
    if not (0 <= i1 < i2 < i3):
        raise AssertionError("InjectBundle order violated in rendered prompt")
    return body


def bump_blocker_streak(goal_payload: dict[str, Any], blocker_id: str | None) -> dict[str, Any]:
    """Track consecutive goal turns with same blocker for blocked audit (≥3)."""
    counters = goal_payload.get("goal_turn_counters")
    if not isinstance(counters, dict):
        counters = {}
    current = str(blocker_id or "").strip()
    prev = str(counters.get("active_blocker_id") or "")
    if not current:
        counters["active_blocker_id"] = ""
        counters["streak"] = 0
    elif current == prev:
        counters["streak"] = int(counters.get("streak") or 0) + 1
    else:
        counters["active_blocker_id"] = current
        counters["streak"] = 1
    goal_payload["goal_turn_counters"] = counters
    # surface streak to blocked_streak when ≥3
    if int(counters.get("streak") or 0) >= 3 and current:
        goal_payload["blocked_streak"] = max(int(goal_payload.get("blocked_streak") or 0), int(counters["streak"]))
    return goal_payload


def objective_fingerprint(goal_payload: dict[str, Any]) -> str:
    return str(goal_payload.get("utterance") or goal_payload.get("objective") or "").strip()


def detect_objective_updated(goal_payload: dict[str, Any], driver_state: dict[str, Any] | None) -> bool:
    driver_state = driver_state or {}
    last = str(driver_state.get("last_objective_fp") or "")
    cur = objective_fingerprint(goal_payload)
    if not last:
        return False
    return bool(cur) and cur != last
