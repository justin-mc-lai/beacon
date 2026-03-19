"""v1.1.0 prompt catalog contracts."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.command_catalog import SUPPORTED_SUBCOMMANDS
from beacon.utils.intent_router import DEFAULT_ROUTABLE_INTENTS, SUPPORTED_INTENTS

runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_prompt_catalog_should_cover_routable_intents(tmp_path: Path):
    result = _invoke([
        "prompt",
        "catalog",
        "--project-root",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "--json",
    ])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    routable = set(payload.get("routable_intents", []))
    expected = set(DEFAULT_ROUTABLE_INTENTS)
    assert routable == expected

    explicit_only = set(payload.get("explicit_only_intents", []))
    assert explicit_only == {intent for intent in SUPPORTED_INTENTS if intent not in expected and intent != "outside-boundary"}


def test_non_routable_commands_should_have_explicit_fallbacks(tmp_path: Path):
    result = _invoke([
        "prompt",
        "catalog",
        "--project-root",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "--json",
    ])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    routable = set(payload.get("routable_intents", []))
    explicit_only = set(payload.get("explicit_only_intents", []))
    expected_non_routable = sorted([cmd for cmd in SUPPORTED_SUBCOMMANDS if cmd not in routable and cmd not in explicit_only])
    assert payload.get("non_routable_commands", []) == expected_non_routable

    fallback = payload.get("fallback_commands", {})
    assert isinstance(fallback, dict)
    assert all(str(fallback.get(cmd, "")).strip() for cmd in expected_non_routable)


def test_prompt_catalog_should_include_omc_omx_team_templates(tmp_path: Path):
    result = _invoke([
        "prompt",
        "catalog",
        "--project-root",
        str(tmp_path),
        "--version",
        "v1.1.0",
        "--json",
    ])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    templates = "\n".join(payload.get("omc_omx_team_templates", []))
    assert "omc run" in templates
    assert "omx run" in templates
    assert "beacon team start" in templates


def test_prompt_optimize_should_output_boundary_safe_command_pack(tmp_path: Path):
    result = _invoke([
        "prompt",
        "optimize",
        "请先检查 gate 并直接写代码上线",
        "--project-root",
        str(tmp_path),
        "--json",
    ])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    pack = payload.get("boundary_safe_command_pack", {})
    assert isinstance(pack, dict)
    assert pack.get("boundary_state") == "mixed_need_confirm"
    fallback_commands = pack.get("fallback_commands", [])
    assert isinstance(fallback_commands, list)
    assert any("--plan-only" in cmd for cmd in fallback_commands)
