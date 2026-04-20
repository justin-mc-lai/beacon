from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_v131_human_loop_contract
from beacon.commands.report import _human_summary
from beacon.main import app
from beacon.utils.artifact_paths import change_docs_file, change_file_output
from beacon.utils.help_support import build_help_payload
from beacon.utils.requirement_clarity import (
    load_requirement_clarity_state,
    requirement_clarity_json_path,
    requirement_clarity_markdown_path,
    requirement_clarity_state_path,
)
from beacon.utils.release_scorecard import build_release_scorecard, summarize_release_scorecard
from beacon.utils.technical_review_contract import technical_review_contract_json_path, technical_review_contract_markdown_path


runner = CliRunner()
VERSION = "v1.3.1"
CLARITY_VERSION = "v1.3.3"
LEGACY_DOCS_VERSION = "v1.0.0"
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


def _seed_docs(
    root: Path,
    *,
    version: str = VERSION,
    unresolved: bool = False,
    freeze_deliverables: list[str] | None = None,
) -> None:
    _init_git_repo(root)
    base = root / "docs" / "beacon" / version
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{version}.md").write_text("# Release\n", encoding="utf-8")
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
    if freeze_deliverables:
        prd_lines.extend(
            [
                "",
                "## 冻结交付物",
                "",
                *[f"- `{item}`" for item in freeze_deliverables],
            ]
        )
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


def _write_contract(
    root: Path,
    *,
    review_status: str = "approved",
    approved_by: str = "tech-lead",
    reviewed_at: str = "2026-04-13T09:00:00+08:00",
    base_branch: str = "main",
    target_branch: str | None = None,
    branch_prefix: str = "beacon/",
    use_git_worktree: bool = False,
    worktree_root: str | None = None,
    service_directories: list[str] | None = None,
    writable_services: list[str] | None = None,
    reference_only_services: list[str] | None = None,
) -> None:
    path = technical_review_contract_json_path(root, VERSION, FEATURE)
    path.parent.mkdir(parents=True, exist_ok=True)
    target_branch = target_branch or f"beacon/{VERSION}"
    worktree_root = worktree_root or str(root)
    service_directories = service_directories or ["."]
    writable_services = writable_services or list(service_directories)
    reference_only_services = reference_only_services or ["docs"]
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "revision_id": "R1",
                "base_branch": base_branch,
                "target_branch": target_branch,
                "branch_prefix": branch_prefix,
                "use_git_worktree": use_git_worktree,
                "worktree_root": worktree_root,
                "environment_mode": "local-dev",
                "isolation_strategy": "repo-local isolation",
                "service_directories": service_directories,
                "writable_services": writable_services,
                "reference_only_services": reference_only_services,
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


