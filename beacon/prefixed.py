"""Prefixed command launchers like `beacon-think` -> `beacon think`."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer

PREFIX = "beacon-"

SUPPORTED_SUBCOMMANDS = (
    "analyze",
    "api-design",
    "auto-test",
    "brainstorm",
    "data-dictionary",
    "debug",
    "design",
    "doctor",
    "evolution-summary",
    "feedback",
    "gate",
    "init",
    "jtbd",
    "kano",
    "moscow",
    "prd",
    "ralph-bridge",
    "recall",
    "release",
    "remember",
    "report",
    "resume",
    "roadmap",
    "run",
    "save",
    "status",
    "team",
    "test-case",
    "test-progress",
    "think",
    "ui-spec",
    "user-story",
    "version",
    "wireframe",
    "work",
    "workflow",
)


def resolve_prefixed_subcommand(prog_name: str) -> Optional[str]:
    """Resolve `beacon-<subcommand>` to `<subcommand>`."""
    command_name = Path(prog_name).name
    if not command_name.startswith(PREFIX):
        return None

    subcommand = command_name[len(PREFIX) :]
    if subcommand in SUPPORTED_SUBCOMMANDS:
        return subcommand
    return None


def build_prefixed_args(prog_name: str, argv: list[str]) -> list[str]:
    """Build argument list for beacon app invocation."""
    subcommand = resolve_prefixed_subcommand(prog_name)
    if subcommand is None:
        valid = ", ".join(f"{PREFIX}{name}" for name in SUPPORTED_SUBCOMMANDS)
        raise typer.BadParameter(
            f"Unknown prefixed command: {Path(prog_name).name}. "
            f"Use one of: {valid}"
        )

    return [subcommand, *argv[1:]]


def invoke_beacon_app(args: list[str], prog_name: str) -> None:
    """Invoke the main beacon typer app."""
    from .main import app

    app(args=args, prog_name=prog_name)


def main() -> None:
    """Console script entrypoint for all `beacon-<subcommand>` aliases."""
    prog_name = Path(sys.argv[0]).name
    try:
        args = build_prefixed_args(prog_name=prog_name, argv=sys.argv)
    except typer.BadParameter as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2)

    invoke_beacon_app(args=args, prog_name=prog_name)
