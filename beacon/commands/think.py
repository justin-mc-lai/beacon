"""Beacon think command - Product thinking vNext"""
import typer
from typing import Optional
import json
from pathlib import Path
import os

from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="think", help="Product thinking vNext")


class ThinkSession:
    """Manages think vNext session state"""

    def __init__(self, project_root: Path, version: str = "v1.0.0"):
        self.project_root = project_root
        self.version = (version or "v1.0.0").strip() or "v1.0.0"
        self.state_dir = project_root / ".beacon" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.versioned_dir = self.state_dir / "think-progress"
        self.versioned_dir.mkdir(parents=True, exist_ok=True)
        self.legacy_progress_file = self.state_dir / "think-progress.json"
        self.progress_file = self.versioned_dir / f"{self.version}.json"

    def load_progress(self) -> dict:
        if self.progress_file.exists():
            return json.loads(self.progress_file.read_text())
        if self.legacy_progress_file.exists():
            return json.loads(self.legacy_progress_file.read_text())
        return {
            "round": 0,
            "confirmed_facts": [],
            "assumptions": [],
            "conflicts": [],
            "open_questions": [],
            "round_summaries": [],
            "version": self.version,
        }

    def save_progress(self, data: dict):
        data["version"] = self.version
        self.progress_file.write_text(json.dumps(data, indent=2))
        # Keep compatibility with legacy readers.
        self.legacy_progress_file.write_text(json.dumps(data, indent=2))

    def add_fact(self, fact: str):
        data = self.load_progress()
        data["confirmed_facts"].append(fact)
        self.save_progress(data)

    def add_question(self, question: dict):
        data = self.load_progress()
        data["open_questions"].append(question)
        self.save_progress(data)

    def get_status(self) -> dict:
        return self.load_progress()


@app.command()
def start(
    topic: str = typer.Argument(..., help="Product topic to analyze"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Start a new think session"""
    project_root = Path(project) if project else Path.cwd()
    session = ThinkSession(project_root, version=resolve_target_version(project_root, version))

    typer.echo(f"Starting think session for: {topic}")
    typer.echo(f"Project root: {project_root}")

    # Initialize session
    data = session.load_progress()
    data["topic"] = topic
    data["round"] = 1
    context_path = os.environ.get("BEACON_STAGE_CONTEXT_PATH", "").strip()
    if context_path:
        data["memory_context_path"] = context_path
        try:
            ctx_data = json.loads(Path(context_path).read_text(encoding="utf-8"))
            data["memory_context_recall_count"] = len(ctx_data.get("memory_recall", []))
        except Exception:
            data["memory_context_recall_count"] = 0
    session.save_progress(data)

    typer.echo(f"\nRound 1: Let's explore '{topic}'")
    typer.echo("Please answer the following questions:\n")


@app.command()
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Show current think session status"""
    project_root = Path(project) if project else Path.cwd()
    session = ThinkSession(project_root, version=resolve_target_version(project_root, version))
    data = session.get_status()

    typer.echo(f"Think Session Status")
    typer.echo("=" * 40)
    typer.echo(f"Topic: {data.get('topic', 'N/A')}")
    typer.echo(f"Round: {data.get('round', 0)}")
    typer.echo(f"Confirmed Facts: {len(data.get('confirmed_facts', []))}")
    typer.echo(f"Assumptions: {len(data.get('assumptions', []))}")
    typer.echo(f"Conflicts: {len(data.get('conflicts', []))}")
    typer.echo(f"Open Questions: {len(data.get('open_questions', []))}")


@app.command()
def confirm(
    fact: str = typer.Argument(..., help="Confirmed fact"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Confirm a fact"""
    project_root = Path(project) if project else Path.cwd()
    session = ThinkSession(project_root, version=resolve_target_version(project_root, version))
    session.add_fact(fact)
    typer.echo(f"Confirmed: {fact}")


@app.command()
def question(
    question: str = typer.Argument(..., help="Question to add"),
    priority: str = typer.Option("medium", "--priority", help="Priority: high/medium/low"),
    blocking: bool = typer.Option(False, "--blocking", help="Is this blocking?"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Add an open question"""
    project_root = Path(project) if project else Path.cwd()
    session = ThinkSession(project_root, version=resolve_target_version(project_root, version))

    q_data = {
        "id": len(session.get_status().get("open_questions", [])) + 1,
        "question": question,
        "priority": priority,
        "blocking": blocking,
        "status": "open"
    }
    session.add_question(q_data)
    typer.echo(f"Added question: {question}")


@app.command()
def conflict(
    conflict_type: str = typer.Argument(..., help="Conflict type: semantic/boundary/goal/constraint"),
    description: str = typer.Argument(..., help="Conflict description"),
    severity: str = typer.Option("high", "--severity", help="Severity: critical/high/medium/low"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Record a conflict"""
    project_root = Path(project) if project else Path.cwd()
    session = ThinkSession(project_root, version=resolve_target_version(project_root, version))

    data = session.load_progress()
    data["conflicts"].append({
        "type": conflict_type,
        "description": description,
        "severity": severity,
        "status": "open"
    })
    session.save_progress(data)
    typer.echo(f"Recorded conflict: {description}")


@app.command()
def summarize(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Generate round summary"""
    project_root = Path(project) if project else Path.cwd()
    session = ThinkSession(project_root, version=resolve_target_version(project_root, version))
    data = session.get_status()

    typer.echo("\n" + "=" * 50)
    typer.echo("THINK SESSION SUMMARY")
    typer.echo("=" * 50)

    if data.get("confirmed_facts"):
        typer.echo("\n✓ Confirmed Facts:")
        for fact in data["confirmed_facts"]:
            typer.echo(f"  - {fact}")

    if data.get("assumptions"):
        typer.echo("\n⚠ Assumptions:")
        for assumption in data["assumptions"]:
            typer.echo(f"  - {assumption}")

    if data.get("conflicts"):
        typer.echo("\n✗ Conflicts:")
        for conflict in data["conflicts"]:
            typer.echo(f"  - [{conflict['severity']}] {conflict['description']}")

    if data.get("open_questions"):
        typer.echo("\n? Open Questions:")
        for q in data["open_questions"]:
            status_icon = "🔴" if q.get("blocking") else "🟡"
            typer.echo(f"  {status_icon} [{q.get('priority')}] {q.get('question')}")


if __name__ == "__main__":
    app()
