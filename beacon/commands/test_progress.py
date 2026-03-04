"""Beacon test-progress command - Test progress tracking"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime
import json

app = typer.Typer(name="test-progress", help="Test progress tracking")


def _default_progress() -> dict:
    return {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "blocked": 0,
        "pending": 0,
        "pass_rate": 0.0,
        "automation_rate": 0.0,
        "scope": "",
        "source": "manual",
        "last_updated": datetime.now().isoformat(),
    }


def _sync_from_auto_test(project_root: Path) -> dict:
    status_file = project_root / ".beacon" / "auto-test-status.json"
    if not status_file.exists():
        return _default_progress()

    try:
        status_payload = json.loads(status_file.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return _default_progress()

    qa9 = status_payload.get("qa9")
    if isinstance(qa9, dict) and isinstance(qa9.get("summary"), dict):
        summary = qa9["summary"]
        total = int(summary.get("cases_total", 0) or 0)
        passed = int(summary.get("passed", 0) or 0)
        failed = int(summary.get("failed", 0) or 0)
        blocked = int(summary.get("blocked", 0) or 0)
        pending = int(summary.get("pending", 0) or 0)
        pass_rate = float(summary.get("pass_rate", 0.0) or 0.0)
        automation_rate = float(summary.get("automation_rate", 0.0) or 0.0)
    else:
        execution = status_payload.get("execution")
        layers = execution.get("layers") if isinstance(execution, dict) else []
        if not isinstance(layers, list):
            layers = []
        total = len(layers)
        passed = sum(1 for x in layers if str((x or {}).get("status", "")).lower() == "passed")
        failed = sum(1 for x in layers if str((x or {}).get("status", "")).lower() == "failed")
        blocked = sum(1 for x in layers if str((x or {}).get("status", "")).lower() in {"blocked", "not_executed"})
        pending = max(0, total - passed - failed - blocked)
        pass_rate = float(passed) / float(total or 1)
        automation_rate = 0.0

    progress_data = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "blocked": blocked,
        "pending": pending,
        "pass_rate": round(pass_rate, 4),
        "automation_rate": round(automation_rate, 4),
        "scope": str(status_payload.get("scope", "")),
        "source": "auto-test-status",
        "auto_test_status": str(status_payload.get("status", "")),
        "last_updated": datetime.now().isoformat(),
    }
    return progress_data


def _write_progress(project_root: Path, payload: dict) -> Path:
    progress_file = project_root / ".beacon" / "test-progress.json"
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    progress_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return progress_file


@app.command()
def show(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    sync: bool = typer.Option(False, "--sync", help="Sync from auto-test-status before showing"),
):
    """Show test progress"""
    project_root = Path(project) if project else Path.cwd()
    progress_file = project_root / ".beacon" / "test-progress.json"
    if sync:
        synced = _sync_from_auto_test(project_root)
        _write_progress(project_root, synced)

    if not progress_file.exists():
        progress_data = _default_progress()
    else:
        progress_data = json.loads(progress_file.read_text(encoding="utf-8"))

    if json_output:
        typer.echo(json.dumps(progress_data, indent=2, ensure_ascii=False))
    else:
        typer.echo("Test Progress")
        typer.echo("=" * 40)
        typer.echo(f"Total: {progress_data.get('total', 0)}")
        typer.echo(f"Passed: {progress_data.get('passed', 0)}")
        typer.echo(f"Failed: {progress_data.get('failed', 0)}")
        typer.echo(f"Blocked: {progress_data.get('blocked', 0)}")
        typer.echo(f"Pending: {progress_data.get('pending', 0)}")
        typer.echo(f"Pass Rate: {progress_data.get('pass_rate', 0)}")
        typer.echo(f"Automation Rate: {progress_data.get('automation_rate', 0)}")
        typer.echo(f"Source: {progress_data.get('source', 'manual')}")

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
        "blocked": 0,
        "pending": pending,
        "pass_rate": round(float(passed) / float((passed + failed + pending) or 1), 4),
        "automation_rate": 0.0,
        "scope": "",
        "source": "manual",
        "last_updated": datetime.now().isoformat(),
    }

    progress_file = _write_progress(project_root, progress_data)

    typer.echo("✓ Test progress updated")
    typer.echo(f"  Passed: {passed}, Failed: {failed}, Pending: {pending}")
    typer.echo(f"  File: {progress_file}")


@app.command()
def sync(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Sync test progress from .beacon/auto-test-status.json."""
    project_root = Path(project) if project else Path.cwd()
    progress_data = _sync_from_auto_test(project_root)
    progress_file = _write_progress(project_root, progress_data)
    typer.echo("✓ Test progress synced from auto-test status")
    typer.echo(f"  File: {progress_file}")
    typer.echo(
        f"  Total={progress_data.get('total', 0)} "
        f"Passed={progress_data.get('passed', 0)} "
        f"Failed={progress_data.get('failed', 0)} "
        f"Blocked={progress_data.get('blocked', 0)}"
    )


if __name__ == "__main__":
    app()
