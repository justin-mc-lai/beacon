"""Beacon workflow command - Full product workflow"""
import typer
from typing import Optional
from pathlib import Path

app = typer.Typer(name="workflow", help="Full product workflow")


@app.command()
def start(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Start full product workflow"""
    project_root = Path(project) if project else Path.cwd()

    typer.echo(f"Starting Beacon Workflow: {feature}")
    typer.echo(f"Project: {project_root}")
    typer.echo("\n" + "=" * 50)
    typer.echo("WORKFLOW STAGES")
    typer.echo("=" * 50)
    typer.echo("1. think    - Product thinking (vNext)")
    typer.echo("2. user-story - Generate user stories")
    typer.echo("3. prd      - Generate PRD")
    typer.echo("4. test-case - Generate test cases")
    typer.echo("5. gate     - Run gate checks")
    typer.echo("\nUse --help for each stage")


@app.command()
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Show workflow status"""
    project_root = Path(project) if project else Path.cwd()

    typer.echo("Beacon Workflow Status")
    typer.echo("=" * 40)

    # Check each stage
    stages = ["think", "user-story", "prd", "test-case"]
    for stage in stages:
        stage_dir = project_root / "docs" / "product" / "latest" / stage.replace("-", "-")
        if stage_dir.exists() and list(stage_dir.glob("*.md")):
            typer.echo(f"✓ {stage}: Completed")
        else:
            typer.echo(f"○ {stage}: Not started")


@app.command()
def gate(
    stage: Optional[str] = typer.Argument(None, help="Stage to check (think/user-story/prd/test-case/release)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Run gate checks for stages"""
    project_root = Path(project) if project else Path.cwd()

    stages = ["think", "user-story", "prd", "test-case", "release"] if not stage else [stage]

    typer.echo("Beacon Gate Check")
    typer.echo("=" * 50)

    for s in stages:
        typer.echo(f"\n--- {s.upper()} Gate ---")

        if s == "think":
            # Check think progress
            state_file = project_root / ".beacon" / "state" / "think-progress.json"
            if state_file.exists():
                typer.echo("✓ PASS: Think session exists")
            else:
                typer.echo("✗ FAIL: No think session found")

        elif s == "user-story":
            us_dir = project_root / "docs" / "product" / "latest" / "user-story"
            if us_dir.exists() and list(us_dir.glob("*.md")):
                typer.echo("✓ PASS: User stories exist")
            else:
                typer.echo("✗ FAIL: No user stories found")

        elif s == "prd":
            prd_dir = project_root / "docs" / "product" / "latest" / "prd"
            if prd_dir.exists() and list(prd_dir.glob("*.md")):
                typer.echo("✓ PASS: PRD exists")
            else:
                typer.echo("✗ FAIL: No PRD found")

        elif s == "test-case":
            tc_dir = project_root / "docs" / "product" / "latest" / "qa" / "test-cases"
            if tc_dir.exists() and list(tc_dir.glob("*.md")):
                typer.echo("✓ PASS: Test cases exist")
            else:
                typer.echo("✗ FAIL: No test cases found")

        elif s == "release":
            typer.echo("⚠ WARN: Release gate requires smoke tests")
            typer.echo("Run: beacon auto-test --type smoke")


if __name__ == "__main__":
    app()
