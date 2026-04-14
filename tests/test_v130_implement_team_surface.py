from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.3.0"
FEATURE = "V130 Team Feature"
SLUG = "v130-team-feature"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    (root / ".gitkeep").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "switch", "-c", f"beacon/{VERSION}"], cwd=root, check=True, capture_output=True, text=True)


def _seed_docs(root: Path) -> None:
    if not (root / ".git").exists():
        _init_git_repo(root)
    base = root / "docs" / "beacon" / VERSION
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text(f"# Release {VERSION}\n", encoding="utf-8")
    (base / "user-story" / f"{SLUG}.md").write_text(
        """# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Team | Implement team surface |\n| TEST-001 | Verify | QA should stay isolated |\n""",
        encoding="utf-8",
    )
    (base / "prd" / f"{SLUG}.md").write_text(
        """# PRD\n\n## 功能需求\n\n- FR-001 Team Surface: add stable implement team routing.\n- FR-002 QA Isolation: keep qa isolated from implement context.\n""",
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")


def test_v130_implement_plan_should_emit_team_mode_contract(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])

    result = _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    team_mode = payload.get("team_mode", {})
    assert team_mode["preferred_surface"] == "implement-team"
    assert team_mode["preferred_runner"] == "codex-subagents"
    assert "qa team-run" in team_mode["qa_team_command"]
    assert team_mode["context_isolation"]["qa_surface"] == "qa-team"
    assert team_mode["config_source"] == "beacon/team_roles/implement-team.json"
    assert "implementation-architect" in team_mode["roles"]
    assert payload["git_workflow_ref"].endswith(f"git-workflow-{SLUG}.json")
    assert payload["git_workflow_markdown_ref"].endswith(f"git-workflow-{SLUG}.md")
    assert payload["git_workflow"]["expected_branch"] == f"beacon/{VERSION}"
    assert (tmp_path / payload["git_workflow_ref"]).exists()
    assert (tmp_path / payload["git_workflow_markdown_ref"]).exists()


def test_v130_implement_run_auto_should_use_codex_subagents_team_surface(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION])

    result = _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "auto", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["runner"] == "codex-subagents"
    assert payload["team_surface"] == "implement-team"
    team_execution = payload.get("team_execution", {})
    assert team_execution.get("team_surface") == "implement-team"
    assert team_execution.get("terminal_status") == "Pass"
    assert "qa-team" in team_execution.get("context_isolation", {}).get("isolated_from", [])
    assert "codex-subagents" in team_execution.get("artifact_dir", "")
    assert "implementation-architect" in team_execution.get("roles", [])


def test_v130_help_should_prefer_codex_subagents_and_qa_team_run(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION])

    help_before = _invoke(["help", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"])
    assert help_before.exit_code == 0, help_before.stdout
    help_before_payload = json.loads(help_before.stdout)
    assert "beacon implement dev-run" in help_before_payload["next_step"]["command"]

    _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "codex-subagents"])
    qa_status_dir = tmp_path / ".beacon" / "qa"
    qa_status_dir.mkdir(parents=True, exist_ok=True)
    feature_dir = qa_status_dir / "features" / SLUG
    feature_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(json.dumps({"status": "passed", "summary": {"blocked": 0}}), encoding="utf-8")
    scorecard = {
        "continue_decision": "continue",
        "coverage_current": {"executed_scenarios": 1, "required_scenarios": 2, "coverage_rate": 0.5},
        "stop_reasons": [],
    }
    feature_status = {
        "status": "blocked",
        "feature": FEATURE,
        "feature_scorecard": scorecard,
    }
    (qa_status_dir / f"{SLUG}.json").write_text(json.dumps(feature_status), encoding="utf-8")
    (feature_dir / "scorecard.json").write_text(json.dumps(scorecard), encoding="utf-8")

    help_after = _invoke(["help", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE, "--json"])
    assert help_after.exit_code == 0, help_after.stdout
    help_after_payload = json.loads(help_after.stdout)
    assert "beacon qa team-run" in help_after_payload["next_step"]["command"]


