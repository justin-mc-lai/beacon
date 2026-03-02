"""Beacon workflow command - Full product workflow"""
import typer
from typing import Optional
from pathlib import Path
import subprocess
import sys
import os

from beacon.utils.runtime import generate_run_id, now_iso, save_run_state
from beacon.utils.workflow_memory import append_lifecycle_event, write_stage_context, record_stage_writeback

app = typer.Typer(name="workflow", help="Full product workflow")


def run_beacon_command(args: list, project_root: Path, extra_env: Optional[dict[str, str]] = None) -> int:
    """Run a beacon subcommand"""
    cmd = [sys.executable, "-m", "beacon.main"] + args
    env = os.environ.copy()
    env.update(extra_env or {})
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode


def ensure_output_dirs(project_root: Path, version: str = "latest"):
    """Ensure output directories exist - supports both docs/beacon and docs/product"""
    dirs = [
        # Beacon primary directories
        project_root / "docs" / "beacon" / version / "user-story",
        project_root / "docs" / "beacon" / version / "prd",
        project_root / "docs" / "beacon" / version / "qa" / "test-cases",
        # PTK compatibility directories
        project_root / "docs" / "product" / version / "user-story",
        project_root / "docs" / "product" / version / "prd",
        project_root / "docs" / "product" / version / "qa" / "test-cases",
        # State directory
        project_root / ".beacon" / "state",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def _slug(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "-")


def _stage_output_candidates(project_root: Path, stage: str, feature: str, version: str) -> list[Path]:
    slug = _slug(feature)
    if stage == "think":
        return [project_root / ".beacon" / "state" / "think-progress.json"]
    if stage == "user-story":
        return [
            project_root / "docs" / "product" / "latest" / "user-story" / f"{slug}.md",
            project_root / "docs" / "beacon" / version / "user-story" / f"{slug}.md",
        ]
    if stage == "prd":
        return [
            project_root / "docs" / "product" / "latest" / "prd" / f"{slug}.md",
            project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md",
        ]
    if stage == "test-case":
        return [
            project_root / "docs" / "product" / "latest" / "qa" / "test-cases" / f"{slug}.md",
            project_root / "docs" / "beacon" / version / "qa" / "test-cases" / f"{slug}.md",
        ]
    return []


@app.command()
def start(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("latest", "--version", "-v", help="Version"),
    auto: bool = typer.Option(False, "--auto", "-a", help="Auto-run all stages"),
    skip: Optional[str] = typer.Option(None, "--skip", "-s", help="Skip stages (e.g., think,user-story)"),
):
    """Start full product workflow"""
    project_root = Path(project) if project else Path.cwd()

    # Ensure directories exist
    ensure_output_dirs(project_root, version)
    run_id = generate_run_id(project_root)
    started_at = now_iso()
    save_run_state(
        project_root,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "mode": "auto" if auto else "manual",
            "feature": feature,
            "version": version,
            "status": "running",
            "started_at": started_at,
            "events": [{"event": "workflow_started", "ts": started_at}],
        },
    )

    typer.echo(f"Starting Beacon Workflow: {feature}")
    typer.echo(f"Project: {project_root}")
    typer.echo(f"Version: {version}")
    typer.echo(f"Run ID: {run_id}")
    typer.echo("\n" + "=" * 50)
    typer.echo("WORKFLOW STAGES")
    typer.echo("=" * 50)

    stages = [
        ("think", "Product thinking (vNext)", "beacon think start"),
        ("user-story", "Generate user stories", "beacon user-story create"),
        ("prd", "Generate PRD", "beacon prd create"),
        ("test-case", "Generate test cases", "beacon test-case create"),
    ]

    # Parse skip list
    skip_stages = set(skip.split(",")) if skip else set()

    for i, (stage, desc, cmd) in enumerate(stages, 1):
        if stage in skip_stages:
            typer.echo(f"{i}. {stage:12} - {desc} [SKIPPED]")
            continue

        typer.echo(f"{i}. {stage:12} - {desc}")
        append_lifecycle_event(
            project_root,
            run_id=run_id,
            stage=stage,
            event="stage_started",
            source="workflow.start",
            details={"feature": feature, "version": version},
        )
        context_path = write_stage_context(
            project_root,
            run_id=run_id,
            stage=stage,
            feature=feature,
        )

        if auto:
            typer.echo(f"    → Running: {cmd} {feature}")
            stage_env = {
                "BEACON_WORKFLOW_RUN_ID": run_id,
                "BEACON_WORKFLOW_STAGE": stage,
                "BEACON_STAGE_CONTEXT_PATH": str(context_path),
            }
            # Run the command
            if stage == "think":
                rc = run_beacon_command(
                    ["think", "start", feature, "--project", str(project_root)],
                    project_root,
                    extra_env=stage_env,
                )
            elif stage == "user-story":
                rc = run_beacon_command(
                    ["user-story", "create", feature, "--project", str(project_root)],
                    project_root,
                    extra_env=stage_env,
                )
            elif stage == "prd":
                rc = run_beacon_command(
                    ["prd", "create", feature, "--project", str(project_root)],
                    project_root,
                    extra_env=stage_env,
                )
            elif stage == "test-case":
                rc = run_beacon_command(
                    ["test-case", "create", feature, "--project", str(project_root)],
                    project_root,
                    extra_env=stage_env,
                )
            else:
                rc = 1

            if rc == 0:
                typer.echo(f"    ✓ {stage} completed")
                evidence = [
                    str(path.relative_to(project_root))
                    for path in _stage_output_candidates(project_root, stage, feature, version)
                    if path.exists()
                ]
                append_lifecycle_event(
                    project_root,
                    run_id=run_id,
                    stage=stage,
                    event="stage_finished",
                    source="workflow.start",
                    evidence_ref=evidence,
                    details={"exit_code": rc},
                )
                record_stage_writeback(
                    project_root,
                    run_id=run_id,
                    stage=stage,
                    feature=feature,
                    evidence_ref=evidence,
                    status="completed",
                )
            else:
                typer.echo(f"    ✗ {stage} failed (exit={rc})")
                append_lifecycle_event(
                    project_root,
                    run_id=run_id,
                    stage=stage,
                    event="stage_failed",
                    source="workflow.start",
                    details={"exit_code": rc},
                )
                save_run_state(
                    project_root,
                    run_id,
                    {
                        "run_id": run_id,
                        "workflow": "workflow.start",
                        "mode": "auto",
                        "feature": feature,
                        "version": version,
                        "status": "blocked",
                        "reason": f"{stage}_failed",
                        "started_at": started_at,
                        "ended_at": now_iso(),
                    },
                )
                raise typer.Exit(rc)

    typer.echo("\n" + "=" * 50)
    typer.echo("WORKFLOW COMPLETE")
    typer.echo("=" * 50)
    save_run_state(
        project_root,
        run_id,
        {
            "run_id": run_id,
            "workflow": "workflow.start",
            "mode": "auto" if auto else "manual",
            "feature": feature,
            "version": version,
            "status": "completed",
            "reason": "ok",
            "started_at": started_at,
            "ended_at": now_iso(),
        },
    )

    if not auto:
        typer.echo("\nUse --auto to run all stages automatically")
        typer.echo("Or run stages individually:")
        for stage, _, cmd in stages:
            typer.echo(f"  beacon {cmd.split(' ', 1)[1]} {feature}")


