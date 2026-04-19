from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_materials(root: Path, *, version: str = "v1.1.1", feature: str = "feature") -> None:
    research_dir = root / "docs" / "beacon" / version / "research"
    us_dir = root / "docs" / "beacon" / version / "user-story"
    prd_dir = root / "docs" / "beacon" / version / "prd"
    tc_dir = root / "docs" / "beacon" / version / "qa" / "test-cases"
    release_dir = root / "docs" / "beacon" / version / "release"
    for directory in (research_dir, us_dir, prd_dir, tc_dir, release_dir):
        directory.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / version / "SUMMARY.md").write_text("# summary\n", encoding="utf-8")
    (research_dir / "brainstorm-sample.md").write_text("# brainstorm\n", encoding="utf-8")
    (us_dir / f"{feature}.md").write_text("# User Story\n", encoding="utf-8")
    (prd_dir / f"{feature}.md").write_text("# PRD\n", encoding="utf-8")
    (tc_dir / f"{feature}.md").write_text("# Test Cases\n", encoding="utf-8")
    (release_dir / f"{version}.md").write_text("# Release\n", encoding="utf-8")
    (tc_dir / f"{feature}.ac-test-matrix.json").write_text(json.dumps({"entries": []}, ensure_ascii=False), encoding="utf-8")
    (tc_dir / f"{feature}.qa9-matrix.json").write_text(json.dumps({"entries": []}, ensure_ascii=False), encoding="utf-8")


