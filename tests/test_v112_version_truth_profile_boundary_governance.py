from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon import __toolkit_version__
from beacon.main import app
from beacon.utils.governance import evaluate_takeover_baseline_gate
from beacon.utils.learning_loop import (
    ensure_evo_skeleton,
    load_learning_plane_contract,
    validate_learning_surface_mutation,
)
from beacon.utils.runtime import write_json
from beacon.utils.versioning import describe_project_version_context


runner = CliRunner()
VERSION = "v1.1.12"
FEATURE = "Governance Feature"
SLUG = "governance-feature"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_version_truth(root: Path) -> None:
    (root / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "beacon" / "__init__.py").write_text(
        '__version__ = "1.1.12"\n__toolkit_version__ = "v1.1.12"\n',
        encoding="utf-8",
    )
    (root / "beacon" / "version-truth.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "package_version": "1.1.12",
                "runtime_version": "v1.1.12",
                "docs_default_line": "v1.1.12",
                "current_runtime_release_line": "v1.1.12",
                "planning_lines": [],
                "partial_runtime_supplement_lines": [],
                "lines": {
                    "v1.1.11": {"status": "historical_release"},
                    "v1.1.12": {"status": "current_runtime_release"},
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "beacon" / "version-semantics.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "artifact": "beacon-version-semantics",
                "fields": {
                    "runtime_version": {"kind": "runtime", "meaning": "runtime line"},
                    "docs_default_line": {"kind": "docs", "meaning": "default docs line"},
                    "current_runtime_release_line": {"kind": "release_truth", "meaning": "release line"},
                },
                "resolver_contract": {
                    "version_context": "describe_project_version_context()",
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _seed_feature_docs(root: Path, *, version: str = VERSION, feature: str = FEATURE) -> None:
    _seed_version_truth(root)
    slug = feature.lower().replace(" ", "-")
    base = root / "docs" / "beacon" / version
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "user-story" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# User Story",
                "",
                "| AC ID | Theme | Description |",
                "| --- | --- | --- |",
                "| AC-001 | Governance | Help should expose the correct execution surface |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base / "prd" / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "release" / f"{version}.md").write_text(f"# Release {version}\n", encoding="utf-8")
    (base / "SUMMARY.md").write_text(f"# Summary {version}\n", encoding="utf-8")
    (base / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")


def _seed_context_markers(root: Path, version: str = VERSION) -> None:
    marker = f"<!-- BEACON:VERSION:{version} -->\n"
    (root / "AGENTS.md").write_text(marker, encoding="utf-8")
    (root / "CLAUDE.md").write_text(marker, encoding="utf-8")


def _seed_split_context_markers(root: Path, *, runtime_version: str, docs_version: str) -> None:
    content = (
        "<!-- BEACON:START -->\n"
        f"<!-- BEACON:VERSION:{runtime_version} -->\n"
        f"<!-- BEACON:DOCS_VERSION:{docs_version} -->\n"
        "# Context\n"
        "<!-- BEACON:END -->\n"
    )
    (root / "AGENTS.md").write_text(content, encoding="utf-8")
    (root / "CLAUDE.md").write_text(content, encoding="utf-8")


def _write_takeover_state(root: Path, *, frozen_at: str = "") -> None:
    (root / ".beacon" / "state").mkdir(parents=True, exist_ok=True)
    write_json(
        root / ".beacon" / "state" / "project-onboarding.json",
        {
            "schema_version": "1.0",
            "project_mode": "takeover",
            "docs_version": VERSION,
            "runtime_version": __toolkit_version__,
            "takeover_baseline_status": "frozen" if frozen_at else "draft",
            "takeover_baseline_frozen_at": frozen_at,
        },
    )


def test_v112_version_truth_should_promote_v112_to_current_runtime_release(tmp_path: Path):
    _seed_version_truth(tmp_path)
    for version in ("v1.1.11", "v1.1.12"):
        base = tmp_path / "docs" / "beacon" / version
        (base / "release").mkdir(parents=True, exist_ok=True)
        (base / "release" / f"{version}.md").write_text(f"# Release {version}\n", encoding="utf-8")

    payload = describe_project_version_context(tmp_path, docs_version="v1.1.12")
    assert payload["docs_default_line"] == "v1.1.12"
    assert payload["current_runtime_release_line"] == "v1.1.12"
    assert payload["release_truth_status"] == "current_runtime_release"
    assert payload["planning_lines"] == []
    assert payload["partial_runtime_supplement_lines"] == []
    assert payload["version_truth_source"] == "beacon/version-truth.json"
    assert payload["version_semantics_source"] == "beacon/version-semantics.json"
    assert payload["version_semantics"]["fields"]["runtime_version"]["meaning"]
    assert payload["version_semantics"]["resolver_contract"]["version_context"] == "describe_project_version_context()"


def test_v112_help_and_status_should_expose_execution_learning_surfaces_and_decision_trace(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    result = _invoke(["help", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["blocked_reason"] == "revision_not_frozen"
    assert payload["version_semantics"]["fields"]["docs_default_line"]["kind"] == "docs"
    assert payload["execution_surface"]["selected_surface"] == "native-default"
    assert "qa_policy" in payload["learning_surface"]["subject_surface"]
    assert payload["decision_trace"][0]["step"] == "version_truth"

    status = _invoke(["status", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE])
    assert status.exit_code == 0, status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["project_mode"] == "greenfield"
    assert status_payload["revision"]["blocked_reason"] == "revision_not_frozen"
    assert status_payload["version_semantics"]["fields"]["current_runtime_release_line"]["kind"] == "release_truth"
    assert status_payload["execution_surface"]["selected_surface"] == "native-default"
    assert "design_policy" in status_payload["learning_surface"]["subject_surface"]


def test_v112_help_should_block_when_requested_version_conflicts_with_context_markers(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _seed_context_markers(tmp_path, VERSION)

    result = _invoke(["help", "--project-root", str(tmp_path), "--version", "v1.1.11", "--feature", FEATURE, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["blocked_reason"] == "context_version_mismatch"
    assert payload["context_version_guard"]["recommended_version"] == VERSION
    assert payload["next_step"]["action"] == "use-context-version"


def test_v112_user_story_create_should_block_on_context_version_mismatch(tmp_path: Path):
    _seed_version_truth(tmp_path)
    _seed_context_markers(tmp_path, VERSION)

    result = _invoke(["user-story", "create", "Guarded Story", "--project", str(tmp_path), "--version", "v1.1.11"])
    assert result.exit_code == 2, result.stdout
    assert "context-managed version" in result.stdout
    assert VERSION in result.stdout


def test_v112_help_should_prefer_context_docs_target_over_runtime_marker_for_planning_line(tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.1.12")
    _seed_split_context_markers(tmp_path, runtime_version="v1.1.12", docs_version="v1.1.13")
    extra = tmp_path / "docs" / "beacon" / "v1.1.13"
    (extra / "execution").mkdir(parents=True, exist_ok=True)
    (extra / "SUMMARY.md").write_text("# Summary v1.1.13\n", encoding="utf-8")
    (extra / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")

    result = _invoke(["help", "--project-root", str(tmp_path), "--version", "v1.1.13", "--feature", FEATURE, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["blocked_reason"] != "context_version_mismatch"
    assert payload["version_context"]["context_managed_version"] == "v1.1.12"
    assert payload["version_context"]["context_docs_version"] == "v1.1.13"


def test_v112_project_skill_boundary_should_block_stage_capability_and_evidence_mismatch(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    (tmp_path / "beacon.config.yaml").write_text(
        """
project_skills:
  registry:
    shell-skill:
      id: shell-skill
      kind: external
      entry: /bin/sh
      capabilities:
        - review
      supported_stages:
        - review
      evidence_contract: []
  profiles:
    boundary:
      project: demo
      profile_id: boundary
      description: Boundary profile
      skills:
        verify: shell-skill
      required_evidence:
        - uat_pipeline_run
      required_cases: []
      orchestration:
        nodes:
          -
            id: invalid
            stage: verify
            skill: shell-skill
            command_template: "python3 -c 'from pathlib import Path; Path(r\"{project_root}/.beacon/should-not-run.txt\").write_text(\"boom\")'"
            produces_evidence:
              - uat_pipeline_run
""".strip()
        + "\n",
        encoding="utf-8",
    )
    bind = _invoke(["skill", "bind", FEATURE, "--profile", "boundary", "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert bind.exit_code == 0, bind.stdout

    result = _invoke(["verify", "run", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["orchestration"]["status"] == "blocked"
    node = payload["orchestration"]["nodes"][0]
    reason_codes = {item["reason_code"] for item in node["issues"]}
    assert "project_skill_stage_unsupported" in reason_codes
    assert "project_skill_capability_missing" in reason_codes
    assert "project_skill_evidence_contract_mismatch" in reason_codes
    assert not (tmp_path / ".beacon" / "should-not-run.txt").exists()


def test_v112_learning_plane_contract_should_be_typed_and_forbid_execution_surfaces(tmp_path: Path):
    ensure_evo_skeleton(tmp_path)
    contract = load_learning_plane_contract(tmp_path)
    assert set(contract["subject_surface"]) >= {
        "qa_policy",
        "design_policy",
        "contract_policy",
        "rewrite_policy",
        "debug_policy",
        "benchmark_policy",
    }
    assert "design_brief_extraction" in contract["policy_topics"]["design_policy"]
    assert "review_thresholds" in contract["policy_topics"]["design_policy"]

    verdict = validate_learning_surface_mutation(
        tmp_path,
        subject_surface=["qa_policy", "project_skill_command_template"],
    )
    assert verdict["status"] == "blocked"
    assert any(item["reason_code"] == "learning_surface_forbidden" for item in verdict["issues"])


def test_v112_takeover_help_and_implement_should_block_until_baseline_is_ready(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    _write_takeover_state(tmp_path)

    help_result = _invoke(["help", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"])
    assert help_result.exit_code == 0, help_result.stdout
    help_payload = json.loads(help_result.stdout)
    assert help_payload["blocked_reason"] == "takeover_baseline_required"
    assert help_payload["next_step"]["action"] == "takeover-baseline"

    implement_result = _invoke(
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
            "--json",
        ]
    )
    assert implement_result.exit_code == 2, implement_result.stdout
    implement_payload = json.loads(implement_result.stdout)
    assert implement_payload["reason_code"] == "takeover_baseline_required"


def test_v112_takeover_baseline_gate_should_pass_when_docs_are_ready_and_frozen(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    execution_root = tmp_path / "docs" / "beacon" / VERSION / "execution"
    (execution_root / "architecture-blueprint.md").write_text("# Architecture Blueprint\n\n- status: frozen\n", encoding="utf-8")
    (execution_root / "current-state-service-map.md").write_text("# Current State Service Map\n\n- status: frozen\n", encoding="utf-8")
    (execution_root / "refactor-boundaries.md").write_text("# Refactor Boundaries\n\n- status: frozen\n", encoding="utf-8")
    _write_takeover_state(tmp_path, frozen_at="2026-04-01T00:00:00Z")

    payload = evaluate_takeover_baseline_gate(tmp_path, version=VERSION)
    assert payload["status"] == "pass"
    assert payload["baseline_frozen"] is True


def test_v112_takeover_baseline_gate_should_accept_frozen_docs_without_extra_state_flag(tmp_path: Path):
    _seed_feature_docs(tmp_path)
    execution_root = tmp_path / "docs" / "beacon" / VERSION / "execution"
    (execution_root / "architecture-blueprint.md").write_text("# Architecture Blueprint\n\n- status: frozen\n", encoding="utf-8")
    (execution_root / "current-state-service-map.md").write_text("# Current State Service Map\n\n- status: frozen\n", encoding="utf-8")
    (execution_root / "refactor-boundaries.md").write_text("# Refactor Boundaries\n\n- status: frozen\n", encoding="utf-8")
    _write_takeover_state(tmp_path)

    payload = evaluate_takeover_baseline_gate(tmp_path, version=VERSION)
    assert payload["status"] == "pass"
    assert payload["baseline_frozen"] is True