@app.command()
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("latest", "--version", "-v", help="Version"),
):
    """Show workflow status"""
    project_root = Path(project) if project else Path.cwd()

    typer.echo("Beacon Workflow Status")
    typer.echo("=" * 40)

    # Check docs/beacon first, fallback to docs/product
    beacon_dir = project_root / "docs" / "beacon" / version
    product_dir = project_root / "docs" / "product" / version

    # Determine which docs dir to use
    beacon_has_docs = beacon_dir.exists() and any(beacon_dir.rglob("*.md"))
    product_has_docs = product_dir.exists() and any(product_dir.rglob("*.md"))
    if beacon_has_docs:
        docs_dir = beacon_dir
        docs_type = "beacon"
    elif product_has_docs:
        docs_dir = product_dir
        docs_type = "product"
    elif beacon_dir.exists():
        docs_dir = beacon_dir
        docs_type = "beacon"
    else:
        docs_dir = beacon_dir  # Use beacon as default
        docs_type = "beacon"

    typer.echo(f"Using: docs/{docs_type}/{version}")

    # Check each stage
    stages = [
        ("think", ".beacon/state/think-progress.json"),
        ("user-story", "user-story"),
        ("prd", "prd"),
        ("test-case", "qa/test-cases"),
    ]

    for stage, path in stages:
        stage_path = project_root / path if stage == "think" else docs_dir / path
        if stage_path.exists():
            if stage_path.is_file():
                typer.echo(f"✓ {stage}: Completed")
            elif stage_path.is_dir():
                files = list(stage_path.glob("*.md"))
                if files:
                    typer.echo(f"✓ {stage}: Completed ({len(files)} files)")
                else:
                    typer.echo(f"○ {stage}: Started (empty)")
            else:
                typer.echo(f"○ {stage}: Not started")
        else:
            typer.echo(f"○ {stage}: Not started")


