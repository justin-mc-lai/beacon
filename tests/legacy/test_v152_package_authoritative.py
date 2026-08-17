from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon import app
from beacon.utils.acceptance_kit import write_acceptance_kit_projection
from beacon.utils.ceo_review_surface import run_ceo_review
from beacon.utils.feature_package import validate_feature_package
from beacon.utils.implementation_plan import compile_implementation_plan, implementation_plan_progress_path, implementation_task_ledger_markdown_path
from beacon.utils.material_audit import build_material_audit
from beacon.utils.project_governance import commit_governance_payload
from beacon.utils.prototype_utils import source_doc_paths
from beacon.utils.qa_evo_deep import default_qa_evo_deep_findings, load_qa_evo_deep_source_materials
from beacon.utils.requirement_deepening import build_requirement_completeness_gate
from beacon.utils.requirement_refs import requirement_truth_paths
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime_projection import build_runtime_projection
from beacon.utils.runtime import write_json
from beacon.utils.semantic_runtime import _load_requirement_docs
from beacon.utils.story_state import freeze_story_state
from beacon.utils.truth_map import (
    TRUTH_SOURCE_MODEL,
    TRUTH_SOURCE_MODEL_AUTHORITATIVE,
    feature_package_authoritative,
    rebuild_machine_json,
    resolve_feature_truth,
    resolve_legacy_absorb_targets,
    resolve_legacy_rebuild_targets,
    resolve_machine_json_plan,
    resolve_truth_entrypoint_inventory,
    resolve_truth_read_refs,
    resolve_truth_map,
    truth_source_model_for_version,
    verify_truth_entrypoint_inventory,
    verify_truth_map,
)
from beacon.utils.version_aggregate_projection import version_aggregate_projection_status

