"""Beacon prompt command (NL intent routing + optimization)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import typer
from typer.testing import CliRunner

from beacon.utils.intent_router import optimize_prompt_to_plan
from beacon.utils.runtime import now_iso

app = typer.Typer(
    name="prompt",
    help="Optimize natural language prompts into executable beacon command plans.",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _execute_recommended_command(args: list[str]) -> dict[str, Any]:
    from beacon.main import app as beacon_app

    runner = CliRunner()
    result = runner.invoke(beacon_app, args)
    return {
        "args": args,
        "exit_code": int(result.exit_code),
        "stdout": result.stdout,
    }


def _resolve_min_confidence(plan: dict[str, Any], min_confidence: Optional[float]) -> float:
    if min_confidence is not None:
        try:
            return max(0.0, min(1.0, float(min_confidence)))
        except Exception:  # noqa: BLE001
            return 0.62
    policy = plan.get("execution_policy", {}) if isinstance(plan, dict) else {}
    try:
        return max(0.0, min(1.0, float(policy.get("min_confidence", 0.62))))
    except Exception:  # noqa: BLE001
        return 0.62


def _resolve_boundary_state(plan: dict[str, Any]) -> str:
    boundary = plan.get("boundary", {}) if isinstance(plan, dict) else {}
    state = str(boundary.get("state", "")).strip()
    if state:
        return state
    if plan.get("intent") == "outside-boundary":
        return "out_of_scope"
    if boundary.get("in_scope") is True:
        return "in_scope"
    return "out_of_scope"


def _append_router_history(project_root: Path, event: dict[str, Any]) -> None:
    history_path = project_root / ".beacon" / "memory" / "prompt-router-history.jsonl"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def _execution_block_reason(
    *,
    plan: dict[str, Any],
    min_confidence: float,
    allow_mixed: bool,
    allow_low_confidence: bool,
) -> str:
    boundary_state = _resolve_boundary_state(plan)
    confidence = float(plan.get("confidence", 0.0) or 0.0)

    if boundary_state == "out_of_scope":
        return "outside-beacon-boundary"
    if boundary_state == "mixed_need_confirm" and not allow_mixed:
        return "mixed-boundary-needs-confirmation"
    if confidence < min_confidence and not allow_low_confidence:
        return "low-confidence"
    return ""


def _optimize_impl(
    goal: str,
    *,
    project_root: str,
    version: str,
    router_mode: str,
    execute: bool,
    json_output: bool,
    allow_mixed: bool,
    allow_low_confidence: bool,
    min_confidence: Optional[float],
) -> int:
    root = Path(project_root) if project_root else Path.cwd()
    plan = optimize_prompt_to_plan(
        goal,
        project_root=root,
        version=version,
        router_mode=router_mode,
    )

    effective_min_confidence = _resolve_min_confidence(plan, min_confidence)
    blocked_reason = ""
    if execute:
        blocked_reason = _execution_block_reason(
            plan=plan,
            min_confidence=effective_min_confidence,
            allow_mixed=allow_mixed,
            allow_low_confidence=allow_low_confidence,
        )
        if blocked_reason:
            plan["executed"] = {
                "blocked": True,
                "reason": blocked_reason,
                "boundary_state": _resolve_boundary_state(plan),
                "min_confidence": round(effective_min_confidence, 2),
                "confidence": float(plan.get("confidence", 0.0) or 0.0),
            }
            exit_code = 2
        else:
            executed = _execute_recommended_command(list(plan.get("recommended_args", [])))
            plan["executed"] = executed
            exit_code = int(executed.get("exit_code", 1))
    else:
        exit_code = 0

    event = {
        "ts": now_iso(),
        "input_goal": goal,
        "intent": plan.get("intent", ""),
        "confidence": plan.get("confidence", 0.0),
        "router_mode": plan.get("router_mode", "rule"),
        "boundary_state": _resolve_boundary_state(plan),
        "recommended_command": plan.get("recommended_command", ""),
        "execute_requested": bool(execute),
        "execute_blocked": bool(blocked_reason),
        "block_reason": blocked_reason,
        "execute_exit_code": int(plan.get("executed", {}).get("exit_code", 0) or 0)
        if execute and not blocked_reason
        else None,
    }
    _append_router_history(root, event)

    if json_output:
        typer.echo(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        typer.echo("Beacon Prompt Optimize")
        typer.echo("=" * 24)
        typer.echo(f"intent      : {plan.get('intent')}")
        typer.echo(f"confidence  : {plan.get('confidence')}")
        typer.echo(f"router_mode : {plan.get('router_mode')}")
        typer.echo(f"command     : {plan.get('recommended_command')}")
        typer.echo(f"min_conf    : {round(effective_min_confidence, 2)}")
        typer.echo(f"boundary    : {_resolve_boundary_state(plan)}")
        for hint in plan.get("risk_hints", []):
            typer.echo(f"- risk: {hint}")
        for hint in plan.get("boundary_hints", []):
            typer.echo(f"- boundary: {hint}")
        if execute:
            executed = plan.get("executed", {})
            if executed.get("blocked"):
                typer.echo(f"execution   : blocked ({executed.get('reason', 'policy-blocked')})")
            else:
                typer.echo(f"execution   : exit_code={executed.get('exit_code')}")
                output = str(executed.get("stdout", "")).strip()
                if output:
                    typer.echo("--- command output ---")
                    typer.echo(output)
    return exit_code


@app.callback(invoke_without_command=True)
def prompt_callback(
    ctx: typer.Context,
    goal: str = typer.Option("", "--goal", "-g", help="Natural-language goal."),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", help="Version context for generated command."),
    router_mode: str = typer.Option("auto", "--router-mode", help="Router mode: auto/rule/llm."),
    execute: bool = typer.Option(False, "--execute", help="Execute recommended command."),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
    allow_mixed: bool = typer.Option(
        False,
        "--allow-mixed",
        help="Allow execution for mixed boundary prompts.",
    ),
    allow_low_confidence: bool = typer.Option(
        False,
        "--allow-low-confidence",
        help="Allow execution when intent confidence is below threshold.",
    ),
    min_confidence: Optional[float] = typer.Option(
        None,
        "--min-confidence",
        help="Execution confidence threshold override (0~1).",
    ),
):
    """Optimize prompt directly (flat syntax)."""
    if ctx.invoked_subcommand is None:
        if not goal.strip():
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        raise typer.Exit(
            code=_optimize_impl(
                goal=goal,
                project_root=project_root,
                version=version,
                router_mode=router_mode,
                execute=execute,
                json_output=json_output,
                allow_mixed=allow_mixed,
                allow_low_confidence=allow_low_confidence,
                min_confidence=min_confidence,
            )
        )


@app.command("optimize")
def optimize(
    goal: str = typer.Argument(..., help="Natural-language goal."),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", help="Version context for generated command."),
    router_mode: str = typer.Option("auto", "--router-mode", help="Router mode: auto/rule/llm."),
    execute: bool = typer.Option(False, "--execute", help="Execute recommended command."),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
    allow_mixed: bool = typer.Option(
        False,
        "--allow-mixed",
        help="Allow execution for mixed boundary prompts.",
    ),
    allow_low_confidence: bool = typer.Option(
        False,
        "--allow-low-confidence",
        help="Allow execution when intent confidence is below threshold.",
    ),
    min_confidence: Optional[float] = typer.Option(
        None,
        "--min-confidence",
        help="Execution confidence threshold override (0~1).",
    ),
):
    """Generate a normalized command plan from natural language input."""
    raise typer.Exit(
        code=_optimize_impl(
            goal=goal,
            project_root=project_root,
            version=version,
            router_mode=router_mode,
            execute=execute,
            json_output=json_output,
            allow_mixed=allow_mixed,
            allow_low_confidence=allow_low_confidence,
            min_confidence=min_confidence,
        )
    )


if __name__ == "__main__":
    app()
