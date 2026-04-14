"""Shared Typer app factory to keep entrypoints consistent."""

from __future__ import annotations

import os
from typing import Optional

import typer

from .command_catalog import ADVANCED_SURFACE, BRIDGE_COMMANDS, CORE_COMMANDS, DEPRECATED_COMMANDS, LABS_COMMANDS, SUPPORT_COMMANDS


def build_app(*, package_version: str) -> typer.Typer:
    show_labs = str(os.environ.get("BEACON_LABS", "")).strip().lower() in {"1", "true", "yes", "on"}
    show_bridge = str(os.environ.get("BEACON_ADVANCED", "")).strip().lower() in {"1", "true", "yes", "on"}
    app = typer.Typer(
        name="beacon",
        help=(
            "Beacon - Evidence-first Product Workflow Kernel\n\n"
            "Mainline: think -> user-story -> prd -> test-case -> implement -> qa -> gate -> release"
        ),
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
            typer.echo(f"Beacon CLI v{package_version}")
            raise typer.Exit()

    setattr(
        app,
        "beacon_layers",
        {
            "core": CORE_COMMANDS,
            "support": SUPPORT_COMMANDS,
            "advanced": ADVANCED_SURFACE,
            "labs": LABS_COMMANDS,
            "bridge": BRIDGE_COMMANDS,
            "deprecated": DEPRECATED_COMMANDS,
        },
    )

    labs_app = typer.Typer(
        name="labs",
        help="Optional analysis/template commands outside Beacon default core surface.",
    )
    bridge_app = typer.Typer(
        name="bridge",
        help="Experimental bridge/runtime commands outside Beacon default core surface.",
    )

    # Import and register commands
    from .commands.run import app as run_app
    from .commands.doctor import app as doctor_app
    from .commands.freeze import freeze_entry
    from .commands.reopen import reopen_entry
    from .commands.gate import app as gate_app
    from .commands.init import app as init_app
    from .commands.status import app as status_app
    from .commands.report import app as report_app
    from .commands.review import app as review_app
    from .commands.skill import app as skill_app
    from .commands.profile import app as profile_app
    from .commands.implement import app as implement_app
    from .commands.verify import app as verify_app
    from .commands.orchestrate import app as orchestrate_app
    from .commands.debug import app as debug_app
    from .commands.feedback import app as feedback_app
    from .commands.help import help_entry
    from .commands.ask import ask_entry
    from .commands.prompt import app as prompt_app
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
    from .commands.qa import app as qa_app
    from .commands.test_progress import app as test_progress_app
    from .commands.release import app as release_app
    from .commands.api_design import app as api_design_app
    from .commands.data_dictionary import app as data_dictionary_app

    # Design & Collaboration commands
    from .commands.ui_spec import app as ui_spec_app
    from .commands.wireframe import app as wireframe_app
    from .commands.prototype import app as prototype_app
    from .commands.save import app as save_app
    from .commands.recall import app as recall_app
    from .commands.remember import app as remember_app
    from .commands.team import app as team_app
    from .commands.ralph_bridge import app as ralph_bridge_app

    app.add_typer(think_app, name="think")
    app.add_typer(user_story_app, name="user-story")
    app.add_typer(prd_app, name="prd")
    app.add_typer(test_case_app, name="test-case")
    app.add_typer(implement_app, name="implement")
    app.add_typer(qa_app, name="qa")
    app.add_typer(gate_app, name="gate")
    app.add_typer(release_app, name="release")
    app.command("ask")(ask_entry)
    app.command("help")(help_entry)
    app.add_typer(status_app, name="status")
    app.add_typer(doctor_app, name="doctor")
    app.add_typer(workflow_app, name="workflow")
    app.add_typer(init_app, name="init")
    app.add_typer(profile_app, name="profile")
    app.add_typer(skill_app, name="skill")
    app.add_typer(run_app, name="run", hidden=True)
    app.command("freeze")(freeze_entry)
    app.command("reopen")(reopen_entry)
    app.add_typer(report_app, name="report")
    app.add_typer(review_app, name="review")
    app.add_typer(verify_app, name="verify")
    app.add_typer(orchestrate_app, name="orchestrate")
    app.add_typer(debug_app, name="debug")
    app.add_typer(feedback_app, name="feedback", hidden=True)
    app.add_typer(prompt_app, name="prompt", hidden=True)

    # Planning & Analysis commands
    app.add_typer(analyze_app, name="analyze", hidden=True)
    app.add_typer(brainstorm_app, name="brainstorm", hidden=True)
    app.add_typer(design_app, name="design", hidden=True)
    app.add_typer(jtbd_app, name="jtbd", hidden=True)
    app.add_typer(version_app, name="version")
    app.add_typer(roadmap_app, name="roadmap", hidden=True)
    app.add_typer(persona_app, name="persona", hidden=True)
    app.add_typer(kano_app, name="kano", hidden=True)
    app.add_typer(moscow_app, name="moscow", hidden=True)
    app.add_typer(evolution_summary_app, name="evolution-summary", hidden=True)

    # Testing & Release commands
    app.add_typer(auto_test_app, name="auto-test", hidden=True)
    app.add_typer(test_progress_app, name="test-progress", hidden=True)
    app.add_typer(api_design_app, name="api-design", hidden=True)
    app.add_typer(data_dictionary_app, name="data-dictionary", hidden=True)

    # Design & Collaboration commands
    app.add_typer(ui_spec_app, name="ui-spec", hidden=True)
    app.add_typer(wireframe_app, name="wireframe", hidden=True)
    app.add_typer(prototype_app, name="prototype")
    app.add_typer(save_app, name="save", hidden=True)
    app.add_typer(recall_app, name="recall", hidden=True)
    app.add_typer(remember_app, name="remember", hidden=True)
    app.add_typer(team_app, name="team", hidden=True)
    app.add_typer(ralph_bridge_app, name="ralph-bridge", hidden=True)
    app.command("resume")(resume_entry)

    labs_app.add_typer(analyze_app, name="analyze")
    labs_app.add_typer(api_design_app, name="api-design")
    labs_app.add_typer(brainstorm_app, name="brainstorm")
    labs_app.add_typer(data_dictionary_app, name="data-dictionary")
    labs_app.add_typer(design_app, name="design")
    labs_app.add_typer(jtbd_app, name="jtbd")
    labs_app.add_typer(kano_app, name="kano")
    labs_app.add_typer(moscow_app, name="moscow")
    labs_app.add_typer(persona_app, name="persona")
    labs_app.add_typer(roadmap_app, name="roadmap")
    labs_app.add_typer(ui_spec_app, name="ui-spec")
    labs_app.add_typer(wireframe_app, name="wireframe")

    bridge_app.add_typer(run_app, name="run")
    bridge_app.add_typer(team_app, name="team")
    bridge_app.add_typer(ralph_bridge_app, name="ralph")

    app.add_typer(labs_app, name="labs", hidden=not show_labs)
    app.add_typer(bridge_app, name="bridge", hidden=not show_bridge)

    @app.command("work", hidden=True)
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

    return app
