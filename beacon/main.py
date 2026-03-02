"""Beacon CLI - Main entry point"""
import typer
from typing import Optional

app = typer.Typer(
    name="beacon",
    help="Beacon - AI Product Workflow Toolkit",
    add_completion=False,
)


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

# Planning & Analysis commands
from beacon.commands.analyze import app as analyze_app
from beacon.commands.brainstorm import app as brainstorm_app
from beacon.commands.design import app as design_app
from beacon.commands.jtbd import app as jtbd_app
from beacon.commands.version import app as version_app
from beacon.commands.roadmap import app as roadmap_app
from beacon.commands.persona import app as persona_app
from beacon.commands.kano import app as kano_app
from beacon.commands.moscow import app as moscow_app
from beacon.commands.evolution_summary import app as evolution_summary_app

# Testing & Release commands
from beacon.commands.auto_test import app as auto_test_app
from beacon.commands.test_progress import app as test_progress_app
from beacon.commands.release import app as release_app
from beacon.commands.api_design import app as api_design_app
from beacon.commands.data_dictionary import app as data_dictionary_app

# Design & Collaboration commands
from beacon.commands.ui_spec import app as ui_spec_app
from beacon.commands.wireframe import app as wireframe_app
from beacon.commands.save import app as save_app
from beacon.commands.recall import app as recall_app
from beacon.commands.remember import app as remember_app
from beacon.commands.team import app as team_app
from beacon.commands.ralph_bridge import app as ralph_bridge_app

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


@app.command()
def version():
    """Show beacon version"""
    typer.echo("Beacon CLI v1.0.0")


if __name__ == "__main__":
    app()
