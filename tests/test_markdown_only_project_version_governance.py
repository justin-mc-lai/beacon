from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.commands.implement import commands as implement_commands
from beacon.utils.material_gate_contract import branch_governance_writeback_targets
from beacon.utils.project_governance import (
    GOVERNANCE_MD_REL,
    PARSER_CONTRACT,
    commit_governance_payload,
    governance_json_path,
    governance_md_authoritative,
    governance_md_path,
    load_governance_payload,
    migrate_json_to_governance_md,
    parse_governance_markdown,
    render_governance_markdown,
    resolve_project_governance,
)
from beacon.utils.project_metadata import (
    load_project_metadata,
    metadata_machine_path,
    resolve_project_metadata_view,
    verify_project_metadata,
)
from beacon.utils.truth_map import GENERATED_GOVERNANCE_SURFACES, VERSION_GOVERNANCE_SURFACES


def _seed_governance_md(root: Path, *, version: str = "v9.9.9") -> None:
    payload = {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": "monorepo",
            "default_execution_service": "svc-a",
            "service_bindings": [
                {
                    "service_key": "svc-a",
                    "repo_root": str(root / "svc-a"),
                    "repo_root_relative": "svc-a",
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                },
                {
                    "service_key": "svc-b",
                    "repo_root": str(root / "svc-b"),
                    "repo_root_relative": "svc-b",
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                },
            ],
        },
        "version_scoped_metadata": {
            version: {
                "version": version,
                "participating_services": ["svc-a", "svc-b"],
                "per_service_canonical_branch": {"svc-a": "beacon/v9.9.9", "svc-b": "beacon/v9.9.9-b"},
                "branch_guard_mode": "strict",
                "validation_state": "active",
            }
        },
    }
    commit_governance_payload(root, payload, event_type="test-seed")


