"""Beacon feedback command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.memory import append_memory_entry, load_memory_entries
from beacon.utils.runtime import load_run_state, newest_run_id, now_iso, write_json
from beacon.utils.workflow_memory import append_lifecycle_event

app = typer.Typer(name="feedback", help="Feedback operations")


@app.command()
def sync(
    run_id: str = typer.Argument("latest", help="Run ID"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Sync test feedback to requirements."""
    root = Path(project_root) if project_root else Path.cwd()
    target = run_id if run_id and run_id != "latest" else (newest_run_id(root) or "latest")
    state = load_run_state(root, target) if target != "latest" else None

    feedback_dir = root / ".beacon" / "state" / "requirement-feedback"
    feedback_dir.mkdir(parents=True, exist_ok=True)
    out_file = feedback_dir / f"{target}.json"
    payload = {
        "run_id": target,
        "status": (state or {}).get("status", "unknown"),
        "updated_at": now_iso(),
        "feedback": [
            {
                "type": "compat",
                "note": "Synced from Beacon feedback command",
            }
        ],
    }
    write_json(out_file, payload)

    rel_feedback_path = str(out_file.relative_to(root))
    assimilated = 0
    existing = load_memory_entries(root)
    existing_keys = {
        (
            str(item.get("source_session_id", "")),
            str(item.get("source", "")),
            str(item.get("content", "")),
        )
        for item in existing
        if isinstance(item, dict)
    }
    for row in payload.get("feedback", []):
        if not isinstance(row, dict):
            continue
        note = str(row.get("note", "")).strip()
        if not note:
            continue
        content = f"[feedback:{target}] {note}"
        key = (target, "feedback.sync", content)
        if key in existing_keys:
            continue
        append_memory_entry(
            project_root=root,
            mem_type="insight",
            text=content,
            source_session_id=target,
            source="feedback.sync",
            evidence_ref=[rel_feedback_path],
            confidence=0.7,
            tags=["feedback", "workflow-loop"],
        )
        existing_keys.add(key)
        assimilated += 1
    if assimilated > 0:
        append_lifecycle_event(
            root,
            run_id=target,
            stage="feedback",
            event="feedback_memory_assimilated",
            source="feedback.sync",
            evidence_ref=[rel_feedback_path],
            details={"count": assimilated},
        )

    typer.echo(f"Syncing feedback for run: {target}")
    typer.echo(
        json.dumps(
            {"synced": str(out_file), "run_id": target, "memory_assimilated": assimilated},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    app()
