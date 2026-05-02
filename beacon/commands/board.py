"""Prototype-backed board launcher for Beacon operator workbench surfaces."""

from __future__ import annotations

import json
import subprocess
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.board_launcher import build_board_launcher_contract, ensure_board_runtime_bundle
from beacon.utils.versioning import resolve_operational_docs_version


app = typer.Typer(
    name="board",
    help="Launch the Beacon operator workbench / board surface from a frozen prototype bundle.",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _resolved_operational_version(project_root: Path, version: str, command_name: str) -> str:
    try:
        return resolve_operational_docs_version(project_root, version, command_name=command_name)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc


def _resolve_board_action(contract: dict[str, object], action_id: str) -> dict[str, object]:
    workbench = contract.get("operator_workbench") if isinstance(contract.get("operator_workbench"), dict) else {}
    action_contract = workbench.get("operator_action_contract") if isinstance(workbench.get("operator_action_contract"), dict) else {}
    actions = action_contract.get("actions") if isinstance(action_contract.get("actions"), list) else []
    for item in actions:
        if isinstance(item, dict) and str(item.get("action_id") or "") == action_id:
            return item
    return {}


def _run_board_action_command(project_root: Path, command: str) -> tuple[int, dict[str, object]]:
    rendered = str(command or "").strip()
    if not rendered:
        return 2, {"status": "blocked", "reason_code": "board_action_command_missing"}
    result = subprocess.run(rendered, cwd=str(project_root), shell=True, capture_output=True, text=True)
    payload: dict[str, object] = {
        "status": "completed" if result.returncode == 0 else "failed",
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if result.stdout.strip():
        try:
            payload["result"] = json.loads(result.stdout)
        except Exception:  # noqa: BLE001
            payload["result"] = None
    return result.returncode, payload


@app.callback()
def board(
    ctx: typer.Context,
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    feature: str = typer.Option("", "--feature", help="Prototype feature to launch"),
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host for local web board"),
    port: int = typer.Option(4173, "--port", help="Bind port for local web board"),
    open_browser: bool = typer.Option(False, "--open", help="Open the board in the default browser"),
    desktop: bool = typer.Option(False, "--desktop", help="Emit the desktop launcher contract (planned, not yet implemented)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Resolve launcher contract without starting a server"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON contract and do not start a server"),
):
    """Launch Beacon board or emit its launcher contract."""
    if ctx.invoked_subcommand:
        return

    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "board")
    contract = build_board_launcher_contract(
        project_root,
        version=resolved_version,
        feature=feature or None,
        host=host,
        port=port,
        desktop=desktop,
        open_browser=open_browser,
    )
    if str(contract.get("readiness_status") or "") == "ready":
        bundle_root = Path(ensure_board_runtime_bundle(project_root, contract))
        contract["bundle_root"] = str(bundle_root)
        contract["entry_html_path"] = str(bundle_root / str(contract.get("entry_html") or "index.html"))

    should_emit_only = dry_run or json_output or desktop
    if should_emit_only:
        if json_output:
            typer.echo(json.dumps(contract, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"feature         : {contract.get('feature') or 'unresolved'}")
            typer.echo(f"version         : {contract.get('version')}")
            typer.echo(f"mode            : {contract.get('mode')}")
            typer.echo(f"readiness       : {contract.get('readiness_status')}")
            typer.echo(f"failure_reason  : {contract.get('failure_reason') or 'none'}")
            typer.echo(f"prototype_root  : {contract.get('prototype_root') or 'missing'}")
            typer.echo(f"entry_html      : {contract.get('entry_html') or 'missing'}")
            typer.echo(f"board_url       : {contract.get('board_url') or 'n/a'}")
        if str(contract.get("readiness_status") or "") == "ready" or desktop:
            raise typer.Exit(0)
        raise typer.Exit(2)

    if str(contract.get("readiness_status") or "") != "ready":
        typer.echo(str(contract.get("failure_reason") or "board is not ready"), err=True)
        raise typer.Exit(2)

    prototype_root = Path(str(contract.get("prototype_root") or ""))
    if not prototype_root.exists():
        typer.echo(f"prototype root missing: {prototype_root}", err=True)
        raise typer.Exit(2)

    entry_html = str(contract.get("entry_html") or "").strip()
    bundle_root = Path(str(contract.get("bundle_root") or "")) if str(contract.get("bundle_root") or "").strip() else Path(ensure_board_runtime_bundle(project_root, contract))
    handler = partial(SimpleHTTPRequestHandler, directory=str(bundle_root))

    try:
        with ThreadingHTTPServer((host, port), handler) as server:
            resolved_port = int(server.server_address[1])
            url = f"http://{host}:{resolved_port}/{entry_html}" if entry_html else f"http://{host}:{resolved_port}/"
            typer.echo(f"Beacon board ready: {url}")
            typer.echo(f"prototype_root: {prototype_root}")
            typer.echo(f"bundle_root: {bundle_root}")
            if open_browser:
                try:
                    webbrowser.open(url)
                except Exception:  # noqa: BLE001
                    pass
            server.serve_forever()
    except OSError as exc:
        typer.echo(f"board launch failed: {exc}", err=True)
        raise typer.Exit(2) from exc


@app.command("dispatch")
def dispatch(
    action: str = typer.Argument(..., help="Action id: continue|stop|retry|repair"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    feature: str = typer.Option("", "--feature", help="Prototype feature to dispatch against"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host for contract resolution"),
    port: int = typer.Option(4173, "--port", help="Port for contract resolution"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Resolve dispatch contract without execution"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Dispatch one operator action through the existing Beacon CLI contract."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "board dispatch")
    contract = build_board_launcher_contract(
        project_root,
        version=resolved_version,
        feature=feature or None,
        host=host,
        port=port,
        desktop=False,
        open_browser=False,
    )
    selected = _resolve_board_action(contract, str(action or "").strip())
    if not selected:
        payload = {
            "status": "blocked",
            "reason_code": "board_action_not_found",
            "action": action,
            "feature": contract.get("feature", ""),
            "version": resolved_version,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Board action not found: {action}", err=True)
        raise typer.Exit(2)

    payload = {
        "status": "planned" if dry_run else "ready",
        "feature": contract.get("feature", ""),
        "version": resolved_version,
        "action": selected,
        "readiness_status": contract.get("readiness_status", ""),
    }
    availability = str(selected.get("availability") or "")
    command = str(selected.get("command") or "")

    if dry_run:
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"action      : {selected.get('action_id')}")
            typer.echo(f"availability: {availability}")
            typer.echo(f"command     : {command or 'n/a'}")
        raise typer.Exit(0)

    if str(contract.get("readiness_status") or "") != "ready":
        payload.update({"status": "blocked", "reason_code": "board_not_ready"})
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(str(contract.get("failure_reason") or "board is not ready"), err=True)
        raise typer.Exit(2)

    if availability == "unavailable" or not command:
        payload.update({"status": "blocked", "reason_code": "board_action_unavailable"})
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"Board action unavailable: {action}", err=True)
        raise typer.Exit(2)

    exit_code, result = _run_board_action_command(project_root, command)
    payload.update({"status": "completed" if exit_code == 0 else "failed", "execution": result})
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Board dispatch status: {payload['status']}")
        typer.echo(f"command: {command}")
    raise typer.Exit(exit_code)
