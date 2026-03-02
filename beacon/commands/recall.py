"""Beacon recall command - Restore session"""
import typer
from typing import Optional
from pathlib import Path
import json

from beacon.utils.memory import load_memory_entries, normalize_memory_type, search_memory_entries

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


@app.command("memory")
def memory(
    query: str = typer.Argument("", help="Search query (empty means list recent)"),
    memory_type: str = typer.Option("", "--type", "-y", help="Filter: insight/decision/vocabulary"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Recall memory entries with source/evidence/session context."""
    project_root = Path(project) if project else Path.cwd()
    normalized_type = None
    if memory_type:
        try:
            normalized_type = normalize_memory_type(memory_type)
        except ValueError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=2)

    if query:
        results = search_memory_entries(project_root, query, mem_type=normalized_type, limit=limit)
    else:
        results = load_memory_entries(project_root, mem_type=normalized_type)[: max(0, limit)]

    if json_output:
        typer.echo(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if not results:
        typer.echo("No memory entries found")
        return

    typer.echo(f"Memory entries ({len(results)}):")
    for item in results:
        typer.echo(f"- {item.get('memory_id', '<unknown>')} [{item.get('type', 'unknown')}]")
        typer.echo(f"  content: {item.get('content', '')[:160]}")
        typer.echo(f"  source_session_id: {item.get('source_session_id', 'manual')}")
        typer.echo(f"  source: {item.get('source', 'remember')}")
        refs = item.get("evidence_ref", [])
        if isinstance(refs, list) and refs:
            typer.echo(f"  evidence_ref: {', '.join(str(x) for x in refs)}")


if __name__ == "__main__":
    app()