VERSION = "v1.5.2"
V151 = "v1.5.1"
FEATURE = "Beacon Truth Map Center and Package Cutover"
SLUG = "beacon-truth-map-center-and-package-cutover"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def _init_git_repo(root: Path, branch: str = "main") -> None:
    """Seed a minimal git repo so truth-authoring branch guards pass in tmp fixtures."""
    subprocess.run(["git", "init", "-b", branch], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    _write(root, ".gitkeep", "test\n")
    subprocess.run(["git", "add", ".gitkeep"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)


def _seed_governance(root: Path, version: str = VERSION) -> None:
    commit_governance_payload(
        root,
        {
            "schema_version": "1.0",
            "project_root": str(root),
            "global_project_metadata": {
                "project_root": str(root),
                "topology_kind": "single_repo",
                "default_execution_service": "beacon",
                "service_bindings": [
                    {
                        "service_key": "beacon",
                        "repo_root": str(root),
                        "repo_root_relative": ".",
                        "role": "service",
                        "writable": True,
                        "worktree_path_policy": "follow-repo-root",
                    }
                ],
            },
            "version_scoped_metadata": {
                version: {
                    "version": version,
                    "participating_services": ["beacon"],
                    "per_service_canonical_branch": {"beacon": "main"},
                    "branch_guard_mode": "strict",
                    "validation_state": "active",
                }
            },
        },
        event_type="test-seed",
    )
    base = f"docs/beacon/{version}"
    _write(root, "docs/beacon/global-boundaries.md", "# Global\n")
    _write(root, f"{base}/SUMMARY.md", f"# {version}\n")
    _write(root, f"{base}/execution/boundaries.md", "# Boundaries\n")
    _write(root, f"{base}/execution/project-skill-qa-evolution-blueprint.md", "# Skill QA\n")
    _write(root, f"{base}/source-architecture/index.md", "# Source Architecture\n")
    _write(root, f"{base}/release/{version}.md", "# Release\n")


def _seed_package(root: Path, *, version: str = VERSION, legacy: bool = False) -> None:
    _seed_governance(root, version)
    base = f"docs/beacon/{version}"
    truth_model = truth_source_model_for_version(version)
    _write(
        root,
        f"{base}/features/{SLUG}/truth.md",
        "\n".join(
            [
                "---",
                f"slug: {SLUG}",
                f"version: {version}",
                "status: frozen",
                "language: zh",
                "canonical_refs:",
                f"  prd: {base}/features/{SLUG}/truth.md",
                f"  user_story: {base}/features/{SLUG}/truth.md",
                f"  test_case: {base}/features/{SLUG}/tests.md",
                "parser_contract: beacon-feature-package-v1",
                f"truth_source_model: {truth_model}",
                "truth_map_contract: beacon-truth-map-v1",
                "---",
                "",
                "# Feature Truth",
                "",
                "## Acceptance Criteria",
                "",
                "| AC ID | Theme | Description |",
                "|---|---|---|",
                "| AC-001 | package-authoritative | Package truth wins. |",
                "| AC-002 | resolver-required | Resolver is required. |",
                "| AC-003 | legacy-not-canonical | Legacy is not authority. |",
                "| AC-004 | doctor-rebuild | Doctor rebuilds legacy outputs. |",
                "| AC-005 | change-absorb | Change absorbs legacy inputs. |",
                "| AC-006 | no-json-twin-requirement | JSON twin not required. |",
                "| AC-007 | gate-consumption | Gates consume package truth. |",
                "| AC-008 | drift-fail-closed | Legacy drift fails closed. |",
            ]
        )
        + "\n",
    )
    _write(
        root,
        f"{base}/features/{SLUG}/tests.md",
        "\n".join(
            [
                "# Tests",
                "",
                "| AC ID | TC ID | Layer | Planned Command | Assertion |",
                "|---|---|---|---|---|",
                "| AC-001 | TC-001 | unit | pytest | Package truth wins. |",
                "| AC-002 | TC-002 | unit | pytest | Resolver required. |",
                "| AC-003 | TC-003 | unit | pytest | Legacy not canonical. |",
                "| AC-004 | TC-004 | unit | pytest | Doctor route. |",
                "| AC-005 | TC-005 | unit | pytest | Change route. |",
                "| AC-006 | TC-006 | unit | pytest | JSON not required. |",
                "| AC-007 | TC-007 | unit | pytest | Gates use package. |",
                "| AC-008 | TC-008 | unit | pytest | Drift fail closed. |",
            ]
        )
        + "\n",
    )
    _write(
        root,
        f"{base}/features/{SLUG}/tasks.md",
        "\n".join(
            [
                "# Tasks",
                "",
                "> Gold shape: every task binds ac= + evidence= (global-boundaries §2.1).",
                "",
                f"- [ ] TASK-001 Route through resolver · ac=AC-001 · evidence=`.beacon/evidence/implement/{SLUG}/AC-001.json`",
                f"- [ ] TASK-002 Validate package · ac=AC-002 · evidence=`.beacon/evidence/implement/{SLUG}/AC-002.json`",
                "",
            ]
        ),
    )
    # Evidence stubs for binding paths (unchecked tasks only need metadata; stubs keep freeze/refreeze happy)
    for ac in ("AC-001", "AC-002"):
        _write(
            root,
            f".beacon/evidence/implement/{SLUG}/{ac}.json",
            f'{{"schema":"implement-evidence.v1","feature":"{SLUG}","ac":"{ac}","status":"planned"}}\n',
        )
    _write(
        root,
        f"{base}/features/{SLUG}/evidence.md",
        "\n".join(
            [
                "# Evidence",
                "",
                "| surface | authority | path |",
                "|---------|-----------|------|",
                f"| package | requirement_truth | {base}/features/{SLUG}/truth.md |",
                f"| tests | test_truth | {base}/features/{SLUG}/tests.md |",
                f"| unit | qa_verdict | tests/test_v152_package_authoritative.py |",
                "",
            ]
        ),
    )
    if legacy:
        _write(root, f"{base}/prd/{SLUG}.md", "# PRD\n\nlegacy drift\n")
        _write(root, f"{base}/user-story/{SLUG}.md", "# User Story\n\nlegacy drift\n")
        _write(root, f"{base}/qa/test-cases/{SLUG}.md", "# Test Cases\n\nlegacy drift\n")


def test_package_markdown_is_authoritative(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    payload = resolve_truth_map(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["truth_source_model"] == TRUTH_SOURCE_MODEL_AUTHORITATIVE
    assert payload["authority_flip_allowed"] is True
    assert payload["feature_truth"]["truth_authority"] == "markdown_feature_package"


def test_consumers_require_truth_map_resolver(tmp_path: Path) -> None:
    _seed_package(tmp_path)
    for rel in (
        "beacon/commands/prd.py",
        "beacon/commands/user_story.py",
        "beacon/commands/test_case.py",
        "beacon/commands/workflow.py",
        "beacon/commands/truth.py",
        "beacon/commands/gate.py",
        "beacon/utils/prd_bootstrap.py",
        "beacon/utils/requirement_clarity.py",
        "beacon/utils/requirement_deepening.py",
        "beacon/utils/manifest.py",
        "beacon/utils/acceptance_kit.py",
        "skills/beacon/demo/SKILL.md",
        ".agents/skills/demo/SKILL.md",
    ):
        _write(tmp_path, rel, "ok\n")

    payload = verify_truth_entrypoint_inventory(tmp_path, version=VERSION, strict=True)

    assert payload["status"] == "pass"
    assert not payload["diagnostics"]
    assert all(entry["truth_center_routed"] for entry in payload["entries"] if entry["classification"] != "generated_state_exception")

    refs = resolve_truth_read_refs(tmp_path, version=VERSION, feature=FEATURE, consumer="test")
    assert refs["requirement_refs"]["prd"].endswith(f"features/{SLUG}/truth.md")
    assert refs["requirement_refs"]["user_story"].endswith(f"features/{SLUG}/truth.md")
    assert refs["requirement_refs"]["test_case"].endswith(f"features/{SLUG}/tests.md")


def test_legacy_triptych_is_not_canonical(tmp_path: Path) -> None:
    _seed_package(tmp_path, legacy=True)

    rebuild = resolve_legacy_rebuild_targets(tmp_path, version=VERSION, feature=FEATURE)
    absorb = resolve_legacy_absorb_targets(tmp_path, version=VERSION, feature=FEATURE)

    assert rebuild["legacy_authority"] is False
    assert absorb["legacy_authority"] is False
    assert rebuild["status"] == "legacy_output_only"
    assert absorb["status"] == "package_truth_target_only"


def test_doctor_rebuilds_legacy_from_package(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    plan = resolve_machine_json_plan(tmp_path, version=VERSION, feature=FEATURE)

    assert plan["routes"]["doctor_rebuild"]["status"] == "legacy_output_only"
    assert plan["source_paths"]["truth"].endswith(f"features/{SLUG}/truth.md")


def test_change_absorbs_legacy_into_package(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    plan = resolve_machine_json_plan(tmp_path, version=VERSION, feature=FEATURE)

    assert plan["routes"]["change_absorb"]["status"] == "package_truth_target_only"
    assert "absorb-legacy-truth-into-feature-package" in plan["routes"]["change_absorb"]["command"]


def test_json_twin_not_required(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    payload = verify_truth_map(tmp_path, version=VERSION, feature=FEATURE, strict=True)

    assert payload["status"] == "pass"
    assert payload["checked_machine_json"] == []
    assert payload["json_authority"] is False


def test_gate_qa_release_consume_package_truth(tmp_path: Path) -> None:
    _seed_package(tmp_path)
    write_json(tmp_path / ".beacon" / "qa" / "status.json", {"version": VERSION, "status": "passed"})

    from beacon.utils.release_scorecard import build_release_scorecard

    scorecard = build_release_scorecard(tmp_path, version=VERSION)

    assert scorecard["truth_map_governance"]["truth_source_model"] == TRUTH_SOURCE_MODEL_AUTHORITATIVE
    assert scorecard["truth_map_governance"]["json_authority"] is False


def test_legacy_drift_fails_closed_package_wins(tmp_path: Path) -> None:
    _seed_package(tmp_path, legacy=True)

    payload = resolve_feature_truth(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["source_paths"]["truth"].endswith(f"features/{SLUG}/truth.md")
    assert payload["truth_source_model"] == TRUTH_SOURCE_MODEL_AUTHORITATIVE
    assert "legacy drift" not in json.dumps(payload, ensure_ascii=False)


def test_resolver_policy_is_version_aware() -> None:
    # v1.6.10+ §2.1: docs version is not a package-authority downgrade switch
    assert truth_source_model_for_version(V151) == TRUTH_SOURCE_MODEL_AUTHORITATIVE
    assert truth_source_model_for_version(VERSION) == TRUTH_SOURCE_MODEL_AUTHORITATIVE
    assert feature_package_authoritative(V151) is True
    assert feature_package_authoritative(VERSION) is True
    assert feature_package_authoritative("v0.0.13") is True


def test_truth_frontmatter_model_matches_resolver_policy(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    validation = validate_feature_package(tmp_path, version=VERSION, feature=FEATURE)
    resolved = resolve_feature_truth(tmp_path, version=VERSION, feature=FEATURE)

    assert validation["truth_frontmatter"]["truth_source_model"] == TRUTH_SOURCE_MODEL_AUTHORITATIVE
    assert resolved["truth_source_model"] == validation["truth_frontmatter"]["truth_source_model"]


def test_entrypoint_inventory_rejects_v151_legacy_exceptions_for_v152(tmp_path: Path) -> None:
    _seed_package(tmp_path)
    for rel in (
        "beacon/commands/prd.py",
        "beacon/commands/user_story.py",
        "beacon/commands/test_case.py",
        "beacon/commands/workflow.py",
        "beacon/commands/truth.py",
        "beacon/commands/gate.py",
        "beacon/utils/prd_bootstrap.py",
        "beacon/utils/requirement_clarity.py",
        "beacon/utils/requirement_deepening.py",
        "beacon/utils/manifest.py",
        "beacon/utils/acceptance_kit.py",
        "skills/beacon/demo/SKILL.md",
        ".agents/skills/demo/SKILL.md",
    ):
        _write(tmp_path, rel, "ok\n")

    payload = resolve_truth_entrypoint_inventory(tmp_path, version=VERSION)

    violations = [entry for entry in payload["entries"] if entry.get("cutover_violation")]
    assert not violations
    assert payload["status"] == "pass"
    assert all(
        entry["truth_center_routed"] or entry["classification"] == "generated_state_exception"
        for entry in payload["entries"]
    )


def test_material_audit_package_complete_without_legacy_triptych(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    payload = build_material_audit(tmp_path, version=VERSION, strict=True, feature=SLUG)
    main_chain = next(item for item in payload["checks"] if item["name"] == "main_chain_feature_completeness")

    assert main_chain["status"] == "pass"
    assert main_chain["details"]["missing_by_feature"] == {}


def test_manifest_truth_paths_are_generated_index_not_authority(tmp_path: Path) -> None:
    _seed_package(tmp_path)
    write_json(
        tmp_path / f"docs/beacon/{VERSION}/.machine/manifest/version-features.json",
        {
            "version": VERSION,
            "truth_authority": False,
            "json_authority": False,
            "features": [
                {
                    "slug": SLUG,
                    "truth_paths": {
                        "prd": f"docs/beacon/{VERSION}/prd/{SLUG}.md",
                        "user_story": f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
                        "test_case": f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
                    },
                }
            ],
        },
    )

    payload = build_material_audit(tmp_path, version=VERSION, strict=True, feature=SLUG)

    assert payload["truth_map_governance"]["generated_state_surfaces"]["version_feature_manifest"]["truth_authority"] is False
    assert payload["status"] == "pass"


def test_generated_json_claiming_truth_authority_fails_closed(tmp_path: Path) -> None:
    _seed_package(tmp_path)
    rebuild = rebuild_machine_json(tmp_path, version=VERSION, feature=FEATURE)
    path = tmp_path / rebuild["plan"]["outputs"]["requirement_package_state"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["truth_authority"] = True
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    verify = verify_truth_map(tmp_path, version=VERSION, feature=FEATURE, strict=True)
    codes = {item["code"] for item in verify["diagnostics"]}

    assert verify["status"] == "blocked"
    assert "machine_json_claims_truth_authority" in codes


def test_existing_machine_json_may_be_absent_or_stale_without_invalidating_markdown(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    validation = validate_feature_package(tmp_path, version=VERSION, feature=FEATURE)

    assert validation["status"] == "pass"
    assert validation["runtime_json_requires_markdown_twin"] is False


def test_acceptance_kit_uses_package_refs_for_skill_scenario_trace(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    payload = write_acceptance_kit_projection(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        acceptance_envelope={"feature": FEATURE, "version": VERSION, "verdict": "passed"},
    )

    assert payload["layers"]["skill-contract"]["source_truth_ref"].endswith(f"features/{SLUG}/truth.md")
    assert payload["layers"]["trace-scorecard"]["source_truth_ref"].endswith(f"features/{SLUG}/tests.md")


def test_status_surface_reports_package_authority(tmp_path: Path) -> None:
    _seed_package(tmp_path)
    runner = CliRunner()

    result = runner.invoke(app, ["status", "--project-root", str(tmp_path), "--version", VERSION])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["truth_map_governance"]["truth_source_model"] == TRUTH_SOURCE_MODEL_AUTHORITATIVE
    assert payload["source_of_truth"]["json_authority"] is False


def test_status_surface_accepts_relative_project_root_for_machine_path(tmp_path: Path, monkeypatch) -> None:
    _seed_package(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(app, ["status", "--project-root", ".", "--version", VERSION])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["source_of_truth"]["machine_root"] == f"docs/beacon/{VERSION}/.machine"


def test_gate_blocks_when_package_surfaces_are_missing_even_if_legacy_exists(tmp_path: Path) -> None:
    _seed_governance(tmp_path)
    base = f"docs/beacon/{VERSION}"
    _write(tmp_path, f"{base}/prd/{SLUG}.md", "# PRD\n")
    _write(tmp_path, f"{base}/user-story/{SLUG}.md", "# User Story\n")
    _write(tmp_path, f"{base}/qa/test-cases/{SLUG}.md", "# Test Cases\n")

    payload = validate_feature_package(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["status"] == "blocked"
    codes = {item["code"] for item in payload["diagnostics"]}
    assert {"missing_truth", "missing_tests", "missing_tasks", "missing_evidence"} <= codes


def test_requirement_completeness_gate_accepts_authoritative_package_without_legacy_projection(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    gate = build_requirement_completeness_gate(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        target_stage="qa",
    )

    assert gate["status"] == "pass"
    assert gate["blocked"] is False
    assert gate["projection_status"] == "package_authoritative"
    assert gate["package_authoritative_truth"]["validation"]["status"] == "pass"
    assert gate["recommended_command"] == ""


def test_change_refreeze_chain_uses_package_surfaces_without_legacy_triptych(tmp_path: Path) -> None:
    _seed_package(tmp_path)
    _init_git_repo(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    freeze_story_state(tmp_path, VERSION, FEATURE)

    result = CliRunner().invoke(
        app,
        [
            "change",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--reason",
            "package-authoritative refreeze",
            "--refreeze-chain",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["refreeze_status"] == "complete"
    assert payload["blocked_reason"] == ""
    assert payload["touched_surfaces"] == [
        "change",
        "truth",
        "tests",
        "tasks",
        "evidence",
        "requirement_clarity",
        "freeze",
        "feature_package_validation",
    ]
    assert payload["surface_statuses"]["change"]["status"] == "package_change_optional"
    for surface in ["truth", "tests", "tasks", "evidence"]:
        assert payload["surface_statuses"][surface]["status"] == "present"
        assert payload["surface_statuses"][surface]["authority"] == "markdown_feature_package"
    assert payload["requirement_package"]["status"] == "synced"
    assert payload["requirement_package"]["requirement_refs"]["prd"] == f"docs/beacon/{VERSION}/features/{SLUG}/truth.md"
    assert payload["requirement_package"]["story_sync"]["ac_count"] == 8
    assert payload["truth_revision_after"]["baseline_hash"] != "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert payload["release_projection_sync"]["status"] == "pass"
    assert payload["release_projection_sync"]["truth_authority"] is False
    projection_status = version_aggregate_projection_status(tmp_path, version=VERSION, current_feature=FEATURE)
    assert projection_status["status"] == "pass"
    assert projection_status["includes_current_feature"] is True
    assert projection_status["feature_projection"]["status"] == "pass"


def test_change_refreeze_chain_accepts_relative_project_root_for_package_authority(tmp_path: Path, monkeypatch) -> None:
    _seed_package(tmp_path)
    _init_git_repo(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    freeze_story_state(tmp_path, VERSION, FEATURE)

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        app,
        [
            "change",
            FEATURE,
            "--project",
            ".",
            "--version",
            VERSION,
            "--reason",
            "package-authoritative refreeze",
            "--refreeze-chain",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["refreeze_status"] == "complete"
    assert payload["blocked_reason"] == ""
    assert payload["artifacts"]["machine_path"].startswith(f"docs/beacon/{VERSION}/.machine/change/")


def test_implement_plan_consumes_package_tasks_without_mutating_task_ledger(tmp_path: Path, monkeypatch) -> None:
    _seed_package(tmp_path)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    freeze_story_state(tmp_path, VERSION, FEATURE)
    tasks_path = tmp_path / f"docs/beacon/{VERSION}/features/{SLUG}/tasks.md"
    before = tasks_path.read_text(encoding="utf-8")

    monkeypatch.setattr("beacon.utils.implementation_plan.feature_requires_technical_review", lambda *_args, **_kwargs: False)
    code, payload = compile_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)

    assert code == 0
    assert payload["status"] == "not_required"
    assert payload["task_alignment"]["status"] == "aligned"
    assert payload["task_alignment"]["task_count"] == 2
    assert payload["task_alignment"]["draft_implementation_tasks"][0]["source_task_id"] == "TASK-001"
    assert tasks_path.read_text(encoding="utf-8") == before

    monkeypatch.setattr("beacon.utils.implementation_plan.feature_requires_technical_review", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        "beacon.utils.implementation_plan.build_technical_review_gate_payload",
        lambda *_args, **_kwargs: {"blocked": False, "reason_code": ""},
    )
    code, payload = compile_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)

    assert code == 2
    assert payload["status"] == "blocked"
    assert payload["task_alignment"]["status"] == "aligned"
    assert payload["task_alignment"]["draft_implementation_tasks"][0]["source_task_id"] == "TASK-001"
    assert tasks_path.read_text(encoding="utf-8") == before

    monkeypatch.setattr(
        "beacon.utils.implementation_plan.build_material_gate_preflight",
        lambda *_args, **_kwargs: {"blocked": False, "status": "pass", "reason_code": ""},
    )
    code, payload = compile_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)

    assert code == 0
    assert payload["status"] == "planned"
    plan = json.loads((tmp_path / payload["plan_path"]).read_text(encoding="utf-8"))
    assert plan["task_mapping_source"] == "package-tasks"
    assert plan["tasks"][0]["source_task_id"] == "TASK-001"
    assert payload["task_alignment"]["package_tasks_mutated"] is False
    assert implementation_plan_progress_path(tmp_path, VERSION, FEATURE).exists()
    assert implementation_task_ledger_markdown_path(tmp_path, VERSION, FEATURE).exists()
    assert tasks_path.read_text(encoding="utf-8") == before


def test_package_requirement_refs_replace_legacy_triptych_for_runtime_consumers(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    refs = requirement_truth_paths(tmp_path, version=VERSION, feature=FEATURE, consumer="test")

    assert refs["prd"] == tmp_path / f"docs/beacon/{VERSION}/features/{SLUG}/truth.md"
    assert refs["user_story"] == tmp_path / f"docs/beacon/{VERSION}/features/{SLUG}/truth.md"
    assert refs["test_case"] == tmp_path / f"docs/beacon/{VERSION}/features/{SLUG}/tests.md"
    assert refs["tasks"] == tmp_path / f"docs/beacon/{VERSION}/features/{SLUG}/tasks.md"
    assert refs["evidence"] == tmp_path / f"docs/beacon/{VERSION}/features/{SLUG}/evidence.md"


def test_ceo_review_binds_to_package_truth_without_legacy_triptych(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    payload = run_ceo_review(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        focus="full",
        decision="hold",
    )

    assert payload["blocked"] is False
    assert payload["truth_refs"] == [
        f"docs/beacon/{VERSION}/features/{SLUG}/truth.md",
        f"docs/beacon/{VERSION}/features/{SLUG}/tests.md",
        f"docs/beacon/{VERSION}/features/{SLUG}/tasks.md",
        f"docs/beacon/{VERSION}/features/{SLUG}/evidence.md",
    ]


def test_runtime_projection_reports_package_truth_paths_without_legacy_triptych(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    payload = build_runtime_projection(tmp_path, docs_version=VERSION, feature=FEATURE)
    feature_package = payload["feature_packages"][0]
    material_rows = payload["stage_material_status"]
    truth_artifacts = [item for item in payload["artifact_refs"] if item["artifact_scope"] == "truth"]

    assert feature_package["prd_path"] == f"docs/beacon/{VERSION}/features/{SLUG}/truth.md"
    assert feature_package["user_story_path"] == f"docs/beacon/{VERSION}/features/{SLUG}/truth.md"
    assert feature_package["test_case_path"] == f"docs/beacon/{VERSION}/features/{SLUG}/tests.md"
    assert {row["truth_path"] for row in material_rows} == {
        f"docs/beacon/{VERSION}/features/{SLUG}/truth.md",
        f"docs/beacon/{VERSION}/features/{SLUG}/tests.md",
    }
    assert {item["path"] for item in truth_artifacts} == {
        f"docs/beacon/{VERSION}/features/{SLUG}/truth.md",
        f"docs/beacon/{VERSION}/features/{SLUG}/tests.md",
    }


def test_qa_evo_deep_source_materials_use_package_truth_without_legacy_triptych(tmp_path: Path) -> None:
    _seed_package(tmp_path)
    _write(tmp_path, f".beacon/qa/features/{SLUG}/scorecard.json", "{}\n")
    _write(tmp_path, f".beacon/qa/features/{SLUG}/ac-closure.json", "{}\n")

    materials = load_qa_evo_deep_source_materials(tmp_path, version=VERSION, feature=FEATURE)
    findings = default_qa_evo_deep_findings(feature=FEATURE, version=VERSION, source_materials=materials)

    assert materials["status"] == "ready"
    assert materials["materials"]["prd"]["path"] == f"docs/beacon/{VERSION}/features/{SLUG}/truth.md"
    assert materials["materials"]["user_story"]["path"] == f"docs/beacon/{VERSION}/features/{SLUG}/truth.md"
    assert materials["materials"]["test_case"]["path"] == f"docs/beacon/{VERSION}/features/{SLUG}/tests.md"
    assert findings[0]["source_refs"] == [
        f"docs/beacon/{VERSION}/features/{SLUG}/truth.md",
        f"docs/beacon/{VERSION}/features/{SLUG}/truth.md",
        f"docs/beacon/{VERSION}/features/{SLUG}/tests.md",
    ]


def test_prototype_and_semantic_runtime_load_package_truth_without_legacy_triptych(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    prototype_refs = source_doc_paths(tmp_path, VERSION, FEATURE)
    docs = _load_requirement_docs(tmp_path, VERSION, FEATURE)

    assert prototype_refs["prd"] == tmp_path / f"docs/beacon/{VERSION}/features/{SLUG}/truth.md"
    assert prototype_refs["user-story"] == tmp_path / f"docs/beacon/{VERSION}/features/{SLUG}/truth.md"
    assert prototype_refs["test-case"] == tmp_path / f"docs/beacon/{VERSION}/features/{SLUG}/tests.md"
    assert {item["path"] for item in docs} == {
        f"docs/beacon/{VERSION}/features/{SLUG}/truth.md",
        f"docs/beacon/{VERSION}/features/{SLUG}/tests.md",
    }


def test_run_strict_accepts_package_truth_without_legacy_user_story(tmp_path: Path) -> None:
    _seed_package(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "run",
            "workflow",
            "workflow",
            "--mode",
            "strict",
            "--feature",
            FEATURE,
            "--version",
            VERSION,
            "--project-root",
            str(tmp_path),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
