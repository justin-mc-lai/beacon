from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.artifact_paths import uses_machine_surface
from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.runtime import write_json
from beacon.utils.versioning import resolve_docs_version, resolve_runtime_version, resolve_target_version


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_release_repo(root: Path) -> None:
    (root / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "beacon" / "__init__.py").write_text(
        '__version__ = "1.1.4"\n__toolkit_version__ = "v1.1.4"\n',
        encoding="utf-8",
    )
    for version in ("v1.1.4", "v1.1.5"):
        base = root / "docs" / "beacon" / version
        (base / "release").mkdir(parents=True, exist_ok=True)
        (base / "release" / f"{version}.md").write_text(f"# Release {version}\n", encoding="utf-8")


def _seed_v115_feature_docs(root: Path, feature: str = "Machine Feature") -> str:
    slug = feature.lower().replace(" ", "-")
    base = root / "docs" / "beacon" / "v1.1.5"
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "user-story" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# User Story: {feature}",
                "",
                "| AC ID | Description |",
                "| --- | --- |",
                "| AC-001 | flow works |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base / "prd" / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "release" / "v1.1.5.md").write_text("# Release v1.1.5\n", encoding="utf-8")
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    return slug


def test_resolve_target_version_auto_should_prefer_current_runtime_release(tmp_path: Path):
    _seed_release_repo(tmp_path)
    assert resolve_target_version(tmp_path, "auto") == "v1.1.4"
    assert resolve_target_version(tmp_path, None) == "v1.1.4"
    assert resolve_target_version(tmp_path, "latest-docs") == "v1.1.5"
    assert resolve_target_version(tmp_path, "v1.1.5") == "v1.1.5"


def test_resolve_target_version_auto_should_prefer_onboarding_docs_version(tmp_path: Path):
    _seed_release_repo(tmp_path)
    (tmp_path / ".beacon" / "state").mkdir(parents=True, exist_ok=True)
    write_json(
        tmp_path / ".beacon" / "state" / "project-onboarding.json",
        {
            "schema_version": "1.0",
            "docs_version": "v0.1.0",
            "runtime_version": "v1.1.8",
        },
    )

    assert resolve_docs_version(tmp_path, "auto") == "v0.1.0"
    assert resolve_target_version(tmp_path, "auto") == "v0.1.0"


def test_resolve_runtime_version_auto_should_follow_active_toolkit_version(tmp_path: Path):
    (tmp_path / ".beacon" / "state").mkdir(parents=True, exist_ok=True)
    write_json(
        tmp_path / ".beacon" / "state" / "project-onboarding.json",
        {
            "schema_version": "1.0",
            "docs_version": "v0.1.0",
            "runtime_version": "v9.9.9",
        },
    )

    assert resolve_runtime_version(tmp_path, "auto") == "v1.1.8"


def test_machine_surface_should_follow_toolkit_version_not_delivery_version():
    assert uses_machine_surface("v0.0.1") is True


def test_user_story_without_version_should_use_current_runtime_release(tmp_path: Path):
    _seed_release_repo(tmp_path)
    result = _invoke(["user-story", "create", "Runtime Default Feature", "--project", str(tmp_path)])
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "docs" / "beacon" / "v1.1.4" / "user-story" / "runtime-default-feature.md").exists()
    assert not (tmp_path / "docs" / "beacon" / "v1.1.5" / "user-story" / "runtime-default-feature.md").exists()


def test_project_release_v001_should_still_write_machine_surface_artifacts(tmp_path: Path):
    _seed_release_repo(tmp_path)
    feature = "Project Delivery Feature"
    slug = feature.lower().replace(" ", "-")
    base = tmp_path / "docs" / "beacon" / "v0.0.1"
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "user-story" / f"{slug}.md").write_text("# Story\n\n| AC ID | Description |\n| --- | --- |\n| AC-001 | flow works |\n", encoding="utf-8")
    (base / "prd" / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "release" / "v0.0.1.md").write_text("# Release v0.0.1\n", encoding="utf-8")

    init_result = _invoke(["init", "--project-root", str(tmp_path), "--version", "v0.0.1", "--apply"])
    assert init_result.exit_code == 0, init_result.stdout
    assert (base / ".machine" / "execution").exists()
    assert (base / ".machine" / "qa").exists()

    case_result = _invoke(["test-case", "create", feature, "--project", str(tmp_path), "--version", "v0.0.1"])
    assert case_result.exit_code == 0, case_result.stdout
    assert (base / "qa" / "test-cases" / f"{slug}.md").exists()
    assert (base / ".machine" / "qa" / f"{slug}.ac-test-matrix.json").exists()
    assert (base / ".machine" / "qa" / f"{slug}.qa9-matrix.json").exists()