def test_governance_md_is_sole_authority_path(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    view = resolve_project_governance(tmp_path, version="v9.9.9")
    assert view["authority"] == "markdown_project_governance"
    assert view["parser_contract"] == PARSER_CONTRACT
    assert view["paths"]["governance_md"].endswith(str(GOVERNANCE_MD_REL))


def test_governance_json_absence_fail_closed(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    json_path = governance_json_path(tmp_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text("{}", encoding="utf-8")
    verdict = verify_project_metadata(tmp_path, version="v9.9.9")
    json_check = next(item for item in verdict["checks"] if item["name"] == "governance_json_forbidden")
    assert json_check["status"] == "fail"


def test_consumers_use_resolve_project_governance(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    view = resolve_project_metadata_view(tmp_path, version="v9.9.9")
    assert view.get("authority") == "markdown_project_governance"
    assert view["paths"]["governance_md"]


def test_load_project_metadata_reads_md_only(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    json_path = metadata_machine_path(tmp_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps({"global_project_metadata": {"topology_kind": "wrong"}}), encoding="utf-8")
    payload = load_project_metadata(tmp_path)
    assert payload["global_project_metadata"]["topology_kind"] == "monorepo"


def test_commit_writes_md_not_governance_json(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    payload = load_governance_payload(tmp_path)
    payload["global_project_metadata"]["topology_kind"] = "single_repo"
    commit_governance_payload(tmp_path, payload, event_type="test-update")
    assert governance_md_authoritative(tmp_path)
    assert not governance_json_path(tmp_path).exists()


def test_execution_triple_branch_merge_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_governance_md(tmp_path)
    monkeypatch.setattr(
        implement_commands,
        "load_execution_branch_contract",
        lambda *_args, **_kwargs: {
            "material_paths": ["docs/beacon/v9.9.9/execution/git-workflow-demo.md"],
            "expected_branch": "origin/master",
            "service_branch_map": {"svc-a": "origin/master"},
        },
    )
    monkeypatch.setattr(
        implement_commands,
        "load_or_seed_implementation_git_workflow_contract",
        lambda *_args, **_kwargs: {"expected_branch": "origin/master"},
    )
    payload = implement_commands._branch_guard_inputs(tmp_path, version="v9.9.9", feature="demo")
    assert payload["expected_branch"] == "beacon/v9.9.9"
    assert payload["service_branch_map"]["svc-a"] == "beacon/v9.9.9"
    assert payload["execution_branch_contract"]["execution_branch_override_blocked"] is True


def test_toolkit_shared_md_transaction(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    targets = branch_governance_writeback_targets(tmp_path, version="v9.9.9", feature="demo")
    assert targets["target_artifacts"]["metadata_contract"].endswith("project-version-governance.md")


def test_branch_guard_inputs_from_resolver_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_governance_md(tmp_path)
    monkeypatch.setattr(
        implement_commands,
        "load_execution_branch_contract",
        lambda *_args, **_kwargs: {
            "material_paths": ["docs/beacon/v9.9.9/execution/branch-governance-demo.md"],
            "service_branch_map": {"svc-a": "wrong/from-execution"},
        },
    )
    monkeypatch.setattr(
        implement_commands,
        "load_or_seed_implementation_git_workflow_contract",
        lambda *_args, **_kwargs: {},
    )
    payload = implement_commands._branch_guard_inputs(tmp_path, version="v9.9.9", feature="demo")
    assert "wrong/from-execution" not in payload.get("service_branch_map", {}).values()


def test_monorepo_version_contract_from_md(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    view = resolve_project_governance(tmp_path, version="v9.9.9")
    assert view["topology_kind"] == "monorepo"
    assert set(view["version_contract"]["per_service_canonical_branch"].keys()) == {"svc-a", "svc-b"}


def test_migrate_removes_governance_json(tmp_path: Path) -> None:
    json_path = governance_json_path(tmp_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "project_root": str(tmp_path),
                "global_project_metadata": {
                    "project_root": str(tmp_path),
                    "topology_kind": "single_repo",
                    "default_execution_service": "beacon",
                    "service_bindings": [
                        {
                            "service_key": "beacon",
                            "repo_root": str(tmp_path),
                            "role": "service",
                            "writable": True,
                            "worktree_path_policy": "follow-repo-root",
                        }
                    ],
                },
                "version_scoped_metadata": {
                    "v1.0.0": {
                        "version": "v1.0.0",
                        "participating_services": ["beacon"],
                        "per_service_canonical_branch": {"beacon": "beacon/v1.0.0"},
                        "branch_guard_mode": "strict",
                        "validation_state": "active",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    result = migrate_json_to_governance_md(tmp_path)
    assert result["status"] == "ok"
    assert governance_md_authoritative(tmp_path)
    assert not json_path.exists()


def test_material_gate_uses_governance_md_resolver(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    targets = branch_governance_writeback_targets(tmp_path, version="v9.9.9", feature="demo")
    rel = targets["target_artifacts"]["metadata_contract"]
    assert "project-version-governance.md" in rel
    assert "project-version-metadata.json" not in rel


def test_truth_map_registers_project_governance_surface() -> None:
    assert "project_governance" in VERSION_GOVERNANCE_SURFACES
    path_template, role, required = VERSION_GOVERNANCE_SURFACES["project_governance"]
    assert path_template.endswith("project-version-governance.md")
    assert role == "version_governance_truth"
    assert required is True
    generated_path, _, _ = GENERATED_GOVERNANCE_SURFACES["project_version_metadata"]
    assert generated_path.endswith("project-version-metadata.json")
    governance_md_path_template, _, _ = VERSION_GOVERNANCE_SURFACES["project_governance"]
    assert generated_path != governance_md_path_template


def test_explicit_version_canonical_branch_from_governance_md(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_governance_md(tmp_path)
    monkeypatch.setattr(
        implement_commands,
        "load_execution_branch_contract",
        lambda *_args, **_kwargs: {"material_paths": [], "expected_branch": "origin/master"},
    )
    monkeypatch.setattr(
        implement_commands,
        "load_or_seed_implementation_git_workflow_contract",
        lambda *_args, **_kwargs: {"expected_branch": "origin/master"},
    )
    payload = implement_commands._branch_guard_inputs(tmp_path, version="v9.9.9", feature="demo")
    assert payload["expected_branch"] != "origin/master"
    assert payload["expected_branch"] == "beacon/v9.9.9"


def test_parse_render_roundtrip_preserves_version_contract(tmp_path: Path) -> None:
    _seed_governance_md(tmp_path)
    original = load_governance_payload(tmp_path)
    text = render_governance_markdown(original)
    parsed = parse_governance_markdown(text, project_root=tmp_path)
    assert parsed["version_scoped_metadata"]["v9.9.9"]["per_service_canonical_branch"]["svc-a"] == "beacon/v9.9.9"
