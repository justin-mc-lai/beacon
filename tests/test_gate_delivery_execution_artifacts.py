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
