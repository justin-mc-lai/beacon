"""Beacon recall command - Restore session"""
import typer
from typing import Optional
from pathlib import Path
import json

app = typer.Typer(name="recall", help="Restore saved session")


@app.command()
def run(
    name: str = typer.Argument(..., help="Session name to restore"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Restore a saved session"""
    project_root = Path(project) if project else Path.cwd()
    sessions_dir = project_root / ".beacon" / "sessions"

    if not sessions_dir.exists():
        typer.echo("No saved sessions found")
        raise typer.Exit(1)

    session_file = sessions_dir / f"{name}.json"
    if not session_file.exists():
        # Try to find by partial match
        sessions = list(sessions_dir.glob("*.json"))
        for s in sessions:
            if name in s.stem:
                session_file = s
                break

    if not session_file.exists():
        typer.echo(f"Session '{name}' not found")
        raise typer.Exit(1)

    session_data = json.loads(session_file.read_text())

    typer.echo(f"✓ Restoring session: {session_data.get('name', name)}")
    typer.echo(f"  Created: {session_data.get('created_at', 'unknown')}")
    typer.echo(f"  Working dir: {session_data.get('cwd', project_root)}")

    if "branch" in session_data:
        typer.echo(f"  Branch: {session_data['branch']}")


@app.command("list")
def _list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all saved sessions"""
    project_root = Path(project) if project else Path.cwd()
    sessions_dir = project_root / ".beacon" / "sessions"

    if not sessions_dir.exists():
        typer.echo("No saved sessions found")
        return

    sessions = list(sessions_dir.glob("*.json"))
    if not sessions:
        typer.echo("No saved sessions found")
        return

    typer.echo(f"Saved Sessions ({len(sessions)} found):")
    for session in sorted(sessions, key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            data = json.loads(session.read_text())
            created = data.get("created_at", "unknown")
            typer.echo(f"  - {session.stem}")
            typer.echo(f"    Created: {created}")
        except Exception:
            typer.echo(f"  - {session.stem}")


if __name__ == "__main__":
    app()