def _write_version_change_docs(root: Path, *, version: str = VERSION, feature: str = FEATURE, slug: str = SLUG) -> None:
    feature_json = change_file_output(root, version, f"{slug}.json")
    feature_md = change_docs_file(root, version, f"{slug}.md")
    version_json = change_file_output(root, version, f"{version}.json")
    version_md = change_docs_file(root, version, f"{version}.md")
    for path in (feature_json, feature_md, version_json, version_md):
        path.parent.mkdir(parents=True, exist_ok=True)

    feature_payload = {
        "schema_version": "1.0",
        "version": version,
        "feature": feature,
        "feature_slug": slug,
        "status": "completed",
        "summary": "Human loop feature landed",
        "added": ["Added human-loop release contract"],
        "removed": [],
        "fixed": [],
        "traceability_refs": [f"docs/beacon/{version}/execution/implementation-summary-{slug}.json"],
    }
    version_payload = {
        "schema_version": "1.0",
        "version": version,
        "status": "generated",
        "feature_count": 1,
        "features": [
            {
                "feature": feature,
                "feature_slug": slug,
                "summary": "Human loop feature landed",
                "status": "completed",
            }
        ],
        "added": [f"[{slug}] Added human-loop release contract"],
        "removed": [],
        "fixed": [],
        "traceability_refs": [
            f"docs/beacon/{version}/.machine/change/{slug}.json",
            f"docs/beacon/{version}/change/{slug}.md",
        ],
    }
    feature_json.write_text(json.dumps(feature_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    feature_md.write_text(f"# {slug}\n", encoding="utf-8")
    version_json.write_text(json.dumps(version_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    version_md.write_text(f"# {version} change\n", encoding="utf-8")


def test_v131_freeze_should_block_when_requirement_clarity_has_open_items(tmp_path: Path):
    _seed_docs(tmp_path, version=CLARITY_VERSION, unresolved=True)
    result = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", CLARITY_VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "requirement_clarity_open"
    assert payload["requirement_clarity_gate"]["blocked"] is True
    assert payload["requirement_clarity_gate"]["findings"]
    assert (tmp_path / payload["requirement_clarity_report"]["json"]).exists()
    assert (tmp_path / payload["requirement_clarity_report"]["markdown"]).exists()
    assert (tmp_path / payload["requirement_clarity_writeback"]["state_path"]).exists()


def test_v131_doctor_should_materialize_requirement_clarity_state(tmp_path: Path):
    _seed_docs(tmp_path, version=CLARITY_VERSION, unresolved=True)
    result = _invoke(
        [
            "doctor",
            "sync-requirement-clarity",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            CLARITY_VERSION,
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


def test_v131_freeze_should_block_when_required_freeze_artifacts_are_missing(tmp_path: Path):
    _seed_docs(
        tmp_path,
        version=CLARITY_VERSION,
        unresolved=False,
        freeze_deliverables=[
            f"docs/beacon/{CLARITY_VERSION}/execution/lifecycle-state-machine.md",
            "skills/beacon/beacon-change/SKILL.md",
        ],
    )
    result = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", CLARITY_VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    findings = payload["requirement_clarity_gate"]["findings"]
    assert any(item["kind"] == "missing_required_artifact" for item in findings)
    assert any("lifecycle-state-machine.md" in item.get("text", "") for item in findings)
    assert any("skills/beacon/beacon-change/SKILL.md" in item.get("text", "") for item in findings)


def test_v131_freeze_should_pass_when_required_freeze_artifacts_exist(tmp_path: Path):
    _seed_docs(
        tmp_path,
        version=CLARITY_VERSION,
        unresolved=False,
        freeze_deliverables=[
            f"docs/beacon/{CLARITY_VERSION}/execution/lifecycle-state-machine.md",
            "skills/beacon/beacon-change/SKILL.md",
        ],
    )
    (tmp_path / "docs" / "beacon" / CLARITY_VERSION / "execution" / "lifecycle-state-machine.md").write_text(
        "# Lifecycle State Machine\n",
        encoding="utf-8",
    )
    skill_path = tmp_path / "skills" / "beacon" / "beacon-change"
    skill_path.mkdir(parents=True, exist_ok=True)
    (skill_path / "SKILL.md").write_text(
        "---\nname: beacon-change\n---\n",
        encoding="utf-8",
    )

    result = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", CLARITY_VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "frozen"
    assert not payload["requirement_clarity_gate"]["blocked"]


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


def test_v131_sync_git_workflow_should_prefer_approved_technical_review_contract_over_config_seed(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    _init_git_repo(workspace)
    base = workspace / "docs" / "beacon" / VERSION
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "user-story" / f"{SLUG}.md").write_text("# User Story\n\n## US-001：A\n\n### 验收标准\n\n- [ ] A\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text("# PRD\n\n## 功能需求\n\n### FR-001 A\n- A\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    (workspace / "beacon.config.yaml").write_text(
        (
            "implementation:\n"
            "  branch_guard:\n"
            "    expected_branch: beacon/from-config\n"
            "    branch_prefix: beacon/\n"
            "    base_branch: main\n"
            "    git_roots:\n"
            "      - config-service\n"
        ),
        encoding="utf-8",
    )
    assert _invoke(["freeze", FEATURE, "--project", str(workspace), "--version", VERSION]).exit_code == 0
    contract_path = technical_review_contract_json_path(workspace, VERSION, FEATURE)
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "revision_id": "R1",
                "base_branch": "master",
                "target_branch": "feature/v1.3.1-human-loop",
                "branch_prefix": "feature/",
                "use_git_worktree": True,
                "worktree_root": str(workspace / ".worktrees" / "human-loop"),
                "environment_mode": "isolated-local",
                "isolation_strategy": "per-service worktrees",
                "service_directories": ["svc-api", "svc-web"],
                "writable_services": ["svc-api", "svc-web"],
                "reference_only_services": ["docs"],
                "review_status": "approved",
                "approved_by": "tech-lead",
                "reviewed_at": "2026-04-13T09:00:00+08:00",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = _invoke(
        [
            "implement",
            "sync-git-workflow",
            FEATURE,
            "--project",
            str(workspace),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["git_workflow"]["expected_branch"] == "feature/v1.3.1-human-loop"
    assert payload["git_workflow"]["branch_prefix"] == "feature/"
    assert payload["git_workflow"]["service_directories"] == ["svc-api", "svc-web"]
    assert payload["git_workflow"]["direct_delivery_services"] == ["svc-api", "svc-web"]
    assert payload["git_workflow"]["source"] == "technical_review_contract"


def test_v131_check_branch_should_use_materialized_git_workflow_from_approved_contract(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for name in ("svc-api", "svc-web"):
        service_root = workspace / name
        service_root.mkdir()
        _init_git_repo(service_root)
        subprocess.run(
            ["git", "switch", "-c", "feature/v1.3.1-human-loop"],
            cwd=service_root,
            check=True,
            capture_output=True,
            text=True,
        )
    base = workspace / "docs" / "beacon" / VERSION
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "user-story" / f"{SLUG}.md").write_text("# User Story\n\n## US-001：A\n\n### 验收标准\n\n- [ ] A\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text("# PRD\n\n## 功能需求\n\n### FR-001 A\n- A\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    assert _invoke(["freeze", FEATURE, "--project", str(workspace), "--version", VERSION]).exit_code == 0
    _write_contract(
        workspace,
        review_status="approved",
        approved_by="tech-lead",
        reviewed_at="2026-04-13T09:00:00+08:00",
        base_branch="main",
        target_branch="feature/v1.3.1-human-loop",
        branch_prefix="feature/",
        use_git_worktree=True,
        worktree_root=str(workspace / ".worktrees" / "human-loop"),
        service_directories=["svc-api", "svc-web"],
        writable_services=["svc-api", "svc-web"],
        reference_only_services=["docs"],
    )
    _invoke(["implement", "sync-git-workflow", FEATURE, "--project", str(workspace), "--version", VERSION])
    result = _invoke(
        [
            "implement",
            "check-branch",
            "--project-root",
            str(workspace),
            "--version",
            VERSION,
            "--feature",
            FEATURE,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["expected_branch"] == "feature/v1.3.1-human-loop"
    assert payload["git_workflow"]["service_directories"] == ["svc-api", "svc-web"]
    assert payload["git_workflow"]["direct_delivery_services"] == ["svc-api", "svc-web"]
    assert payload["git_workflow"]["source"] == "technical_review_contract"


def test_v131_sync_git_workflow_should_not_shrink_to_writable_services_subset(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    _init_git_repo(workspace)
    base = workspace / "docs" / "beacon" / VERSION
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "user-story" / f"{SLUG}.md").write_text("# User Story\n\n## US-001：A\n\n### 验收标准\n\n- [ ] A\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text("# PRD\n\n## 功能需求\n\n### FR-001 A\n- A\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    assert _invoke(["freeze", FEATURE, "--project", str(workspace), "--version", VERSION]).exit_code == 0
    _write_contract(
        workspace,
        review_status="approved",
        approved_by="tech-lead",
        reviewed_at="2026-04-13T09:00:00+08:00",
        base_branch="master",
        target_branch="feature/v1.3.1-human-loop",
        branch_prefix="feature/",
        use_git_worktree=True,
        worktree_root=str(workspace / ".worktrees" / "human-loop"),
        service_directories=["svc-api", "svc-web"],
        writable_services=["svc-api"],
        reference_only_services=["docs", "svc-web"],
    )
    result = _invoke(
        [
            "implement",
            "sync-git-workflow",
            FEATURE,
            "--project",
            str(workspace),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["git_workflow"]["service_directories"] == ["svc-api", "svc-web"]
    assert payload["git_workflow"]["direct_delivery_services"] == ["svc-api", "svc-web"]


def test_v131_release_scorecard_should_include_human_loop_surfaces(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _write_version_change_docs(tmp_path)
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
    qa_root = tmp_path / ".beacon" / "qa"
    (qa_root / "features" / SLUG).mkdir(parents=True, exist_ok=True)
    (qa_root / "status.json").write_text(
        json.dumps({"feature": FEATURE, "status": "passed", "evidence_done": True}, ensure_ascii=False),
        encoding="utf-8",
    )
    (qa_root / "features" / SLUG / "scorecard.json").write_text(
        json.dumps(
            {
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "unresolved_closure_outcomes": [],
                "release_confidence_min": 0.95,
                "release_confidence_avg": 0.98,
                "review_required_count": 0,
                "needs_replay_count": 0,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "gate-report.json").write_text(json.dumps({"status": "pass", "issues": []}, ensure_ascii=False), encoding="utf-8")

    scorecard = build_release_scorecard(tmp_path, version=VERSION)
    summary = summarize_release_scorecard(scorecard)
    assert scorecard["requirement_clarity"]["blocked"] is False
    assert scorecard["technical_review"]["review_status"] == "approved"
    assert scorecard["change_documents"]["status"] == "pass"
    assert scorecard["change_documents"]["includes_current_feature"] is True
    assert scorecard["release_ready"] is True
    assert summary["requirement_clarity_status"] == "pass"
    assert summary["technical_review_review_status"] == "approved"
    assert summary["change_documents_status"] == "pass"


def test_v131_release_scorecard_should_allow_feature_scorecard_to_override_legacy_qa_evidence_flag(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _write_version_change_docs(tmp_path)
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
    qa_root = tmp_path / ".beacon" / "qa"
    (qa_root / "features" / SLUG).mkdir(parents=True, exist_ok=True)
    (qa_root / "status.json").write_text(
        json.dumps(
            {
                "feature": FEATURE,
                "status": "passed",
                "evidence_done": False,
                "execution_mode": "feature-aware",
                "version": VERSION,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (qa_root / "features" / SLUG / "scorecard.json").write_text(
        json.dumps(
            {
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "unresolved_closure_outcomes": [],
                "project_profile_gate_status": "pass",
                "project_profile_id": "admin-browser-local",
                "release_confidence_min": 1.0,
                "release_confidence_avg": 1.0,
                "review_required_count": 0,
                "needs_replay_count": 0,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "pass", "issues": [], "version": VERSION}, ensure_ascii=False),
        encoding="utf-8",
    )

    scorecard = build_release_scorecard(tmp_path, version=VERSION)
    assert scorecard["qa"]["evidence_done"] is False
    assert scorecard["feature_qa_scorecard"]["release_ready"] is True
    assert scorecard["release_ready"] is True


def test_v131_release_scorecard_should_allow_authoritative_feature_scorecard_to_override_blocked_exhaustiveness(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _write_version_change_docs(tmp_path)
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
    qa_root = tmp_path / ".beacon" / "qa"
    feature_root = qa_root / "features" / SLUG
    feature_root.mkdir(parents=True, exist_ok=True)
    (qa_root / "status.json").write_text(
        json.dumps(
            {
                "feature": FEATURE,
                "status": "passed",
                "evidence_done": False,
                "execution_mode": "feature-aware",
                "version": VERSION,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (feature_root / "scorecard.json").write_text(
        json.dumps(
            {
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "unresolved_closure_outcomes": [],
                "project_profile_gate_status": "pass",
                "project_profile_id": "admin-browser-local",
                "release_confidence_min": 1.0,
                "release_confidence_avg": 1.0,
                "review_required_count": 0,
                "needs_replay_count": 0,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (feature_root / "exhaustiveness-report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "run_id": "run-qa",
                "status": "blocked",
                "score": 0.75,
                "threshold": 0.8,
                "missing_axes": [],
                "missing_browser_evidence_scenarios": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "pass", "issues": [], "version": VERSION}, ensure_ascii=False),
        encoding="utf-8",
    )

    scorecard = build_release_scorecard(tmp_path, version=VERSION)
    assert scorecard["exhaustiveness"]["status"] == "blocked"
    assert scorecard["feature_qa_scorecard"]["release_ready"] is True
    assert scorecard["release_ready"] is True


def test_v131_release_scorecard_should_allow_authoritative_feature_scorecard_with_change_docs_to_force_release_ready(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _write_version_change_docs(tmp_path)
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
    qa_root = tmp_path / ".beacon" / "qa"
    feature_root = qa_root / "features" / SLUG
    feature_root.mkdir(parents=True, exist_ok=True)
    (qa_root / "status.json").write_text(
        json.dumps(
            {
                "feature": FEATURE,
                "status": "passed",
                "evidence_done": False,
                "execution_mode": "feature-aware",
                "version": VERSION,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (feature_root / "scorecard.json").write_text(
        json.dumps(
            {
                "release_ready": True,
                "continue_decision": "ready_for_release",
                "unresolved_closure_outcomes": [],
                "project_profile_gate_status": "pass",
                "project_profile_id": "admin-browser-local",
                "release_confidence_min": 1.0,
                "release_confidence_avg": 1.0,
                "review_required_count": 0,
                "needs_replay_count": 0,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (feature_root / "exhaustiveness-report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "feature": FEATURE,
                "feature_slug": SLUG,
                "run_id": "run-qa",
                "status": "blocked",
                "score": 0.75,
                "threshold": 0.8,
                "missing_axes": [],
                "missing_browser_evidence_scenarios": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / ".beacon" / "gate-report.json").write_text(
        json.dumps({"status": "pass", "issues": [], "version": VERSION}, ensure_ascii=False),
        encoding="utf-8",
    )

    scorecard = build_release_scorecard(tmp_path, version=VERSION)
    assert scorecard["change_documents"]["status"] == "pass"
    assert scorecard["feature_qa_scorecard"]["release_ready"] is True
    assert scorecard["release_ready"] is True


def test_v131_report_human_summary_should_show_human_loop_gates(tmp_path: Path):
    machine = {
        "run_id": "latest",
        "workflow": "workflow",
        "mode": "normal",
        "status": "completed",
        "release_scorecard": {
            "release_ready": False,
            "gate": {"status": "blocked", "blocked_count": 1},
            "qa": {"status": "passed", "execution_mode": "feature-aware", "evidence_done": True, "project_profile_gate_status": "pass"},
            "feature_qa_scorecard": {"release_confidence_min": 0.9, "release_confidence_avg": 0.95, "review_required_count": 0, "needs_replay_count": 0, "continue_decision": "continue", "test_case_backfill_required": False},
            "learning_scorecard": {"main_kpi": "false_complete_rate", "decision_summary": {"keep": 1, "review": 0, "discard": 0}},
            "latest_experiment": {"main_kpi_score": 0.1},
            "requirement_clarity": {"status": "blocked", "blocked": True, "finding_count": 2},
            "technical_review": {"status": "pass", "blocked": False, "review_status": "approved"},
            "change_documents": {"status": "blocked", "markdown_exists": False, "json_exists": False, "feature_count": 0, "includes_current_feature": False},
        },
        "artifacts": {},
    }
    summary = _human_summary(machine)
    assert "requirement_clarity_status" in summary
    assert "technical_review_review_status" in summary
    assert "change_documents_status" in summary
    assert "## Human-Loop Gates" in summary


def test_v131_gate_release_should_block_when_human_loop_contracts_are_unresolved(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=True)
    issues = check_v131_human_loop_contract(tmp_path, GateMode.STRICT, "release", VERSION)
    reason_codes = {item["reason_code"] for item in issues}
    assert "feature_name_missing" in reason_codes or "requirement_clarity_state_missing" in reason_codes


def test_v131_gate_release_should_pass_when_human_loop_contracts_are_closed(tmp_path: Path):
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
    qa_root = tmp_path / ".beacon" / "qa"
    (qa_root / "features" / SLUG).mkdir(parents=True, exist_ok=True)
    (qa_root / "status.json").write_text(json.dumps({"feature": FEATURE, "status": "passed", "evidence_done": True}, ensure_ascii=False), encoding="utf-8")
    issues = check_v131_human_loop_contract(tmp_path, GateMode.STRICT, "release", VERSION)
    assert issues == []


def test_v131_implement_plan_should_pass_with_technical_review_contract(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    _write_contract(tmp_path)
    result = _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "planned"
    assert payload["revision_id"] == "R1"


def test_v131_runtime_capability_should_block_freeze_on_legacy_docs_line(tmp_path: Path):
    _seed_docs(tmp_path, version=LEGACY_DOCS_VERSION, unresolved=True)
    assert _invoke(["doctor", "setup-context", "--project-root", str(tmp_path)]).exit_code == 0
    result = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", LEGACY_DOCS_VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["version"] == LEGACY_DOCS_VERSION
    assert payload["requirement_clarity_gate"]["required"] is True
    assert payload["requirement_clarity_gate"]["runtime_capability_line"] == VERSION
    assert payload["requirement_clarity_gate"]["blocked"] is True
    assert (tmp_path / "docs" / "beacon" / VERSION).exists() is False


def test_v131_runtime_capability_should_require_technical_review_on_legacy_docs_line(tmp_path: Path):
    _seed_docs(tmp_path, version=LEGACY_DOCS_VERSION, unresolved=False)
    assert _invoke(["doctor", "setup-context", "--project-root", str(tmp_path)]).exit_code == 0
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", LEGACY_DOCS_VERSION]).exit_code == 0
    result = _invoke(["implement", "plan", FEATURE, "--project", str(tmp_path), "--version", LEGACY_DOCS_VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["version"] == LEGACY_DOCS_VERSION
    assert payload["reason_code"] == "technical_review_contract_missing"
    assert payload["technical_review_gate"]["required"] is True
    assert payload["technical_review_gate"]["runtime_capability_line"] == VERSION


def test_v131_help_should_show_runtime_capability_lines_for_legacy_docs_line(tmp_path: Path):
    _seed_docs(tmp_path, version=LEGACY_DOCS_VERSION, unresolved=False)
    assert _invoke(["doctor", "setup-context", "--project-root", str(tmp_path)]).exit_code == 0
    payload = build_help_payload(tmp_path, version=LEGACY_DOCS_VERSION, feature=FEATURE)
    assert payload["docs_version"] == LEGACY_DOCS_VERSION
    assert VERSION in payload["version_context"]["runtime_capability_lines"]


def test_v131_help_should_point_to_technical_review_contract_before_implement(tmp_path: Path):
    _seed_docs(tmp_path, unresolved=False)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["next_step"]["action"] == "technical-review-contract"
    assert "deterministic-implementation-contract" in payload["next_step"]["command"]


def test_v131_help_should_point_to_requirement_clarity_before_freeze(tmp_path: Path):
    _seed_docs(tmp_path, version=CLARITY_VERSION, unresolved=True)
    subprocess.run(
        ["git", "switch", "-C", f"beacon/{CLARITY_VERSION}"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = build_help_payload(tmp_path, version=CLARITY_VERSION, feature=FEATURE)
    assert payload["next_step"]["action"] == "requirement-clarity"
    assert "requirement-clarity" in payload["next_step"]["command"]


def test_v131_freeze_should_write_requirement_clarity_report_when_clean(tmp_path: Path):
    _seed_docs(tmp_path, version=CLARITY_VERSION, unresolved=False)
    result = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", CLARITY_VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    report = payload["requirement_clarity_report"]
    assert (tmp_path / report["json"]).exists()
    assert (tmp_path / report["markdown"]).exists()
    assert requirement_clarity_json_path(tmp_path, CLARITY_VERSION, FEATURE).exists()
    assert requirement_clarity_markdown_path(tmp_path, CLARITY_VERSION, FEATURE).exists()
    assert requirement_clarity_state_path(tmp_path, FEATURE).exists()
    assert not payload["requirement_clarity_gate"]["blocked"]
