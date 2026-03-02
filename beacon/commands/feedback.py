"""Beacon feedback command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.runtime import load_run_state, newest_run_id, now_iso, write_json

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
    typer.echo(f"Syncing feedback for run: {target}")
    typer.echo(json.dumps({"synced": str(out_file), "run_id": target}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()

