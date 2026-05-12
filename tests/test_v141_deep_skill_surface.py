from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.command_catalog import CORE_COMMANDS, SUPPORT_COMMANDS, SUPPORTED_SUBCOMMANDS
from beacon.main import app

from v141_deep_helpers import FEATURE, VERSION, seed_deep_project

runner = CliRunner()


def test_support_skill_boundary() -> None:
    assert "deep" in SUPPORT_COMMANDS
    assert "deep" in SUPPORTED_SUBCOMMANDS
    assert "deep" not in CORE_COMMANDS

    host_skill = Path("skills/beacon/SKILL.md").read_text(encoding="utf-8")
    assert "`beacon-deep`" in host_skill
    assert "deep analysis support surface" in host_skill

    subskill = Path("skills/beacon/beacon-deep/SKILL.md").read_text(encoding="utf-8")
    assert "name: beacon-deep" in subskill
    assert "beacon deep run" in subskill
    assert "not a primary lifecycle stage" in subskill


def test_deep_run_public_entry(tmp_path: Path) -> None:
    seed_deep_project(tmp_path)

    result = runner.invoke(
        app,
        [
            "deep",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "closed"
    assert payload["feature"] == FEATURE
    assert payload["artifact_refs"]["loop_trace"]["json"].endswith("deep-loop-trace.json")


def test_deep_run_should_use_runtime_capability_not_target_docs_version(tmp_path: Path) -> None:
    legacy_docs_version = "v1.3.5"
    seed_deep_project(tmp_path, feature="Legacy Deep Feature", docs_version=legacy_docs_version)

    result = runner.invoke(
        app,
        [
            "deep",
            "run",
            "Legacy Deep Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            legacy_docs_version,
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "closed"
    assert payload["version"] == legacy_docs_version
    assert payload["artifact_refs"]["loop_trace"]["json"].startswith(
        f"docs/beacon/{legacy_docs_version}/.machine/deep/legacy-deep-feature/"
    )


def test_internal_toolkits_do_not_expand_lifecycle() -> None:
    internal_toolkits = {
        "beacon-toolkit-deep-loop",
        "beacon-toolkit-state-machine",
        "beacon-toolkit-test-delta",
        "beacon-toolkit-risk-register",
    }
    assert not (internal_toolkits & set(CORE_COMMANDS))
    assert not (internal_toolkits & set(SUPPORTED_SUBCOMMANDS))
