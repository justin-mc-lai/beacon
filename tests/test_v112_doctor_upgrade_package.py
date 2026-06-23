from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.version_package_upgrade import registered_upgrade_steps


runner = CliRunner()
VERSION = "v1.1.12"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_old_v112_layout(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (base / "execution" / "config.json").write_text(json.dumps({"resolved_project": {}, "docs": {}, "implementation": {}, "source_info": {}, "git": {}, "research": {}, "delivery": {}}, ensure_ascii=False), encoding="utf-8")
    (base / "execution" / "source.json").write_text(json.dumps({"project_name": "demo", "project_root": str(root), "workspace_root": str(root.parent), "repo_url": "https://example.com/demo.git", "branch": f"beacon/{VERSION}", "commit": "abc123", "run_id": "run-1", "version": VERSION}, ensure_ascii=False), encoding="utf-8")
    (base / "execution" / "git-alignment.json").write_text(json.dumps({"git_refs": {"base_branch": "main", "target_branch": f"beacon/{VERSION}", "current_branch": f"beacon/{VERSION}", "commit": "abc123", "tag": "", "worktree_path": str(root)}, "alignment": {"version_ref_satisfied": True}, "version_ref": VERSION, "blocked": False}, ensure_ascii=False), encoding="utf-8")
    (base / "execution" / "delivery-manifest.json").write_text(json.dumps({"affected_projects": [{"name": "demo", "project_root": str(root), "repo_url": "https://example.com/demo.git", "change_scope": "docs", "changed_layers": ["user-story", "prd", "test-case"], "base_branch": "main", "target_branch": f"beacon/{VERSION}", "current_branch": f"beacon/{VERSION}", "commit": "abc123", "tag": "", "worktree_path": str(root)}]}, ensure_ascii=False), encoding="utf-8")
    (base / "execution" / "change-impact.json").write_text(json.dumps({"changed_layers": ["user-story", "prd", "test-case"], "tasks": [{"task": "finalize", "status": "completed"}], "research_converged": True, "main_chain_converged": True, "delivery_manifest_ready": True}, ensure_ascii=False), encoding="utf-8")
    (base / "execution" / "terminal.json").write_text(json.dumps({"status": "completed"}, ensure_ascii=False), encoding="utf-8")
    (base / "user-story" / "feature.md").write_text("# User Story\n", encoding="utf-8")
    (base / "prd" / "feature.md").write_text("# PRD\n", encoding="utf-8")
    (base / "qa" / "test-cases" / "feature.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / "feature.ac-test-matrix.json").write_text(json.dumps({"entries": []}, ensure_ascii=False), encoding="utf-8")


def test_doctor_upgrade_package_should_apply_cumulative_v112_material_upgrades(tmp_path: Path):
    _seed_old_v112_layout(tmp_path)

    result = _invoke(["doctor", "upgrade-package", "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["result"]["summary"]["written"] >= 1
    assert payload["result"]["summary"]["step_count"] >= 3

    machine_exec = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution"
    assert (machine_exec / "config.json").exists()
    assert (machine_exec / "implementation-plan-support.json").exists()
    assert (tmp_path / "docs" / "beacon" / VERSION / "source-architecture" / "index.md").exists()
    assert (tmp_path / "docs" / "beacon" / VERSION / "execution" / "project-skill-qa-evolution-blueprint.md").exists()

    verify = _invoke(["doctor", "verify-materials", "--project-root", str(tmp_path), "--version", VERSION, "--strict", "--json"])
    assert verify.exit_code == 0, verify.stdout
    verify_payload = json.loads(verify.stdout)
    assert verify_payload["status"] == "PASS"


def test_doctor_upgrade_package_should_expose_append_only_registry_for_future_versions():
    def _semver_tuple(value: str) -> tuple[int, int, int]:
        major, minor, patch = value.lstrip("v").split(".")
        return int(major), int(minor), int(patch)

    registry = registered_upgrade_steps()
    assert [item["step"] for item in registry] == [
        "v1.1.5-machine-surface",
        "v1.1.10-source-architecture",
        "v1.1.12-implementation-plan-support",
        "v1.1.13-release-stub",
    ]
    assert [_semver_tuple(item["min_version"]) for item in registry] == sorted(_semver_tuple(item["min_version"]) for item in registry)
    assert all("append" in str(item.get("future_rule", "")).lower() for item in registry)
