from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon import app
from beacon.utils.feature_package import validate_feature_package
from beacon.utils.material_audit import build_material_audit
from beacon.utils.project_governance import commit_governance_payload
from beacon.utils.runtime import write_json
from beacon.utils.truth_map import (
    GENERATED_GOVERNANCE_STATE_ROLE,
    GOVERNANCE_RESOLVER_MODE,
    MACHINE_JSON_GENERATOR,
    MACHINE_JSON_ROLE,
    RUNTIME_JSON_ROLE,
    TRUTH_MAP_CONTRACT,
    TRUTH_PACKAGE_CONTRACT,
    TRUTH_SOURCE_MODEL,
    VERSION_GOVERNANCE_TRUTH_ROLE,
    resolve_gate_inputs,
    is_runtime_json_exempt,
    rebuild_machine_json,
    resolve_feature_truth,
    resolve_governance_surface,
    resolve_legacy_absorb_targets,
    resolve_legacy_rebuild_targets,
    resolve_machine_json_plan,
    resolve_truth_entrypoint_inventory,
    resolve_truth_map,
    resolve_truth_read_refs,
    resolve_version_governance,
    resolve_truth_write_target,
    verify_truth_entrypoint_inventory,
    verify_governance_truth,
    verify_truth_map,
)

VERSION = "v1.5.1"
FEATURE = "Beacon Truth Map Center and Package Cutover"
SLUG = "beacon-truth-map-center-and-package-cutover"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_v151_package(root: Path, *, version: str = VERSION) -> None:
    base = f"docs/beacon/{version}"
    _write(root, "docs/beacon/global-boundaries.md", "# Global\n")
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
                        "repo_root_relative": "",
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
    _write(root, f"{base}/SUMMARY.md", f"# {version}\n")
    _write(root, f"{base}/execution/boundaries.md", "# Boundaries\n")
    _write(root, f"{base}/execution/project-skill-qa-evolution-blueprint.md", "# Project Skill QA\n")
    _write(root, f"{base}/source-architecture/index.md", "# Source Architecture\n")
    _write(root, f"{base}/release/{version}.md", "# Release\n")
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
                f"  prd: {base}/prd/{SLUG}.md",
                f"  user_story: {base}/user-story/{SLUG}.md",
                f"  test_case: {base}/qa/test-cases/{SLUG}.md",
                "parser_contract: beacon-feature-package-v1",
                f"truth_source_model: {TRUTH_SOURCE_MODEL}",
                f"truth_map_contract: {TRUTH_MAP_CONTRACT}",
                "---",
                "",
                "# Feature Truth",
                "",
                "## Acceptance Criteria",
                "",
                "| AC ID | Theme | Description |",
                "|---|---|---|",
                "| AC-001 | resolver-center | Resolver exists. |",
                "| AC-002 | no-json-authority | JSON projection is not authority. |",
                "| AC-003 | md-authority-ready | Feature package is canonical-ready. |",
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
                "| AC-001 | TC-001 | unit | pytest | Resolver exists. |",
                "| AC-002 | TC-002 | unit | pytest | JSON is generated state. |",
                "| AC-003 | TC-003 | contract | pytest | Package is canonical-ready. |",
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
                "- [ ] TASK-001 Define resolver",
                "- [x] TASK-002 Add CLI",
                "- [-] TASK-003 Verify drift",
            ]
        )
        + "\n",
    )
    _write(
        root,
        f"{base}/features/{SLUG}/evidence.md",
        "\n".join(
            [
                "# Evidence",
                "",
                "| Surface | Authority | Canonical Artifact | Status | Route |",
                "|---|---|---|---|---|",
                f"| beacon-brainstorm | support_advisory | {base}/research/{SLUG}.md | indexed | change |",
                f"| qa | qa_verdict | {base}/qa/test-cases/{SLUG}.md | frozen | qa |",
            ]
        )
        + "\n",
    )


