from __future__ import annotations

import json
from pathlib import Path

from beacon.commands.gate import GateMode, check_delivery_execution_artifacts


def _seed_release_execution(root: Path, *, version: str = "v1.1.1", with_manifest: bool = True, pending_task: bool = False) -> None:
    exec_dir = root / "docs" / "beacon" / version / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / "config.json").write_text(
        json.dumps(
            {
                "resolved_project": {},
                "docs": {},
                "implementation": {},
                "source_info": {},
                "git": {},
                "research": {},
                "delivery": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (exec_dir / "source.json").write_text(
        json.dumps(
            {
                "project_name": "demo",
                "project_root": str(root),
                "workspace_root": str(root.parent),
                "repo_url": "https://example.com/demo.git",
                "branch": "beacon/v1.1.1",
                "commit": "abc123",
                "run_id": "run-1",
                "version": version,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (exec_dir / "git-alignment.json").write_text(
        json.dumps(
            {
                "git_refs": {
                    "base_branch": "main",
                    "target_branch": "beacon/v1.1.1",
                    "current_branch": "beacon/v1.1.1",
                    "commit": "abc123",
                    "tag": "",
                    "worktree_path": str(root),
                },
                "alignment": {"version_ref_satisfied": True},
                "version_ref": version,
                "blocked": False,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (exec_dir / "change-impact.json").write_text(
        json.dumps(
            {
                "changed_layers": ["execution"],
                "tasks": [{"task": "finalize", "status": "pending" if pending_task else "completed"}],
                "research_converged": True,
                "main_chain_converged": True,
                "delivery_manifest_ready": True,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    if with_manifest:
        (exec_dir / "delivery-manifest.json").write_text(
            json.dumps(
                {
                    "affected_projects": [
                        {
                            "name": "demo",
                            "project_root": str(root),
                            "repo_url": "https://example.com/demo.git",
                            "change_scope": "docs",
                            "changed_layers": ["execution"],
                            "base_branch": "main",
                            "target_branch": "beacon/v1.1.1",
                            "current_branch": "beacon/v1.1.1",
                            "commit": "abc123",
                            "tag": "",
                            "worktree_path": str(root),
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


def test_gate_release_should_flag_delivery_manifest_missing(tmp_path: Path):
    _seed_release_execution(tmp_path, with_manifest=False)
    issues = check_delivery_execution_artifacts(tmp_path, GateMode.STRICT, "release", "v1.1.1")
    reason_codes = {item["reason_code"] for item in issues}
    assert "delivery_manifest_missing" in reason_codes


def test_gate_release_should_flag_change_impact_open_tasks(tmp_path: Path):
    _seed_release_execution(tmp_path, pending_task=True)
    issues = check_delivery_execution_artifacts(tmp_path, GateMode.STRICT, "release", "v1.1.1")
    reason_codes = {item["reason_code"] for item in issues}
    assert "change_impact_open_tasks" in reason_codes


def test_gate_release_should_skip_delivery_execution_contract_before_v111(tmp_path: Path):
    _seed_release_execution(tmp_path, version="v1.0.0", pending_task=True)
    issues = check_delivery_execution_artifacts(tmp_path, GateMode.STRICT, "release", "v1.0.0")
    assert issues == []


def test_gate_release_should_require_git_workflow_contract_for_v130_plans(tmp_path: Path):
    version = "v1.3.0"
    _seed_release_execution(tmp_path, version=version, pending_task=False)
    machine_dir = tmp_path / "docs" / "beacon" / version / ".machine" / "execution"
    machine_dir.mkdir(parents=True, exist_ok=True)
    (machine_dir / "implementation-plan-demo.json").write_text(
        json.dumps(
            {
                "feature": "Demo",
                "feature_slug": "demo",
                "version": version,
                "tasks": [{"task_id": "ITASK-001"}],
                "source_refs": {"prd": "docs/beacon/v1.3.0/prd/demo.md"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    issues = check_delivery_execution_artifacts(tmp_path, GateMode.STRICT, "release", version)
    reason_codes = {item["reason_code"] for item in issues}
    assert "git_workflow_contract_missing" in reason_codes


def test_gate_release_should_ignore_support_implementation_plan_marker(tmp_path: Path):
    version = "v1.3.0"
    _seed_release_execution(tmp_path, version=version, pending_task=False)
    machine_dir = tmp_path / "docs" / "beacon" / version / ".machine" / "execution"
    machine_dir.mkdir(parents=True, exist_ok=True)
    (machine_dir / "implementation-plan-support.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "version": version,
                "supported": True,
                "notes": ["feature-specific implementation plans are generated on demand"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    issues = check_delivery_execution_artifacts(tmp_path, GateMode.STRICT, "release", version)
    reason_codes = {item["reason_code"] for item in issues}
    assert "git_workflow_contract_missing" not in reason_codes


def test_gate_release_should_detect_delivery_manifest_git_workflow_mismatch(tmp_path: Path):
    version = "v1.3.0"
    _seed_release_execution(tmp_path, version=version, pending_task=False)
    machine_dir = tmp_path / "docs" / "beacon" / version / ".machine" / "execution"
    exec_dir = tmp_path / "docs" / "beacon" / version / "execution"
    machine_dir.mkdir(parents=True, exist_ok=True)
    (machine_dir / "implementation-plan-demo.json").write_text(
        json.dumps(
            {
                "feature": "Demo",
                "feature_slug": "demo",
                "version": version,
                "tasks": [{"task_id": "ITASK-001"}],
                "source_refs": {"prd": "docs/beacon/v1.3.0/prd/demo.md"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (machine_dir / "git-workflow-demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": "Demo",
                "feature_slug": "demo",
                "version": version,
                "mode": "single-repo",
                "expected_branch": "feature/v1.3.0-demo",
                "branch_prefix": "feature/",
                "base_branch": "main",
                "use_git_worktree": False,
                "require_clean_worktree_for_switch": True,
                "service_directories": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (exec_dir / "git-workflow-demo.md").write_text("# Contract\n", encoding="utf-8")
    issues = check_delivery_execution_artifacts(tmp_path, GateMode.STRICT, "release", version)
    reason_codes = {item["reason_code"] for item in issues}
    assert "git_workflow_delivery_manifest_mismatch" in reason_codes
