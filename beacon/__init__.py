#!/usr/bin/env python3
"""Beacon CLI - AI Product Workflow Toolkit"""

from .commands import (
    run,
    doctor,
    gate,
    init,
    status,
    report,
    debug,
    feedback,
)
from .commands.resume import resume_entry

__version__ = "1.0.3"
__toolkit_version__ = "v1.0.3"


def create_app():
    """Create and configure the Typer application."""
    import typer
    from typing import Optional

    app = typer.Typer(
        name="beacon",
        help="Beacon - AI Product Workflow Toolkit",
        add_completion=False,
    )

    # Version callback
    @app.callback()
    def version_callback(
        version: Optional[str] = typer.Option(
            None,
            "--version",
            "-V",
            help="Show version and exit",
        ),
    ):
        if version:
            typer.echo(f"Beacon v{__toolkit_version__}")
            raise typer.Exit()

    # Register commands
    app.add_typer(run, name="run")
    app.add_typer(doctor, name="doctor")
    app.add_typer(gate, name="gate")
    app.add_typer(init, name="init")
    app.add_typer(status, name="status")
    app.add_typer(report, name="report")
    app.add_typer(debug, name="debug")
    app.add_typer(feedback, name="feedback")
    app.command("resume")(resume_entry)

    return app


app = create_app()


if __name__ == "__main__":
    app()
