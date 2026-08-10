from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_release_repo(root: Path) -> None:
    (root / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "beacon" / "__init__.py").write_text(
        '__version__ = "1.1.4"\n__toolkit_version__ = "v1.1.4"\n',
        encoding="utf-8",
    )
    for version in ("v1.1.4", "v1.1.5"):
        base = root / "docs" / "beacon" / version
        (base / "release").mkdir(parents=True, exist_ok=True)
        (base / "release" / f"{version}.md").write_text(f"# Release {version}\n", encoding="utf-8")


def test_prompt_catalog_should_expose_v115_first_principles_contract(tmp_path: Path):
    _seed_release_repo(tmp_path)
    result = _invoke(["prompt", "catalog", "--project-root", str(tmp_path), "--version", "v1.1.5", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    contract = payload["first_principles_contract"]
    assert contract["enabled"] is True
    assert contract["reasoning_order"] == ["human_needs", "machine_needs", "beacon_responsibility"]
    assert contract["reading_order"][0].endswith("/SUMMARY.md")
    assert ".machine" in contract["reading_order"][2]
    assert contract["output_policy"]["progressive_disclosure"] is True
    assert contract["doctor_role"]["mode"] == "destructive_repairer"


def test_prompt_optimize_should_attach_v115_contract_and_clarification_gate(tmp_path: Path):
    _seed_release_repo(tmp_path)
    result = _invoke(["prompt", "optimize", "帮我处理一下", "--project-root", str(tmp_path), "--version", "v1.1.5", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["clarification_gate"]["required"] is True
    contract = payload["first_principles_contract"]
    assert contract["memory_contract"]["human_default"] == "consumption_projection"
    assert "compatibility_first" in contract["disallowed_defaults"]


def test_prompt_optimize_should_keep_human_first_reading_order_for_v115(tmp_path: Path):
    _seed_release_repo(tmp_path)
    result = _invoke(
        [
            "prompt",
            "optimize",
            "请帮我做登录需求澄清，并进入规范化产物流程",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.5",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    contract = payload["first_principles_contract"]
    assert contract["surface_roles"]["human_primary"][0].endswith("/SUMMARY.md")
    assert contract["surface_roles"]["machine_secondary"][0].endswith("/.machine/execution/")
    assert contract["clarification_gate"]["default_action"] == "clarify_before_execute"
