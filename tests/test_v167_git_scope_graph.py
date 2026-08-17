"""Tests for beacon-git-scope-graph-v167 (GitScopeGraph + topology_gate)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from beacon.utils.git_scope_graph import (
    SCHEMA_VERSION,
    TOPOLOGY_MULTI,
    TOPOLOGY_SINGLE,
    aggregate_topology_gate,
    artifact_path,
    build_git_scope_graph,
    resolve_project_topology,
    run_topology_resolve,
    topology_gate_required,
)
from beacon.utils.project_governance import commit_governance_payload


def _git(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return str(result.stdout or "").strip()


def _seed_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(["git", "init", "-b", "main"], cwd=root)
    _git(["git", "config", "user.email", "test@example.com"], cwd=root)
    _git(["git", "config", "user.name", "Beacon Test"], cwd=root)
    (root / "README.md").write_text("ok\n", encoding="utf-8")
    _git(["git", "add", "README.md"], cwd=root)
    _git(["git", "commit", "-m", "init"], cwd=root)


def _seed_governance(root: Path, *, topology_kind: str = "single_repo", extra_bindings: list | None = None) -> None:
    bindings = extra_bindings or [
        {
            "service_key": "beacon",
            "repo_root": str(root),
            "repo_root_relative": ".",
            "role": "primary",
            "writable": True,
            "worktree_path_policy": "follow-repo-root",
        }
    ]
    payload = {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": topology_kind,
            "default_execution_service": "beacon",
            "service_bindings": bindings,
        },
        "version_scoped_metadata": {
            "v1.6.7": {
                "version": "v1.6.7",
                "participating_services": ["beacon"],
                "per_service_canonical_branch": {"beacon": "beacon/v1.6.7"},
                "branch_guard_mode": "strict",
                "previous_version_baseline_branch": "main",
                "next_version_feature_branch": "beacon/v1.6.7/<feature-slug>",
                "worktree_mode": "dedicated",
                "worktree_path": ".beacon/worktrees/v1.6.7",
                "require_workspace_admission": False,
                "admission_invalidation": "dirty_only",
            }
        },
    }
    commit_governance_payload(root, payload, event_type="test-seed")
    meta_path = root / ".beacon" / "metadata" / "project-version-metadata.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    docs = root / "docs" / "beacon"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "VERSION").write_text("v1.6.7\n", encoding="utf-8")


def test_schema_minimum_fields(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    graph = build_git_scope_graph(tmp_path, version="v1.6.7", feature="demo-f")
    assert graph["schema_version"] == SCHEMA_VERSION
    assert graph["project_topology"] == TOPOLOGY_SINGLE
    assert graph["scopes"]
    assert "topology_gate_status" in graph


def test_single_repo_equivalent_to_v166(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path, topology_kind="single_repo")
    graph = build_git_scope_graph(tmp_path, version="v1.6.7", feature="demo-f")
    assert graph["topology_gate_status"] == "pass"
    assert len(graph["scopes"]) == 1
    assert graph["scopes"][0]["scope_id"] == "primary"


def test_monorepo_dirty_service_blocks(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    (tmp_path / "svc-a").mkdir()
    (tmp_path / "svc-a" / "dirty.txt").write_text("x\n", encoding="utf-8")
    _seed_governance(
        tmp_path,
        topology_kind="monorepo",
        extra_bindings=[
            {
                "service_key": "svc-a",
                "repo_root_relative": ".",
                "role": "primary",
                "writable": True,
                "path": "svc-a",
            }
        ],
    )
    graph = build_git_scope_graph(tmp_path, version="v1.6.7", feature="demo-f")
    assert graph["topology_gate_status"] == "blocked"


def test_multi_git_satellite_blocked(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    sat = tmp_path / "satellite"
    _seed_repo(sat)
    (sat / "dirty.txt").write_text("y\n", encoding="utf-8")
    _git(["git", "add", "dirty.txt"], cwd=sat)
    _seed_governance(
        tmp_path,
        topology_kind="multi_git_workspace",
        extra_bindings=[
            {"service_key": "primary", "repo_root_relative": ".", "role": "primary", "writable": True},
            {
                "service_key": "sat",
                "repo_root_relative": "satellite",
                "role": "satellite",
                "writable": False,
                "dirty_policy": "fail_closed",
            },
        ],
    )
    graph = build_git_scope_graph(tmp_path, version="v1.6.7", feature="demo-f")
    assert graph["topology_gate_status"] == "blocked"
    assert graph["project_topology"] == TOPOLOGY_MULTI


def test_topology_resolve_cli_writes_artifact(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    payload = run_topology_resolve(tmp_path, version="v1.6.7", feature="demo-f", dry_run=False)
    path = artifact_path(tmp_path, version="v1.6.7", feature="demo-f")
    assert path.is_file()
    assert payload.get("topology_gate_ref")


def test_topology_gate_required_v167() -> None:
    assert topology_gate_required("v1.6.7") is True
    assert topology_gate_required("v1.6.6") is False


def test_aggregate_topology_gate_pass_and_block() -> None:
    assert aggregate_topology_gate([{"status": "pass"}])[0] == "pass"
    status, codes = aggregate_topology_gate([{"status": "blocked", "reason_codes": ["x"]}])
    assert status == "blocked"
    assert "x" in codes


def test_v2_branch_context_parity_fixture(tmp_path: Path) -> None:
    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    graph = build_git_scope_graph(tmp_path, version="v1.6.7", feature="demo-f")
    fixture = tmp_path / "docs/beacon/v1.6.7/.machine/schemas/git-scope-graph-v167.fixture.json"
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    loaded = json.loads(fixture.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == SCHEMA_VERSION
    assert "scopes" in loaded

def test_program_level_profile_sidepilot(tmp_path: Path) -> None:
    """AC-GSG-005: program-level branch_resolution_mode maps to single scope profile."""
    _seed_repo(tmp_path)
    worktree = tmp_path / "sidepilot-v167"
    worktree.mkdir(parents=True, exist_ok=True)
    _git(["git", "branch", "beacon/v1.6.7"], cwd=tmp_path)
    _git(["git", "worktree", "add", str(worktree), "beacon/v1.6.7"], cwd=tmp_path)
    exec_dir = tmp_path / "docs" / "beacon" / "v1.6.7" / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / "git-workflow-sidepilot-pi-host.md").write_text(
        "\n".join(
            [
                "# Git Workflow",
                "",
                "- feature: `sidepilot-pi-host`",
                "- version: `v1.6.7`",
                "- branch_resolution_mode: `program-level`",
                "- expected_branch: `beacon/v1.6.7`",
                f"- dedicated_worktree_path: `{worktree}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _seed_governance(
        tmp_path,
        extra_bindings=[
            {
                "service_key": "beacon",
                "repo_root_relative": ".",
                "role": "primary",
                "writable": True,
                "branch_resolution_mode": "program-level",
                "target_branch": "beacon/v1.6.7",
                "worktree_path": str(worktree),
            }
        ],
    )
    _git(["git", "add", "docs"], cwd=tmp_path)
    _git(["git", "commit", "-m", "seed sidepilot program-level"], cwd=tmp_path)
    graph = build_git_scope_graph(tmp_path, version="v1.6.7", feature="sidepilot-pi-host")
    assert len(graph["scopes"]) == 1
    assert graph["scopes"][0]["branch_resolution_mode"] == "program-level"
    assert graph["scopes"][0]["scope_id"] == "primary"


def test_precheck_bundle_includes_topology_gate(tmp_path: Path) -> None:
    from beacon.utils.standard_execution_precheck import run_standard_execution_precheck

    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    docs = tmp_path / "docs" / "beacon" / "v1.6.7" / "features" / "demo-f"
    for name in ("truth.md", "tests.md", "tasks.md", "evidence.md"):
        docs.mkdir(parents=True, exist_ok=True)
        (docs / name).write_text(f"---\nslug: demo-f\nversion: v1.6.7\nstatus: frozen\n---\n\n# {name}\n", encoding="utf-8")
    payload = run_standard_execution_precheck(tmp_path, version="v1.6.7", feature="demo-f", run_id="tc-gsg-007")
    bundle = payload.get("verification_bundle") or {}
    assert "topology_gate" in bundle
    assert payload.get("topology_gate_ref")


def test_loop_goal_rejects_missing_topology_ref(tmp_path: Path) -> None:
    import json
    from beacon.utils.loop_goal_state import init, record_standard_execution_precheck

    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    state = init(tmp_path, version="v1.6.7", feature="demo-f", utterance="u1")
    ref = f".beacon/state/loop-goal/{state['run_id']}.verification-bundle.json"
    path = tmp_path / ref
    path.parent.mkdir(parents=True, exist_ok=True)
    cli_payload = {
        "schema_version": "standard-execution-precheck.v1",
        "produced_by": "beacon.status.standard-execution-precheck",
        "cli_owned": True,
        "verification_bundle": {
            "truth_map_verify": {"status": "pass"},
            "verify_materials_strict": {"status": "pass"},
            "git_diff_check": {"status": "pass"},
            "branch_governance_verify": {"status": "pass"},
            "workspace_admission": {"status": "pass"},
            "topology_gate": {"status": "pass"},
        },
        "canonical_refreeze_committed": True,
        "truth_baseline_merged": True,
        "truth_baseline_commit": "abc123",
        "feature_worktree_reconciled": True,
        "workspace_admission_ref": ".beacon/state/workspace-admission/v1.6.7/demo-f.json",
    }
    path.write_text(json.dumps(cli_payload), encoding="utf-8")
    precheck = {
        "truth_baseline_commit": "abc123",
        "canonical_refreeze_committed": True,
        "truth_baseline_merged": True,
        "feature_worktree_reconciled": True,
        "verification_bundle": cli_payload["verification_bundle"],
        "verification_bundle_ref": ref,
        "workspace_admission_ref": ".beacon/state/workspace-admission/v1.6.7/demo-f.json",
    }
    result = record_standard_execution_precheck(tmp_path, run_id=state["run_id"], precheck=precheck)
    assert result.get("reason_code") == "topology_gate_ref_missing"


def test_git_scopes_ledger_projection(tmp_path: Path) -> None:
    from beacon.utils.runtime_projection import build_runtime_projection

    _seed_repo(tmp_path)
    _seed_governance(tmp_path)
    run_topology_resolve(tmp_path, version="v1.6.7", feature="demo-f", dry_run=False)
    projection = build_runtime_projection(tmp_path, docs_version="v1.6.7", feature="demo-f")
    git_scopes = projection.get("source_snapshot", {}).get("git_scopes") or projection.get("git_scopes") or []
    assert git_scopes
    assert any(str(scope.get("role") or "") == "primary" for scope in git_scopes)
