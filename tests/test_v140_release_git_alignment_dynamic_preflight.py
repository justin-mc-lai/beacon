from __future__ import annotations

import importlib
import json
from pathlib import Path

from beacon.commands.gate import GateMode, check_delivery_execution_artifacts
from beacon.utils.runtime import write_json


VERSION = "v1.4.0"
FEATURE = "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution"
SLUG = "beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution"
gate_module = importlib.import_module("beacon.commands.gate")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_v140_delivery_contract_allows_dynamic_git_preflight_pass_when_static_git_alignment_is_stale(tmp_path: Path, monkeypatch) -> None:
    machine_exec = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution"
    human_exec = tmp_path / "docs" / "beacon" / VERSION / "execution"
    machine_exec.mkdir(parents=True, exist_ok=True)
    human_exec.mkdir(parents=True, exist_ok=True)

    for name, payload in {
        "config.json": {
            "resolved_project": {},
            "docs": {},
            "implementation": {},
            "source_info": {},
            "git": {},
            "research": {},
            "delivery": {},
        },
        "source.json": {
            "project_name": "beacon",
            "project_root": str(tmp_path),
            "workspace_root": str(tmp_path.parent),
            "repo_url": "https://example.com/repo.git",
            "branch": "main",
            "commit": "abc123",
            "run_id": "run-1",
            "version": VERSION,
        },
        "git-alignment.json": {
            "git_refs": {
                "base_branch": "main",
                "target_branch": f"beacon/{VERSION}",
                "current_branch": "main",
            },
            "alignment": {
                "branch_matches_target": False,
                "branch_has_required_prefix": False,
                "version_ref_satisfied": False,
            },
            "version_ref": VERSION,
            "blocked": True,
            "reason_codes": [
                "git_branch_target_mismatch",
                "git_branch_prefix_mismatch",
                "git_version_ref_not_satisfied",
            ],
        },
        "delivery-manifest.json": {
            "affected_projects": [
                {
                    "name": "beacon",
                    "project_root": str(tmp_path),
                    "repo_url": "https://example.com/repo.git",
                    "change_scope": "feature",
                    "changed_layers": ["beacon", "tests"],
                    "base_branch": "main",
                    "target_branch": f"beacon/{VERSION}",
                    "current_branch": "main",
                    "commit": "abc123",
                    "tag": "",
                    "worktree_path": str(tmp_path),
                }
            ]
        },
        "change-impact.json": {
            "changed_layers": [],
            "tasks": [],
            "research_converged": True,
            "main_chain_converged": True,
            "delivery_manifest_ready": True,
        },
    }.items():
        _write_json(machine_exec / name, payload)

    workflow_payload = {
        "feature": FEATURE,
        "feature_slug": SLUG,
        "version": VERSION,
        "mode": "single-repo",
        "expected_branch": f"beacon/{VERSION}",
        "branch_prefix": "beacon/",
        "base_branch": "main",
        "use_git_worktree": False,
        "require_clean_worktree_for_switch": True,
        "service_directories": ["."],
        "direct_delivery_services": ["."],
        "git_roots": ["."],
    }
    write_json(machine_exec / f"implementation-plan-{SLUG}.json", {"feature": FEATURE})
    write_json(machine_exec / f"git-workflow-{SLUG}.json", workflow_payload)
    (human_exec / f"git-workflow-{SLUG}.md").write_text("# git workflow\n", encoding="utf-8")

    metadata_payload = {
        "schema_version": "1.0",
        "project_root": str(tmp_path.resolve()),
        "global_project_metadata": {
            "project_root": str(tmp_path.resolve()),
            "topology_kind": "single_repo",
            "default_execution_service": "beacon",
            "service_bindings": [
                {
                    "service_key": "beacon",
                    "repo_root": str(tmp_path.resolve()),
                    "repo_root_relative": "",
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                }
            ],
        },
        "version_scoped_metadata": {
            VERSION: {
                "participating_services": ["beacon"],
                "per_service_canonical_branch": {"beacon": "main"},
                "branch_guard_mode": "metadata",
                "validation_state": "pass",
                "branch_governance": {
                    "target_branch": "main",
                    "blocked": False,
                    "reason_codes": [],
                },
            }
        },
        "transaction": {},
    }
    write_json(tmp_path / ".beacon" / "metadata" / "project-version-metadata.json", metadata_payload)

    monkeypatch.setattr(
        gate_module,
        "build_implement_branch_guard_payload",
        lambda *_args, **_kwargs: {
            "status": "pass",
            "blocked": False,
            "expected_branch": "main",
            "current_branch": "main",
            "reason_codes": [],
        },
    )

    issues = check_delivery_execution_artifacts(tmp_path, GateMode.STRICT, "release", version=VERSION)
    reason_codes = {item["reason_code"] for item in issues}
    assert "git_alignment_blocked" not in reason_codes
