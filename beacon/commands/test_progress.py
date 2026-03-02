"""Beacon test-progress command - Test progress tracking"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime
import json

app = typer.Typer(name="test-progress", help="Test progress tracking")


@app.command()
def show(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Show test progress"""
    project_root = Path(project) if project else Path.cwd()
    progress_file = project_root / ".beacon" / "test-progress.json"

    if not progress_file.exists():
        # Default progress
        progress_data = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "pending": 0,
            "last_updated": datetime.now().isoformat(),
        }
    else:
        progress_data = json.loads(progress_file.read_text())

    if json_output:
        typer.echo(json.dumps(progress_data, indent=2))
    else:
        typer.echo("Test Progress")
        typer.echo("=" * 40)
        typer.echo(f"Total: {progress_data.get('total', 0)}")
        typer.echo(f"Passed: {progress_data.get('passed', 0)}")
        typer.echo(f"Failed: {progress_data.get('failed', 0)}")
        typer.echo(f"Pending: {progress_data.get('pending', 0)}")

        total = progress_data.get('total', 0)
        if total > 0:
            pct = (progress_data.get('passed', 0) / total) * 100
            typer.echo(f"Completion: {pct:.1f}%")


@app.command()
def update(
    passed: int = typer.Option(0, "--passed", help="Number of passed tests"),
    failed: int = typer.Option(0, "--failed", help="Number of failed tests"),
    pending: int = typer.Option(0, "--pending", help="Number of pending tests"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Update test progress"""
    project_root = Path(project) if project else Path.cwd()

    progress_data = {
        "total": passed + failed + pending,
        "passed": passed,
        "failed": failed,
        "pending": pending,
        "last_updated": datetime.now().isoformat(),
    }

    progress_file = project_root / ".beacon" / "test-progress.json"
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    progress_file.write_text(json.dumps(progress_data, indent=2))

    typer.echo("✓ Test progress updated")
    typer.echo(f"  Passed: {passed}, Failed: {failed}, Pending: {pending}")


if __name__ == "__main__":
    app()
