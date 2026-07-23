"""Regression: freeze/package path must register monorepo version branch contracts."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.program_plan_runtime import governance_precheck
from beacon.utils.project_metadata import (
    ensure_version_contract_from_feature_package,
    load_project_metadata,
)
from beacon.utils.project_governance import commit_governance_payload, load_governance_payload
from beacon.utils.truth_map import evaluate_implement_version_governance_preflight


def _seed_monorepo(tmp_path: Path) -> Path:
    root = tmp_path / "rolo-like"
    root.mkdir()
    (root / "docs" / "beacon" / "governance").mkdir(parents=True)
    (root / "docs" / "beacon" / "v9.9.1" / "features" / "demo-cutover").mkdir(parents=True)
    (root / "marketing_sys").mkdir()
    (root / "push-svr").mkdir()
    payload = {
        "schema_version": "1.0",
        "project_root": str(root),
        "global_project_metadata": {
            "project_root": str(root),
            "topology_kind": "monorepo",
            "default_execution_service": "marketing_sys",
            "service_bindings": [
                {
                    "service_key": "marketing_sys",
                    "repo_root": str(root / "marketing_sys"),
                    "repo_root_relative": "marketing_sys",
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                },
                {
                    "service_key": "push-svr",
                    "repo_root": str(root / "push-svr"),
                    "repo_root_relative": "push-svr",
                    "role": "service",
                    "writable": True,
                    "worktree_path_policy": "follow-repo-root",
                },
            ],
        },
        "version_scoped_metadata": {
            "v9.9.0": {
                "version": "v9.9.0",
                "participating_services": ["marketing_sys"],
                "per_service_canonical_branch": {"marketing_sys": "feature/v9.9.0"},
                "branch_guard_mode": "strict",
                "validation_state": "active",
                # intentionally omit truth_canonical to exercise defaulting
            }
        },
    }
    commit_governance_payload(root, payload, event_type="test-seed")
    truth = root / "docs" / "beacon" / "v9.9.1" / "features" / "demo-cutover" / "truth.md"
    truth.write_text(
        """---
slug: demo-cutover
version: v9.9.1
status: frozen
language: zh
parser_contract: beacon-feature-package-v2
git_canonical_branch: beacon/v9.9.1/demo-cutover
participating_services: [marketing_sys, push-svr]
canonical_refs: {}
---

# truth
""",
        encoding="utf-8",
    )
    return root


def test_governance_precheck_defaults_truth_canonical_when_contract_exists(tmp_path: Path) -> None:
    root = _seed_monorepo(tmp_path)
    result = governance_precheck(root, "v9.9.0")
    assert result["status"] == "pass"
    assert result["truth_canonical"] == "main"
    assert result.get("truth_canonical_defaulted") is True


def test_ensure_version_contract_from_feature_package_registers_feature_branch(tmp_path: Path) -> None:
    root = _seed_monorepo(tmp_path)
    result = ensure_version_contract_from_feature_package(
        root,
        version="v9.9.1",
        feature="demo-cutover",
    )
    assert result["status"] == "ok"
    assert result["branch"] == "feature/v9.9.1"
    assert set(result["services"]) == {"marketing_sys", "push-svr"}
    payload = load_project_metadata(root)
    contract = payload["version_scoped_metadata"]["v9.9.1"]
    assert contract["truth_canonical"] == "main"
    assert contract["per_service_canonical_branch"]["marketing_sys"] == "feature/v9.9.1"
    assert contract["per_service_canonical_branch"]["push-svr"] == "feature/v9.9.1"
    gov = governance_precheck(root, "v9.9.1")
    assert gov["status"] == "pass"


def test_implement_preflight_blocks_unregistered_version_with_clear_reason(tmp_path: Path) -> None:
    root = _seed_monorepo(tmp_path)
    preflight = evaluate_implement_version_governance_preflight(
        root,
        version="v9.9.1",
        feature="demo-cutover",
    )
    assert preflight["blocked"] is True
    assert preflight["reason_code"] == "governance_version_not_registered"
