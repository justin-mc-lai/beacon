"""Beacon ask command - natural language entrypoint for skill triggering."""

from __future__ import annotations

from typing import Optional

import typer

from beacon.commands.prompt import _optimize_impl


def ask_entry(
    goal: str = typer.Argument(..., help="Natural-language goal."),
    project_root: str = typer.Option("", "--project-root", "-p", help="Project root path"),
    version: str = typer.Option("auto", "--version", help="Version context for generated command."),
    router_mode: str = typer.Option("auto", "--router-mode", help="Router mode: auto/rule/llm."),
    execute: bool = typer.Option(
        True,
        "--execute/--plan-only",
        help="Execute routed command by default; use --plan-only to only preview plan.",
    ),
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
    """Route one natural-language prompt to Beacon skill command."""
    code = _optimize_impl(
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
    raise typer.Exit(code=code)
