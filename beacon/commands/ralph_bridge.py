"""Beacon ralph-bridge command - Ralph bridge for OMC integration"""
import typer
from typing import Optional
from pathlib import Path
import json
from datetime import datetime

from beacon.utils.memory import append_memory_entry
from beacon.utils.workflow_memory import append_lifecycle_event

app = typer.Typer(name="ralph-bridge", help="Ralph bridge for OMC integration")


RALPH_STATE_FILE = "ralph-bridge.json"


def get_ralph_path(project_root: Path) -> Path:
    """Get Ralph bridge state file path"""
    return project_root / ".beacon" / RALPH_STATE_FILE


def load_ralph_state(project_root: Path) -> dict:
    """Load Ralph bridge state"""
    ralph_path = get_ralph_path(project_root)
    if ralph_path.exists():
        return json.loads(ralph_path.read_text())
    return {
        "active": False,
        "mode": "work",
        "started_at": None,
        "sessions": [],
    }


def save_ralph_state(project_root: Path, state: dict):
    """Save Ralph bridge state"""
    ralph_path = get_ralph_path(project_root)
    ralph_path.parent.mkdir(parents=True, exist_ok=True)
    ralph_path.write_text(json.dumps(state, indent=2, ensure_ascii=False))


@app.command()
def start(
    mode: str = typer.Argument("work", help="Ralph mode: work/plan/review"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Start Ralph bridge"""
    project_root = Path(project) if project else Path.cwd()
    state = load_ralph_state(project_root)

    if state["active"]:
        typer.echo("Ralph bridge is already active")
        typer.echo(f"  Mode: {state.get('mode', 'N/A')}")
        raise typer.Exit(1)

    valid_modes = ["work", "plan", "review", "ultrawork", "ralph"]
    if mode not in valid_modes:
        typer.echo(f"Invalid mode. Valid modes: {', '.join(valid_modes)}")
        raise typer.Exit(1)

    state["active"] = True
    state["mode"] = mode
    state["started_at"] = datetime.now().isoformat()

    save_ralph_state(project_root, state)
    append_memory_entry(
        project_root=project_root,
        mem_type="insight",
        text=f"[ralph-bridge.start] mode={mode}",
        source_session_id="ralph-bridge",
        source="ralph-bridge.start",
        evidence_ref=[str(get_ralph_path(project_root).relative_to(project_root))],
        confidence=0.7,
        tags=["ralph-bridge", "workflow-loop"],
    )
    append_lifecycle_event(
        project_root,
        run_id="ralph-bridge",
        stage="ralph-bridge",
        event="bridge_decision_recorded",
        source="ralph-bridge.start",
        evidence_ref=[str(get_ralph_path(project_root).relative_to(project_root))],
        details={"mode": mode, "active": True},
    )

    typer.echo(f"✓ Ralph bridge started")
    typer.echo(f"  Mode: {mode}")
    typer.echo(f"  Time: {state['started_at']}")
    typer.echo(f"\nRalph is now active. Use 'beacon ralph-bridge status' to monitor.")


@app.command()
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Show Ralph bridge status"""
    project_root = Path(project) if project else Path.cwd()
    state = load_ralph_state(project_root)

    if not state["active"]:
        typer.echo("Ralph bridge is not active")
        return

    typer.echo("Ralph Bridge Status:")
    typer.echo(f"  Active: Yes")
    typer.echo(f"  Mode: {state.get('mode', 'N/A')}")
    typer.echo(f"  Started: {state.get('started_at', 'N/A')}")

    sessions = state.get("sessions", [])
    if sessions:
        typer.echo(f"\n  Sessions ({len(sessions)}):")
        for s in sessions:
            typer.echo(f"    - {s.get('name', 'N/A')} ({s.get('status', 'unknown')})")


@app.command()
def stop(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Stop Ralph bridge"""
    project_root = Path(project) if project else Path.cwd()
    state = load_ralph_state(project_root)

    if not state["active"]:
        typer.echo("Ralph bridge is not active")
        return

    state["active"] = False
    state["ended_at"] = datetime.now().isoformat()
    save_ralph_state(project_root, state)
    append_memory_entry(
        project_root=project_root,
        mem_type="decision",
        text="[ralph-bridge.stop] bridge stopped",
        source_session_id="ralph-bridge",
        source="ralph-bridge.stop",
        evidence_ref=[str(get_ralph_path(project_root).relative_to(project_root))],
        confidence=0.8,
        tags=["ralph-bridge", "workflow-loop"],
    )
    append_lifecycle_event(
        project_root,
        run_id="ralph-bridge",
        stage="ralph-bridge",
        event="bridge_decision_recorded",
        source="ralph-bridge.stop",
        evidence_ref=[str(get_ralph_path(project_root).relative_to(project_root))],
        details={"active": False},
    )

    typer.echo("✓ Ralph bridge stopped")


if __name__ == "__main__":
    app()
