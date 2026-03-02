"""Beacon save command - Save current session"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime
import json

app = typer.Typer(name="save", help="Save current session state")


@app.command()
def run(
    name: Optional[str] = typer.Argument(None, help="Session name (optional, defaults to timestamp)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """Save current session state"""
    project_root = Path(project) if project else Path.cwd()

    session_name = name or datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(output) if output else project_root / ".beacon" / "sessions"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Session data structure
    session_data = {
        "name": session_name,
        "created_at": datetime.now().isoformat(),
        "cwd": str(project_root),
        "files": [],
        "notes": "",
    }

    # Try to gather current context
    git_dir = project_root / ".git"
    if git_dir.exists():
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                session_data["branch"] = result.stdout.strip()
        except Exception:
            pass

    output_file = output_dir / f"{session_name}.json"
    output_file.write_text(json.dumps(session_data, indent=2, ensure_ascii=False))

    typer.echo(f"✓ Session saved: {session_name}")
    typer.echo(f"  Location: {output_file}")


if __name__ == "__main__":
    app()
