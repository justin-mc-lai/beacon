from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.help_support import build_help_payload
from beacon.utils.requirement_clarity import (
    load_requirement_clarity_state,
    requirement_clarity_json_path,
    requirement_clarity_markdown_path,
    requirement_clarity_state_path,
)
from beacon.utils.technical_review_contract import technical_review_contract_json_path, technical_review_contract_markdown_path


runner = CliRunner()
VERSION = "v1.3.1"
FEATURE = "Human Loop Feature"
SLUG = "human-loop-feature"


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


def _seed_docs(root: Path, *, unresolved: bool = False) -> None:
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
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    user_story_lines = [
        "# User Story",
        "",
        "## US-001：极简主闭环",
        "",
        "### 验收标准",
        "",
        "- [ ] 人类只需看到 prd -> user-story -> test-case -> implement -> qa -> release",
    ]
    prd_lines = [
        "# PRD",
        "",
        "## 功能需求",
        "",
        "### FR-001 Human primary loop",
        "- keep the primary loop narrow and stable",
    ]
    if unresolved:
        user_story_lines.extend(
            [
                "",
                "## 未决项",
                "",
                "- 这里还有一个待澄清问题？",
            ]
        )
    (base / "user-story" / f"{SLUG}.md").write_text("\n".join(user_story_lines) + "\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text("\n".join(prd_lines) + "\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")


def _write_contract(root: Path, *, review_status: str = "approved", approved_by: str = "tech-lead", reviewed_at: str = "2026-04-13T09:00:00+08:00") -> None:
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
                "review_status": review_status,
                "approved_by": approved_by,
                "reviewed_at": reviewed_at,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_v131_freeze_should_block_when_requirement_clarity_has_open_items(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=True)
    result = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "requirement_clarity_open"
    assert payload["requirement_clarity_gate"]["blocked"] is True
    assert payload["requirement_clarity_gate"]["findings"]
    assert (tmp_path / payload["requirement_clarity_report"]["json"]).exists()
    assert (tmp_path / payload["requirement_clarity_report"]["markdown"]).exists()
    assert (tmp_path / payload["requirement_clarity_writeback"]["state_path"]).exists()


def test_v131_doctor_should_materialize_requirement_clarity_state(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=True)
    result = _invoke(
        [
            "doctor",
            "sync-requirement-clarity",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    report = payload["result"]["report"]
    writeback = payload["result"]["writeback"]
    assert (tmp_path / report["json"]).exists()
    assert (tmp_path / report["markdown"]).exists()
    assert (tmp_path / writeback["state_path"]).exists()
    state = load_requirement_clarity_state(tmp_path, feature=FEATURE)
    assert state["blocked"] is True


def test_v131_implement_plan_should_block_without_technical_review_contract(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    result = _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "technical_review_contract_missing"
    assert payload["technical_review_gate"]["blocked"] is True


def test_v131_doctor_should_materialize_draft_technical_review_contract(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    result = _invoke(
        [
            "doctor",
            "sync-technical-review-contract",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--revision-id",
            "R1",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["result"]["review_status"] == "draft"
    assert (tmp_path / payload["result"]["contract_json_path"]).exists()
    assert (tmp_path / payload["result"]["contract_markdown_path"]).exists()
    assert (tmp_path / payload["result"]["state_path"]).exists()


def test_v131_implement_plan_should_block_with_unapproved_technical_review_contract(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _write_contract(tmp_path, review_status="draft", approved_by="", reviewed_at="")
    result = _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "technical_review_contract_invalid"
    validation = payload["technical_review_gate"]["validation"]
    assert "review_status" in validation["invalid_fields"] or "approved_by" in validation["missing_fields"]


def test_v131_doctor_approved_contract_should_unlock_implement_plan(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    result = _invoke(
        [
            "doctor",
            "sync-technical-review-contract",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--revision-id",
            "R1",
            "--review-status",
            "approved",
            "--approved-by",
            "tech-lead",
            "--reviewed-at",
            "2026-04-13T09:00:00+08:00",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    approved = json.loads(result.stdout)
    assert approved["result"]["review_status"] == "approved"
    plan = _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert plan.exit_code == 0, plan.stdout


def test_v131_status_should_surface_technical_review_state(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _invoke(
        [
            "doctor",
            "sync-technical-review-contract",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--revision-id",
            "R1",
            "--review-status",
            "approved",
            "--approved-by",
            "tech-lead",
            "--reviewed-at",
            "2026-04-13T09:00:00+08:00",
        ]
    )
    result = _invoke(["status", "--board", "--project-root", str(tmp_path), "--version", VERSION, "--feature", FEATURE])
    assert result.exit_code == 0, result.stdout
    assert "requirement_clarity: pass findings=0" in result.stdout
    assert "technical_review: pass review_status=approved" in result.stdout


def test_v131_implement_plan_should_pass_with_technical_review_contract(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _write_contract(tmp_path)
    result = _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "planned"
    assert payload["revision_id"] == "R1"


def test_v131_help_should_point_to_technical_review_contract_before_implement(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["next_step"]["action"] == "technical-review-contract"
    assert "deterministic-implementation-contract" in payload["next_step"]["command"]


def test_v131_help_should_point_to_requirement_clarity_before_freeze(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=True)
    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["next_step"]["action"] == "requirement-clarity"
    assert "requirement-clarity" in payload["next_step"]["command"]


def test_v131_freeze_should_write_requirement_clarity_report_when_clean(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    result = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    report = payload["requirement_clarity_report"]
    assert (tmp_path / report["json"]).exists()
    assert (tmp_path / report["markdown"]).exists()
    assert requirement_clarity_json_path(tmp_path, VERSION, FEATURE).exists()
    assert requirement_clarity_markdown_path(tmp_path, VERSION, FEATURE).exists()
    assert requirement_clarity_state_path(tmp_path, FEATURE).exists()
    assert not payload["requirement_clarity_gate"]["blocked"]
