from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_execution(root: Path) -> None:
    exec_dir = root / "docs" / "beacon" / "v1.1.1" / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (exec_dir / "config.json").write_text(
        json.dumps({"resolved_project": {}, "docs": {}, "implementation": {}, "source_info": {}, "git": {}, "research": {}, "delivery": {}}, ensure_ascii=False),
        encoding="utf-8",
    )
    (exec_dir / "source.json").write_text(
        json.dumps({"project_name": "demo", "project_root": str(root), "workspace_root": str(root.parent), "repo_url": "https://example.com/demo.git", "branch": "beacon/v1.1.1", "commit": "abc123", "run_id": "run-1", "version": "v1.1.1"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (exec_dir / "git-alignment.json").write_text(json.dumps({"git_refs": {}, "alignment": {}, "version_ref": "v1.1.1", "blocked": False}, ensure_ascii=False), encoding="utf-8")
    (exec_dir / "delivery-manifest.json").write_text(json.dumps({"affected_projects": [{"name": "demo", "project_root": str(root), "repo_url": "https://example.com/demo.git", "change_scope": "docs", "changed_layers": ["execution"], "base_branch": "main", "target_branch": "beacon/v1.1.1", "current_branch": "beacon/v1.1.1", "commit": "abc123", "tag": "", "worktree_path": str(root)}]}, ensure_ascii=False), encoding="utf-8")
    (exec_dir / "change-impact.json").write_text(json.dumps({"changed_layers": ["execution"], "tasks": [], "research_converged": True, "main_chain_converged": True, "delivery_manifest_ready": True}, ensure_ascii=False), encoding="utf-8")


def test_verify_config_should_pass_when_config_and_source_are_present(tmp_path: Path):
    _seed_execution(tmp_path)
    result = _invoke(["doctor", "verify-config", "--project-root", str(tmp_path), "--version", "v1.1.1", "--strict", "--json"])
    assert result.exit_code == 0, result.stdout


def test_verify_config_should_block_when_source_missing(tmp_path: Path):
    _seed_execution(tmp_path)
    (tmp_path / "docs" / "beacon" / "v1.1.1" / "execution" / "source.json").unlink()
    result = _invoke(["doctor", "verify-config", "--project-root", str(tmp_path), "--version", "v1.1.1", "--strict", "--json"])
    assert result.exit_code == 2