def _seed_delivery(root: Path, *, version: str = "v1.1.1", pending_task: bool = False) -> None:
    (root / "docs" / "beacon" / version / "SUMMARY.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / version / "SUMMARY.md").write_text("# summary\n", encoding="utf-8")
    release_dir = root / "docs" / "beacon" / version / "release"
    release_dir.mkdir(parents=True, exist_ok=True)
    (release_dir / f"{version}.md").write_text("# Release\n", encoding="utf-8")
    exec_dir = root / "docs" / "beacon" / version / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
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
                "changed_layers": ["user-story", "prd", "test-case"],
                "tasks": [
                    {"task": "finalize", "status": "pending" if pending_task else "completed"},
                ],
                "research_converged": True,
                "main_chain_converged": True,
                "delivery_manifest_ready": True,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_doctor_verify_materials_should_pass_when_main_chain_complete(tmp_path: Path):
    _seed_materials(tmp_path)
    result = _invoke(["doctor", "verify-materials", "--project-root", str(tmp_path), "--version", "v1.1.1", "--strict", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload.get("status") == "PASS"


def test_doctor_verify_delivery_should_block_when_change_impact_has_pending_tasks(tmp_path: Path):
    _seed_delivery(tmp_path, pending_task=True)
    result = _invoke(["doctor", "verify-delivery", "--project-root", str(tmp_path), "--version", "v1.1.1", "--strict", "--json"])
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload.get("status") in {"FAIL", "BLOCKED"}
    checks = payload.get("result", {}).get("checks", [])
    names = {item.get("name"): item for item in checks}
    assert names["change_impact_schema_and_closure"]["status"] == "fail"


def test_doctor_verify_config_should_pass_when_execution_config_and_source_present(tmp_path: Path):
    _seed_delivery(tmp_path, pending_task=False)
    result = _invoke(["doctor", "verify-config", "--project-root", str(tmp_path), "--version", "v1.1.1", "--strict", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload.get("status") in {"PASS", "WARN"}


def test_doctor_verify_git_alignment_should_block_when_git_alignment_is_blocked(tmp_path: Path):
    _seed_delivery(tmp_path, pending_task=False)
    exec_dir = tmp_path / "docs" / "beacon" / "v1.1.1" / "execution"
    (exec_dir / "git-alignment.json").write_text(
        json.dumps(
            {
                "git_refs": {"base_branch": "main", "target_branch": "beacon/v1.1.1", "current_branch": "main", "commit": "abc123", "tag": "", "worktree_path": str(tmp_path)},
                "alignment": {"version_ref_satisfied": False},
                "version_ref": "v1.1.1",
                "blocked": True,
                "reason_codes": ["git_version_ref_not_satisfied"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    result = _invoke(["doctor", "verify-git-alignment", "--project-root", str(tmp_path), "--version", "v1.1.1", "--strict", "--json"])
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload.get("status") == "BLOCKED"


def test_doctor_verify_materials_should_block_when_summary_or_release_missing(tmp_path: Path):
    _seed_materials(tmp_path)
    (tmp_path / "docs" / "beacon" / "v1.1.1" / "SUMMARY.md").unlink()
    release_doc = tmp_path / "docs" / "beacon" / "v1.1.1" / "release" / "v1.1.1.md"
    release_doc.unlink()

    result = _invoke(["doctor", "verify-materials", "--project-root", str(tmp_path), "--version", "v1.1.1", "--strict", "--json"])
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    checks = {item["name"]: item for item in payload["result"]["checks"]}
    assert checks["formal_summary_present"]["status"] == "fail"
    assert checks["formal_release_present"]["status"] == "fail"


def test_doctor_verify_materials_should_use_v113_minimum_closure_without_research_or_qa9(tmp_path: Path):
    version = "v1.1.3"
    root = tmp_path / "docs" / "beacon" / version
    (root / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "prd").mkdir(parents=True, exist_ok=True)
    (root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (root / "release").mkdir(parents=True, exist_ok=True)
    (root / "execution").mkdir(parents=True, exist_ok=True)
    (root / "SUMMARY.md").write_text("# summary\n", encoding="utf-8")
    (root / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (root / "user-story" / "feature.md").write_text("# User Story\n", encoding="utf-8")
    (root / "prd" / "feature.md").write_text("# PRD\n", encoding="utf-8")
    (root / "qa" / "test-cases" / "feature.md").write_text("# Test Cases\n", encoding="utf-8")
    (root / "qa" / "test-cases" / "feature.ac-test-matrix.json").write_text(
        json.dumps({"entries": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    (root / "release" / f"{version}.md").write_text("# Release\n", encoding="utf-8")

    result = _invoke(["doctor", "verify-materials", "--project-root", str(tmp_path), "--version", version, "--strict", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    checks = {item["name"]: item for item in payload["result"]["checks"]}
    assert payload.get("status") == "PASS"
    assert checks["research_directory_present"]["status"] == "pass"
    assert checks["research_documents_present"]["status"] == "pass"
    assert checks["formal_boundaries_present"]["status"] == "pass"


def test_doctor_verify_materials_should_ignore_prototype_source_user_story_alias(tmp_path: Path):
    version = "v1.3.4"
    root = tmp_path / "docs" / "beacon" / version
    (root / "user-story").mkdir(parents=True, exist_ok=True)
    (root / "prd").mkdir(parents=True, exist_ok=True)
    (root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (root / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (root / "execution").mkdir(parents=True, exist_ok=True)
    (root / "release").mkdir(parents=True, exist_ok=True)
    (root / "source-architecture").mkdir(parents=True, exist_ok=True)
    (root / "SUMMARY.md").write_text("# summary\n", encoding="utf-8")
    (root / "execution" / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
    (root / "execution" / "project-skill-qa-evolution-blueprint.md").write_text("# blueprint\n", encoding="utf-8")
    (root / "source-architecture" / "index.md").write_text("# source arch\n", encoding="utf-8")
    (root / "release" / f"{version}.md").write_text("# release\n", encoding="utf-8")

    canonical = "beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane"
    alias = "beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane"
    (root / "user-story" / f"{canonical}.md").write_text("# canonical user story\n", encoding="utf-8")
    (root / "prd" / f"{canonical}.md").write_text("# canonical prd\n", encoding="utf-8")
    (root / "qa" / "test-cases" / f"{canonical}.md").write_text("# canonical test cases\n", encoding="utf-8")
    (root / ".machine" / "qa" / f"{canonical}.ac-test-matrix.json").write_text(json.dumps({"entries": [{}]}), encoding="utf-8")

    (root / "user-story" / f"{alias}.md").write_text(
        "# Prototype Alias\n\n**Status**: `prototype-source`\n",
        encoding="utf-8",
    )

    result = _invoke(["doctor", "verify-materials", "--project-root", str(tmp_path), "--version", version, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    feature_check = {item["name"]: item for item in payload["result"]["checks"]}["main_chain_feature_completeness"]
    assert feature_check["status"] == "pass"
    assert feature_check["details"]["features"] == [canonical]
