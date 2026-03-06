"""Beacon release command - Release checklist"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime
import json

from beacon.utils.memory import append_memory_entry
from beacon.utils.versioning import resolve_target_version
from beacon.utils.workflow_memory import append_lifecycle_event

app = typer.Typer(name="release", help="Release checklist")


def _extract_run_id(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ""
    direct = str(payload.get("run_id", "")).strip()
    if direct:
        return direct
    execution = payload.get("execution")
    if isinstance(execution, dict):
        return str(execution.get("run_id", "")).strip()
    return ""


def _extract_version(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ""
    direct = str(payload.get("version", "")).strip()
    if direct:
        return direct
    execution = payload.get("execution")
    if isinstance(execution, dict):
        return str(execution.get("version", "")).strip()
    return ""


@app.command()
def create(
    version: str = typer.Argument(..., help="Release version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create release checklist"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    release_content = f"""# Release Checklist: {resolved_version}

**Version**: {resolved_version}
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
    output_paths = (
        [Path(output)]
        if output
        else [
            project_root / "docs" / "beacon" / resolved_version / "release" / f"{resolved_version}.md",
            project_root / "docs" / "product" / resolved_version / "release" / f"{resolved_version}.md",
        ]
    )
    for output_path in output_paths:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(release_content)
    output_path = output_paths[0]

    rel = str(output_path.relative_to(project_root))
    append_memory_entry(
        project_root=project_root,
        mem_type="decision",
        text=f"[release.create] release checklist created for {resolved_version}",
        source_session_id=f"release:{resolved_version}",
        source="release.create",
        evidence_ref=[rel],
        confidence=0.8,
        tags=["release", "workflow-loop"],
    )
    append_lifecycle_event(
        project_root,
        run_id=f"release:{resolved_version}",
        stage="release",
        event="release_decision_recorded",
        source="release.create",
        evidence_ref=[rel],
        details={"action": "create", "version": resolved_version},
    )

    typer.echo(f"✓ Release checklist created: {output_path}")