@app.command()
def gate(
    stage: Optional[str] = typer.Argument(None, help="Stage to check (think/user-story/prd/test-case/release)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("latest", "--version", "-v", help="Version"),
):
    """Run gate checks for stages"""
    project_root = Path(project) if project else Path.cwd()

    stages = ["think", "user-story", "prd", "test-case", "release"] if not stage else [stage]

    typer.echo("Beacon Gate Check")
    typer.echo("=" * 50)

    # Check docs/beacon first, fallback to docs/product
    beacon_dir = project_root / "docs" / "beacon" / version
    product_dir = project_root / "docs" / "product" / version

    if beacon_dir.exists():
        docs_dir = beacon_dir
        docs_type = "beacon"
    elif product_dir.exists():
        docs_dir = product_dir
        docs_type = "product"
    else:
        docs_dir = beacon_dir  # Use beacon as default
        docs_type = "beacon"

    typer.echo(f"Checking: docs/{docs_type}/{version}")

    all_passed = True

    for s in stages:
        typer.echo(f"\n--- {s.upper()} Gate ---")

        if s == "think":
            # Check think progress
            state_file = project_root / ".beacon" / "state" / "think-progress.json"
            if state_file.exists():
                typer.echo("✓ PASS: Think session exists")
            else:
                typer.echo("✗ FAIL: No think session found")
                all_passed = False

        elif s == "user-story":
            us_dir = docs_dir / "user-story"
            if us_dir.exists() and list(us_dir.glob("*.md")):
                typer.echo("✓ PASS: User stories exist")
            else:
                typer.echo("✗ FAIL: No user stories found")
                all_passed = False

        elif s == "prd":
            prd_dir = docs_dir / "prd"
            if prd_dir.exists() and list(prd_dir.glob("*.md")):
                typer.echo("✓ PASS: PRD exists")
            else:
                typer.echo("✗ FAIL: No PRD found")
                all_passed = False

        elif s == "test-case":
            tc_dir = docs_dir / "qa" / "test-cases"
            if tc_dir.exists() and list(tc_dir.glob("*.md")):
                typer.echo("✓ PASS: Test cases exist")
            else:
                typer.echo("✗ FAIL: No test cases found")
                all_passed = False

        elif s == "release":
            typer.echo("⚠ WARN: Release gate requires smoke tests")
            typer.echo("Run: beacon auto-test --type smoke")

    typer.echo("\n" + "=" * 50)
    if all_passed:
        typer.echo("GATE RESULT: PASS")
    else:
        typer.echo("GATE RESULT: FAIL")


@app.command()
def run(
    command: str = typer.Argument(..., help="Command to run (think/user-story/prd/test-case/analyze/brainstorm/etc)"),
    feature: Optional[str] = typer.Argument(None, help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("latest", "--version", "-v", help="Version"),
    options: Optional[str] = typer.Option(None, "--options", "-o", help="Additional options as JSON string"),
):
    """Run any beacon subcommand from workflow"""
    project_root = Path(project) if project else Path.cwd()

    # Map command names to actual commands
    command_map = {
        "think": "think",
        "user-story": "user-story",
        "user_story": "user-story",
        "prd": "prd",
        "test-case": "test-case",
        "test_case": "test-case",
        "analyze": "analyze",
        "brainstorm": "brainstorm",
        "design": "design",
        "jtbd": "jtbd",
        "kano": "kano",
        "moscow": "moscow",
        "roadmap": "roadmap",
        "persona": "persona",
        "version": "version",
        "doctor": "doctor",
        "status": "status",
        "report": "report",
        "debug": "debug",
        "auto-test": "auto-test",
        "auto_test": "auto-test",
        "release": "release",
        "api-design": "api-design",
        "api_design": "api-design",
        "data-dictionary": "data-dictionary",
        "data_dictionary": "data-dictionary",
        "ui-spec": "ui-spec",
        "ui_spec": "ui-spec",
        "wireframe": "wireframe",
        "save": "save",
        "recall": "recall",
        "remember": "remember",
        "team": "team",
    }

    cmd = command_map.get(command.lower(), command)

    typer.echo(f"Running: beacon {cmd}" + (f" {feature}" if feature else ""))
    typer.echo(f"Project: {project_root}")

    # Build the command
    full_cmd = [cmd]
    if feature:
        full_cmd.append(feature)

    # Run the command
    result = subprocess.run(
        [sys.executable, "-m", "beacon.main"] + full_cmd,
        cwd=project_root,
    )

    if result.returncode == 0:
        typer.echo(f"\n✓ Command completed successfully")
    else:
        typer.echo(f"\n✗ Command failed with code {result.returncode}")
        raise typer.Exit(result.returncode)


if __name__ == "__main__":
    app()
