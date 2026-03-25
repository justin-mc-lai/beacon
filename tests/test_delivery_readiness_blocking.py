from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_delivery_package(root: Path, *, version: str = "v1.1.1", blocked: bool = False) -> None:
    exec_dir = root / "docs" / "beacon" / version / ".machine" / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / version / "execution").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / version / "execution" / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
    (exec_dir / "config.json").write_text(json.dumps({"resolved_project": {}, "docs": {}, "implementation": {}, "source_info": {}, "git": {}, "research": {}, "delivery": {}}), encoding="utf-8")
    (exec_dir / "source.json").write_text(json.dumps({"project_name": "demo", "project_root": str(root), "workspace_root": str(root.parent), "repo_url": "https://example.com/demo.git", "branch": "main", "commit": "abc123", "run_id": "run-demo", "version": version}), encoding="utf-8")
    (exec_dir / "git-alignment.json").write_text(json.dumps({"git_refs": {}, "alignment": {}, "version_ref": version, "blocked": blocked, "reason_codes": ["branch_drift"] if blocked else []}), encoding="utf-8")
    (exec_dir / "delivery-manifest.json").write_text(json.dumps({"affected_projects": [{"name": "demo", "project_root": str(root), "repo_url": "https://example.com/demo.git", "change_scope": "docs", "changed_layers": ["execution"], "base_branch": "main", "target_branch": version, "current_branch": version, "commit": "abc123", "tag": version, "worktree_path": str(root)}]}), encoding="utf-8")
    (exec_dir / "change-impact.json").write_text(json.dumps({"changed_layers": ["execution"], "tasks": [], "research_converged": True, "main_chain_converged": True, "delivery_manifest_ready": True}), encoding="utf-8")
    (exec_dir / "terminal.json").write_text(json.dumps({"status": "Pass", "traceability": {}, "version": version, "run_id": "run-demo", "feature": "demo"}), encoding="utf-8")


def test_verify_delivery_should_match_git_alignment_blocking_state(tmp_path: Path):
    _seed_delivery_package(tmp_path, blocked=False)
    result = _invoke(["doctor", "verify-delivery", "--project-root", str(tmp_path), "--version", "v1.1.1", "--strict", "--json"])
    payload = json.loads(result.stdout)
    checks = payload.get("result", {}).get("checks", [])
    git_check = next(item for item in checks if item.get("name") == "execution_git_alignment_schema")
    blocked = bool(git_check.get("details", {}).get("blocked"))
    if blocked:
        assert result.exit_code == 2, result.stdout
        assert payload["status"] == "FAIL"
        assert git_check["status"] == "fail"
    else:
        assert result.exit_code == 0, result.stdout
        assert payload["status"] == "PASS"
        assert git_check["status"] == "pass"
