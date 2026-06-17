"""Agent Eval CLI — public entry `beacon eval`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.agent_eval_kit import (
    AGENT_EVAL_VERSION,
    build_agent_eval_scorecard,
    materialize_agent_eval_catalog,
    run_agent_eval,
    run_agent_eval_benchmark,
)
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(
    name="eval",
    help="Beacon Agent Eval scorecard harness (runtime evidence only).",
    no_args_is_help=True,
)


@app.command("catalog")
def catalog_cmd(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    materialize: bool = typer.Option(False, "--materialize", help="Write catalog and live skill matrix JSON"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Materialize or inspect the Agent Eval capability catalog."""
    root = Path(project_root).resolve() if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    if materialize or not json_output:
        payload = materialize_agent_eval_catalog(root, version=resolved_version)
    else:
        from beacon.utils.agent_eval_kit import catalog_path

        path = catalog_path(root, resolved_version)
        payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else materialize_agent_eval_catalog(root, version=resolved_version)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        if payload.get("status") == "blocked" and payload.get("blocked"):
            raise typer.Exit(2)
        return
    typer.echo(f"✓ Agent Eval catalog: {payload.get('path')}")


@app.command("run")
def run_cmd(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    split: str = typer.Option("regression-core", "--split", help="regression-core|optimization|holdout|all"),
    runner: str = typer.Option("replay", "--runner", help="replay|simulated|live"),
    live_tier: Optional[str] = typer.Option(
        None,
        "--live-tier",
        help="local_admitted|release_hook|ci_default (live runner only)",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Run Agent Eval cases and write runtime traces."""
    root = Path(project_root).resolve() if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    payload = run_agent_eval(
        root,
        split=split,
        runner=runner,
        version=resolved_version,
        live_tier=live_tier,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        if payload.get("status") == "blocked" or payload.get("status") == "fail":
            raise typer.Exit(2)
        return
    typer.echo(f"✓ Agent Eval run: {payload.get('metrics_path') or payload.get('reason_code')}")


@app.command("scorecard")
def scorecard_cmd(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", "-v", help="Docs version"),
    runner: Optional[str] = typer.Option(None, "--runner", help="replay|simulated|live"),
    live_tier: Optional[str] = typer.Option(
        None,
        "--live-tier",
        help="local_admitted|release_hook|ci_default (when synthesizing from live run)",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Synthesize Agent Eval dimension scores and composite scorecard."""
    root = Path(project_root).resolve() if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    if runner == "live" and live_tier:
        run_agent_eval(root, split="regression-core", runner="live", version=resolved_version, live_tier=live_tier)
    payload = build_agent_eval_scorecard(root, version=resolved_version, runner=runner)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        if payload.get("status") == "blocked":
            raise typer.Exit(2)
        return
    typer.echo(f"✓ Agent Eval scorecard: {payload.get('path')}")


@app.command("benchmark")
def benchmark_cmd(
    project_root: str = typer.Option("", "--project-root", "--project", "-p", help="Project root path"),
    version: str = typer.Option(AGENT_EVAL_VERSION, "--version", "-v", help="Benchmark case set version"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
):
    """Run Agent Eval benchmark and write behavior evidence artifacts."""
    root = Path(project_root).resolve() if project_root else Path.cwd()
    resolved_version = resolve_target_version(root, version)
    payload = run_agent_eval_benchmark(root, version=resolved_version)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        if payload.get("status") != "pass":
            raise typer.Exit(2)
        return
    typer.echo(f"✓ Agent Eval benchmark: {payload.get('root')}")
