"""Beacon team command - Team collaboration"""
import typer
from typing import Optional
from pathlib import Path
import json
from datetime import datetime

app = typer.Typer(name="team", help="Team collaboration management")


TEAM_STATE_FILE = "team-state.json"


def get_team_path(project_root: Path) -> Path:
    """Get team state file path"""
    return project_root / ".beacon" / TEAM_STATE_FILE


def load_team_state(project_root: Path) -> dict:
    """Load team state"""
    team_path = get_team_path(project_root)
    if team_path.exists():
        return json.loads(team_path.read_text())
    return {
        "active": False,
        "tasks": [],
        "started_at": None,
    }


def save_team_state(project_root: Path, state: dict):
    """Save team state"""
    team_path = get_team_path(project_root)
    team_path.parent.mkdir(parents=True, exist_ok=True)
    team_path.write_text(json.dumps(state, indent=2, ensure_ascii=False))


@app.command()
def start(
    task: str = typer.Argument(..., help="Team task description"),
    members: Optional[int] = typer.Option(3, "--members", "-m", help="Number of team members"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Start a team task"""
    project_root = Path(project) if project else Path.cwd()
    state = load_team_state(project_root)

    if state["active"]:
        typer.echo("Team is already active")
        typer.echo(f"  Task: {state.get('current_task', 'unknown')}")
        raise typer.Exit(1)

    state["active"] = True
    state["current_task"] = task
    state["members"] = members
    state["started_at"] = datetime.now().isoformat()
    state["tasks"] = [
        {"id": i + 1, "description": f"Task {i + 1}", "status": "pending"}
        for i in range(members)
    ]

    save_team_state(project_root, state)

    typer.echo(f"✓ Team task started")
    typer.echo(f"  Task: {task}")
    typer.echo(f"  Members: {members}")
    typer.echo(f"  Time: {state['started_at']}")


@app.command()
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Show team status"""
    project_root = Path(project) if project else Path.cwd()
    state = load_team_state(project_root)

    if not state["active"]:
        typer.echo("No active team task")
        return

    typer.echo("Team Status:")
    typer.echo(f"  Task: {state.get('current_task', 'N/A')}")
    typer.echo(f"  Members: {state.get('members', 0)}")
    typer.echo(f"  Started: {state.get('started_at', 'N/A')}")

    tasks = state.get("tasks", [])
    if tasks:
        typer.echo(f"\n  Tasks ({len(tasks)}):")
        for t in tasks:
            status_icon = "✓" if t.get("status") == "done" else "○"
            typer.echo(f"    {status_icon} {t.get('description', 'N/A')}")


@app.command()
def stop(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Stop the team task"""
    project_root = Path(project) if project else Path.cwd()
    state = load_team_state(project_root)

    if not state["active"]:
        typer.echo("No active team task")
        return

    state["active"] = False
    state["ended_at"] = datetime.now().isoformat()
    save_team_state(project_root, state)

    typer.echo("✓ Team task stopped")


if __name__ == "__main__":
    app()
