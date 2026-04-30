from __future__ import annotations

import json
import importlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.release_scorecard import build_release_scorecard
from beacon.utils.story_scenarios import expand_story_scenarios

implement_command = importlib.import_module("beacon.commands.implement")


runner = CliRunner()
VERSION = "v1.3.9"
FEATURE = "Beacon v1.3.9 runtime skill admission and host-validated third-party skill compatibility"
SLUG = "beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_skill(root: Path, *, skill_id: str, supported_hosts: list[str]) -> Path:
    skill_root = root / ".agents" / "skills" / skill_id
    skill_root.mkdir(parents=True, exist_ok=True)
    (skill_root / "SKILL.md").write_text(f"# {skill_id}\n", encoding="utf-8")
    (skill_root / "beacon-skill-contract.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "skill_id": skill_id,
                "supported_stages": ["implement"],
                "supported_host_runtimes": supported_hosts,
                "surface_kind": "content-production",
                "output_contract": {"result_file": "result.json"},
                "evidence_contract": ["acceptance_notes"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return skill_root


def _seed_project_local_skill(root: Path, *, skill_id: str, supported_hosts: list[str]) -> Path:
    skill_root = root / "skills" / skill_id
    skill_root.mkdir(parents=True, exist_ok=True)
    (skill_root / "SKILL.md").write_text(f"# {skill_id}\n", encoding="utf-8")
    (skill_root / "beacon-skill-contract.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "skill_id": skill_id,
                "supported_stages": ["implement"],
                "supported_host_runtimes": supported_hosts,
                "surface_kind": "content-production",
                "output_contract": {"result_file": "result.json"},
                "evidence_contract": ["acceptance_notes"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return skill_root


def _prepare_project(root: Path, monkeypatch) -> None:
    (root / "docs" / "beacon" / VERSION / "execution").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / VERSION / ".machine" / "execution").mkdir(parents=True, exist_ok=True)
    legacy = implement_command._legacy_cli
    monkeypatch.setattr(legacy, "evaluate_takeover_baseline_gate", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(legacy, "_run_branch_preflight", lambda *args, **kwargs: {"blocked": False, "current_branch": "beacon/v1.3.9"})
    monkeypatch.setattr(legacy, "implementation_plan_supported", lambda *args, **kwargs: False)
    monkeypatch.setattr(legacy, "load_or_build_semantic_layer", lambda *args, **kwargs: {})


def _prepare_delegation_ready_feature(root: Path, *, feature_slug: str) -> None:
    docs_root = root / "docs" / "beacon" / VERSION
    (docs_root / "prd").mkdir(parents=True, exist_ok=True)
    (docs_root / "user-story").mkdir(parents=True, exist_ok=True)
    (docs_root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs_root / ".machine" / "execution").mkdir(parents=True, exist_ok=True)
    (docs_root / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (docs_root / "prd" / f"{feature_slug}.md").write_text("# PRD\n", encoding="utf-8")
    (docs_root / "user-story" / f"{feature_slug}.md").write_text("# User Story\n", encoding="utf-8")
    (docs_root / "qa" / "test-cases" / f"{feature_slug}.md").write_text("# Test Cases\n", encoding="utf-8")
    (docs_root / ".machine" / "execution" / f"implementation-plan-{feature_slug}.json").write_text("{}", encoding="utf-8")
    (docs_root / ".machine" / "execution" / f"git-workflow-{feature_slug}.json").write_text("{}", encoding="utf-8")
    (docs_root / ".machine" / "qa" / f"{feature_slug}.ac-test-matrix.json").write_text("{}", encoding="utf-8")
    (docs_root / ".machine" / "qa" / f"{feature_slug}.qa9-matrix.json").write_text("{}", encoding="utf-8")
    (docs_root / ".machine" / "qa" / f"{feature_slug}.story-scenario-map.json").write_text("{}", encoding="utf-8")


def test_v139_implement_skill_admission_should_write_cache_and_project_delivery_contract(tmp_path: Path, monkeypatch) -> None:
    _prepare_project(tmp_path, monkeypatch)
    _seed_skill(tmp_path, skill_id="storyverse-workbench", supported_hosts=["codex", "claude"])

    result = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--runner",
            "native-single",
            "--host-runtime",
            "codex",
            "--skill",
            "storyverse-workbench",
            "--dry-run",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "dry_run"
    assert payload["skill_admission"]["status"] == "pass"
    assert payload["skill_admission"]["contract"]["surface_kind"] == "content-production"
    assert payload["delivery_contract"]["capability_snapshot"]["skill_admission_status"] == "pass"
    assert payload["delivery_contract"]["capability_snapshot"]["skill_non_code_supported"] is True
    assert (tmp_path / payload["skill_admission"]["artifacts"]["state_path"]).exists()
    assert (tmp_path / payload["skill_admission"]["artifacts"]["machine_path"]).exists()


def test_v139_implement_skill_admission_should_block_when_host_runtime_is_incompatible(tmp_path: Path, monkeypatch) -> None:
    _prepare_project(tmp_path, monkeypatch)
    _seed_skill(tmp_path, skill_id="claude-only-workbench", supported_hosts=["claude"])

    result = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--runner",
            "native-single",
            "--host-runtime",
            "codex",
            "--skill",
            "claude-only-workbench",
            "--dry-run",
            "--json",
        ]
    )

    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "skill_host_incompatible"
    assert payload["skill_admission"]["status"] == "blocked"
    assert payload["skill_admission"]["validation"]["issues"][0]["reason_code"] == "skill_host_incompatible"


def test_v139_implement_skill_admission_should_discover_project_local_skill_root(tmp_path: Path, monkeypatch) -> None:
    _prepare_project(tmp_path, monkeypatch)
    skill_root = _seed_project_local_skill(tmp_path, skill_id="inkos-novel-iteration", supported_hosts=["codex"])

    result = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--runner",
            "native-single",
            "--host-runtime",
            "codex",
            "--skill",
            "inkos-novel-iteration",
            "--dry-run",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "dry_run"
    assert payload["skill_admission"]["status"] == "pass"
    assert payload["skill_admission"]["discovery"]["skill_root"] == str(skill_root)


def test_v139_implement_skill_execution_should_block_on_native_runner_even_after_admission(tmp_path: Path, monkeypatch) -> None:
    _prepare_project(tmp_path, monkeypatch)
    _seed_project_local_skill(tmp_path, skill_id="inkos-novel-iteration", supported_hosts=["codex"])
    _prepare_delegation_ready_feature(tmp_path, feature_slug=SLUG)

    result = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--runner",
            "codex-subagents",
            "--host-runtime",
            "codex",
            "--skill",
            "inkos-novel-iteration",
            "--json",
        ]
    )

    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "native_skill_execution_unsupported"
    assert payload["status"] == "blocked"
    assert payload["skill_admission"]["status"] == "pass"


def test_v139_release_scorecard_should_surface_skill_admission_from_implement_delivery_contract(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "beacon" / VERSION
    (docs / "execution").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "qa").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "Pass", "version": VERSION, "issues": []}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "qa" / "status.json").write_text(
        json.dumps(
            {
                "feature": FEATURE,
                "version": VERSION,
                "status": "passed",
                "evidence_done": True,
                "execution_mode": "feature-aware",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (docs / "execution" / f"implementation-summary-{SLUG}.json").write_text(
        json.dumps(
            {
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "status": "completed",
                "delivery_contract": {
                    "schema_version": "1.0",
                    "feature": FEATURE,
                    "version": VERSION,
                    "host_runtime": "codex",
                    "runner": "native-single",
                    "adapter_type": "native",
                    "execution_mode": "single",
                    "effective_mode": "single",
                    "requested_mode": "single",
                    "runner_mode": "native-single",
                    "execution_surface": "native-single",
                    "capability_snapshot": {
                        "skill_admission_status": "pass",
                        "skill_id": "storyverse-workbench",
                        "skill_surface_kind": "content-production",
                        "skill_non_code_supported": True,
                    },
                    "traceability_refs": [
                        f"docs/beacon/{VERSION}/.machine/execution/skill-admission-{SLUG}.json"
                    ],
                    "risk_flags": [],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    payload = build_release_scorecard(tmp_path, version=VERSION)

    snapshot = payload["host_native_delivery"]["implement"]["capability_snapshot"]
    assert snapshot["skill_admission_status"] == "pass"
    assert snapshot["skill_surface_kind"] == "content-production"
    assert snapshot["skill_non_code_supported"] is True


def test_v139_story_scenarios_should_not_force_browser_for_non_ui_functional_runtime_feature() -> None:
    payload = expand_story_scenarios(
        feature=FEATURE,
        version=VERSION,
        story_sequence=[
            {
                "ac_id": "AC-005",
                "theme": "security",
                "text": "仅授权用户可执行敏感操作，越权请求被拒绝。",
            }
        ],
        entries=[
            {
                "ac_id": "AC-005",
                "tc_id": "TC-010",
                "qa_type": "functional",
                "layer": "functional",
                "assertion": "Web UI assertions and key actions pass",
                "title": "runtime skill admission functional coverage",
                "text": "host validated skill compatibility and authorization checks",
            }
        ],
    )

    scenarios = payload["scenarios"]
    assert scenarios
    assert all(item["browser_required"] is False for item in scenarios)
    assert [item["scenario_family"] for item in scenarios] == ["primary"]


def test_v139_test_case_should_not_synthesize_browser_functional_coverage_for_non_ui_runtime_feature(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "beacon" / VERSION
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    (docs / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs / "user-story" / f"{SLUG}.md").write_text(
        "# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-005 | security | 仅授权用户可执行敏感操作，越权请求被拒绝。 |\n",
        encoding="utf-8",
    )
    (docs / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")

    result = _invoke(
        [
            "test-case",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--qa-types",
            "unit,functional,compatibility",
        ]
    )

    assert result.exit_code == 0, result.stdout
    qa9 = json.loads(
        (docs / ".machine" / "qa" / f"{SLUG}.qa9-matrix.json").read_text(encoding="utf-8")
    )
    qa_types = [item["qa_type"] for item in qa9["entries"]]
    assert "unit" in qa_types
    assert "functional" not in qa_types
    assert "compatibility" not in qa_types
