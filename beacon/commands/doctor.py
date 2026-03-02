"""Beacon doctor command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from beacon.utils.runtime import now_iso

app = typer.Typer(
    name="doctor",
    help="Run environment diagnostics",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _doctor_impl(json_output: bool, project_root: str, fix: bool, upgrade: bool) -> int:
    root = Path(project_root) if project_root else Path.cwd()
    checks: list[dict[str, str]] = []

    if upgrade:
        typer.echo("Beacon doctor upgrade flow (compat mode)")
        typer.echo("Tip: use `beacon init --apply` after upgrade checks.")
        return 0

    if not root.exists():
        payload = {
            "schema_version": "1.0",
            "beacon_version": "v1.0.0",
            "project_root": str(root),
            "overall": "BLOCKED",
            "checks": [{"name": "project_root", "status": "FAIL", "detail": "project root not found"}],
            "generated_at": now_iso(),
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon Doctor: BLOCKED")
            typer.echo(f"- FAIL: project_root ({root})")
        return 2

    beacon_dir = root / ".beacon"
    docs_dir = root / "docs"
    skills_dir = root / "skills"

    if beacon_dir.exists():
        checks.append({"name": "beacon_directory", "status": "PASS", "detail": ".beacon"})
    else:
        checks.append({"name": "beacon_directory", "status": "WARN", "detail": ".beacon missing"})
        if fix:
            beacon_dir.mkdir(parents=True, exist_ok=True)

    if docs_dir.exists():
        checks.append({"name": "docs_directory", "status": "PASS", "detail": "docs"})
    else:
        checks.append({"name": "docs_directory", "status": "WARN", "detail": "docs missing"})
        if fix:
            docs_dir.mkdir(parents=True, exist_ok=True)

    if skills_dir.exists():
        checks.append({"name": "skills_directory", "status": "PASS", "detail": "skills"})
    else:
        checks.append({"name": "skills_directory", "status": "WARN", "detail": "skills missing"})

    overall = "PASS"
    if any(item["status"] == "FAIL" for item in checks):
        overall = "BLOCKED"
    elif any(item["status"] == "WARN" for item in checks):
        overall = "WARN"

    payload = {
        "schema_version": "1.0",
        "beacon_version": "v1.0.0",
        "project_root": str(root),
        "overall": overall,
        "checks": checks,
        "generated_at": now_iso(),
    }

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Doctor - Environment Diagnostics")
        typer.echo("=" * 40)
        for item in checks:
            icon = "✓" if item["status"] == "PASS" else ("⚠" if item["status"] == "WARN" else "✗")
            typer.echo(f"{icon} {item['status']}: {item['name']} ({item['detail']})")
        typer.echo(f"Overall: {overall}")

    return 2 if overall == "BLOCKED" else 0


@app.callback(invoke_without_command=True)
def doctor_callback(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    fix: bool = typer.Option(False, "--fix", "-f", help="Auto-fix issues"),
    upgrade: bool = typer.Option(False, "--upgrade", "-u", help="Interactive upgrade"),
):
    """Run diagnostics directly (PTK flat syntax compatibility)."""
    if ctx.invoked_subcommand is None:
        raise typer.Exit(code=_doctor_impl(json_output=json_output, project_root=project_root, fix=fix, upgrade=upgrade))


@app.command("diagnose")
def diagnose(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    fix: bool = typer.Option(False, "--fix", "-f", help="Auto-fix issues"),
    upgrade: bool = typer.Option(False, "--upgrade", "-u", help="Interactive upgrade"),
):
    """Run Beacon diagnostics and health checks."""
    raise typer.Exit(code=_doctor_impl(json_output=json_output, project_root=project_root, fix=fix, upgrade=upgrade))


if __name__ == "__main__":
    app()

