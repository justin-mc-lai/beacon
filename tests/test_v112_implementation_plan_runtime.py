from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_v112_implementation_plan_contract
from beacon.main import app
from beacon.utils.help_support import build_help_payload
from beacon.utils.implementation_plan import (
    _extract_prd_task_candidates,
    load_implementation_plan,
    load_implementation_plan_progress,
)
from beacon.utils.writeback import record_implementation_writeback, record_verification_writeback


runner = CliRunner()
VERSION = "v1.1.12"
FEATURE = "Plan Closure Feature"
SLUG = "plan-closure-feature"


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
    base = root / "docs" / "beacon" / VERSION
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "user-story" / f"{SLUG}.md").write_text(
        "\n".join(
            [
                "# User Story",
                "",
                "| AC ID | Theme | Description |",
                "| --- | --- | --- |",
                "| AC-001 | Plan | Compile implementation plan |",
                "| AC-002 | Progress | Track implementation task progress |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base / "prd" / f"{SLUG}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{SLUG}.md").write_text("# Test Cases\n", encoding="utf-8")


def _seed_release_contract_artifacts(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (base / "execution" / "project-skill-qa-evolution-blueprint.md").write_text("# Project Skill QA Evolution Blueprint\n", encoding="utf-8")
    (base / "source-architecture").mkdir(parents=True, exist_ok=True)
    (base / "source-architecture" / "index.md").write_text("# Source Architecture\n", encoding="utf-8")
    machine_exec = base / ".machine" / "execution"
    machine_exec.mkdir(parents=True, exist_ok=True)
    for filename, payload in {
        "config.json": {"resolved_project": {}, "docs": {}, "implementation": {}, "source_info": {}, "git": {}, "research": {}, "delivery": {}},
        "source.json": {"project_name": "demo", "project_root": str(root), "workspace_root": str(root.parent), "repo_url": "https://example.com/demo.git", "branch": f"beacon/{VERSION}", "commit": "abc123", "run_id": "run-1", "version": VERSION},
        "git-alignment.json": {"git_refs": {"base_branch": "main", "target_branch": f"beacon/{VERSION}", "current_branch": f"beacon/{VERSION}", "commit": "abc123", "tag": "", "worktree_path": str(root)}, "alignment": {"version_ref_satisfied": True}, "version_ref": VERSION, "blocked": False},
        "delivery-manifest.json": {"affected_projects": [{"name": "demo", "project_root": str(root), "repo_url": "https://example.com/demo.git", "change_scope": "docs", "changed_layers": ["user-story", "prd", "test-case"], "base_branch": "main", "target_branch": f"beacon/{VERSION}", "current_branch": f"beacon/{VERSION}", "commit": "abc123", "tag": "", "worktree_path": str(root)}]},
        "change-impact.json": {"changed_layers": ["user-story", "prd", "test-case"], "tasks": [{"task": "finalize", "status": "completed"}], "research_converged": True, "main_chain_converged": True, "delivery_manifest_ready": True},
        "terminal.json": {"status": "completed"},
    }.items():
        (machine_exec / filename).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    (root / ".beacon").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "auto-test-status.json").write_text(json.dumps({"status": "passed", "summary": {"blocked": 0}, "version": VERSION}), encoding="utf-8")
    (root / ".beacon" / "qa").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "qa" / "status.json").write_text(json.dumps({"feature": FEATURE, "status": "passed", "evidence_done": True}, ensure_ascii=False), encoding="utf-8")
    (root / ".beacon" / "state" / "artifact-update-obligations").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "state" / "artifact-update-obligations" / f"{SLUG}.json").write_text(json.dumps({"feature": FEATURE, "obligations": []}, ensure_ascii=False), encoding="utf-8")
    (root / ".beacon" / "state" / "exhaustiveness").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "state" / "exhaustiveness" / f"{SLUG}.json").write_text(json.dumps({"feature": FEATURE, "status": "passed", "score": 1.0, "threshold": 0.8, "missing_axes": [], "missing_replay_scenarios": [], "missing_browser_evidence_scenarios": []}, ensure_ascii=False), encoding="utf-8")
    (root / ".beacon" / "qa" / "features" / SLUG).mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "qa" / "features" / SLUG / "scorecard.json").write_text(json.dumps({"feature": FEATURE, "release_ready": True, "release_confidence_min": 1.0, "review_required_count": 0, "needs_replay_count": 0, "unresolved_closure_outcomes": []}, ensure_ascii=False), encoding="utf-8")


