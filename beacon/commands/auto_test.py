"""Beacon auto-test command - Automated testing."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit

import typer

app = typer.Typer(name="auto-test", help="Automated testing")

NEGATIVE_KEYWORDS = (
    "unauthorized",
    "forbidden",
    "access denied",
    "permission denied",
    "login",
    "sign in",
    "denied",
    "invalid",
    "error",
    "未授权",
    "无权限",
    "拒绝",
    "禁止",
    "登录",
    "错误",
    "失败",
    "异常",
)


def _normalize_url(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        return ""
    try:
        parts = urlsplit(value)
    except Exception:
        return value
    path = parts.path or (value if value.startswith("/") else "")
    if not path and (parts.scheme or parts.netloc):
        path = "/"
    out = path or ""
    if parts.query:
        out = f"{out}?{parts.query}" if out else f"?{parts.query}"
    if parts.fragment:
        out = f"{out}#{parts.fragment}" if out else f"#{parts.fragment}"
    return out or value


def _extract_snapshot_text(snapshot_file: Optional[str], snapshot_text: Optional[str]) -> str:
    if snapshot_text:
        return snapshot_text
    if not snapshot_file:
        return ""

    path = Path(snapshot_file)
    if not path.exists():
        return ""

    raw = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw

    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict) and isinstance(data.get("snapshot"), str):
            return data["snapshot"]
        if isinstance(payload.get("snapshot"), str):
            return payload["snapshot"]
    return raw


def evaluate_ui_false_positive_guard(
    *,
    expectation: str,
    target_url: str,
    origin_url: str,
    snapshot_text: str,
    strict_ui_assertion: bool,
    assertion_count: int,
) -> dict:
    expectation_norm = (expectation or "").strip().lower()
    target_norm = _normalize_url(target_url)
    origin_norm = _normalize_url(origin_url)

    if not origin_norm:
        origin_vs_target = "unknown"
    elif origin_norm == target_norm:
        origin_vs_target = "match"
    else:
        origin_vs_target = "mismatch"

    haystack = f"{origin_url}\n{snapshot_text}".lower()
    negative_hit = any(keyword in haystack for keyword in NEGATIVE_KEYWORDS)

    detail = (
        f"origin_vs_target={origin_vs_target},"
        f"origin={origin_norm or 'unknown'},"
        f"target={target_norm or 'unknown'},"
        f"negative_hit={1 if negative_hit else 0}"
    )

    def outcome(status: str, reason_code: str) -> dict:
        return {
            "status": status,
            "reason_code": reason_code,
            "detail": detail,
            "expectation": expectation_norm or "unknown",
            "strict_ui_assertion": bool(strict_ui_assertion),
            "assertion_count": int(assertion_count),
            "origin_vs_target": origin_vs_target,
            "origin": origin_norm or "",
            "target": target_norm or "",
            "negative_hit": bool(negative_hit),
        }

    if strict_ui_assertion and assertion_count <= 0:
        return outcome("blocked", "ui_assertion_missing_strict")

    if expectation_norm in {"", "unknown"}:
        if strict_ui_assertion:
            return outcome("blocked", "ui_expectation_unknown_strict")
        return outcome("passed", "ui_expectation_unknown_skipped")

    if expectation_norm == "success":
        if origin_vs_target == "match":
            return outcome("passed", "ui_expectation_success_matched")
        if origin_vs_target == "unknown":
            return outcome("blocked", "ui_origin_target_unknown")
        return outcome("failed", "ui_expectation_success_mismatch")

    if expectation_norm == "error":
        if origin_vs_target == "mismatch":
            return outcome("passed", "ui_expectation_error_redirect")
        if negative_hit:
            return outcome("passed", "ui_expectation_error_keyword")
        if origin_vs_target == "unknown":
            return outcome("blocked", "ui_origin_target_unknown")
        return outcome("failed", "ui_expectation_error_not_observed")

    return outcome("blocked", "ui_expectation_invalid")


@app.command()
def create(
    scope: str = typer.Argument("all", help="Test scope: unit/integration/e2e/all"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Test config file"),
    expectation: str = typer.Option("unknown", "--expectation", help="UI expectation: success/error/unknown"),
    target_url: Optional[str] = typer.Option(None, "--target-url", help="UI target URL/path"),
    origin_url: Optional[str] = typer.Option(None, "--origin-url", help="UI actual origin URL/path"),
    snapshot_file: Optional[str] = typer.Option(None, "--snapshot-file", help="JSON snapshot file path"),
    snapshot_text: Optional[str] = typer.Option(None, "--snapshot-text", help="Snapshot text override"),
    ui_assertion: Optional[list[str]] = typer.Option(
        None,
        "--ui-assertion",
        help="Explicit UI assertion expression (repeatable).",
    ),
    strict_ui_assertion: bool = typer.Option(
        False,
        "--strict-ui-assertion",
        help="Block UI case when no explicit assertion exists.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run automated tests."""
    project_root = Path(project) if project else Path.cwd()

    typer.echo(f"Running automated tests: {scope}")
    typer.echo(f"Project: {project_root}")

    # Simulate test execution
    test_status = {
        "scope": scope,
        "timestamp": datetime.now().isoformat(),
        "project": str(project_root),
        "status": "running",
    }

    ui_assertions = ui_assertion or []
    scope_norm = (scope or "").strip().lower()
    ui_guard_requested = bool(
        target_url
        or origin_url
        or snapshot_file
        or snapshot_text
        or strict_ui_assertion
        or ui_assertions
        or (expectation or "").strip().lower() not in {"", "unknown"}
        or scope_norm == "ui"
    )

    if ui_guard_requested:
        snapshot_payload = _extract_snapshot_text(snapshot_file, snapshot_text)
        ui_guard = evaluate_ui_false_positive_guard(
            expectation=expectation,
            target_url=target_url or "",
            origin_url=origin_url or "",
            snapshot_text=snapshot_payload,
            strict_ui_assertion=strict_ui_assertion,
            assertion_count=len(ui_assertions),
        )
        test_status["status"] = ui_guard["status"]
        test_status["ui_guard"] = ui_guard

    status_file = project_root / ".beacon" / "auto-test-status.json"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status_file.write_text(json.dumps(test_status, indent=2))

    typer.echo("✓ Test execution started")
    typer.echo(f"  Scope: {scope}")
    typer.echo(f"  Status file: {status_file}")
    if ui_guard_requested:
        typer.echo(f"  UI Guard: {test_status['status']} ({test_status['ui_guard']['reason_code']})")
        if verbose:
            typer.echo(f"  UI Detail: {test_status['ui_guard']['detail']}")


@app.command()
def status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """View test status."""
    project_root = Path(project) if project else Path.cwd()
    status_file = project_root / ".beacon" / "auto-test-status.json"

    if not status_file.exists():
        typer.echo("No test status found. Run 'beacon auto-test create' first.")
        return

    status_data = json.loads(status_file.read_text())

    if json_output:
        typer.echo(json.dumps(status_data, indent=2))
    else:
        typer.echo("Auto-Test Status")
        typer.echo("=" * 40)
        typer.echo(f"Scope: {status_data.get('scope', 'N/A')}")
        typer.echo(f"Status: {status_data.get('status', 'N/A')}")
        typer.echo(f"Timestamp: {status_data.get('timestamp', 'N/A')}")
        ui_guard = status_data.get("ui_guard")
        if isinstance(ui_guard, dict):
            typer.echo(f"UI Guard: {ui_guard.get('reason_code', 'N/A')}")
            typer.echo(f"UI Detail: {ui_guard.get('detail', 'N/A')}")


if __name__ == "__main__":
    app()
