from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.material_audit import build_delivery_audit


def _seed_execution(root: Path, *, version: str = "v1.1.1") -> Path:
    exec_dir = root / "docs" / "beacon" / version / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (exec_dir / "config.json").write_text(
        json.dumps(
            {
                "resolved_project": {
                    "workspace_root": str(root.parent),
                    "project_name": "demo",
                    "project_root": str(root),
                    "resolved_by": "cli",
                    "resolution_order": ["cli", "env", "cwd", "default"],
                },
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
    (exec_dir / "delivery-manifest.json").write_text(
        json.dumps(
            {
                "affected_projects": [
                    {
                        "name": "demo",
                        "project_root": str(root),
                        "repo_url": "https://example.com/demo.git",
                        "change_scope": "docs",
                        "changed_layers": ["user-story", "prd", "test-case"],
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
    (exec_dir / "change-impact.json").write_text(
        json.dumps(
            {
                "changed_layers": ["user-story"],
                "tasks": [],
                "research_converged": True,
                "main_chain_converged": True,
                "delivery_manifest_ready": True,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return exec_dir


def test_verify_delivery_audit_should_expose_resolution_order(tmp_path: Path):
    exec_dir = _seed_execution(tmp_path)
    payload = build_delivery_audit(tmp_path, version="v1.1.1", strict=True)
    assert payload["status"] in {"pass", "warn"}
    config = json.loads((exec_dir / "config.json").read_text(encoding="utf-8"))
    assert config["resolved_project"]["resolution_order"] == ["cli", "env", "cwd", "default"]


def test_config_should_record_workspace_and_project_paths(tmp_path: Path):
    exec_dir = _seed_execution(tmp_path)
    config = json.loads((exec_dir / "config.json").read_text(encoding="utf-8"))
    assert config["resolved_project"]["project_root"] == str(tmp_path)
    assert config["resolved_project"]["workspace_root"] == str(tmp_path.parent)
