from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_git_alignment(root: Path, *, blocked: bool) -> None:
    exec_dir = root / "docs" / "beacon" / "v1.1.1" / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / "git-alignment.json").write_text(
        json.dumps(
            {
                "git_refs": {
                    "base_branch": "main",
                    "target_branch": "beacon/v1.1.1",
                    "current_branch": "main" if blocked else "beacon/v1.1.1",
                    "commit": "abc123",
                    "tag": "",
                    "worktree_path": str(root),
                },
                "alignment": {"version_ref_satisfied": not blocked},
                "version_ref": "v1.1.1",
                "blocked": blocked,
                "reason_codes": ["git_version_ref_not_satisfied"] if blocked else [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    # supporting files for delivery audit internals
    for name, payload in {
        "config.json": {"resolved_project": {}, "docs": {}, "implementation": {}, "source_info": {}, "git": {}, "research": {}, "delivery": {}},
        "source.json": {"project_name": "demo", "project_root": str(root), "workspace_root": str(root.parent), "repo_url": "https://example.com/demo.git", "branch": "beacon/v1.1.1", "commit": "abc123", "run_id": "run-1", "version": "v1.1.1"},
        "delivery-manifest.json": {"affected_projects": [{"name": "demo", "project_root": str(root), "repo_url": "https://example.com/demo.git", "change_scope": "docs", "changed_layers": ["execution"], "base_branch": "main", "target_branch": "beacon/v1.1.1", "current_branch": "beacon/v1.1.1", "commit": "abc123", "tag": "", "worktree_path": str(root)}]},
        "change-impact.json": {"changed_layers": ["execution"], "tasks": [], "research_converged": True, "main_chain_converged": True, "delivery_manifest_ready": True},
    }.items():
        (exec_dir / name).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_verify_git_alignment_should_block_on_mismatch(tmp_path: Path):
    _seed_git_alignment(tmp_path, blocked=True)
    result = _invoke(["doctor", "verify-git-alignment", "--project-root", str(tmp_path), "--version", "v1.1.1", "--strict", "--json"])
    assert result.exit_code == 2


def test_verify_git_alignment_should_pass_when_branch_matches(tmp_path: Path):
    _seed_git_alignment(tmp_path, blocked=False)
    result = _invoke(["doctor", "verify-git-alignment", "--project-root", str(tmp_path), "--version", "v1.1.1", "--strict", "--json"])
    assert result.exit_code == 0


def test_verify_git_alignment_should_require_git_workflow_contract_when_v130_has_plan(tmp_path: Path):
    version = "v1.3.0"
    exec_dir = tmp_path / "docs" / "beacon" / version / "execution"
    machine_dir = tmp_path / "docs" / "beacon" / version / ".machine" / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    machine_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / "git-alignment.json").write_text(
        json.dumps(
            {
                "git_refs": {
                    "base_branch": "main",
                    "target_branch": "beacon/v1.3.0",
                    "current_branch": "beacon/v1.3.0",
                    "commit": "abc123",
                    "tag": "",
                    "worktree_path": str(tmp_path),
                },
                "alignment": {"version_ref_satisfied": True},
                "version_ref": version,
                "blocked": False,
                "reason_codes": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    for name, payload in {
        "config.json": {"resolved_project": {}, "docs": {}, "implementation": {}, "source_info": {}, "git": {}, "research": {}, "delivery": {}},
        "source.json": {"project_name": "demo", "project_root": str(tmp_path), "workspace_root": str(tmp_path.parent), "repo_url": "https://example.com/demo.git", "branch": "beacon/v1.3.0", "commit": "abc123", "run_id": "run-1", "version": version},
        "delivery-manifest.json": {"affected_projects": [{"name": "demo", "project_root": str(tmp_path), "repo_url": "https://example.com/demo.git", "change_scope": "docs", "changed_layers": ["execution"], "base_branch": "main", "target_branch": "beacon/v1.3.0", "current_branch": "beacon/v1.3.0", "commit": "abc123", "tag": "", "worktree_path": str(tmp_path)}]},
        "change-impact.json": {"changed_layers": ["execution"], "tasks": [], "research_converged": True, "main_chain_converged": True, "delivery_manifest_ready": True},
        "implementation-plan-demo.json": {"feature": "Demo", "feature_slug": "demo", "version": version, "tasks": [{"task_id": "ITASK-001"}], "source_refs": {"prd": "docs/beacon/v1.3.0/prd/demo.md"}},
    }.items():
        target = machine_dir / name if name.startswith("implementation-plan-") else exec_dir / name
        target.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    result = _invoke(["doctor", "verify-git-alignment", "--project-root", str(tmp_path), "--version", version, "--strict", "--json"])
    assert result.exit_code == 2