def test_v130_qa_team_run_should_materialize_isolated_team_surface(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--runner", "codex-subagents"])
    (tmp_path / ".beacon" / "auto-test-status.json").write_text(
        json.dumps({"status": "passed", "summary": {"blocked": 0}}),
        encoding="utf-8",
    )

    result = _invoke(["qa", "team-run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["team_mode"] is True
    assert payload["execution_surface"] == "qa-team"
    team_execution = payload.get("team_execution", {})
    assert team_execution.get("team_surface") == "qa-team"
    assert "implement-team" in team_execution.get("context_isolation", {}).get("isolated_from", [])
    assert Path(tmp_path / team_execution["state_path"]).exists()


def test_v130_team_commands_should_be_explicit_and_stable(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])

    plan_result = _invoke(["implement", "team-plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert plan_result.exit_code == 0, plan_result.stdout
    plan_payload = json.loads(plan_result.stdout)
    assert plan_payload["team_surface"] == "implement-team"
    assert "beacon implement team-run" in plan_payload["recommended_command"]

    run_result = _invoke(["implement", "team-run", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert run_result.exit_code == 0, run_result.stdout
    run_payload = json.loads(run_result.stdout)
    assert run_payload["runner"] == "codex-subagents"
    assert run_payload["team_surface"] == "implement-team"

    qa_plan = _invoke(["qa", "team-plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert qa_plan.exit_code == 0, qa_plan.stdout
    qa_plan_payload = json.loads(qa_plan.stdout)
    assert qa_plan_payload["team_surface"] == "qa-team"
    assert "beacon qa team-run" in qa_plan_payload["team_contract"]["run_command"]
    assert qa_plan_payload["team_contract"]["config_source"] == "beacon/team_roles/qa-team.json"


def test_v130_dev_run_should_auto_compile_plan_and_materialize_git_workflow(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])

    result = _invoke(
        [
            "implement",
            "dev-run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--runtime",
            "file",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert payload["team_surface"] == "implement-team"
    assert payload["preflight_resolution"]["status"] == "completed"
    assert any(step["gate"] == "implementation_plan" and step["status"] == "planned" for step in payload["preflight_resolution"]["steps"])
    assert any(step["gate"] == "git_workflow_contract" for step in payload["preflight_resolution"]["steps"])
    assert "implementation-architect" in payload["team_execution"]["roles"]
    plan_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"implementation-plan-{SLUG}.json"
    assert plan_path.exists()
    git_workflow_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"git-workflow-{SLUG}.json"
    assert git_workflow_path.exists()


def test_v130_git_workflow_contract_should_outlive_project_config(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for name in ("marketing_sys", "health-svr-dotnet"):
        service_root = workspace / name
        service_root.mkdir()
        _init_git_repo(service_root)
        subprocess.run(
            ["git", "switch", "-c", "feature/v1.3.1-dev-account-cleanup-upstream"],
            cwd=service_root,
            check=True,
            capture_output=True,
            text=True,
        )

    base = workspace / "docs" / "beacon" / "v1.3.1-dev"
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / "v1.3.1-dev.md").write_text("# Release\n", encoding="utf-8")
    slug = "workspace-feature"
    feature = "Workspace Feature"
    (base / "user-story" / f"{slug}.md").write_text("# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Team | Workspace |\n| TEST-001 | Verify | QA |\n", encoding="utf-8")
    (base / "prd" / f"{slug}.md").write_text("# PRD\n\n- FR-001 Workspace branch contract\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (workspace / "beacon.config.yaml").write_text(
        (
            "implementation:\n"
            "  branch_guard:\n"
            "    expected_branch: feature/v1.3.1-dev-account-cleanup-upstream\n"
            "    branch_prefix: feature/\n"
            "    base_branch: master\n"
            "    git_roots:\n"
            "      - marketing_sys\n"
            "      - health-svr-dotnet\n"
        ),
        encoding="utf-8",
    )

    _invoke(["freeze", feature, "--project", str(workspace), "--version", "v1.3.1-dev"])
    plan_result = _invoke(["implement", "plan", feature, "--project", str(workspace), "--version", "v1.3.1-dev", "--json"])
    assert plan_result.exit_code == 0, plan_result.stdout
    (workspace / "beacon.config.yaml").unlink()

    branch_result = _invoke(
        [
            "implement",
            "check-branch",
            "--project-root",
            str(workspace),
            "--version",
            "v1.3.1-dev",
            "--feature",
            feature,
            "--json",
        ]
    )
    assert branch_result.exit_code == 0, branch_result.stdout
    branch_payload = json.loads(branch_result.stdout)
    assert branch_payload["status"] == "pass"
    assert branch_payload["expected_branch"] == "feature/v1.3.1-dev-account-cleanup-upstream"
    assert branch_payload["git_workflow"]["mode"] == "workspace"
    assert branch_payload["git_workflow"]["service_directories"] == ["marketing_sys", "health-svr-dotnet"]


def test_v130_sync_git_workflow_should_materialize_contract_from_seed(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    base = workspace / "docs" / "beacon" / "v1.3.1-dev"
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / "v1.3.1-dev.md").write_text("# Release\n", encoding="utf-8")
    (workspace / "beacon.config.yaml").write_text(
        (
            "implementation:\n"
            "  branch_guard:\n"
            "    expected_branch: feature/v1.3.1-dev-account-cleanup-upstream\n"
            "    branch_prefix: feature/\n"
            "    base_branch: master\n"
            "    git_roots:\n"
            "      - marketing_sys\n"
            "      - health-svr-dotnet\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "implement",
            "sync-git-workflow",
            "Workspace Feature",
            "--project",
            str(workspace),
            "--version",
            "v1.3.1-dev",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "materialized"
    assert payload["git_workflow"]["expected_branch"] == "feature/v1.3.1-dev-account-cleanup-upstream"
    assert payload["git_workflow"]["service_directories"] == ["marketing_sys", "health-svr-dotnet"]
    assert (workspace / payload["git_workflow_ref"]).exists()
    assert (workspace / payload["git_workflow_markdown_ref"]).exists()


def test_prerelease_dev_run_should_still_default_to_codex_subagents(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for name in ("marketing_sys", "health-svr-dotnet"):
        service_root = workspace / name
        service_root.mkdir()
        _init_git_repo(service_root)
        subprocess.run(
            ["git", "switch", "-c", "feature/v1.3.1-dev-account-cleanup-upstream"],
            cwd=service_root,
            check=True,
            capture_output=True,
            text=True,
        )
    version = "v1.3.1-dev"
    feature = "Workspace Feature"
    slug = "workspace-feature"
    base = workspace / "docs" / "beacon" / version
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{version}.md").write_text("# Release\n", encoding="utf-8")
    (base / "user-story" / f"{slug}.md").write_text("# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Team | Workspace |\n| TEST-001 | Verify | QA |\n", encoding="utf-8")
    (base / "prd" / f"{slug}.md").write_text("# PRD\n\n- FR-001 Workspace branch contract\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (workspace / "beacon.config.yaml").write_text(
        (
            "implementation:\n"
            "  branch_guard:\n"
            "    expected_branch: feature/v1.3.1-dev-account-cleanup-upstream\n"
            "    branch_prefix: feature/\n"
            "    base_branch: master\n"
            "    git_roots:\n"
            "      - marketing_sys\n"
            "      - health-svr-dotnet\n"
        ),
        encoding="utf-8",
    )
    _invoke(["freeze", feature, "--project", str(workspace), "--version", version])

    result = _invoke(
        [
            "implement",
            "dev-run",
            feature,
            "--project",
            str(workspace),
            "--version",
            version,
            "--runtime",
            "file",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["runner"] == "codex-subagents"
    assert payload["team_surface"] == "implement-team"
    assert "implementation-architect" in payload["team_execution"]["roles"]


def test_v130_team_run_should_emit_hud_paths_in_file_runtime(tmp_path: Path):
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION])

    result = _invoke(
        [
            "implement",
            "team-run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--runtime",
            "file",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    team_execution = payload["team_execution"]
    assert team_execution["runtime"] == "file"
    hud = team_execution["hud"]
    assert (tmp_path / hud["json"]).exists()
    assert (tmp_path / hud["html"]).exists()


def test_v130_team_run_should_materialize_tmux_session_when_requested(tmp_path: Path):
    if subprocess.run(["/bin/sh", "-lc", "command -v tmux >/dev/null 2>&1"], capture_output=True, text=True).returncode != 0:
        return
    _seed_docs(tmp_path)
    _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION])
    _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION])

    result = _invoke(
        [
            "implement",
            "team-run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--runtime",
            "tmux",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    team_execution = payload["team_execution"]
    assert team_execution["runtime"] == "tmux"
    assert team_execution["tmux_session"]
    assert any(str(item.get("pane_id", "")) for item in team_execution["role_reports"].values())