def _git(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _seed_git_repo(root: Path, branch: str = "main") -> None:
    _git(["git", "init", "-b", branch], cwd=root)
    _git(["git", "config", "user.email", "beacon@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def _seed_project_metadata(root: Path, *, branch: str) -> None:
    write_json(
        root / ".beacon" / "metadata" / "project-version-metadata.json",
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
                        "repo_root_relative": "",
                        "role": "service",
                        "writable": True,
                        "worktree_path_policy": "follow-repo-root",
                    }
                ],
            },
            "version_scoped_metadata": {
                VERSION: {
                    "version": VERSION,
                    "participating_services": ["beacon"],
                    "per_service_canonical_branch": {"beacon": branch},
                    "branch_guard_mode": "strict",
                    "validation_state": "active",
                }
            },
            "transaction": {},
        },
    )


def _seed_git_workflow(root: Path, *, expected_branch: str) -> None:
    write_json(
        root / f"docs/beacon/{VERSION}/.machine/execution/git-workflow-{SLUG}.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "feature_slug": SLUG,
            "version": VERSION,
            "mode": "single-repo",
            "expected_branch": expected_branch,
            "branch_prefix": "beacon/",
            "base_branch": "main",
            "use_git_worktree": False,
            "require_clean_worktree_for_switch": True,
            "service_directories": ["."],
            "direct_delivery_services": ["."],
            "git_roots": ["."],
            "worktree_root": str(root),
            "source": "test-existing-contract",
        },
    )


