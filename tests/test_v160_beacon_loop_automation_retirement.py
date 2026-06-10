from __future__ import annotations

import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.command_catalog import DEFAULT_USER_SURFACE, SUPPORTED_SUBCOMMANDS
from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def test_v160_automation_is_not_active_command_surface() -> None:
    assert "automation" not in DEFAULT_USER_SURFACE
    assert "automation" not in SUPPORTED_SUBCOMMANDS

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "automation" not in result.stdout


def test_v160_old_automation_queue_job_assets_are_retired() -> None:
    queue = "beacon-" + "automation-" + "queue"
    hourly = "beacon-" + "hourly-" + "qa"
    repair = "repair-" + "window"
    result = subprocess.run(
        [
            "rg",
            f"{queue}|{hourly}|{repair}",
            "beacon",
            "automation",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1, result.stdout


def test_v160_active_surfaces_do_not_recommend_old_automation_or_lfg() -> None:
    forbidden = [
        "beacon automation init",
        "beacon automation capabilities",
        "beacon automation validate-queue",
        "beacon automation summarize-qa",
        "beacon automation build-summary",
        "beacon automation update-queue",
        "beacon-loop lfg",
    ]
    active_paths = [
        ROOT / "beacon",
        ROOT / "automation",
        ROOT / "packages" / "beacon-loop" / "src",
        ROOT / "skills",
        ROOT / ".agents" / "skills",
    ]
    for phrase in forbidden:
        result = subprocess.run(
            ["rg", "--fixed-strings", phrase, *[str(path.relative_to(ROOT)) for path in active_paths if path.exists()]],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1, result.stdout


def test_v160_automation_module_is_blocking_stub_only() -> None:
    from beacon.commands.automation import app as automation_app

    result = runner.invoke(automation_app, ["--json"])

    assert result.exit_code == 2
    assert "automation_retired_use_beacon_loop_goal" in result.stdout
    assert "beacon-loop goal" in result.stdout
