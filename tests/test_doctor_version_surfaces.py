from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.doctor_diagnostics import build_doctor_payload


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_self_repo_surfaces(root: Path, *, manifest_package: str = "1.4.0", manifest_runtime: str = "v1.4.0") -> None:
    (root / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "skills" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / ".trae" / "rules").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "state").mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: beacon",
                "version: 1.3.11",
                "description: test",
                "---",
                "",
                "> **Skill Version**: v1.3.11",
                "> **CLI Version**: v1.3.11",
                "",
                "- **当前发布线**：`v1.3.11`",
                "- **当前包版本**：`1.3.11`",
                "- **最新已接受文档线**：`v1.3.11`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (root / "beacon" / "__init__.py").write_text(
        '__version__ = "1.3.11"\n__toolkit_version__ = "v1.3.11"\n',
        encoding="utf-8",
    )
    (root / "beacon" / "version-truth.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "package_version": manifest_package,
                "runtime_version": manifest_runtime,
                "docs_default_line": manifest_runtime,
                "current_runtime_release_line": manifest_runtime,
                "planning_lines": [],
                "partial_runtime_supplement_lines": [],
                "lines": {
                    "v1.3.11": {"status": "historical_release"},
                    manifest_runtime: {"status": "current_runtime_release"},
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "skills" / "beacon" / "metadata.json").write_text(
        json.dumps(
            {
                "name": "beacon",
                "version": "1.3.11",
                "skills": "./",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / ".trae" / "rules" / "project_rules.md").write_text(
        "\n".join(
            [
                "<!-- BEACON:AGENT_SURFACE:START -->",
                "<!-- BEACON:VERSION:v1.3.11 -->",
                "<!-- BEACON:DOCS_VERSION:v1.3.11 -->",
                "# Beacon Trae Project Rules",
                "<!-- BEACON:AGENT_SURFACE:END -->",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / ".beacon" / "state" / "agent-surfaces.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "runtime_version": "v1.3.11",
                "docs_version": "v1.3.11",
                "agents": {"trae": {"agent": "trae"}},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_sync_version_surfaces_should_project_manifest_into_managed_surfaces(tmp_path: Path):
    _seed_self_repo_surfaces(tmp_path)

    result = _invoke(
        [
            "doctor",
            "sync-version-surfaces",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["action"] == "sync-version-surfaces"
    assert payload["status"] == "PASS"
    assert payload["result"]["changed_surface_count"] >= 4

    init_text = (tmp_path / "beacon" / "__init__.py").read_text(encoding="utf-8")
    assert '__version__ = "1.4.0"' in init_text
    assert '__toolkit_version__ = "v1.4.0"' in init_text

    skill_metadata = json.loads((tmp_path / "skills" / "beacon" / "metadata.json").read_text(encoding="utf-8"))
    assert skill_metadata["version"] == "1.4.0"

    root_skill = (tmp_path / "SKILL.md").read_text(encoding="utf-8")
    assert "version: 1.4.0" in root_skill
    assert "> **Skill Version**: v1.4.0" in root_skill
    assert "> **CLI Version**: v1.4.0" in root_skill
    assert "- **当前发布线**：`v1.4.0`" in root_skill
    assert "- **当前包版本**：`1.4.0`" in root_skill
    assert "- **最新已接受文档线**：`v1.4.0`" in root_skill

    rules_text = (tmp_path / ".trae" / "rules" / "project_rules.md").read_text(encoding="utf-8")
    assert "<!-- BEACON:VERSION:v1.4.0 -->" in rules_text
    assert "<!-- BEACON:DOCS_VERSION:v1.4.0 -->" in rules_text

    state = json.loads((tmp_path / ".beacon" / "state" / "agent-surfaces.json").read_text(encoding="utf-8"))
    assert state["runtime_version"] == "v1.4.0"
    assert state["docs_version"] == "v1.4.0"


def test_verify_version_surfaces_should_block_when_drift_exists_in_strict_mode(tmp_path: Path):
    _seed_self_repo_surfaces(tmp_path)

    result = _invoke(
        [
            "doctor",
            "verify-version-surfaces",
            "--project-root",
            str(tmp_path),
            "--strict",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["action"] == "verify-version-surfaces"
    assert payload["status"] == "BLOCKED"
    failed = {item["name"]: item["status"] for item in payload["result"]["checks"]}
    assert failed["beacon_init_surface"] == "fail"
    assert failed["skill_metadata_surface"] == "fail"
    assert failed["root_skill_md_surface"] == "fail"
    assert failed["trae_rules_surface"] == "fail"
    assert failed["agent_surface_state"] == "fail"


def test_verify_version_surfaces_should_pass_after_sync(tmp_path: Path):
    _seed_self_repo_surfaces(tmp_path)
    sync = _invoke(["doctor", "sync-version-surfaces", "--project-root", str(tmp_path)])
    assert sync.exit_code == 0, sync.stdout

    verify = _invoke(
        [
            "doctor",
            "verify-version-surfaces",
            "--project-root",
            str(tmp_path),
            "--strict",
            "--json",
        ]
    )
    assert verify.exit_code == 0, verify.stdout
    payload = json.loads(verify.stdout)
    assert payload["status"] == "PASS"
    assert all(item["status"] == "pass" for item in payload["result"]["checks"])


def test_doctor_diagnose_should_report_version_surface_governance_drift(tmp_path: Path):
    _seed_self_repo_surfaces(tmp_path)
    payload = build_doctor_payload(tmp_path, strict=False)

    assert payload["compatibility_checks"]["version_surface_governance"]["status"] in {"WARN", "FAIL"}
    repair = payload["compatibility_checks"]["version_surface_governance"]["repair"]
    assert "beacon doctor sync-version-surfaces --project-root" in repair[0]
    assert "beacon doctor verify-version-surfaces --project-root" in repair[1]
    assert "--strict" in repair[1]
    incompatibility_codes = {item["code"] for item in payload["incompatibilities"]}
    assert "COMP-102" in incompatibility_codes


def test_doctor_diagnose_should_clear_version_surface_governance_after_sync(tmp_path: Path):
    _seed_self_repo_surfaces(tmp_path)
    sync = _invoke(["doctor", "sync-version-surfaces", "--project-root", str(tmp_path)])
    assert sync.exit_code == 0, sync.stdout

    payload = build_doctor_payload(tmp_path, strict=False)
    assert payload["compatibility_checks"]["version_surface_governance"]["status"] == "PASS"