def test_truth_map_resolver_contract(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)

    payload = resolve_truth_map(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["truth_map_contract"] == TRUTH_MAP_CONTRACT
    assert payload["truth_source_model"] == TRUTH_SOURCE_MODEL
    assert payload["feature_truth"]["status"] == "resolved"
    assert payload["feature_truth"]["json_authority"] is False


def test_truth_map_json_is_projection_only(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)

    rebuild = rebuild_machine_json(tmp_path, version=VERSION, feature=FEATURE)
    projection_path = tmp_path / rebuild["plan"]["outputs"]["truth_map_projection"]
    projection = json.loads(projection_path.read_text(encoding="utf-8"))

    assert projection["machine_json_role"] == MACHINE_JSON_ROLE
    assert projection["generated_by"] == MACHINE_JSON_GENERATOR
    assert projection["truth_authority"] is False
    assert projection["json_authority"] is False


def test_feature_package_canonical_ready_contract(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)

    payload = validate_feature_package(tmp_path, version=VERSION, feature=FEATURE, write_report=True)

    assert payload["status"] == "pass"
    assert payload["truth_map_contract"] == TRUTH_MAP_CONTRACT
    assert payload["truth_source_model"] == TRUTH_SOURCE_MODEL
    assert payload["truth_package_contract"] == TRUTH_PACKAGE_CONTRACT
    assert payload["machine_json_role"] == MACHINE_JSON_ROLE
    assert payload["json_authority"] is False


def test_truth_map_static_contract_constants() -> None:
    assert TRUTH_MAP_CONTRACT == "beacon-truth-map-v1"
    assert TRUTH_SOURCE_MODEL == "feature_package_authoritative_ready"
    assert TRUTH_PACKAGE_CONTRACT == "beacon-feature-package-v2"
    assert MACHINE_JSON_ROLE == "generated_state_not_truth"
    assert RUNTIME_JSON_ROLE == "runtime_process_record_not_requirement_truth"
    assert VERSION_GOVERNANCE_TRUTH_ROLE == "version_governance_truth"
    assert GENERATED_GOVERNANCE_STATE_ROLE == "generated_governance_state_not_truth"
    assert GOVERNANCE_RESOLVER_MODE == "resolver_first"


def test_new_truth_consumers_use_resolver() -> None:
    root = Path(__file__).resolve().parents[1]

    assert (root / "beacon" / "commands" / "truth_map.py").exists()
    command_source = (root / "beacon" / "commands" / "truth_map.py").read_text(encoding="utf-8")
    package_source = (root / "beacon" / "utils" / "feature_package.py").read_text(encoding="utf-8")
    cli_source = (root / "beacon" / "cli_factory.py").read_text(encoding="utf-8")

    assert "resolve_truth_map" in command_source
    assert "resolve_feature_truth" in package_source
    assert "truth_map_app" in cli_source


def test_skill_guidance_points_to_package_authoritative_truth_map_first() -> None:
    root = Path(__file__).resolve().parents[1]
    for rel in (
        "skills/beacon/beacon-prd/SKILL.md",
        "skills/beacon/beacon-user-story/SKILL.md",
        "skills/beacon/beacon-test-case/SKILL.md",
        "skills/beacon/beacon-implement/SKILL.md",
        "skills/beacon/beacon-qa/SKILL.md",
        "skills/beacon/beacon-release/SKILL.md",
        ".agents/skills/beacon-prd/SKILL.md",
        ".agents/skills/beacon-user-story/SKILL.md",
        ".agents/skills/beacon-test-case/SKILL.md",
        ".agents/skills/beacon-implement/SKILL.md",
        ".agents/skills/beacon-qa/SKILL.md",
        ".agents/skills/beacon-release/SKILL.md",
    ):
        content = (root / rel).read_text(encoding="utf-8")
        normalized = content.lower()
        assert "v1.5.2 Package-Authoritative Read Order" in content
        assert "beacon truth-map resolve" in content
        assert "--version v1.5.2" in content
        assert "--version v1.5.1" not in content
        assert "generated state" in normalized
        assert "not requirement truth" in normalized or "not truth authority" in normalized


def test_md_truth_does_not_require_json_twin(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)

    payload = verify_truth_map(tmp_path, version=VERSION, feature=FEATURE, strict=True)

    assert payload["status"] == "pass"
    assert payload["checked_machine_json"] == []
    assert payload["json_authority"] is False


def test_project_low_version_package_ready_truth_map_should_verify(tmp_path: Path) -> None:
    project_version = "v0.0.1"
    _seed_v151_package(tmp_path, version=project_version)

    rebuild_machine_json(tmp_path, version=project_version, feature=FEATURE, strict=True)
    payload = verify_truth_map(tmp_path, version=project_version, feature=FEATURE, strict=True)
    resolved = resolve_truth_map(tmp_path, version=project_version, feature=FEATURE)

    assert payload["status"] == "pass"
    assert payload["blocked"] is False
    assert payload["truth_source_model"] == TRUTH_SOURCE_MODEL
    assert resolved["supported"] is True
    assert not any(item["code"] == "truth_map_unsupported_version" for item in payload["diagnostics"])


def test_doctor_rebuild_route_declared(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)

    plan = resolve_machine_json_plan(tmp_path, version=VERSION, feature=FEATURE)

    assert plan["routes"]["doctor_rebuild"]["status"] == "reserved_fail_closed"
    assert "truth-map rebuild-machine" in plan["routes"]["doctor_rebuild"]["command"]


def test_change_absorb_route_declared(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)

    plan = resolve_machine_json_plan(tmp_path, version=VERSION, feature=FEATURE)

    assert plan["routes"]["change_absorb"]["status"] == "reserved_fail_closed"
    assert "absorb-legacy-truth-into-feature-package" in plan["routes"]["change_absorb"]["command"]


def test_truth_map_verify_detects_drift(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)
    rebuild_machine_json(tmp_path, version=VERSION, feature=FEATURE)
    _write(tmp_path, f"docs/beacon/{VERSION}/features/{SLUG}/tasks.md", "# Tasks\n\n- [ ] TASK-001 Changed\n")

    payload = verify_truth_map(tmp_path, version=VERSION, feature=FEATURE, strict=True)
    codes = {item["code"] for item in payload["diagnostics"]}

    assert payload["status"] == "blocked"
    assert "machine_json_source_hash_stale" in codes


def test_truth_map_rebuilds_requirement_machine_json(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)

    payload = rebuild_machine_json(tmp_path, version=VERSION, feature=FEATURE, strict=True)

    assert payload["status"] == "rebuilt"
    assert f"docs/beacon/{VERSION}/.machine/requirement/{SLUG}.truth-map.json" in payload["written"]
    assert f"docs/beacon/{VERSION}/.machine/requirement/{SLUG}.requirement-package.json" in payload["written"]


def test_machine_json_role_labels_are_not_truth(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)
    payload = rebuild_machine_json(tmp_path, version=VERSION, feature=FEATURE)
    state_path = tmp_path / payload["plan"]["outputs"]["requirement_package_state"]
    state = json.loads(state_path.read_text(encoding="utf-8"))

    assert state["machine_json_role"] == MACHINE_JSON_ROLE
    assert state["truth_authority"] is False
    assert state["json_authority"] is False


def test_machine_json_source_hash_freshness(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)
    rebuild_machine_json(tmp_path, version=VERSION, feature=FEATURE)

    payload = verify_truth_map(tmp_path, version=VERSION, feature=FEATURE, strict=True)

    assert payload["status"] == "pass"
    assert payload["source_hashes"]
    assert len(payload["checked_machine_json"]) == 3


def test_runtime_json_is_exempt_from_markdown_twin_requirement(tmp_path: Path) -> None:
    runtime_path = tmp_path / ".beacon" / "runs" / "run-1" / "state.json"
    write_json(runtime_path, {"runtime": True})

    assert is_runtime_json_exempt(runtime_path) is True

    _seed_v151_package(tmp_path)
    plan = resolve_machine_json_plan(tmp_path, version=VERSION, feature=FEATURE)
    assert plan["runtime_json_exemption"]["requires_markdown_twin"] is False
    assert plan["runtime_json_exemption"]["requirement_authority"] is False


def test_stale_machine_json_fails_closed(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)
    rebuild_machine_json(tmp_path, version=VERSION, feature=FEATURE)
    bad_path = tmp_path / f"docs/beacon/{VERSION}/.machine/requirement/{SLUG}.requirement-package.json"
    bad_payload = json.loads(bad_path.read_text(encoding="utf-8"))
    bad_payload["generated_by"] = "manual"
    bad_payload["machine_json_role"] = "truth"
    bad_payload["json_authority"] = True
    bad_path.write_text(json.dumps(bad_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    payload = verify_truth_map(tmp_path, version=VERSION, feature=FEATURE, strict=True)
    codes = {item["code"] for item in payload["diagnostics"]}

    assert payload["status"] == "blocked"
    assert "machine_json_not_resolver_generated" in codes
    assert "machine_json_role_mismatch" in codes
    assert "machine_json_claims_truth_authority" in codes


def test_truth_map_cli_commands_emit_json(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)
    runner = CliRunner()

    resolve_result = runner.invoke(app, ["truth-map", "resolve", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert resolve_result.exit_code == 0, resolve_result.stdout
    assert json.loads(resolve_result.stdout)["truth_map_contract"] == TRUTH_MAP_CONTRACT

    rebuild_result = runner.invoke(
        app,
        ["truth-map", "rebuild-machine", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--strict", "--json"],
    )
    assert rebuild_result.exit_code == 0, rebuild_result.stdout
    assert json.loads(rebuild_result.stdout)["machine_json_role"] == MACHINE_JSON_ROLE

    verify_result = runner.invoke(
        app,
        ["truth-map", "verify", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--strict", "--json"],
    )
    assert verify_result.exit_code == 0, verify_result.stdout
    assert json.loads(verify_result.stdout)["status"] == "pass"


def test_current_v151_package_passes_resolver_validation() -> None:
    root = Path(__file__).resolve().parents[1]

    payload = validate_feature_package(root, version=VERSION, feature=SLUG, write_report=True)

    assert payload["status"] == "pass"
    assert payload["truth_map_contract"] == TRUTH_MAP_CONTRACT
    assert payload["machine_json_role"] == MACHINE_JSON_ROLE
    assert payload["source_hashes"]["truth"]


def test_material_audit_uses_truth_map_when_manifest_lacks_truth_paths(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)
    _write(tmp_path, f"docs/beacon/{VERSION}/prd/{SLUG}.md", "# PRD\n")
    _write(tmp_path, f"docs/beacon/{VERSION}/user-story/{SLUG}.md", "# User Story\n")
    _write(tmp_path, f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md", "# Test Cases\n")
    _write(
        tmp_path,
        f"docs/beacon/{VERSION}/.machine/manifest/version-features.json",
        json.dumps(
            {
                "schema_version": "1.0",
                "version": VERSION,
                "features": [{"slug": SLUG, "status": "frozen", "truth_paths": {}}],
                "version_level_paths": {},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )

    payload = build_material_audit(tmp_path, version=VERSION, strict=True, feature=SLUG)
    main_chain = next(item for item in payload["checks"] if item["name"] == "main_chain_feature_completeness")

    assert main_chain["status"] == "pass"
    assert main_chain["details"]["missing_by_feature"] == {}


def test_version_governance_resolver_contract(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)

    payload = resolve_version_governance(tmp_path, version=VERSION)

    assert payload["status"] == "pass"
    assert payload["resolver_mode"] == GOVERNANCE_RESOLVER_MODE
    assert payload["truth_surfaces"]["summary"]["truth_authority"] is True
    assert payload["generated_state_surfaces"]["version_feature_manifest"]["truth_authority"] is False


def test_governance_authority_classification(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)

    payload = resolve_version_governance(tmp_path, version=VERSION)
    classification = payload["authority_classification"]

    assert classification["feature_truth"] == "markdown_feature_package"
    assert classification["version_governance_truth"] == VERSION_GOVERNANCE_TRUTH_ROLE
    assert classification["generated_governance_state"] == GENERATED_GOVERNANCE_STATE_ROLE
    assert classification["runtime_process_record"] == RUNTIME_JSON_ROLE


def test_manifest_index_is_not_truth_authority(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)

    surface = resolve_governance_surface(tmp_path, version=VERSION, surface="version_feature_manifest")

    assert surface["generated_governance_state"] is True
    assert surface["truth_authority"] is False
    assert surface["json_authority"] is False
    assert surface["role"] == GENERATED_GOVERNANCE_STATE_ROLE


def test_material_audit_reads_resolver_first(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)
    _write(tmp_path, f"docs/beacon/{VERSION}/prd/{SLUG}.md", "# PRD\n")
    _write(tmp_path, f"docs/beacon/{VERSION}/user-story/{SLUG}.md", "# User Story\n")
    _write(tmp_path, f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md", "# Test Cases\n")

    payload = build_material_audit(tmp_path, version=VERSION, strict=False, feature=SLUG)
    resolver_check = next(item for item in payload["checks"] if item["name"] == "version_governance_resolver_first")

    assert payload["truth_map_governance"]["resolver_mode"] == GOVERNANCE_RESOLVER_MODE
    assert resolver_check["status"] == "pass"
    assert resolver_check["details"]["manifest_authority"] is False


def test_qa_release_status_read_resolver_first(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)
    runner = CliRunner()

    qa_status = {
        "schema_version": "1.0",
        "version": VERSION,
        "feature": SLUG,
        "status": "passed",
        "evidence_done": True,
    }
    write_json(tmp_path / ".beacon" / "qa" / "status.json", qa_status)

    from beacon.utils.qa_runtime import load_qa_status
    from beacon.utils.release_scorecard import build_release_scorecard

    loaded_qa = load_qa_status(tmp_path)
    release = build_release_scorecard(tmp_path, version=VERSION)
    status_result = runner.invoke(app, ["status", "--project-root", str(tmp_path), "--version", VERSION])

    assert loaded_qa["resolver_mode"] == GOVERNANCE_RESOLVER_MODE
    assert loaded_qa["truth_authority"] is False
    assert release["truth_map_governance"]["resolver_mode"] == GOVERNANCE_RESOLVER_MODE
    assert status_result.exit_code == 0, status_result.stdout
    status_payload = json.loads(status_result.stdout)
    assert status_payload["truth_map_governance"]["resolver_mode"] == GOVERNANCE_RESOLVER_MODE
    assert status_payload["source_of_truth"]["manifest_authority"] is False


def test_governance_drift_fails_closed(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)
    (tmp_path / f"docs/beacon/{VERSION}/SUMMARY.md").unlink()

    payload = verify_governance_truth(tmp_path, version=VERSION, strict=True)
    codes = {item["code"] for item in payload["diagnostics"]}

    assert payload["status"] == "blocked"
    assert "version_governance_truth_missing" in codes


def test_feature_package_does_not_contain_version_governance(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)
    feature_truth = resolve_feature_truth(tmp_path, version=VERSION, feature=FEATURE)
    governance = resolve_version_governance(tmp_path, version=VERSION)

    assert set(feature_truth["source_paths"]) == {"truth", "tests", "tasks", "evidence"}
    assert "summary" in governance["truth_surfaces"]
    assert "release_notes" in governance["truth_surfaces"]


def test_generated_governance_state_labels(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)
    manifest_path = tmp_path / f"docs/beacon/{VERSION}/.machine/manifest/version-features.json"
    write_json(
        manifest_path,
        {
            "schema_version": "1.0",
            "version": VERSION,
            "features": [],
            "governance_state_role": GENERATED_GOVERNANCE_STATE_ROLE,
            "truth_authority": False,
            "json_authority": False,
        },
    )

    payload = verify_governance_truth(tmp_path, version=VERSION, strict=True)

    assert payload["status"] == "pass"
    assert payload["generated_state_surfaces"]["version_feature_manifest"]["role"] == GENERATED_GOVERNANCE_STATE_ROLE


def test_implement_version_governance_preflight_blocks_metadata_branch_drift(tmp_path: Path) -> None:
    _seed_git_repo(tmp_path, branch="main")
    _seed_v151_package(tmp_path)
    _seed_git_workflow(tmp_path, expected_branch="beacon/v1.5.1")
    runner = CliRunner()

    plan_result = runner.invoke(
        app,
        ["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"],
    )
    assert plan_result.exit_code == 2, plan_result.stdout
    plan_payload = json.loads(plan_result.stdout)
    assert plan_payload["reason_code"] == "implement_git_workflow_metadata_drift"
    assert plan_payload["implement_version_governance_preflight"]["status"] == "blocked"
    assert "doctor metadata verify" in plan_payload["recommended_command"]
    assert not (tmp_path / f"docs/beacon/{VERSION}/.machine/execution/implementation-plan-{SLUG}.json").exists()

    dev_result = runner.invoke(
        app,
        [
            "implement",
            "dev-run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--no-auto-switch-branch",
            "--json",
        ],
    )
    assert dev_result.exit_code == 2, dev_result.stdout
    dev_payload = json.loads(dev_result.stdout)
    assert dev_payload["reason_code"] == "implement_git_workflow_metadata_drift"
    assert dev_payload["preflight_resolution"]["steps"][0]["gate"] == "implement_version_governance_preflight"


def test_truth_center_integration_sweep_policy_boundary(tmp_path: Path) -> None:
    _seed_v151_package(tmp_path)

    read_refs = resolve_truth_read_refs(tmp_path, version=VERSION, feature=FEATURE, consumer="qa")
    write_target = resolve_truth_write_target(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        surface="truth",
        producer="prd",
    )
    gate_inputs = resolve_gate_inputs(tmp_path, version=VERSION, feature=FEATURE, gate="release")
    rebuild_targets = resolve_legacy_rebuild_targets(tmp_path, version=VERSION, feature=FEATURE)
    absorb_targets = resolve_legacy_absorb_targets(tmp_path, version=VERSION, feature=FEATURE)

    for payload in (read_refs, write_target, gate_inputs, rebuild_targets, absorb_targets):
        assert payload["route_mode"] == "truth_center_resolver"
        assert payload["truth_source_model"] == TRUTH_SOURCE_MODEL
        assert payload["authority_state"] == "feature_package_authoritative_ready"
        assert payload["authority_flip_allowed"] is False
        assert payload["json_authority"] is False
    assert write_target["target_path"].endswith(f"features/{SLUG}/truth.md")
    assert rebuild_targets["status"] == "reserved_fail_closed"
    assert absorb_targets["status"] == "reserved_fail_closed"


def test_truth_center_entrypoint_inventory_covers_high_risk_surfaces() -> None:
    root = Path(__file__).resolve().parents[1]

    payload = verify_truth_entrypoint_inventory(root, version=VERSION, strict=True)
    paths = {entry["path"]: entry for entry in payload["entries"]}

    expected_paths = {
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
        "skills/beacon/**/SKILL.md",
        ".agents/skills/**/SKILL.md",
    }

    assert payload["status"] == "pass"
    assert set(paths) == expected_paths
    assert payload["required_entrypoint_count"] == len(expected_paths)
    for entry in paths.values():
        assert entry["exists"] is True
        assert entry["truth_center_routed"] or entry["explicit_v151_exception"]
        if entry["explicit_v151_exception"]:
            assert entry["fail_closed"] is True
            assert entry["cutover_version"] == "v1.5.2"

    inventory = resolve_truth_entrypoint_inventory(root, version=VERSION)
    assert inventory["authority_state"] == TRUTH_SOURCE_MODEL
    assert inventory["authority_flip_allowed"] is False


def test_truth_map_entrypoint_inventory_cli_emits_json() -> None:
    root = Path(__file__).resolve().parents[1]
    runner = CliRunner()

    result = runner.invoke(app, ["truth-map", "entrypoint-inventory", "--project", str(root), "--version", VERSION, "--strict", "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["required_entrypoint_count"] >= 13