@app.command()
def check(
    version: str = typer.Argument(..., help="Release version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Check release conditions"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    typer.echo(f"Checking release conditions for {resolved_version}")
    typer.echo("=" * 40)

    auto_test_path = project_root / ".beacon" / "auto-test-status.json"
    gate_report_path = project_root / ".beacon" / "gate-report.json"
    manifest_path = project_root / ".beacon" / "evidence-manifest.json"
    coverage_summary_path = project_root / ".beacon" / "coverage-summary.json"

    checks: list[tuple[str, bool, str]] = []
    evidence_refs: list[str] = []

    auto_test_ok = False
    auto_test_status = "missing"
    auto_test_run_id = ""
    auto_test_version = ""
    if auto_test_path.exists():
        try:
            auto_test_payload = json.loads(auto_test_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            auto_test_payload = {}
        auto_test_status = str(auto_test_payload.get("status", "")).strip().lower() or "unknown"
        auto_test_ok = auto_test_status == "passed"
        auto_test_run_id = _extract_run_id(auto_test_payload)
        auto_test_version = _extract_version(auto_test_payload)
        evidence_refs.append(str(auto_test_path.relative_to(project_root)))
    checks.append(("auto-test status passed", auto_test_ok, f"status={auto_test_status}"))
    checks.append(
        (
            "auto-test version matches release version",
            bool(auto_test_version) and auto_test_version == resolved_version,
            f"artifact_version={auto_test_version or 'missing'}, expected={resolved_version}",
        )
    )
    checks.append(
        (
            "auto-test run_id present",
            bool(auto_test_run_id),
            f"run_id={auto_test_run_id or 'missing'}",
        )
    )

    gate_ok = False
    gate_status = "missing"
    gate_coverage_full: Optional[bool] = None
    gate_run_id = ""
    gate_version = ""
    if gate_report_path.exists():
        try:
            gate_payload = json.loads(gate_report_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            gate_payload = {}
        gate_status = str(gate_payload.get("status", "")).strip()
        gate_ok = gate_status.lower() == "pass"
        gate_run_id = _extract_run_id(gate_payload)
        gate_version = _extract_version(gate_payload)
        coverage_payload = gate_payload.get("coverage")
        if isinstance(coverage_payload, dict) and "full_coverage" in coverage_payload:
            gate_coverage_full = bool(coverage_payload.get("full_coverage"))
        evidence_refs.append(str(gate_report_path.relative_to(project_root)))
    checks.append(("gate report pass", gate_ok, f"status={gate_status or 'unknown'}"))
    checks.append(
        (
            "gate report version matches release version",
            bool(gate_version) and gate_version == resolved_version,
            f"artifact_version={gate_version or 'missing'}, expected={resolved_version}",
        )
    )
    checks.append(
        (
            "gate report run_id matches auto-test",
            bool(gate_run_id) and bool(auto_test_run_id) and gate_run_id == auto_test_run_id,
            f"gate_run_id={gate_run_id or 'missing'}, auto_test_run_id={auto_test_run_id or 'missing'}",
        )
    )

    manifest_ok = False
    manifest_entries = 0
    manifest_run_id = ""
    manifest_version = ""
    if manifest_path.exists():
        try:
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            manifest_payload = {}
        entries = manifest_payload.get("entries")
        if isinstance(entries, list):
            manifest_entries = len(entries)
            manifest_ok = manifest_entries > 0
        manifest_run_id = _extract_run_id(manifest_payload)
        manifest_version = _extract_version(manifest_payload)
        evidence_refs.append(str(manifest_path.relative_to(project_root)))
    checks.append(("evidence manifest present", manifest_ok, f"entries={manifest_entries}"))
    checks.append(
        (
            "evidence manifest version matches release version",
            bool(manifest_version) and manifest_version == resolved_version,
            f"artifact_version={manifest_version or 'missing'}, expected={resolved_version}",
        )
    )
    expected_run_id = auto_test_run_id or gate_run_id
    checks.append(
        (
            "evidence manifest run_id matches test artifacts",
            bool(manifest_run_id) and bool(expected_run_id) and manifest_run_id == expected_run_id,
            f"manifest_run_id={manifest_run_id or 'missing'}, expected={expected_run_id or 'missing'}",
        )
    )

    coverage_ok = False
    coverage_detail = "missing"
    if coverage_summary_path.exists():
        try:
            coverage_payload = json.loads(coverage_summary_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            coverage_payload = {}
        rate = coverage_payload.get("coverage_rate")
        if isinstance(rate, (int, float)):
            coverage_ok = float(rate) >= 0.8
            coverage_detail = f"coverage_rate={float(rate):.4f}"
        elif "full_coverage" in coverage_payload:
            coverage_ok = bool(coverage_payload.get("full_coverage"))
            coverage_detail = f"full_coverage={coverage_ok}"
        evidence_refs.append(str(coverage_summary_path.relative_to(project_root)))
    elif gate_coverage_full is not None:
        coverage_ok = bool(gate_coverage_full)
        coverage_detail = f"gate_report.coverage.full_coverage={coverage_ok}"
    checks.append(("coverage artifact ready", coverage_ok, coverage_detail))

    all_passed = True
    failed_checks: list[str] = []
    for check_name, passed, detail in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        typer.echo(f"{status}: {check_name} ({detail})")
        if not passed:
            all_passed = False
            failed_checks.append(check_name)

    if all_passed:
        typer.echo("\n✓ Release conditions met")
        status = "pass"
    else:
        typer.echo("\n✗ Some checks failed")
        status = "blocked"

    append_memory_entry(
        project_root=project_root,
        mem_type="decision",
        text=f"[release.check] version={resolved_version} status={status}",
        source_session_id=f"release:{resolved_version}",
        source="release.check",
        evidence_ref=sorted(set(evidence_refs)),
        confidence=0.75,
        tags=["release", "gate", status],
    )
    append_lifecycle_event(
        project_root,
        run_id=f"release:{resolved_version}",
        stage="release",
        event="release_decision_recorded",
        source="release.check",
        evidence_ref=sorted(set(evidence_refs)),
        details={
            "action": "check",
            "version": resolved_version,
            "status": status,
            "failed_checks": failed_checks,
        },
    )
    if not all_passed:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
