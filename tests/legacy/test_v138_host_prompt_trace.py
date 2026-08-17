from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.help_support import build_help_payload
from beacon.utils.technical_review_contract import technical_review_contract_json_path


runner = CliRunner()
VERSION = "v1.3.8"
FEATURE = "V138 Host Prompt Trace Feature"
SLUG = "v138-host-prompt-trace-feature"


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
    _init_git_repo(root)
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    base = root / "docs" / "beacon" / VERSION
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text(
        (
            "# PRD\n\n"
            "## 功能需求\n\n"
            "- FR-001 Team should complete the frozen implementation baseline.\n\n"
            "## 11. Diagram Truth Layer\n\n"
            "### 11.1 Diagram Types\n"
            "- `branch-flow`\n"
            "- `state-machine`\n"
            "- `decision-priority`\n\n"
            "### 11.2 State Axes\n"
            "- `relation`\n"
            "- `sale`\n"
        ),
        encoding="utf-8",
    )
    (base / "user-story" / f"{SLUG}.md").write_text(
        "# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Team | Execute team then Ralph |\n",
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{SLUG}.qa9-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (base / ".machine" / "qa" / f"{SLUG}.story-scenario-map.json").write_text('{"scenarios":[]}\n', encoding="utf-8")


def _write_contract(root: Path) -> None:
    path = technical_review_contract_json_path(root, VERSION, FEATURE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "revision_id": "R1",
                "base_branch": "main",
                "target_branch": f"beacon/{VERSION}",
                "branch_prefix": "beacon/",
                "use_git_worktree": False,
                "worktree_root": str(root),
                "environment_mode": "local-dev",
                "isolation_strategy": "repo-local isolation",
                "service_directories": ["."],
                "writable_services": ["."],
                "reference_only_services": ["docs"],
                "review_status": "approved",
                "approved_by": "tech-lead",
                "reviewed_at": "2026-04-24T10:00:00+08:00",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_v138_host_prompt_trace_should_record_events_and_project_ralph_next_step(tmp_path: Path):
    _seed_docs(tmp_path)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _write_contract(tmp_path)

    team_plan = _invoke(
        [
            "implement",
            "team-plan",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--host-prompt",
            "根据冻结需求先生成 team plan",
            "--json",
        ]
    )
    assert team_plan.exit_code == 0, team_plan.stdout
    team_plan_payload = json.loads(team_plan.stdout)
    trace_path = tmp_path / team_plan_payload["host_prompt_trace_ref"]
    assert trace_path.exists()
    trace_payload = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace_payload["latest_event"]["surface"] == "implement-team-plan"
    assert trace_payload["latest_event"]["original_host_prompt"] == "根据冻结需求先生成 team plan"

    team_run = _invoke(
        [
            "implement",
            "team-run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--host-prompt",
            "继续 team run 并准备 Ralph",
            "--json",
        ]
    )
    assert team_run.exit_code == 0, team_run.stdout
    team_run_payload = json.loads(team_run.stdout)
    assert team_run_payload["next_action"] == "ralph"
    assert "--mode ralph" in team_run_payload["recommended_command"]
    assert team_run_payload["host_prompt_trace_ref"]

    trace_payload = json.loads((tmp_path / team_run_payload["host_prompt_trace_ref"]).read_text(encoding="utf-8"))
    assert len(trace_payload["events"]) >= 2
    assert trace_payload["latest_event"]["surface"] == "implement-team-run"
    assert trace_payload["latest_event"]["mapped_command"].startswith("beacon implement team-run")
    assert trace_payload["latest_event"]["route_status"] == "completed"

    help_payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert help_payload["execution_surface"]["host_prompt_trace_ref"].endswith(f"host-prompt-trace-{SLUG}.json")
    assert help_payload["execution_surface"]["team_phase"] == "completed"
    assert help_payload["execution_surface"]["ralph_status"] == "pending"
    assert help_payload["next_step"]["action"] == "ralph"
    assert "--mode ralph" in help_payload["next_step"]["command"]
