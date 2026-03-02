#!/usr/bin/env python3
"""Beacon CLI - Main entry point"""
import typer
from typing import Optional

app = typer.Typer(
    name="beacon",
    help="Beacon - AI Product Workflow Toolkit",
    add_completion=False,
)


@app.callback()
def main_callback(
    version: Optional[str] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit",
    ),
):
    """Beacon - AI Product Workflow Toolkit"""
    if version:
        typer.echo("Beacon v1.0.0")
        raise typer.Exit()


# Import and register commands
from beacon.commands.run import app as run_app
from beacon.commands.doctor import app as doctor_app
from beacon.commands.gate import app as gate_app
from beacon.commands.init import app as init_app
from beacon.commands.status import app as status_app
from beacon.commands.report import app as report_app
from beacon.commands.debug import app as debug_app
from beacon.commands.feedback import app as feedback_app
from beacon.commands.resume import app as resume_app
from beacon.commands.think import app as think_app
from beacon.commands.user_story import app as user_story_app
from beacon.commands.prd import app as prd_app
from beacon.commands.test_case import app as test_case_app
from beacon.commands.workflow import app as workflow_app

app.add_typer(run_app, name="run")
app.add_typer(doctor_app, name="doctor")
app.add_typer(gate_app, name="gate")
app.add_typer(init_app, name="init")
app.add_typer(status_app, name="status")
app.add_typer(report_app, name="report")
app.add_typer(debug_app, name="debug")
app.add_typer(feedback_app, name="feedback")
app.add_typer(resume_app, name="resume")
app.add_typer(think_app, name="think")
app.add_typer(user_story_app, name="user-story")
app.add_typer(prd_app, name="prd")
app.add_typer(test_case_app, name="test-case")
app.add_typer(workflow_app, name="workflow")


if __name__ == "__main__":
    app()
