"""Beacon debug command."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.control_plane import (
    append_recovery_checkpoint,
    build_resume_contract,
    exhaustion_for_run,
    load_recovery_checkpoint,
    record_stage_failure,
)
from beacon.utils.codex_hud_hook import HUD_HOOK_ACTIVATION_SOURCE_ENV, record_codex_hud_hook_activation
from beacon.utils.debug_feedback import (
    append_debug_event_memory,
    append_debug_feedback_event,
    debug_ideas_dir,
    debug_index_path,
    debug_issues_dir,
    debug_root,
    debug_feedback_path,
    load_debug_mode_state,
    resolve_debug_run_id,
    save_debug_mode_state,
)
from beacon.utils.help_support import build_help_payload
from beacon.utils.intent_router import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    ROUTER_CONFIG_FILE,
    build_prompt_adaptation_pack,
    optimize_prompt_to_plan,
)
from beacon.utils.input_audit import append_user_input_audit, load_user_input_audit, user_input_audit_path
from beacon.utils.learning_loop import refresh_learning_loop
from beacon.utils.prompt_router_history import (
    append_prompt_router_history,
    load_prompt_router_history,
    prompt_router_history_path,
)
from beacon.utils.runtime import newest_run_id, now_iso, run_events_path, write_json
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="debug", help="Debug helpers")
confidence_app = typer.Typer(name="confidence", help="Prompt confidence threshold controls.")
checkpoint_app = typer.Typer(name="checkpoint", help="Checkpoint / resume contract helpers.")
exhaustion_app = typer.Typer(name="exhaustion", help="Failure streak / escalation state helpers.")
app.add_typer(confidence_app, name="confidence")
app.add_typer(checkpoint_app, name="checkpoint")
app.add_typer(exhaustion_app, name="exhaustion")


HUD_HOOK_CONTEXT_PREFIX = "[beacon-hud]"
HUD_HOOK_SUPPORTED_EVENTS = {"UserPromptSubmit", "SessionStart", "SessionResume", "SessionRefresh"}


def _router_config_path(project_root: Path) -> Path:
    return project_root / ".beacon" / ROUTER_CONFIG_FILE


def _load_router_config(project_root: Path) -> dict[str, Any]:
    path = _router_config_path(project_root)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        payload = {}
    return payload if isinstance(payload, dict) else {}


def _save_router_config(project_root: Path, payload: dict[str, Any]) -> Path:
    path = _router_config_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _to_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:  # noqa: BLE001
        return fallback


def _read_codex_hook_event_name(payload: dict[str, Any]) -> str:
    for key in ("hook_event_name", "hookEventName", "event", "name"):
        value = str(payload.get(key, "") or "").strip()
        if value:
            return value
    return ""


def _read_codex_prompt_text(payload: dict[str, Any]) -> str:
    for key in ("prompt", "input", "user_prompt", "userPrompt", "text"):
        value = str(payload.get(key, "") or "").strip()
        if value:
            return value
    return ""


def _read_codex_feature(payload: dict[str, Any]) -> str:
    for key in ("feature", "feature_slug", "featureSlug"):
        value = str(payload.get(key, "") or "").strip()
        if value:
            return value
    return ""


def _load_hook_payload(payload_json: str = "") -> dict[str, Any]:
    raw = str(payload_json or "").strip()
    if not raw:
        raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        raise typer.BadParameter(f"invalid JSON payload: {exc}") from exc
    if not isinstance(payload, dict):
        raise typer.BadParameter("hook payload must be a JSON object")
    return payload


def _prompt_block_reason(plan: dict[str, Any]) -> str:
    boundary_state = str(plan.get("boundary", {}).get("state", "in_scope") or "in_scope")
    if boundary_state == "out_of_scope":
        return "outside-beacon-boundary"
    if boundary_state == "mixed_need_confirm":
        return "mixed-boundary-needs-confirmation"
    confidence = float(plan.get("confidence", 0.0) or 0.0)
    min_confidence = float(
        plan.get("execution_policy", {}).get("min_confidence", DEFAULT_CONFIDENCE_THRESHOLD)
        or DEFAULT_CONFIDENCE_THRESHOLD
    )
    if confidence < min_confidence:
        return "low-confidence"
    return ""


def _append_codex_hook_snapshot(
    project_root: Path,
    *,
    run_id: str,
    payload: dict[str, Any],
    plan: dict[str, Any],
    adaptation: dict[str, Any],
) -> Path:
    run_dir = debug_root(project_root) / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "codex-user-prompt-submit.jsonl"
    record = {
        "ts": now_iso(),
        "hook_event_name": _read_codex_hook_event_name(payload),
        "session_id": str(payload.get("session_id", payload.get("sessionId", "")) or ""),
        "thread_id": str(payload.get("thread_id", payload.get("threadId", "")) or ""),
        "turn_id": str(payload.get("turn_id", payload.get("turnId", "")) or ""),
        "transcript_path": str(payload.get("transcript_path", payload.get("transcriptPath", "")) or ""),
        "prompt": _read_codex_prompt_text(payload),
        "plan": plan,
        "adaptation": adaptation,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def _render_fixed_hud_context(lines: list[str]) -> str:
    cleaned = [str(item).strip() for item in lines if str(item).strip()]
    if not cleaned:
        return ""
    return "\n".join([HUD_HOOK_CONTEXT_PREFIX, *cleaned])


def _append_codex_fixed_hud_snapshot(
    project_root: Path,
    *,
    run_id: str,
    payload: dict[str, Any],
    hook_event_name: str,
    feature: str,
    version: str,
    status: str,
    reason: str,
    minimal_hud: dict[str, Any],
    context_text: str,
    parse_error: str = "",
    render_error: str = "",
) -> Path:
    run_dir = debug_root(project_root) / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "codex-fixed-hud.jsonl"
    record = {
        "ts": now_iso(),
        "hook_event_name": hook_event_name,
        "session_id": str(payload.get("session_id", payload.get("sessionId", "")) or ""),
        "thread_id": str(payload.get("thread_id", payload.get("threadId", "")) or ""),
        "turn_id": str(payload.get("turn_id", payload.get("turnId", "")) or ""),
        "transcript_path": str(payload.get("transcript_path", payload.get("transcriptPath", "")) or ""),
        "feature": feature,
        "version": version,
        "status": status,
        "reason": reason,
        "minimal_hud": minimal_hud,
        "additional_context": context_text,
        "parse_error": parse_error,
        "render_error": render_error,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def _sync_prompt_history_into_debug(
    project_root: Path,
    *,
    run_id: str,
    limit: int = 0,
) -> dict[str, Any]:
    rows = load_prompt_router_history(project_root, limit=limit)
    imported = 0
    target_path = debug_feedback_path(project_root, run_id)
    for row in rows:
        goal = str(row.get("input_goal", "")).strip()
        if not goal:
            continue
        _, target_path, event_payload = append_debug_feedback_event(
            project_root,
            run_id=run_id,
            source="debug.sync.prompt-history",
            goal=goal,
            intent=str(row.get("intent", "think") or "think"),
            confidence=_to_float(row.get("confidence"), 0.0),
            boundary_state=str(row.get("boundary_state", "unknown") or "unknown"),
            block_reason=str(row.get("block_reason", "") or ""),
            recommended_command=str(row.get("recommended_command", "") or ""),
            executed=bool(row.get("execute_requested", False)),
            exit_code=(
                int(row.get("execute_exit_code"))
                if row.get("execute_exit_code") is not None
                else None
            ),
            note="imported-from-prompt-router-history",
            extra={"history_ts": str(row.get("ts", "") or "")},
        )
        append_debug_event_memory(
            project_root,
            run_id=run_id,
            event_payload=event_payload,
            evidence_path=target_path,
            source="debug.sync.prompt-history",
        )
        imported += 1
    return {
        "run_id": run_id,
        "imported": imported,
        "path": str(target_path.relative_to(project_root)),
        "history_path": str(prompt_router_history_path(project_root).relative_to(project_root)),
    }


@app.command()
def watch(
    run_id: str = typer.Argument("", help="Run ID"),
    tail: int = typer.Option(20, "--tail", "-n", help="Tail lines"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow mode"),
    poll_interval: float = typer.Option(0.2, "--poll-interval", help="Polling interval seconds"),
    idle_exit: float = typer.Option(2.0, "--idle-exit", help="Exit after idle seconds (<=0 never exits)"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Watch run events."""
    root = Path(project_root) if project_root else Path.cwd()
    target_run = run_id or newest_run_id(root)
    if not target_run:
        typer.echo("No run found.", err=True)
        raise typer.Exit(code=2)

    events_file = run_events_path(root, target_run)
    if not events_file.exists():
        typer.echo(f"No events for run: {target_run}", err=True)
        raise typer.Exit(code=2)

    lines = events_file.read_text(encoding="utf-8").splitlines()
    tail_lines = lines[-tail:] if tail > 0 else lines
    for line in tail_lines:
        typer.echo(line)

    if not follow:
        return

    consumed = len(lines)
    idle_for = 0.0
    while True:
        time.sleep(max(poll_interval, 0.05))
        latest = events_file.read_text(encoding="utf-8").splitlines()
        if len(latest) > consumed:
            for line in latest[consumed:]:
                typer.echo(line)
            consumed = len(latest)
            idle_for = 0.0
            continue

        idle_for += max(poll_interval, 0.05)
        if idle_exit > 0 and idle_for >= idle_exit:
            break