def test_v115_test_case_should_write_machine_matrices_and_human_markdown(tmp_path: Path):
    _seed_release_repo(tmp_path)
    slug = _seed_v115_feature_docs(tmp_path)
    result = _invoke(["test-case", "create", "Machine Feature", "--project", str(tmp_path), "--version", "v1.1.5"])
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "docs" / "beacon" / "v1.1.5" / "qa" / "test-cases" / f"{slug}.md").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.1.5" / "qa" / "test-cases" / "index.md").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.1.5" / ".machine" / "qa" / f"{slug}.ac-test-matrix.json").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.1.5" / ".machine" / "qa" / f"{slug}.qa9-matrix.json").exists()


def test_v115_verify_delivery_should_accept_machine_execution_artifacts(tmp_path: Path):
    _seed_release_repo(tmp_path)
    slug = _seed_v115_feature_docs(tmp_path)
    _invoke(["test-case", "create", "Machine Feature", "--project", str(tmp_path), "--version", "v1.1.5"])
    machine_exec = tmp_path / "docs" / "beacon" / "v1.1.5" / ".machine" / "execution"
    machine_exec.mkdir(parents=True, exist_ok=True)
    (machine_exec / "config.json").write_text(
        json.dumps(
            {
                "resolved_project": {},
                "docs": {},
                "implementation": {},
                "source_info": {},
                "git": {},
                "research": {},
                "delivery": {},
            }
        ),
        encoding="utf-8",
    )
    (machine_exec / "source.json").write_text(
        json.dumps(
            {
                "project_name": "beacon",
                "project_root": str(tmp_path),
                "workspace_root": str(tmp_path.parent),
                "repo_url": "https://example.com/repo.git",
                "branch": "beacon/v1.1.5",
                "commit": "abc123",
                "run_id": "run-1",
                "version": "v1.1.5",
            }
        ),
        encoding="utf-8",
    )
    (machine_exec / "git-alignment.json").write_text(
        json.dumps(
            {
                "git_refs": {},
                "alignment": {},
                "version_ref": "v1.1.5",
                "blocked": False,
                "reason_codes": [],
            }
        ),
        encoding="utf-8",
    )
    (machine_exec / "delivery-manifest.json").write_text(
        json.dumps(
            {
                "affected_projects": [
                    {
                        "name": "beacon",
                        "project_root": str(tmp_path),
                        "repo_url": "https://example.com/repo.git",
                        "change_scope": "docs",
                        "changed_layers": ["execution"],
                        "base_branch": "main",
                        "target_branch": "beacon/v1.1.5",
                        "current_branch": "beacon/v1.1.5",
                        "commit": "abc123",
                        "tag": "",
                        "worktree_path": str(tmp_path),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (machine_exec / "change-impact.json").write_text(
        json.dumps(
            {
                "changed_layers": ["execution"],
                "tasks": [],
                "research_converged": True,
                "main_chain_converged": True,
                "delivery_manifest_ready": True,
            }
        ),
        encoding="utf-8",
    )
    (machine_exec / "terminal.json").write_text(
        json.dumps({"status": "Pass", "traceability": {"evidence_refs": []}}),
        encoding="utf-8",
    )
    result = _invoke(["doctor", "verify-delivery", "--project-root", str(tmp_path), "--version", "v1.1.5", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"


def test_v115_coverage_metrics_should_read_machine_ac_matrix(tmp_path: Path):
    _seed_release_repo(tmp_path)
    slug = _seed_v115_feature_docs(tmp_path)
    evidence = tmp_path / ".beacon" / "evidence" / "test-results" / slug / "TC-001.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("{}", encoding="utf-8")
    marker = tmp_path / ".beacon" / "state" / f"implementation-{slug}.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text('{"status":"completed"}', encoding="utf-8")
    machine_qa = tmp_path / "docs" / "beacon" / "v1.1.5" / ".machine" / "qa"
    machine_qa.mkdir(parents=True, exist_ok=True)
    (machine_qa / f"{slug}.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "ac_id": "AC-001",
                        "tc_id": "TC-001",
                        "evidence_path": str(evidence.relative_to(tmp_path)),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    metrics = compute_coverage_metrics(tmp_path, version="v1.1.5", feature="Machine Feature")
    assert metrics["planned_story"] == 1
    assert metrics["implemented_story"] == 1
    assert metrics["total_ac"] == 1
    assert metrics["executed_tc"] == 1
    assert metrics["full_coverage"] is True
