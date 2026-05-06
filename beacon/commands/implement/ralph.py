"""Ralph runtime integration for implement command."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.ralph_runtime import (
    append_ralph_round,
    finalize_ralph_state,
    initialize_ralph_state,
    load_ralph_state,
    mark_ralph_handoff_required,
    save_ralph_state,
)
from beacon.utils.runtime import now_iso


def refresh_ralph_state_after_resume(
    project_root: Path,
    *,
    feature: str,
    resumed_action: str,
    exit_code: int,
    result: dict[str, Any] | None,
) -> None:
    """Refresh Ralph state after resuming from a specific action."""
    state = load_ralph_state(project_root, feature=feature)
    if not state:
        return
    payload = result if isinstance(result, dict) else {}
    version = str(state.get("version", "") or "").strip()
    updated = False

    # Use immutable pattern - create new state instead of mutating
    updated_state = None

    if resumed_action == "review_quality":
        if exit_code != 0:
            return
        gate_ready = bool(payload.get("gate_ready", False))
        if gate_ready:
            release_cmd = f"beacon gate check release --project-root {project_root} --version {version}" if version else ""
            updated_state = {
                **state,
                "review_gate_ready": True,
                "current_blocker": "gate_release_pending",
                "next_action": "release",
                "recommended_command": release_cmd,
                "stop_state": "human_blocked",
                "updated_at": now_iso(),
            }
    elif resumed_action == "release":
        gate_status = str(payload.get("status", "") or "").strip().lower()
        release_check_cmd = f"beacon gate check release --project-root {project_root} --version {version}" if version else ""
        requirement_gate = payload.get("requirement_completeness") if isinstance(payload.get("requirement_completeness"), dict) else {}
        if not requirement_gate and isinstance(payload.get("requirement_completeness_gate"), dict):
            requirement_gate = payload.get("requirement_completeness_gate")
        if gate_status == "pass":
            updated_state = {
                **state,
                "gate_release_status": "pass",
                "stop_state": "release_ready",
                "current_blocker": "",
                "next_action": "release",
                "recommended_command": f"beacon release check {version} --project {project_root}" if version else "",
                "updated_at": now_iso(),
            }
        elif gate_status:
            requirement_blocked = (
                isinstance(requirement_gate, dict)
                and (
                    bool(requirement_gate.get("blocked"))
                    or str(requirement_gate.get("status") or "").strip().lower() == "blocked"
                )
            )
            requirement_handoff = requirement_gate.get("human_loop_handoff") if isinstance(requirement_gate.get("human_loop_handoff"), dict) else {}
            updated_state = {
                **state,
                "gate_release_status": gate_status,
                "stop_state": "human_blocked",
                "current_blocker": str(requirement_gate.get("reason_code") or "gate_release_blocked") if requirement_blocked else "gate_release_blocked",
                "next_action": "human_review" if requirement_blocked else "release",
                "recommended_command": (
                    str(requirement_handoff.get("recommended_command") or requirement_gate.get("recommended_command") or "")
                    if requirement_blocked
                    else release_check_cmd
                ),
                "updated_at": now_iso(),
            }

    if updated_state:
        save_ralph_state(project_root, feature=feature, payload=updated_state)


def render_ralph_round_markdown(payload: dict[str, Any]) -> str:
    """Render Ralph round payload as markdown."""
    round_index = payload.get("round_index", 0)
    status = payload.get("status", "unknown")

    lines = [
        f"# Ralph Round {round_index}",
        "",
        f"**Status**: {status}",
        f"**Timestamp**: {payload.get('timestamp', 'N/A')}",
        "",
        "## Execution",
        "",
    ]

    if "result" in payload:
        lines.extend([
            "### Result",
            "",
            f"```json",
            f"{payload['result']}",
            f"```",
            "",
        ])

    if "verification" in payload:
        lines.extend([
            "### Verification",
            "",
            f"```json",
            f"{payload['verification']}",
            f"```",
            "",
        ])

    return "\n".join(lines)


def build_ralph_summary(auto_qa_payload: dict[str, Any] | None) -> dict[str, Any]:
    """Build Ralph summary from auto-QA payload."""
    summary = {
        "ralph_mode": True,
        "auto_qa_executed": auto_qa_payload is not None,
    }

    if auto_qa_payload:
        summary.update({
            "qa_status": auto_qa_payload.get("status"),
            "qa_coverage": auto_qa_payload.get("coverage"),
            "qa_passed": auto_qa_payload.get("passed", False),
        })

    return summary


def render_ralph_summary_markdown(payload: dict[str, Any]) -> str:
    """Render Ralph summary as markdown."""
    lines = [
        "# Ralph Implementation Summary",
        "",
        f"**Feature**: {payload.get('feature', 'N/A')}",
        f"**Version**: {payload.get('version', 'N/A')}",
        f"**Status**: {payload.get('status', 'unknown')}",
        "",
        "## Rounds",
        "",
    ]

    rounds = payload.get("rounds", [])
    for i, round_data in enumerate(rounds):
        lines.extend([
            f"### Round {i + 1}",
            "",
            f"- Status: {round_data.get('status', 'unknown')}",
            f"- Timestamp: {round_data.get('timestamp', 'N/A')}",
            "",
        ])

    if "auto_qa" in payload:
        lines.extend([
            "## Auto-QA",
            "",
            f"- Executed: {payload['auto_qa'].get('executed', False)}",
            f"- Passed: {payload['auto_qa'].get('passed', False)}",
            f"- Coverage: {payload['auto_qa'].get('coverage', 'N/A')}",
            "",
        ])

    return "\n".join(lines)