@app.command("status")
def debug_status(
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Show debug mode state."""
    root = Path(project_root) if project_root else Path.cwd()
    state = load_debug_mode_state(root)
    run_id = str(state.get("run_id", "") or "") or resolve_debug_run_id(root, run_id="")
    config = _load_router_config(root)
    resume_contract = build_resume_contract(root, run_id=run_id)
    payload = {
        "enabled": bool(state.get("enabled", False)),
        "run_id": run_id,
        "debug_feedback_path": str(debug_feedback_path(root, run_id).relative_to(root)),
        "prompt_history_path": str(prompt_router_history_path(root).relative_to(root)),
        "confidence_threshold": round(_to_float(config.get("confidence_threshold"), DEFAULT_CONFIDENCE_THRESHOLD), 2),
        "exhaustion": exhaustion_for_run(root, run_id=run_id),
        "resume_contract": resume_contract,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon Debug Status")
    typer.echo(f"- enabled: {payload['enabled']}")
    typer.echo(f"- run_id: {payload['run_id']}")
    typer.echo(f"- debug_feedback_path: {payload['debug_feedback_path']}")
    typer.echo(f"- prompt_history_path: {payload['prompt_history_path']}")
    typer.echo(f"- confidence_threshold: {payload['confidence_threshold']}")


@app.command("enable")
def enable_debug_mode(
    run_id: str = typer.Option("", "--run-id", help="Debug run id (default auto-resolve)"),
    sync_history: bool = typer.Option(
        True,
        "--sync-history/--no-sync-history",
        help="Sync prompt router history into debug feedback & memory on enable.",
    ),
    history_limit: int = typer.Option(
        0,
        "--history-limit",
        min=0,
        help="Only sync latest N prompt history entries (0 = all).",
    ),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Enable debug mode for prompt capture."""
    root = Path(project_root) if project_root else Path.cwd()
    target_run_id = resolve_debug_run_id(root, run_id=run_id)
    state = save_debug_mode_state(
        root,
        enabled=True,
        run_id=target_run_id,
        source="debug.enable",
    )
    sync_payload = {"imported": 0}
    if sync_history:
        sync_payload = _sync_prompt_history_into_debug(root, run_id=target_run_id, limit=history_limit)
    payload = {
        "status": "enabled",
        "state": state,
        "sync": sync_payload,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("✓ Debug mode enabled")
    typer.echo(f"- run_id: {target_run_id}")
    typer.echo(f"- sync.imported: {sync_payload.get('imported', 0)}")
    typer.echo(f"- debug_feedback: {sync_payload.get('path', str(debug_feedback_path(root, target_run_id).relative_to(root)))}")


@app.command("disable")
def disable_debug_mode(
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Disable debug mode prompt capture."""
    root = Path(project_root) if project_root else Path.cwd()
    current = load_debug_mode_state(root)
    state = save_debug_mode_state(
        root,
        enabled=False,
        run_id=str(current.get("run_id", "") or ""),
        source="debug.disable",
    )
    if json_output:
        typer.echo(json.dumps({"status": "disabled", "state": state}, ensure_ascii=False, indent=2))
        return
    typer.echo("✓ Debug mode disabled")
    typer.echo(f"- run_id: {state.get('run_id', '')}")


@app.command("sync-prompts")
def sync_prompts(
    run_id: str = typer.Option("", "--run-id", help="Debug run id (default auto-resolve)"),
    limit: int = typer.Option(0, "--limit", min=0, help="Sync latest N entries only (0 = all)."),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Sync prompt router history into debug feedback and memory."""
    root = Path(project_root) if project_root else Path.cwd()
    target_run_id = resolve_debug_run_id(root, run_id=run_id)
    payload = _sync_prompt_history_into_debug(root, run_id=target_run_id, limit=limit)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("✓ Prompt history synced to debug feedback")
    typer.echo(f"- run_id: {payload['run_id']}")
    typer.echo(f"- imported: {payload['imported']}")
    typer.echo(f"- path: {payload['path']}")


@app.command("input-audit")
def input_audit(
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    limit: int = typer.Option(20, "--limit", min=0, help="Read latest N audit events (0 = all)."),
    source: str = typer.Option("", "--source", help="Filter by source, e.g. ask/prompt.optimize/codex.user-prompt-submit"),
    hook_event_name: str = typer.Option("", "--hook-event-name", help="Filter by hook event name"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Inspect structured user-input audit events."""
    root = Path(project_root) if project_root else Path.cwd()
    rows = load_user_input_audit(root, limit=limit, source=source, hook_event_name=hook_event_name)
    payload = {
        "path": str(user_input_audit_path(root).relative_to(root)),
        "count": len(rows),
        "events": rows,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon Input Audit")
    typer.echo(f"- path: {payload['path']}")
    typer.echo(f"- count: {payload['count']}")
    for row in rows[-min(len(rows), 10):]:
        typer.echo(
            f"- {row.get('ts', '')} source={row.get('source', '')} intent={row.get('intent', '')} prompt={row.get('input_goal', '')}"
        )


@app.command("codex-user-prompt-submit")
def codex_user_prompt_submit(
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    version: str = typer.Option("auto", "--version", help="Docs version used for prompt adaptation"),
    router_mode: str = typer.Option("auto", "--router-mode", help="Intent router mode"),
    run_id: str = typer.Option("", "--run-id", help="Debug run id (default auto-resolve)"),
    payload_json: str = typer.Option("", "--payload-json", help="Inline hook JSON payload"),
    json_output: bool = typer.Option(True, "--json/--no-json", help="Emit hook JSON output"),
):
    """Adapt Codex UserPromptSubmit payloads into Beacon prompt guidance."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = _load_hook_payload(payload_json)
    hook_event_name = _read_codex_hook_event_name(payload)
    prompt = _read_codex_prompt_text(payload)

    if hook_event_name != "UserPromptSubmit":
        result = {
            "status": "ignored",
            "reason": "unsupported_hook_event",
            "hook_event_name": hook_event_name,
        }
        if json_output:
            typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
            return
        typer.echo("Ignored: unsupported hook event")
        return

    if not prompt:
        raise typer.BadParameter("UserPromptSubmit payload missing prompt/input/user_prompt/text")

    resolved_version = resolve_target_version(root, version)
    plan = optimize_prompt_to_plan(
        prompt,
        project_root=root,
        version=resolved_version,
        requested_version=version,
        router_mode=router_mode,
    )
    adaptation = build_prompt_adaptation_pack(
        prompt,
        plan=plan,
        project_root=root,
        version=resolved_version,
    )

    history_event = {
        "ts": now_iso(),
        "source": "codex.user-prompt-submit",
        "hook_event_name": hook_event_name,
        "input_goal": prompt,
        "intent": plan.get("intent", ""),
        "confidence": plan.get("confidence", 0.0),
        "router_mode": plan.get("router_mode", "rule"),
        "boundary_state": str(plan.get("boundary", {}).get("state", "in_scope") or "in_scope"),
        "recommended_command": plan.get("recommended_command", ""),
        "execute_requested": False,
        "execute_blocked": False,
        "block_reason": _prompt_block_reason(plan),
        "execute_exit_code": None,
        "session_id": str(payload.get("session_id", payload.get("sessionId", "")) or ""),
        "thread_id": str(payload.get("thread_id", payload.get("threadId", "")) or ""),
        "turn_id": str(payload.get("turn_id", payload.get("turnId", "")) or ""),
        "transcript_path": str(payload.get("transcript_path", payload.get("transcriptPath", "")) or ""),
        "normalized_prompt": adaptation.get("normalized_prompt", ""),
        "needs_clarification": bool(adaptation.get("needs_clarification", False)),
    }
    history_path = append_prompt_router_history(root, history_event)
    input_audit_path = append_user_input_audit(
        root,
        {
            "ts": history_event["ts"],
            "source": "codex.user-prompt-submit",
            "channel": "hook",
            "hook_event_name": hook_event_name,
            "input_goal": prompt,
            "raw_prompt": prompt,
            "normalized_prompt": str(adaptation.get("normalized_prompt", "") or ""),
            "intent": plan.get("intent", ""),
            "confidence": plan.get("confidence", 0.0),
            "boundary_state": str(plan.get("boundary", {}).get("state", "in_scope") or "in_scope"),
            "recommended_command": plan.get("recommended_command", ""),
            "recommended_args": list(plan.get("recommended_args", [])),
            "router_mode": plan.get("router_mode", "rule"),
            "execute_requested": False,
            "execute_blocked": False,
            "block_reason": _prompt_block_reason(plan),
            "execute_exit_code": None,
            "session_id": str(payload.get("session_id", payload.get("sessionId", "")) or ""),
            "thread_id": str(payload.get("thread_id", payload.get("threadId", "")) or ""),
            "turn_id": str(payload.get("turn_id", payload.get("turnId", "")) or ""),
            "transcript_path": str(payload.get("transcript_path", payload.get("transcriptPath", "")) or ""),
        },
    )

    target_run_id, feedback_path, debug_event = append_debug_feedback_event(
        root,
        run_id=run_id or None,
        source="debug.codex.user-prompt-submit",
        goal=prompt,
        intent=str(plan.get("intent", "")),
        confidence=float(plan.get("confidence", 0.0) or 0.0),
        boundary_state=str(plan.get("boundary", {}).get("state", "in_scope") or "in_scope"),
        block_reason=_prompt_block_reason(plan),
        recommended_command=str(plan.get("recommended_command", "")),
        executed=False,
        note="captured-from-codex-userpromptsubmit-hook",
        extra={
            "hook_event_name": hook_event_name,
            "session_id": str(payload.get("session_id", payload.get("sessionId", "")) or ""),
            "thread_id": str(payload.get("thread_id", payload.get("threadId", "")) or ""),
            "turn_id": str(payload.get("turn_id", payload.get("turnId", "")) or ""),
            "transcript_path": str(payload.get("transcript_path", payload.get("transcriptPath", "")) or ""),
            "raw_prompt": prompt,
            "normalized_prompt": str(adaptation.get("normalized_prompt", "") or ""),
            "missing_fields": list(adaptation.get("missing_fields", [])),
            "normalize_actions": list(adaptation.get("normalize_actions", [])),
            "suggested_capability": "codex-userpromptsubmit-prompt-adaptation",
            "candidate_doc_slug": "beacon-v121-codex-userpromptsubmit-debug-guidance",
        },
    )
    append_debug_event_memory(
        root,
        run_id=target_run_id,
        event_payload=debug_event,
        evidence_path=feedback_path,
        source="debug.codex.user-prompt-submit",
    )
    snapshot_path = _append_codex_hook_snapshot(
        root,
        run_id=target_run_id,
        payload=payload,
        plan=plan,
        adaptation=adaptation,
    )

    result = {
        "status": "captured",
        "hook_event_name": hook_event_name,
        "version": resolved_version,
        "plan": plan,
        "prompt_adaptation": adaptation,
        "debug_feedback": {
            "run_id": target_run_id,
            "path": str(feedback_path.relative_to(root)),
        },
        "history_path": str(history_path.relative_to(root)),
        "input_audit_path": str(input_audit_path.relative_to(root)),
        "snapshot_path": str(snapshot_path.relative_to(root)),
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": str(adaptation.get("assistant_context", "") or ""),
        },
    }
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon Codex UserPromptSubmit adapter")
    typer.echo(f"- intent: {plan.get('intent', '')}")
    typer.echo(f"- boundary: {adaptation.get('boundary_state', '')}")
    typer.echo(f"- command: {plan.get('recommended_command', '')}")
    typer.echo(f'- normalized_prompt: {adaptation.get("normalized_prompt", "")}')


@app.command("codex-fixed-hud")
def codex_fixed_hud(
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    version: str = typer.Option("auto", "--version", help="Docs version used for fixed HUD rendering"),
    feature: str = typer.Option("", "--feature", help="Feature slug override for HUD context"),
    run_id: str = typer.Option("", "--run-id", help="Debug run id (default auto-resolve)"),
    payload_json: str = typer.Option("", "--payload-json", help="Inline hook JSON payload"),
    fallback_hook_event: str = typer.Option(
        "UserPromptSubmit",
        "--fallback-hook-event",
        help="Fallback hook event when payload is empty/invalid",
    ),
    json_output: bool = typer.Option(True, "--json/--no-json", help="Emit hook JSON output"),
):
    """Render fixed Beacon HUD for Codex hook events without blocking user input on failures."""
    root = Path(project_root) if project_root else Path.cwd()

    payload: dict[str, Any] = {}
    parse_error = ""
    try:
        payload = _load_hook_payload(payload_json)
    except typer.BadParameter as exc:
        parse_error = str(exc)

    hook_event_name = (_read_codex_hook_event_name(payload) or str(fallback_hook_event or "").strip() or "UserPromptSubmit").strip()
    if hook_event_name not in HUD_HOOK_SUPPORTED_EVENTS:
        result = {
            "status": "ignored",
            "reason": "unsupported_hook_event",
            "hook_event_name": hook_event_name,
            "supported_hook_events": sorted(HUD_HOOK_SUPPORTED_EVENTS),
            "hookSpecificOutput": {
                "hookEventName": hook_event_name or str(fallback_hook_event or "UserPromptSubmit"),
                "additionalContext": "",
            },
        }
        if json_output:
            typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
            return
        typer.echo("Ignored: unsupported hook event")
        return

    resolved_feature = str(feature or _read_codex_feature(payload) or "").strip()
    resolved_version = resolve_target_version(root, version)
    minimal_hud: dict[str, Any] = {"schema_version": "1.0", "scenario": "", "line_budget": 0, "lines": []}
    context_text = ""
    status = "captured"
    reason = ""
    render_error = ""
    hud_lines: list[str] = []

    if parse_error:
        status = "degraded"
        reason = "invalid_payload_json"
    else:
        try:
            help_payload = build_help_payload(
                root,
                version=resolved_version,
                feature=resolved_feature or None,
            )
            candidate_hud = help_payload.get("minimal_hud")
            if isinstance(candidate_hud, dict):
                minimal_hud = candidate_hud
            candidate_lines = minimal_hud.get("lines")
            hud_lines = [str(item).strip() for item in candidate_lines] if isinstance(candidate_lines, list) else []
            hud_lines = [line for line in hud_lines if line]
            context_text = _render_fixed_hud_context(hud_lines)
            if not context_text:
                status = "degraded"
                reason = "empty_hud_lines"
        except Exception as exc:  # noqa: BLE001
            status = "degraded"
            reason = "hud_render_failed"
            render_error = str(exc)
            minimal_hud = {"schema_version": "1.0", "scenario": "", "line_budget": 0, "lines": []}
            context_text = ""
            hud_lines = []

    confidence = 1.0 if status == "captured" else 0.0
    input_audit_file = append_user_input_audit(
        root,
        {
            "ts": now_iso(),
            "source": "codex.fixed-hud-hook",
            "channel": "hook",
            "hook_event_name": hook_event_name,
            "input_goal": f"codex fixed hud {hook_event_name}",
            "raw_prompt": _read_codex_prompt_text(payload),
            "normalized_prompt": "",
            "intent": "hud",
            "confidence": confidence,
            "boundary_state": "in_scope",
            "recommended_command": "",
            "recommended_args": [],
            "router_mode": "hud",
            "execute_requested": False,
            "execute_blocked": status != "captured",
            "block_reason": reason,
            "execute_exit_code": None,
            "session_id": str(payload.get("session_id", payload.get("sessionId", "")) or ""),
            "thread_id": str(payload.get("thread_id", payload.get("threadId", "")) or ""),
            "turn_id": str(payload.get("turn_id", payload.get("turnId", "")) or ""),
            "transcript_path": str(payload.get("transcript_path", payload.get("transcriptPath", "")) or ""),
            "feature": resolved_feature,
            "hud_scenario": str(minimal_hud.get("scenario", "") or ""),
            "hud_line_budget": len(hud_lines),
        },
    )
    target_run_id, feedback_path, debug_event = append_debug_feedback_event(
        root,
        run_id=run_id or None,
        source="debug.codex.fixed-hud-hook",
        goal=f"render fixed hud for {hook_event_name}",
        intent="hud",
        confidence=confidence,
        boundary_state="in_scope",
        block_reason=reason,
        recommended_command="",
        executed=False,
        note="captured-from-codex-fixed-hud-hook",
        extra={
            "hook_event_name": hook_event_name,
            "feature": resolved_feature,
            "version": resolved_version,
            "hud_scenario": str(minimal_hud.get("scenario", "") or ""),
            "hud_line_budget": len(hud_lines),
            "status": status,
            "parse_error": parse_error,
            "render_error": render_error,
        },
    )
    append_debug_event_memory(
        root,
        run_id=target_run_id,
        event_payload=debug_event,
        evidence_path=feedback_path,
        source="debug.codex.fixed-hud-hook",
    )
    snapshot_path = _append_codex_fixed_hud_snapshot(
        root,
        run_id=target_run_id,
        payload=payload,
        hook_event_name=hook_event_name,
        feature=resolved_feature,
        version=resolved_version,
        status=status,
        reason=reason,
        minimal_hud=minimal_hud,
        context_text=context_text,
        parse_error=parse_error,
        render_error=render_error,
    )
    activation_source = str(os.environ.get(HUD_HOOK_ACTIVATION_SOURCE_ENV, "") or "").strip()
    activation_record = record_codex_hud_hook_activation(
        root,
        hook_event_name=hook_event_name,
        payload=payload,
        feature=resolved_feature,
        version=resolved_version,
        status=status,
        reason=reason,
        activation_source=activation_source,
        additional_context=context_text,
        minimal_hud=minimal_hud,
    )

    result = {
        "status": status,
        "reason": reason,
        "hook_event_name": hook_event_name,
        "feature": resolved_feature,
        "version": resolved_version,
        "minimal_hud": minimal_hud,
        "debug_feedback": {
            "run_id": target_run_id,
            "path": str(feedback_path.relative_to(root)),
        },
        "input_audit_path": str(input_audit_file.relative_to(root)),
        "snapshot_path": str(snapshot_path.relative_to(root)),
        "runtime_activation_path": activation_record["state_path"],
        "runtime_activation_log_path": activation_record["log_path"],
        "hookSpecificOutput": {
            "hookEventName": hook_event_name,
            "additionalContext": context_text,
        },
    }
    if parse_error:
        result["parse_error"] = parse_error
    if render_error:
        result["render_error"] = render_error

    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon Codex fixed HUD hook")
    typer.echo(f"- status: {status}")
    if reason:
        typer.echo(f"- reason: {reason}")
    typer.echo(f"- hook_event_name: {hook_event_name}")
    typer.echo(f"- feature: {resolved_feature or '<empty>'}")
    typer.echo(f"- version: {resolved_version}")
    if context_text:
        typer.echo(context_text)
    else:
        typer.echo("(empty HUD context)")


@app.command("project-feed")
def project_feed(
    feature: str = typer.Argument("", help="Optional feature slug filter"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Show canonical project-facing debug feedback events."""
    root = Path(project_root) if project_root else Path.cwd()
    debug_index = debug_index_path(root)
    payload = {"root": str(debug_root(root).relative_to(root)), "feature": feature, "runs": []}
    if debug_index.exists():
        try:
            loaded = json.loads(debug_index.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            loaded = {}
        if isinstance(loaded, dict):
            payload["runs"] = list(loaded.get("runs", []))
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("Beacon Debug Project Feed")
    typer.echo(f"- root: {payload['root']}")
    typer.echo(f"- runs: {len(payload['runs'])}")


@app.command("harvest")
def harvest(
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Harvest canonical debug events into issue records."""
    root = Path(project_root) if project_root else Path.cwd()
    runs_root = debug_root(root) / "runs"
    issues_root = debug_issues_dir(root)
    issues_root.mkdir(parents=True, exist_ok=True)
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for events_path in sorted(runs_root.glob("*/events.jsonl")) if runs_root.exists() else []:
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if not isinstance(event, dict):
                continue
            key = (
                str(event.get("feedback_target", "beacon-core") or "beacon-core"),
                str(event.get("reason_code", "runtime_feedback") or "runtime_feedback"),
            )
            groups.setdefault(key, []).append(event)
    issues = []
    for (target, reason_code), events in sorted(groups.items()):
        issue_id = f"{target}--{reason_code}".replace("/", "-")
        payload = {
            "schema_version": "1.0",
            "issue_id": issue_id,
            "feedback_target": target,
            "reason_code": reason_code,
            "count": len(events),
            "latest_event_at": str(events[-1].get("ts", "") if events else ""),
            "sample": str(events[0].get("friction_summary", "") if events else ""),
            "suggested_capability": str(events[0].get("suggested_capability", "") if events else ""),
            "run_ids": sorted({str(item.get("run_id", "")) for item in events if str(item.get("run_id", ""))}),
        }
        path = issues_root / f"{issue_id}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        issues.append(payload)
    index_payload = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "issue_count": len(issues),
        "issues": issues,
    }
    learning_payload = refresh_learning_loop(root)
    index_payload["learning"] = learning_payload
    write_json(debug_index_path(root), {**(json.loads(debug_index_path(root).read_text(encoding="utf-8")) if debug_index_path(root).exists() else {}), "issues": issues, "issue_count": len(issues), "generated_at": now_iso()})
    if json_output:
        typer.echo(json.dumps(index_payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Debug issues harvested: {len(issues)}")
    typer.echo(f"- learning.execution_baseline: {learning_payload.get('execution_baseline')}")


@app.command("export-ideas")
def export_ideas(
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Export harvested issues into markdown idea seeds."""
    root = Path(project_root) if project_root else Path.cwd()
    issues_root = debug_issues_dir(root)
    ideas_root = debug_ideas_dir(root)
    ideas_root.mkdir(parents=True, exist_ok=True)
    idea_paths: list[str] = []
    for issue_file in sorted(issues_root.glob("*.json")) if issues_root.exists() else []:
        try:
            issue = json.loads(issue_file.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(issue, dict):
            continue
        idea_path = ideas_root / f"{issue_file.stem}.md"
        idea_path.write_text(
            "\n".join(
                [
                    f"# {issue.get('issue_id', issue_file.stem)}",
                    "",
                    f"- feedback_target: `{issue.get('feedback_target', '')}`",
                    f"- reason_code: `{issue.get('reason_code', '')}`",
                    f"- count: `{issue.get('count', 0)}`",
                    "",
                    "## Sample Friction",
                    str(issue.get("sample", "")),
                    "",
                    "## Suggested Capability",
                    str(issue.get("suggested_capability", "")),
                    "",
                    "## Run IDs",
                    *[f"- `{run_id}`" for run_id in issue.get("run_ids", []) if str(run_id).strip()],
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        idea_paths.append(str(idea_path.relative_to(root)))
    payload = {"idea_count": len(idea_paths), "ideas": idea_paths}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Debug ideas exported: {len(idea_paths)}")


@app.command("capture")
def capture_prompt(
    goal: str = typer.Argument(..., help="Prompt goal text to capture"),
    intent: str = typer.Option("think", "--intent", help="Resolved intent"),
    confidence: float = typer.Option(0.5, "--confidence", help="Prompt confidence (0~1)"),
    boundary_state: str = typer.Option("in_scope", "--boundary-state", help="Boundary state"),
    block_reason: str = typer.Option("", "--block-reason", help="Execution block reason"),
    recommended_command: str = typer.Option("", "--recommended-command", help="Recommended command"),
    note: str = typer.Option("", "--note", help="Capture note"),
    run_id: str = typer.Option("", "--run-id", help="Debug run id"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Capture one prompt event into debug feedback + memory."""
    root = Path(project_root) if project_root else Path.cwd()
    target_run_id, out_path, payload = append_debug_feedback_event(
        root,
        run_id=run_id or None,
        source="debug.capture",
        goal=goal,
        intent=intent,
        confidence=max(0.0, min(1.0, confidence)),
        boundary_state=boundary_state,
        block_reason=block_reason,
        recommended_command=recommended_command,
        note=note,
    )
    append_debug_event_memory(
        root,
        run_id=target_run_id,
        event_payload=payload,
        evidence_path=out_path,
        source="debug.capture",
    )
    if block_reason.strip():
        record_stage_failure(
            root,
            run_id=target_run_id,
            stage=intent or "debug",
            attempted_strategy=recommended_command or intent or "debug.capture",
            reason_code=block_reason,
            current_blocker=note or goal,
            recommended_command=recommended_command,
            details={"source": "debug.capture"},
        )
    result = {
        "run_id": target_run_id,
        "path": str(out_path.relative_to(root)),
        "captured": 1,
    }
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    typer.echo("✓ Prompt captured into debug feedback")
    typer.echo(f"- run_id: {result['run_id']}")
    typer.echo(f"- path: {result['path']}")


@checkpoint_app.command("save")
def checkpoint_save(
    run_id: str = typer.Argument(..., help="Workflow/debug run id"),
    stage: str = typer.Option("debug", "--stage", help="Stage name"),
    attempted_strategy: str = typer.Option("", "--attempted-strategy", help="Current attempted strategy"),
    excluded_cause: Optional[list[str]] = typer.Option(None, "--excluded-cause", help="Excluded cause (repeatable)"),
    next_hypothesis: str = typer.Option("", "--next-hypothesis", help="Next hypothesis"),
    evidence_gap: Optional[list[str]] = typer.Option(None, "--evidence-gap", help="Evidence gap (repeatable)"),
    current_blocker: str = typer.Option("", "--current-blocker", help="Current blocker summary"),
    reason_code: str = typer.Option("", "--reason-code", help="Reason code"),
    recommended_command: str = typer.Option("", "--recommended-command", help="Recommended next command"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Persist a structured recovery checkpoint."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = append_recovery_checkpoint(
        root,
        run_id=run_id,
        stage=stage,
        attempted_strategy=attempted_strategy or stage,
        excluded_causes=list(excluded_cause or []),
        next_hypothesis=next_hypothesis,
        evidence_gap=list(evidence_gap or []),
        current_blocker=current_blocker,
        reason_code=reason_code,
        recommended_command=recommended_command,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Checkpoint saved: {payload['checkpoint_id']}")
    typer.echo(f"- path: {payload['path']}")


@checkpoint_app.command("show")
def checkpoint_show(
    run_id: str = typer.Argument("", help="Run id (default latest)"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Show the latest recovery checkpoint."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = load_recovery_checkpoint(root, run_id=run_id or None)
    if not payload:
        typer.echo("No checkpoint found.", err=True)
        raise typer.Exit(2)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@exhaustion_app.command("show")
def exhaustion_show(
    run_id: str = typer.Argument("", help="Run id (default latest)"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Show failure streak / escalation state for a run."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = exhaustion_for_run(root, run_id=run_id or None)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command("recover")
def recover(
    run_id: str = typer.Argument("", help="Run id (default latest)"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Render the structured resume contract used by v1.1.9 control plane."""
    root = Path(project_root) if project_root else Path.cwd()
    payload = build_resume_contract(root, run_id=run_id or None)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@confidence_app.command("show")
def show_confidence(
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Show current router confidence threshold."""
    root = Path(project_root) if project_root else Path.cwd()
    config = _load_router_config(root)
    threshold = round(_to_float(config.get("confidence_threshold"), DEFAULT_CONFIDENCE_THRESHOLD), 2)
    payload = {
        "confidence_threshold": threshold,
        "config_path": str(_router_config_path(root).relative_to(root)),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"confidence_threshold: {threshold}")
    typer.echo(f"config_path: {payload['config_path']}")


@confidence_app.command("set")
def set_confidence(
    threshold: float = typer.Argument(..., help="Confidence threshold (0~1)"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Set default router confidence threshold."""
    root = Path(project_root) if project_root else Path.cwd()
    normalized = max(0.0, min(1.0, float(threshold)))
    config = _load_router_config(root)
    config["confidence_threshold"] = round(normalized, 2)
    path = _save_router_config(root, config)
    payload = {
        "confidence_threshold": config["confidence_threshold"],
        "config_path": str(path.relative_to(root)),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("✓ confidence threshold updated")
    typer.echo(f"- confidence_threshold: {payload['confidence_threshold']}")
    typer.echo(f"- config_path: {payload['config_path']}")


if __name__ == "__main__":
    app()
