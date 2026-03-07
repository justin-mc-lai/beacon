"""Beacon debug command."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import typer

from beacon.utils.debug_feedback import (
    append_debug_event_memory,
    append_debug_feedback_event,
    debug_feedback_path,
    load_debug_mode_state,
    resolve_debug_run_id,
    save_debug_mode_state,
)
from beacon.utils.intent_router import DEFAULT_CONFIDENCE_THRESHOLD, ROUTER_CONFIG_FILE
from beacon.utils.runtime import newest_run_id, run_events_path

app = typer.Typer(name="debug", help="Debug helpers")
confidence_app = typer.Typer(name="confidence", help="Prompt confidence threshold controls.")
app.add_typer(confidence_app, name="confidence")


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


def _prompt_history_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "memory" / "prompt-router-history.jsonl"


def _load_prompt_history(project_root: Path, limit: int = 0) -> list[dict[str, Any]]:
    history_path = _prompt_history_path(project_root)
    if not history_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in history_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(row, dict):
            rows.append(row)
    if limit > 0:
        return rows[-limit:]
    return rows


def _sync_prompt_history_into_debug(
    project_root: Path,
    *,
    run_id: str,
    limit: int = 0,
) -> dict[str, Any]:
    rows = _load_prompt_history(project_root, limit=limit)
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
        "history_path": str(_prompt_history_path(project_root).relative_to(project_root)),
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
    payload = {
        "enabled": bool(state.get("enabled", False)),
        "run_id": run_id,
        "debug_feedback_path": str(debug_feedback_path(root, run_id).relative_to(root)),
        "prompt_history_path": str(_prompt_history_path(root).relative_to(root)),
        "confidence_threshold": round(_to_float(config.get("confidence_threshold"), DEFAULT_CONFIDENCE_THRESHOLD), 2),
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