def test_v112_implement_plan_command_should_compile_machine_and_human_artifacts(tmp_path: Path):
    _seed_docs(tmp_path)
    freeze = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    result = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "planned"
    assert payload["counts"]["total"] == 2
    assert (tmp_path / payload["plan_path"]).exists()
    assert (tmp_path / payload["plan_markdown_path"]).exists()
    assert (tmp_path / payload["progress_path"]).exists()

    plan = load_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)
    assert plan["revision_id"] == "R1"
    assert plan["baseline_hash"]
    assert [task["task_id"] for task in plan["tasks"]] == ["ITASK-001", "ITASK-002"]


def test_v112_implement_plan_should_use_prd_sections_and_matrix_alignment(tmp_path: Path):
    _seed_docs(tmp_path)
    base = tmp_path / "docs" / "beacon" / VERSION
    (base / "prd" / f"{SLUG}.md").write_text(
        "\n".join(
            [
                "# PRD",
                "",
                "## Functional Requirements",
                "",
                "### FR-001 Plan compilation",
                "- compile implementation plan from requirement materials",
                "",
                "### FR-002 Progress visibility",
                "- expose task progress and writeback visibility",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    machine_qa = base / ".machine" / "qa"
    machine_qa.mkdir(parents=True, exist_ok=True)
    (machine_qa / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {"ac_id": "AC-001", "tc_id": "TC-001"},
                    {"ac_id": "AC-002", "tc_id": "TC-002"},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    result = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    plan = load_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)
    assert plan["task_mapping_source"] == "prd-sections"
    assert plan["tasks"][0]["title"] == "FR-001 Plan compilation"
    assert plan["tasks"][0]["mapped_test_ids"] == ["TC-001"]
    assert plan["tasks"][1]["mapped_test_ids"] == ["TC-002"]


def test_v112_implement_plan_should_capture_story_and_qa_alignment_when_machine_materials_exist(tmp_path: Path):
    _seed_docs(tmp_path)
    base = tmp_path / "docs" / "beacon" / VERSION
    (base / "prd" / f"{SLUG}.md").write_text(
        "\n".join(
            [
                "# PRD",
                "",
                "## 功能需求",
                "",
                "### FR-001 Plan compilation",
                "- compile implementation plan from requirement materials",
                "",
                "### FR-002 Progress visibility",
                "- expose task progress and writeback visibility",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    machine_qa = base / ".machine" / "qa"
    machine_qa.mkdir(parents=True, exist_ok=True)
    (machine_qa / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps({"entries": [{"ac_id": "AC-001", "tc_id": "TC-001"}, {"ac_id": "AC-002", "tc_id": "TC-002"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (machine_qa / f"{SLUG}.story-scenario-map.json").write_text(
        json.dumps({"scenarios": [{"scenario_id": "SC-001", "ac_id": "AC-001", "source_tc_id": "TC-001"}, {"scenario_id": "SC-002", "ac_id": "AC-002", "source_tc_id": "TC-002"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (machine_qa / f"{SLUG}.qa9-matrix.json").write_text(
        json.dumps({"entries": [{"id": "QA9-001", "ac_id": "AC-001", "tc_id": "TC-001"}, {"id": "QA9-002", "ac_id": "AC-002", "tc_id": "TC-002"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    result = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    plan = load_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)
    assert plan["source_refs"]["story_scenario_map"].endswith(f"{SLUG}.story-scenario-map.json")
    assert plan["source_refs"]["qa9_matrix"].endswith(f"{SLUG}.qa9-matrix.json")
    assert plan["tasks"][0]["mapped_scenario_ids"] == ["SC-001"]
    assert plan["tasks"][0]["mapped_qa_case_ids"] == ["QA9-001"]
    assert plan["tasks"][1]["mapped_scenario_ids"] == ["SC-002"]
    assert plan["tasks"][1]["mapped_qa_case_ids"] == ["QA9-002"]


def test_v112_prd_requirement_parser_should_support_heading_bullet_numbered_and_table_forms():
    candidates = _extract_prd_task_candidates(
        "\n".join(
            [
                "# PRD",
                "",
                "## Functional Requirements",
                "",
                "### FR-001 Plan compiler",
                "- compile implementation plan from frozen requirement materials",
                "",
                "- FR-002 Task auto alignment: merge AC / TEST / scenario / qa9 signals",
                "  - keep alignment deterministic",
                "",
                "1. FR-003 Doctor upgrade registry — append cumulative upgrade steps",
                "",
                "| FR ID | Theme | Description |",
                "| --- | --- | --- |",
                "| FR-004 | Status Integration | surface next task and blocked task in status/help |",
                "",
                "## Non-goals",
                "- stop parsing here",
            ]
        )
        + "\n"
    )

    assert [item["title"] for item in candidates] == [
        "FR-001 Plan compiler",
        "FR-002 Task auto alignment",
        "FR-003 Doctor upgrade registry",
        "FR-004 Status Integration",
    ]
    assert "frozen requirement materials" in candidates[0]["description"]
    assert "keep alignment deterministic" in candidates[1]["description"]
    assert "append cumulative upgrade steps" in candidates[2]["description"]
    assert "next task and blocked task" in candidates[3]["description"]


def test_v112_implement_plan_should_use_requirement_parser_and_ordered_alignment_for_prd_mapping(tmp_path: Path):
    _seed_docs(tmp_path)
    base = tmp_path / "docs" / "beacon" / VERSION
    (base / "user-story" / f"{SLUG}.md").write_text(
        "\n".join(
            [
                "# User Story",
                "",
                "| AC ID | Theme | Description |",
                "| --- | --- | --- |",
                "| AC-001 | Plan Compiler | compile implementation plan |",
                "| AC-002 | Plan Artifact | plan artifacts exist |",
                "| AC-003 | Baseline Binding | bind baseline and revision |",
                "| AC-004 | Pre-implement Gate | enforce gate before implement |",
                "| AC-005 | Task Progress Model | task statuses are explicit |",
                "| AC-006 | Traceability | map story AC TEST refs |",
                "| AC-007 | Writeback Update | writeback updates plan |",
                "| AC-008 | Status Visibility | status shows plan progress |",
                "| AC-009 | Progress Fidelity | task progress is source of truth |",
                "| AC-010 | Closed-Loop Evidence | completed task has evidence |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base / "prd" / f"{SLUG}.md").write_text(
        "\n".join(
            [
                "# PRD",
                "",
                "## Functional Requirements",
                "",
                "### FR-001 PRD/US-to-Plan Compiler",
                "新增一个编译层。",
                "",
                "| FR ID | Theme | Description |",
                "| --- | --- | --- |",
                "| FR-002 | Implementation Plan Artifact | 新增工件。 |",
                "",
                "- FR-003 Task Model: 每个 task 至少应包含 mapped_story_ids mapped_ac_ids mapped_test_ids。",
                "",
                "1. FR-004 Pre-implement Plan Gate — plan baseline hash 与 frozen revision 一致，未对齐不得进入 implement。",
                "",
                "### FR-005 Plan Progress Writeback",
                "writeback 更新 plan task 状态。",
                "",
                "### FR-006 AC/TEST Traceability",
                "保留 AC TEST 到 implementation task traceability。",
                "",
                "### FR-007 Status Integration",
                "status / help 展示 plan-level progress。",
                "",
                "### FR-008 Compatibility With Existing Implement Surface",
                "不破坏 implement runner。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    machine_qa = base / ".machine" / "qa"
    machine_qa.mkdir(parents=True, exist_ok=True)
    (machine_qa / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps(
            {"entries": [{"ac_id": f"AC-{idx:03d}", "tc_id": f"TC-{idx:03d}"} for idx in range(1, 11)]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    result = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    plan = load_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)

    task_map = {task["title"]: task for task in plan["tasks"]}
    assert task_map["FR-001 PRD/US-to-Plan Compiler"]["mapped_ac_ids"] == ["AC-001"]
    assert task_map["FR-002 Implementation Plan Artifact"]["mapped_ac_ids"] == ["AC-002"]
    assert task_map["FR-003 Task Model"]["mapped_ac_ids"] == ["AC-005"]
    assert set(task_map["FR-004 Pre-implement Plan Gate"]["mapped_ac_ids"]) >= {"AC-003", "AC-004"}
    assert "AC-007" in task_map["FR-005 Plan Progress Writeback"]["mapped_ac_ids"]
    assert task_map["FR-006 AC/TEST Traceability"]["mapped_ac_ids"] == ["AC-006"]
    assert "AC-008" in task_map["FR-007 Status Integration"]["mapped_ac_ids"]


def test_v112_implement_plan_should_merge_story_scenario_and_qa9_alignment_into_mapped_test_ids(tmp_path: Path):
    _seed_docs(tmp_path)
    base = tmp_path / "docs" / "beacon" / VERSION
    (base / "prd" / f"{SLUG}.md").write_text(
        "\n".join(
            [
                "# PRD",
                "",
                "## Functional Requirements",
                "",
                "### FR-001 Plan compilation",
                "- compile implementation plan from requirement materials",
                "",
                "### FR-002 Progress visibility",
                "- expose task progress and writeback visibility",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    machine_qa = base / ".machine" / "qa"
    machine_qa.mkdir(parents=True, exist_ok=True)
    (machine_qa / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps({"entries": [{"ac_id": "AC-001", "tc_id": "TC-001"}, {"ac_id": "AC-002", "tc_id": "TC-002"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (machine_qa / f"{SLUG}.story-scenario-map.json").write_text(
        json.dumps(
            {
                "stories": [
                    {
                        "ac_id": "AC-001",
                        "theme": "Plan",
                        "text": "Compile plan",
                        "scenario_ids": ["SC-001", "SC-002"],
                        "scenarios": [
                            {"scenario_id": "SC-001", "source_tc_id": "TC-001", "tc_id": "TC-001-PRIMARY", "scenario_family": "primary", "qa_type": "unit"},
                            {"scenario_id": "SC-002", "source_tc_id": "TC-011", "tc_id": "TC-011-PRIMARY", "scenario_family": "primary", "qa_type": "interface"},
                        ],
                    },
                    {
                        "ac_id": "AC-002",
                        "theme": "Progress",
                        "text": "Track progress",
                        "scenario_ids": ["SC-003"],
                        "scenarios": [
                            {"scenario_id": "SC-003", "source_tc_id": "TC-002", "tc_id": "TC-002-PRIMARY", "scenario_family": "primary", "qa_type": "unit"},
                        ],
                    },
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (machine_qa / f"{SLUG}.qa9-matrix.json").write_text(
        json.dumps(
            {
                "entries": [
                    {"id": "QA9-001", "ac_id": "AC-001", "tc_id": "TC-001", "title": "Plan compiler unit"},
                    {"id": "QA9-011", "ac_id": "AC-001", "tc_id": "TC-011", "title": "Plan compiler interface"},
                    {"id": "QA9-002", "ac_id": "AC-002", "tc_id": "TC-002", "title": "Progress visibility unit"},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    result = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    plan = load_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)

    assert plan["tasks"][0]["mapped_test_ids"] == ["TC-001", "TC-011"]
    assert plan["tasks"][0]["mapped_scenario_ids"] == ["SC-001", "SC-002"]
    assert plan["tasks"][0]["mapped_qa_case_ids"] == ["QA9-001", "QA9-011"]


def test_v112_help_should_recommend_implement_plan_after_freeze_when_plan_missing(tmp_path: Path):
    _seed_docs(tmp_path)
    freeze = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    payload = build_help_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["doc_status"] == "frozen"
    assert payload["blocked_reason"] == "implementation_plan_missing"
    assert payload["next_step"]["action"] == "implement-plan"
    assert "beacon implement plan" in payload["next_step"]["command"]


def test_v112_implement_run_should_block_when_plan_missing(tmp_path: Path):
    _seed_docs(tmp_path)
    freeze = _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    result = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--runner",
            "native-single",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "implementation_plan_missing"
    assert payload["plan_preflight"]["reason_code"] == "implementation_plan_missing"


def test_v112_implement_run_and_status_should_surface_plan_progress(tmp_path: Path):
    _seed_docs(tmp_path)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    assert _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION]).exit_code == 0

    result = _invoke(
        [
            "implement",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--runner",
            "native-single",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert payload["implementation_plan_progress"]["counts"]["completed"] == 2

    status = _invoke(["implement", "status", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert status.exit_code == 0, status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["implementation_plan_exists"] is True
    assert status_payload["implementation_plan_progress"]["counts"]["completed"] == 2


def test_v112_writeback_should_update_plan_progress_and_verification_state(tmp_path: Path):
    _seed_docs(tmp_path)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    assert _invoke(["implement", "compile-plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION]).exit_code == 0

    impl = record_implementation_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-impl",
        implemented_item_ids=["AC-001"],
        changed_files=["beacon/commands/implement.py"],
    )
    progress = load_implementation_plan_progress(tmp_path, version=VERSION, feature=FEATURE)
    assert impl["implementation_plan"]["tasks"][0]["status"] == "completed"
    assert progress["counts"]["completed"] == 1
    assert progress["next_task_id"] == "ITASK-002"

    verify = record_verification_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-verify",
        verified_item_ids=[],
        failed_item_ids=["TEST-002"],
        evidence_ref=[".beacon/auto-test-status.json"],
    )
    progress = load_implementation_plan_progress(tmp_path, version=VERSION, feature=FEATURE)
    assert verify["implementation_plan"]["tasks"][1]["status"] == "blocked"
    assert "ITASK-002" in progress["blocked_task_ids"]


def test_v112_external_runner_task_ids_and_report_review_should_consume_plan_truth(tmp_path: Path):
    _seed_docs(tmp_path)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    assert _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION]).exit_code == 0

    script = tmp_path / "runner.py"
    script.write_text(
        (
            "import json, pathlib, sys\n"
            "request_file = pathlib.Path(sys.argv[1])\n"
            "result_file = pathlib.Path(sys.argv[2])\n"
            "payload = json.loads(request_file.read_text(encoding='utf-8'))\n"
            "result_file.parent.mkdir(parents=True, exist_ok=True)\n"
            "result_file.write_text(json.dumps({\n"
            "  'schema_version':'1.0',\n"
            "  'run_id': payload['run_id'],\n"
            "  'status':'completed',\n"
            "  'summary':'runner finished with task ids',\n"
            "  'changed_files':['beacon/commands/implement.py'],\n"
            "  'verification':[{'command':'pytest -q','status':'passed'}],\n"
            "  'artifact_updates':{'review_quality':{'required':True,'reason':'quality review still required'}, 'acceptance':{'required':True,'reason':'acceptance still required'}},\n"
            "  'implemented_items':['AC-001'],\n"
            "  'implemented_task_ids':['ITASK-001']\n"
            "}, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')\n"
        ),
        encoding="utf-8",
    )
    (tmp_path / "beacon.config.yaml").write_text(
        (
            "skill:\n"
            "  adapters:\n"
            "    fake:\n"
            "      adapter_type: command\n"
            "      runtime_family: fake\n"
            "      command: python3\n"
            "      args:\n"
            "        - \"{project_root}/runner.py\"\n"
            "        - \"{request_file}\"\n"
            "        - \"{result_file}\"\n"
        ),
        encoding="utf-8",
    )

    impl = _invoke(
        ["implement", "run", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--runner", "fake", "--json"]
    )
    assert impl.exit_code == 0, impl.stdout
    impl_payload = json.loads(impl.stdout)
    assert impl_payload["implemented_task_ids"] == ["ITASK-001"]

    progress = load_implementation_plan_progress(tmp_path, version=VERSION, feature=FEATURE)
    assert progress["counts"]["completed"] == 1
    assert progress["counts"]["in_progress"] == 0
    assert progress["next_task_id"] == "ITASK-002"

    quality = _invoke(["review", "quality", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert quality.exit_code == 0, quality.stdout
    quality_payload = json.loads(quality.stdout)
    assert quality_payload["implementation_plan_progress"]["next_task_id"] == "ITASK-002"

    report = _invoke(["report", "--project-root", str(tmp_path), "--version", VERSION, "--machine", "latest"])
    assert report.exit_code == 0, report.stdout
    report_payload = json.loads(report.stdout)
    assert report_payload["implementation_plan"]["next_task_id"] == "ITASK-002"


def test_v112_release_gate_should_block_when_implementation_plan_is_incomplete_and_pass_when_closed(tmp_path: Path):
    _seed_docs(tmp_path)
    _seed_release_contract_artifacts(tmp_path)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    assert _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION]).exit_code == 0

    issues = check_v112_implementation_plan_contract(tmp_path, GateMode.STRICT, "release", VERSION)
    codes = {item["reason_code"] for item in issues}
    assert "implementation_plan_incomplete" in codes

    record_implementation_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-impl",
        implemented_item_ids=["AC-001", "AC-002"],
        task_ids=["ITASK-001", "ITASK-002"],
        changed_files=["beacon/commands/implement.py"],
    )
    issues = check_v112_implementation_plan_contract(tmp_path, GateMode.STRICT, "release", VERSION)
    assert issues == []


def test_v112_release_gate_should_ignore_cross_version_qa_status_and_fallback_to_current_revision(tmp_path: Path):
    _seed_docs(tmp_path)
    _seed_release_contract_artifacts(tmp_path)
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    assert _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION]).exit_code == 0

    (tmp_path / ".beacon" / "qa" / "status.json").write_text(
        json.dumps(
            {
                "feature": "Old Feature",
                "version": "v9.9.9",
                "status": "passed",
                "evidence_done": True,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    record_implementation_writeback(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        run_id="run-impl",
        implemented_item_ids=["AC-001", "AC-002"],
        task_ids=["ITASK-001", "ITASK-002"],
        changed_files=["beacon/commands/implement.py"],
    )

    issues = check_v112_implementation_plan_contract(tmp_path, GateMode.STRICT, "release", VERSION)
    assert issues == []


def test_v112_gate_release_should_require_scenario_and_qa_alignment_when_materials_exist(tmp_path: Path):
    _seed_docs(tmp_path)
    _seed_release_contract_artifacts(tmp_path)
    base = tmp_path / "docs" / "beacon" / VERSION
    machine_qa = base / ".machine" / "qa"
    machine_qa.mkdir(parents=True, exist_ok=True)
    (machine_qa / f"{SLUG}.ac-test-matrix.json").write_text(
        json.dumps({"entries": [{"ac_id": "AC-001", "tc_id": "TC-001"}, {"ac_id": "AC-002", "tc_id": "TC-002"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (machine_qa / f"{SLUG}.story-scenario-map.json").write_text(
        json.dumps({"scenarios": [{"scenario_id": "SC-001", "ac_id": "AC-001", "source_tc_id": "TC-001"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (machine_qa / f"{SLUG}.qa9-matrix.json").write_text(
        json.dumps({"entries": [{"id": "QA9-001", "ac_id": "AC-001", "tc_id": "TC-001"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    assert _invoke(["freeze", FEATURE, "--project", str(tmp_path), "--version", VERSION]).exit_code == 0
    assert _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION]).exit_code == 0
    plan_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"implementation-plan-{SLUG}.json"
    plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
    plan_payload["tasks"][0]["mapped_scenario_ids"] = []
    plan_payload["tasks"][0]["mapped_qa_case_ids"] = []
    plan_path.write_text(json.dumps(plan_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    issues = check_v112_implementation_plan_contract(tmp_path, GateMode.STRICT, "release", VERSION)
    messages = [str(item.get("message", "")) for item in issues]
    assert any("scenario alignment" in message for message in messages)
    assert any("QA alignment" in message for message in messages)
