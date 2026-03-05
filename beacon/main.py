"""Beacon CLI - Main entry point."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer


def _pin_beacon_import_path() -> None:
    """Ensure imports resolve from the same package root as this module.

    This guards against mixed PYTHONPATH environments where multiple `beacon`
    project roots exist (e.g., editable install + skills mirror).
    """
    package_dir = Path(__file__).resolve().parent
    package_root = str(package_dir.parent)

    # Always prioritize current package root.
    sys.path = [package_root, *[p for p in sys.path if p != package_root]]

    # Force package __path__ to this concrete directory only.
    pkg = sys.modules.get("beacon")
    if pkg is not None and hasattr(pkg, "__path__"):
        try:
            pkg.__path__ = [str(package_dir)]
        except Exception:  # noqa: BLE001
            pass


_pin_beacon_import_path()

app = typer.Typer(
    name="beacon",
    help="Beacon - AI Product Workflow Toolkit",
    add_completion=False,
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def _main_callback(
    version_flag: bool = typer.Option(
        False,
        "--version",
        "-V",
        is_eager=True,
        help="Show beacon version and exit",
    )
):
    if version_flag:
        typer.echo("Beacon CLI v1.0.3")
        raise typer.Exit()


# Import and register commands
from .commands.run import app as run_app
from .commands.doctor import app as doctor_app
from .commands.gate import app as gate_app
from .commands.init import app as init_app
from .commands.status import app as status_app
from .commands.report import app as report_app
from .commands.debug import app as debug_app
from .commands.feedback import app as feedback_app
from .commands.resume import resume_entry
from .commands.think import app as think_app
from .commands.user_story import app as user_story_app
from .commands.prd import app as prd_app
from .commands.test_case import app as test_case_app
from .commands.workflow import app as workflow_app

# Planning & Analysis commands
from .commands.analyze import app as analyze_app
from .commands.brainstorm import app as brainstorm_app
from .commands.design import app as design_app
from .commands.jtbd import app as jtbd_app
from .commands.version import app as version_app
from .commands.roadmap import app as roadmap_app
from .commands.persona import app as persona_app
from .commands.kano import app as kano_app
from .commands.moscow import app as moscow_app
from .commands.evolution_summary import app as evolution_summary_app

# Testing & Release commands
from .commands.auto_test import app as auto_test_app
from .commands.test_progress import app as test_progress_app
from .commands.release import app as release_app
from .commands.api_design import app as api_design_app
from .commands.data_dictionary import app as data_dictionary_app

# Design & Collaboration commands
from .commands.ui_spec import app as ui_spec_app
from .commands.wireframe import app as wireframe_app
from .commands.save import app as save_app
from .commands.recall import app as recall_app
from .commands.remember import app as remember_app
from .commands.team import app as team_app
from .commands.ralph_bridge import app as ralph_bridge_app

app.add_typer(run_app, name="run")
app.add_typer(doctor_app, name="doctor")
app.add_typer(gate_app, name="gate")
app.add_typer(init_app, name="init")
app.add_typer(status_app, name="status")
app.add_typer(report_app, name="report")
app.add_typer(debug_app, name="debug")
app.add_typer(feedback_app, name="feedback")
app.add_typer(think_app, name="think")
app.add_typer(user_story_app, name="user-story")
app.add_typer(prd_app, name="prd")
app.add_typer(test_case_app, name="test-case")
app.add_typer(workflow_app, name="workflow")

# Planning & Analysis commands
app.add_typer(analyze_app, name="analyze")
app.add_typer(brainstorm_app, name="brainstorm")
app.add_typer(design_app, name="design")
app.add_typer(jtbd_app, name="jtbd")
app.add_typer(version_app, name="version")
app.add_typer(roadmap_app, name="roadmap")
app.add_typer(persona_app, name="persona")
app.add_typer(kano_app, name="kano")
app.add_typer(moscow_app, name="moscow")
app.add_typer(evolution_summary_app, name="evolution-summary")

# Testing & Release commands
app.add_typer(auto_test_app, name="auto-test")
app.add_typer(test_progress_app, name="test-progress")
app.add_typer(release_app, name="release")
app.add_typer(api_design_app, name="api-design")
app.add_typer(data_dictionary_app, name="data-dictionary")

# Design & Collaboration commands
app.add_typer(ui_spec_app, name="ui-spec")
app.add_typer(wireframe_app, name="wireframe")
app.add_typer(save_app, name="save")
app.add_typer(recall_app, name="recall")
app.add_typer(remember_app, name="remember")
app.add_typer(team_app, name="team")
app.add_typer(ralph_bridge_app, name="ralph-bridge")
app.command("resume")(resume_entry)


@app.command("work")
def work_alias(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    auto: bool = typer.Option(False, "--auto", "-a", help="Auto-run all stages"),
    skip: Optional[str] = typer.Option(None, "--skip", "-s", help="Skip stages"),
):
    """Alias of `workflow start` for PTK/Skill compatibility."""
    from .commands.workflow import start as workflow_start

    workflow_start(feature=feature, project=project, version=version, auto=auto, skip=skip)


if __name__ == "__main__":
    app()
