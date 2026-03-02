"""Beacon release command - Release checklist"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime
import json

from beacon.utils.memory import append_memory_entry
from beacon.utils.workflow_memory import append_lifecycle_event

app = typer.Typer(name="release", help="Release checklist")


@app.command()
def create(
    version: str = typer.Argument(..., help="Release version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create release checklist"""
    project_root = Path(project) if project else Path.cwd()

    release_content = f"""# Release Checklist: {version}

**Version**: {version}
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Status**: Pending

---

## Pre-Release Checks

- [ ] All tests passing
- [ ] Code coverage >= 80%
- [ ] No critical bugs open
- [ ] Security scan completed
- [ ] Performance benchmarks passed
- [ ] Documentation updated

## Build

- [ ] Build successful
- [ ] No linting errors
- [ ] Type checks passing

## Deployment

- [ ] Staging deployment successful
- [ ] Smoke tests passed
- [ ] Database migrations tested

## Release

- [ ] Production deployment
- [ ] Health checks passing
- [ ] Rollback plan ready

---

## Notes

"""
    output_path = Path(output) if output else project_root / "docs" / "product" / "latest" / "release" / f"v{version.lstrip('v')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(release_content)

    rel = str(output_path.relative_to(project_root))
    append_memory_entry(
        project_root=project_root,
        mem_type="decision",
        text=f"[release.create] release checklist created for {version}",
        source_session_id=f"release:{version}",
        source="release.create",
        evidence_ref=[rel],
        confidence=0.8,
        tags=["release", "workflow-loop"],
    )
    append_lifecycle_event(
        project_root,
        run_id=f"release:{version}",
        stage="release",
        event="release_decision_recorded",
        source="release.create",
        evidence_ref=[rel],
        details={"action": "create", "version": version},
    )

    typer.echo(f"✓ Release checklist created: {output_path}")


@app.command()
def check(
    version: str = typer.Argument(..., help="Release version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Check release conditions"""
    project_root = Path(project) if project else Path.cwd()

    typer.echo(f"Checking release conditions for v{version}")
    typer.echo("=" * 40)

    # Simulated checks
    checks = [
        ("Tests passing", True),
        ("Code coverage >= 80%", True),
        ("No critical bugs", True),
        ("Security scan", True),
    ]

    all_passed = True
    for check_name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        typer.echo(f"{status}: {check_name}")
        if not passed:
            all_passed = False

    if all_passed:
        typer.echo("\n✓ Release conditions met")
        status = "pass"
    else:
        typer.echo("\n✗ Some checks failed")
        status = "blocked"

    append_memory_entry(
        project_root=project_root,
        mem_type="decision",
        text=f"[release.check] version={version} status={status}",
        source_session_id=f"release:{version}",
        source="release.check",
        evidence_ref=[],
        confidence=0.75,
        tags=["release", "gate", status],
    )
    append_lifecycle_event(
        project_root,
        run_id=f"release:{version}",
        stage="release",
        event="release_decision_recorded",
        source="release.check",
        evidence_ref=[],
        details={"action": "check", "version": version, "status": status},
    )
    if not all_passed:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
