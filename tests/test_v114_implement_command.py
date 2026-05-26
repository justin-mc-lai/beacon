from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.artifact_paths import change_docs_file, change_file_output, execution_file_output
from beacon.utils.implement_adapters import build_default_task_prompt
from beacon.utils.implement_prompt_boundary import evaluate_implement_prompt_boundary
from beacon.utils.semantic_runtime import load_or_build_semantic_layer
from beacon.utils.workflow_memory import compute_workflow_progress, load_lifecycle_events


runner = CliRunner()
implement_cmd = importlib.import_module("beacon.commands.implement.commands")


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _latest_run_id(project_root: Path) -> str:
    runs_dir = project_root / ".beacon" / "runs"
    runs = sorted([p.name for p in runs_dir.iterdir() if p.is_dir() and (p / "state.json").exists()])
    assert runs
    return runs[-1]


def _init_git_repo(root: Path, *, version: str) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Beacon Tests"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "beacon-tests@example.com"], cwd=root, check=True, capture_output=True, text=True)
    (root / ".gitkeep").write_text("test\n", encoding="utf-8")
    (root / ".gitignore").write_text(".beacon/\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep", ".gitignore"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "switch", "-c", f"beacon/{version}"], cwd=root, check=True, capture_output=True, text=True)


def _seed_feature_docs(root: Path, *, version: str = "v1.1.4", feature: str = "my feature") -> str:
    slug = feature.lower().replace(" ", "-")
    if not (root / ".git").exists():
        _init_git_repo(root, version=version)
    base = root / "docs" / "beacon" / version
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "user-story" / f"{slug}.md").write_text("# User Story\n", encoding="utf-8")
    (base / "prd" / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.md").write_text("# Test Cases\n", encoding="utf-8")
    (base / "qa" / "test-cases" / f"{slug}.ac-test-matrix.json").write_text('{"entries":[]}\n', encoding="utf-8")
    return slug


def _seed_v140_incomplete_closure_docs(root: Path, *, feature: str = "My Feature") -> str:
    slug = _seed_feature_docs(root, version="v1.4.0", feature=feature)
    base = root / "docs" / "beacon" / "v1.4.0"
    (base / "prd" / f"{slug}.md").write_text(
        (
            "# PRD: My Feature\n\n"
            "- version: `v1.4.0`\n"
            "- feature: `My Feature`\n"
            "- status: `draft`\n"
        ),
        encoding="utf-8",
    )
    (base / "user-story" / f"{slug}.md").write_text(
        (
            "# User Story: My Feature\n\n"
            "## Acceptance Criteria\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | happy-path | 系统可以完成补齐。 |\n"
        ),
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / f"{slug}.md").write_text(
        (
            "# Test Cases: My Feature\n\n"
            "## Coverage Matrix\n\n"
            "| TC ID | AC ID | Scenario | Layer | Expected |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| TC-001 | AC-001 | happy | unit | ok |\n"
        ),
        encoding="utf-8",
    )
    return slug


def _write_runner_script(path: Path, *, write_result: bool = True) -> None:
    path.write_text(
        (
            "import json, sys, pathlib\n"
            "request_file = pathlib.Path(sys.argv[1])\n"
            "result_file = pathlib.Path(sys.argv[2])\n"
            "payload = json.loads(request_file.read_text())\n"
            "if " + ("True" if write_result else "False") + ":\n"
            "  result_file.parent.mkdir(parents=True, exist_ok=True)\n"
            "  result_file.write_text(json.dumps({\n"
            "    'schema_version':'1.0',\n"
            "    'run_id': payload['run_id'],\n"
            "    'status':'completed',\n"
            "    'summary':'runner finished',\n"
            "    'changed_files':['beacon/commands/implement.py'],\n"
            "    'verification':[{'command':'pytest -q','status':'passed'}],\n"
            "    'artifact_updates':{'prd':{'required':False}}\n"
            "  }, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')\n"
        ),
        encoding="utf-8",
    )


def _write_sleep_runner_script(path: Path) -> None:
    path.write_text(
        (
            "import time\n"
            "time.sleep(0.2)\n"
        ),
        encoding="utf-8",
    )


def _write_invalid_result_runner_script(path: Path) -> None:
    path.write_text(
        (
            "import sys, pathlib\n"
            "result_file = pathlib.Path(sys.argv[2])\n"
            "result_file.parent.mkdir(parents=True, exist_ok=True)\n"
            "result_file.write_text('{not-json}\\n', encoding='utf-8')\n"
        ),
        encoding="utf-8",
    )


def test_implement_list_runners_should_show_preferred(tmp_path: Path):
    (tmp_path / "beacon.config.yaml").write_text(
        "skill:\n  preferred: omx\n",
        encoding="utf-8",
    )
    result = _invoke(["implement", "list-runners", "--project-root", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["preferred"] == "omx"
    ids = {item["id"] for item in payload["runners"]}
    assert {"omx", "omc", "gstack", "codex-subagents"} <= ids


def test_implement_run_dry_run_should_write_request_and_state(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "omx",
            "--dry-run",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "dry_run"
    assert payload["command"][:5] == ["omx", "exec", "--full-auto", "--cd", str(tmp_path)]
    assert "--skip-git-repo-check" in payload["command"]
    run_id = payload["run_id"]
    assert (tmp_path / ".beacon" / "implement" / run_id / "state.json").exists()
    assert (tmp_path / ".beacon" / "implement" / run_id / "request.json").exists()


def test_implement_run_native_dry_run_should_not_materialize_tracked_delivery_artifacts(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "native-single",
            "--dry-run",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    run_id = payload["run_id"]
    assert payload["status"] == "dry_run"
    assert payload["command"] == []
    assert (tmp_path / ".beacon" / "implement" / run_id / "state.json").exists()
    assert (tmp_path / ".beacon" / "implement" / run_id / "request.json").exists()
    assert not (tmp_path / ".beacon" / "state" / "implementation-my-feature.json").exists()
    assert not execution_file_output(tmp_path, "v1.1.4", "implementation-summary-my-feature.json").exists()
    assert not execution_file_output(tmp_path, "v1.1.4", "technical-implementation-my-feature.json").exists()


def test_review_quality_should_emit_completed_review_quality_obligation_when_gate_ready(tmp_path: Path):
    feature = "My Feature"
    version = "v1.1.4"
    _seed_feature_docs(tmp_path, feature=feature, version=version)

    from beacon.utils.artifact_update_obligations import write_artifact_update_obligations
    from beacon.utils.runtime import write_json

    write_json(tmp_path / ".beacon" / "auto-test-status.json", {"status": "passed"})
    write_json(tmp_path / ".beacon" / "qa" / "status.json", {"evidence_done": True})
    write_json(tmp_path / ".beacon" / "story-state" / version / "my-feature.json", {"feature": feature, "status": "implemented"})
    write_json(tmp_path / "docs" / "beacon" / version / ".machine" / "qa" / "my-feature.ac-test-matrix.json", {"entries": []})
    write_artifact_update_obligations(
        tmp_path,
        version=version,
        feature=feature,
        run_id="run-test",
        technical_archive_path=f"docs/beacon/{version}/.machine/execution/technical-implementation-my-feature.json",
        updates={
            "review_quality": {"required": True, "reason": "run quality review after native implementation"},
            "acceptance": {"required": True, "reason": "acceptance remains a formal post-verify action"},
        },
    )
    (tmp_path / "docs" / "beacon" / version / "SUMMARY.md").write_text("# summary\n", encoding="utf-8")
    (tmp_path / "docs" / "beacon" / version / "execution" / "boundaries.md").write_text("# boundaries\n", encoding="utf-8")
    (tmp_path / "docs" / "beacon" / version / "execution" / "project-skill-qa-evolution-blueprint.md").write_text("# blueprint\n", encoding="utf-8")
    (tmp_path / "docs" / "beacon" / version / "source-architecture").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / version / "source-architecture" / "index.md").write_text("# source architecture\n", encoding="utf-8")
    (tmp_path / "docs" / "beacon" / version / "release").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "beacon" / version / "release" / "index.md").write_text("# release\n", encoding="utf-8")

    result = _invoke(["review", "quality", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["gate_ready"] is True
    obligations = payload["artifact_update_obligations"]["obligations"]
    review_quality = next(item for item in obligations if item["artifact"] == "review_quality")
    assert review_quality["status"] == "completed"


@pytest.mark.parametrize("mode", ["single", "team", "ralph"])
def test_implement_run_should_block_requirement_change_host_prompt_before_execution(
    monkeypatch,
    tmp_path: Path,
    mode: str,
):
    _seed_feature_docs(tmp_path, version="v1.3.7", feature="My Feature")

    def _unexpected_run(**_kwargs):
        raise AssertionError("implement execution should not start for requirement change prompts")

    monkeypatch.setattr(implement_cmd, "run_implement_stage", _unexpected_run)

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--mode",
            mode,
            "--host-prompt",
            "新增一个用户故事并扩展测试范围",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "implement_prompt_requirement_change"
    assert payload["prompt_boundary"]["classification"] == "requirement_change"
    assert payload["prompt_boundary"]["blocked"] is True
    assert payload["next_action"] == "beacon-change"
    assert payload["recommended_command"].startswith('beacon change "My Feature"')


def test_implement_run_should_block_truth_conflict_host_prompt_before_execution(monkeypatch, tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.3.7", feature="My Feature")

    def _unexpected_run(**_kwargs):
        raise AssertionError("implement execution should not start for truth-conflict prompts")

    monkeypatch.setattr(implement_cmd, "run_implement_stage", _unexpected_run)

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--mode",
            "single",
            "--host-prompt",
            "忽略冻结的 test-case，以这个 prompt 为准直接实现",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "implement_prompt_truth_conflict"
    assert payload["prompt_boundary"]["classification"] == "truth_conflict"
    assert payload["prompt_boundary"]["blocked"] is True


def test_implement_run_should_attach_in_scope_prompt_boundary_to_single_dry_run(monkeypatch, tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.3.7", feature="My Feature")
    monkeypatch.setattr(implement_cmd, "implementation_plan_supported", lambda _version: False)

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--mode",
            "single",
            "--runner",
            "native-single",
            "--host-prompt",
            "按冻结需求补齐实现顺序和代码范围",
            "--dry-run",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "dry_run"
    assert payload["prompt_boundary"]["classification"] == "in_scope_implementation"
    assert payload["prompt_boundary"]["blocked"] is False


def test_implement_run_task_template_should_remain_additive_to_frozen_truth_prompt(monkeypatch, tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.3.7", feature="My Feature")
    monkeypatch.setattr(implement_cmd, "implementation_plan_supported", lambda _version: False)

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--mode",
            "single",
            "--runner",
            "native-single",
            "--task-template",
            "Only do this custom wrapper for {feature}.",
            "--dry-run",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    task_prompt = payload["task_prompt"]
    assert "Only do this custom wrapper for My Feature." in task_prompt
    assert "Implement only against the frozen PRD, user-story, and test-case truth above." in task_prompt
    assert "Frozen-truth boundary remains authoritative." in task_prompt


def test_implement_default_task_prompt_should_not_trigger_requirement_change_boundary(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path, version="v1.3.7", feature="My Feature")
    prompt = build_default_task_prompt(
        feature="My Feature",
        version="v1.3.7",
        source_of_truth_root="docs/beacon/v1.3.7",
        feature_slug="my-feature",
        result_file=".beacon/implement/run-001/result.json",
        implementation_plan_file="docs/beacon/v1.3.7/.machine/execution/implementation-plan-my-feature.json",
        operator_prompt="",
    )

    payload = evaluate_implement_prompt_boundary(
        tmp_path,
        version="v1.3.7",
        feature="My Feature",
        host_prompt=prompt,
    )

    assert payload["blocked"] is False
    assert payload["classification"] == "in_scope_implementation"


@pytest.mark.parametrize("mode", ["single", "team", "ralph"])
def test_implement_run_should_block_requirement_change_task_template_before_execution(
    monkeypatch,
    tmp_path: Path,
    mode: str,
):
    _seed_feature_docs(tmp_path, version="v1.3.7", feature="My Feature")

    def _unexpected_run(**_kwargs):
        raise AssertionError("implement execution should not start for requirement-change task templates")

    monkeypatch.setattr(implement_cmd, "run_implement_stage", _unexpected_run)

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--mode",
            mode,
            "--task-template",
            "新增一个用户故事并扩展测试范围，然后执行 {task_prompt}",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "implement_prompt_requirement_change"
    assert payload["prompt_boundary"]["classification"] == "requirement_change"
    assert payload["prompt_boundary"]["surface"] == "task_template"
    assert payload["prompt_boundary"]["blocked"] is True


def test_implement_run_ralph_dry_run_should_not_invoke_controller_or_materialize_tracked_delivery_artifacts(
    monkeypatch,
    tmp_path: Path,
):
    _seed_feature_docs(tmp_path, feature="My Feature")

    def _unexpected_controller(**_kwargs):
        raise AssertionError("ralph controller should not run during dry-run")

    monkeypatch.setattr(implement_cmd, "_run_ralph_controller", _unexpected_controller)
    monkeypatch.setattr(implement_cmd, "runtime_context_precheck_required", lambda **_kwargs: False)
    monkeypatch.setattr(
        implement_cmd,
        "delegation_readiness_precheck",
        lambda *args, **kwargs: {
            "schema_version": "1.0",
            "check": "delegation-readiness",
            "status": "pass",
            "reason_code": "",
            "feature": kwargs.get("feature", args[1] if len(args) > 1 else ""),
            "version": kwargs.get("version", args[2] if len(args) > 2 else ""),
            "checks": [],
            "blocked_checks": [],
            "recommended_command": "",
        },
    )

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--mode",
            "ralph",
            "--runner",
            "native-single",
            "--dry-run",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    run_id = payload["run_id"]
    assert payload["status"] == "dry_run"
    assert payload["mode"] == "ralph"
    assert payload["command"] == []
    assert (tmp_path / ".beacon" / "implement" / run_id / "state.json").exists()
    assert not execution_file_output(tmp_path, "v1.1.4", "ralph-summary-my-feature.json").exists()
    assert not (tmp_path / "docs/beacon/v1.1.4/.machine/trace/ralph/my-feature/ralph-summary-my-feature.md").exists()
    assert not execution_file_output(tmp_path, "v1.1.4", "ralph-round-my-feature-round-001.json").exists()
    assert not (tmp_path / "docs/beacon/v1.1.4/.machine/trace/ralph/my-feature/ralph-round-my-feature-round-001.md").exists()


def test_implement_plan_should_block_requirement_change_host_prompt_before_compiling_plan(monkeypatch, tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.3.7", feature="My Feature")

    def _unexpected_compile(*_args, **_kwargs):
        raise AssertionError("implementation plan should not compile for requirement change prompts")

    monkeypatch.setattr(implement_cmd, "compile_implementation_plan", _unexpected_compile)

    result = _invoke(
        [
            "implement",
            "plan",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--host-prompt",
            "新增一个用户故事并扩展测试范围",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "implement_prompt_requirement_change"
    assert payload["prompt_boundary"]["classification"] == "requirement_change"


def test_implement_run_should_block_when_v140_closure_preflight_requires_supplement(monkeypatch, tmp_path: Path):
    _seed_v140_incomplete_closure_docs(tmp_path, feature="My Feature")

    monkeypatch.setattr(
        implement_cmd,
        "build_requirement_package_gate",
        lambda *_args, **_kwargs: {"status": "pass", "reason_code": "", "recommended_command": ""},
    )
    monkeypatch.setattr(implement_cmd, "implementation_plan_supported", lambda _version: False)

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--mode",
            "single",
            "--runner",
            "native-single",
            "--dry-run",
            "--json",
        ]
    )

    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "requirement_closure_supplement_required"
    assert payload["closure_preflight"]["status"] == "blocked"
    assert payload["closure_preflight"]["closure_verdict"] == "supplement_required"
    assert "goal_defined" in payload["closure_preflight"]["closure_analysis"]["missing_evidence"]


def test_implement_plan_should_block_when_v140_closure_preflight_requires_supplement(monkeypatch, tmp_path: Path):
    _seed_v140_incomplete_closure_docs(tmp_path, feature="My Feature")

    def _unexpected_compile(*_args, **_kwargs):
        raise AssertionError("implementation plan should not compile when closure preflight is blocked")

    monkeypatch.setattr(
        implement_cmd,
        "build_requirement_package_gate",
        lambda *_args, **_kwargs: {"status": "pass", "reason_code": "", "recommended_command": ""},
    )
    monkeypatch.setattr(implement_cmd, "compile_implementation_plan", _unexpected_compile)

    result = _invoke(
        [
            "implement",
            "plan",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--json",
        ]
    )

    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "requirement_closure_supplement_required"
    assert payload["closure_preflight"]["package_state"] == "full_consistent"


def test_implement_run_handoff_should_write_markdown_request(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    (tmp_path / ".claude" / "skills" / "gstack").mkdir(parents=True, exist_ok=True)
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "gstack",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "handoff_required"
    assert (tmp_path / payload["request_markdown"]).exists()
    assert not (tmp_path / ".beacon" / "state" / "implementation-my-feature.json").exists()


def test_implement_run_command_runner_should_write_marker_summary_and_review(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    _write_runner_script(script)
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

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert (tmp_path / ".beacon" / "state" / "implementation-my-feature.json").exists()
    assert execution_file_output(tmp_path, "v1.1.4", "implementation-summary-my-feature.json").exists()
    assert execution_file_output(tmp_path, "v1.1.4", "review-spec-my-feature.json").exists()
    summary_payload = json.loads(
        execution_file_output(tmp_path, "v1.1.4", "implementation-summary-my-feature.json").read_text(encoding="utf-8")
    )
    assert summary_payload["requirement_traceability"]["prd"] == "docs/beacon/v1.1.4/prd/my-feature.md"
    assert summary_payload["requirement_traceability"]["user_story"] == "docs/beacon/v1.1.4/user-story/my-feature.md"
    assert summary_payload["requirement_traceability"]["test_case"] == "docs/beacon/v1.1.4/qa/test-cases/my-feature.md"
    assert summary_payload["delivery_surfaces"]["runtime_mode"] == "single"
    assert summary_payload["delivery_surfaces"]["shipped_surfaces"] == []
    assert summary_payload["delivery_surfaces"]["partial_surfaces"] == []
    assert summary_payload["delivery_surfaces"]["deferred_surfaces"] == []
    assert payload["change_document"]["md"] == "docs/beacon/v1.1.4/change/my-feature.md"
    assert change_docs_file(tmp_path, "v1.1.4", "my-feature.md").exists()
    assert change_file_output(tmp_path, "v1.1.4", "my-feature.json").exists()
    change_text = change_docs_file(tmp_path, "v1.1.4", "my-feature.md").read_text(encoding="utf-8")
    assert "## Fixed" in change_text
    assert "Updated `beacon/commands/implement.py`" in change_text


def test_implement_run_should_fail_when_result_missing(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    _write_runner_script(script, write_result=False)
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
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "runner_result_missing"


def test_implement_run_should_backfill_existing_workflow_lifecycle_when_invoked_directly(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    planned = _invoke(["workflow", "start", "My Feature", "--project", str(tmp_path), "--version", "v1.1.4"])
    assert planned.exit_code == 0, planned.stdout
    run_id = _latest_run_id(tmp_path)

    script = tmp_path / "runner.py"
    _write_runner_script(script)
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

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert payload["workflow_lifecycle_sync"]["synced"] is True
    assert payload["workflow_lifecycle_sync"]["run_id"] == run_id

    progress = compute_workflow_progress(tmp_path, run_id=run_id)
    assert progress["stages"]["implement"]["status"] == "completed"

    names = {item["event"] for item in load_lifecycle_events(tmp_path, run_id=run_id, stage="implement")}
    assert {"stage_started", "stage_context_injected", "stage_finished", "memory_writeback"} <= names


def test_implement_run_should_fail_when_result_json_is_unparseable(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    script.write_text(
        (
            "import sys, pathlib\n"
            "result_file = pathlib.Path(sys.argv[2])\n"
            "result_file.parent.mkdir(parents=True, exist_ok=True)\n"
            "result_file.write_text('{bad json', encoding='utf-8')\n"
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
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "runner_result_invalid"


def test_implement_status_should_prefer_run_matching_requested_version(tmp_path: Path):
    feature = "Friend Match"
    slug = _seed_feature_docs(tmp_path, version="v1.0.0", feature=feature)
    _seed_feature_docs(tmp_path, version="v1.3.1", feature=feature)

    legacy_run = tmp_path / ".beacon" / "implement" / "run-v100" / "state.json"
    legacy_run.parent.mkdir(parents=True, exist_ok=True)
    legacy_run.write_text(
        json.dumps(
            {
                "run_id": "run-v100",
                "feature": feature,
                "feature_slug": slug,
                "version": "v1.0.0",
                "status": "completed",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    newer_run = tmp_path / ".beacon" / "implement" / "run-v131" / "state.json"
    newer_run.parent.mkdir(parents=True, exist_ok=True)
    newer_run.write_text(
        json.dumps(
            {
                "run_id": "run-v131",
                "feature": feature,
                "feature_slug": slug,
                "version": "v1.3.1",
                "status": "completed",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "implement",
            "status",
            feature,
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.0.0",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["run_id"] == "run-v100"
    assert payload["version"] == "v1.0.0"


def test_implement_run_should_fail_when_runner_times_out(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    _write_sleep_runner_script(script)
    (tmp_path / "beacon.config.yaml").write_text(
        (
            "skill:\n"
            "  adapters:\n"
            "    fake:\n"
            "      adapter_type: command\n"
            "      runtime_family: fake\n"
            "      command: python3\n"
            "      timeout_sec: 0.01\n"
            "      args:\n"
            "        - \"{project_root}/runner.py\"\n"
            "        - \"{request_file}\"\n"
            "        - \"{result_file}\"\n"
        ),
        encoding="utf-8",
    )
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "runner_execution_timeout"


def test_implement_run_should_fail_when_result_is_invalid_json(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    _write_invalid_result_runner_script(script)
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
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--json",
        ]
    )
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "runner_result_invalid"
    assert "result json parse failed" in payload["problems"][0]


def test_implement_check_branch_should_block_when_current_branch_is_not_version_branch(tmp_path: Path):
    _init_git_repo(tmp_path, version="v1.1.4")
    subprocess.run(["git", "switch", "main"], cwd=tmp_path, check=True, capture_output=True, text=True)
    result = _invoke(
        [
            "implement",
            "check-branch",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["expected_branch"] == "beacon/v1.1.4"
    assert payload["current_branch"] == "main"


def test_implement_run_should_block_before_runner_when_branch_mismatched(tmp_path: Path):
    _init_git_repo(tmp_path, version="v1.1.4")
    subprocess.run(["git", "switch", "main"], cwd=tmp_path, check=True, capture_output=True, text=True)
    _seed_feature_docs(tmp_path, feature="My Feature")
    subprocess.run(["git", "switch", "main"], cwd=tmp_path, check=True, capture_output=True, text=True)
    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "omx",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "implement_branch_guard_blocked"
    assert payload["expected_branch"] == "beacon/v1.1.4"
    assert payload["current_branch"] == "main"


def test_implement_check_branch_should_auto_switch_when_explicitly_requested(tmp_path: Path):
    _init_git_repo(tmp_path, version="v1.1.4")
    subprocess.run(["git", "switch", "main"], cwd=tmp_path, check=True, capture_output=True, text=True)
    result = _invoke(
        [
            "implement",
            "check-branch",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--auto-switch-branch",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["current_branch"] == "beacon/v1.1.4"
    assert payload["switch_attempt"]["status"] == "switched"


def test_implement_check_branch_should_support_workspace_root_with_child_git_repos(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for name in ("marketing_sys", "health-svr-dotnet"):
        service_root = workspace / name
        service_root.mkdir()
        _init_git_repo(service_root, version="v1.3.1-dev")
        subprocess.run(
            ["git", "switch", "-c", "feature/v1.3.1-dev-account-cleanup-upstream"],
            cwd=service_root,
            check=True,
            capture_output=True,
            text=True,
        )
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
            "check-branch",
            "--project-root",
            str(workspace),
            "--version",
            "v1.3.1-dev",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["expected_branch"] == "feature/v1.3.1-dev-account-cleanup-upstream"
    workspace_repos = payload["git_alignment"]["workspace_repos"]
    assert len(workspace_repos) == 2
    assert all(item["branch_matches_target"] for item in workspace_repos)
    assert payload["service_scope"]["direct_delivery_services"] == ["marketing_sys", "health-svr-dotnet"]


def test_implement_check_branch_should_block_workspace_dirty_repo_before_auto_switch(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    push_root = workspace / "push-svr"
    push_root.mkdir()
    _init_git_repo(push_root, version="v1.3.2.1")
    subprocess.run(
        ["git", "switch", "-c", "feature/v1.3.2.1"],
        cwd=push_root,
        check=True,
        capture_output=True,
        text=True,
    )

    account_root = workspace / "wechat-account-svr"
    account_root.mkdir()
    _init_git_repo(account_root, version="v1.3.2.1")
    subprocess.run(
        ["git", "switch", "-c", "feature/v1.3.1-functional-dev"],
        cwd=account_root,
        check=True,
        capture_output=True,
        text=True,
    )
    (account_root / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    (workspace / "beacon.config.yaml").write_text(
        (
            "implementation:\n"
            "  branch_guard:\n"
            "    expected_branch: feature/v1.3.2.1\n"
            "    branch_prefix: feature/\n"
            "    base_branch: master\n"
            "    git_roots:\n"
            "      - push-svr\n"
            "      - wechat-account-svr\n"
        ),
        encoding="utf-8",
    )
    result = _invoke(
        [
            "implement",
            "check-branch",
            "--project-root",
            str(workspace),
            "--version",
            "v1.3.2.1",
            "--auto-switch-branch",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert "implement_branch_switch_dirty_worktree" in payload["reason_codes"]
    assert "dirty worktree blocks switch" in payload["summary"]
    assert "stash push -u" in payload["recommended_command"]
    assert "switch_attempt" not in payload
    dirty_repo = next(item for item in payload["git_alignment"]["workspace_repos"] if item["relative_root"] == "wechat-account-svr")
    assert dirty_repo["dirty_worktree"] is True
    assert "implement_branch_switch_dirty_worktree" in dirty_repo["reason_codes"]
    assert payload["service_scope"]["direct_delivery_services"] == ["push-svr", "wechat-account-svr"]


def test_implement_run_should_support_auto_review_quality_and_status_surface(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    _write_runner_script(script)
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon" / "auto-test-status.json").write_text('{"status":"passed"}\n', encoding="utf-8")
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

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--auto-review-quality",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["review_quality"]["exit_code"] == 0
    assert execution_file_output(tmp_path, "v1.1.4", "review-quality-my-feature.json").exists()

    status = _invoke(
        [
            "implement",
            "status",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--json",
        ]
    )
    assert status.exit_code == 0, status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["summary_exists"] is True
    assert status_payload["review_spec_exists"] is True
    assert status_payload["review_quality_exists"] is True
    assert status_payload["implementation_marker_exists"] is True


def test_run_auto_qa_sequence_should_follow_supported_handoff_and_rerun(monkeypatch, tmp_path: Path):
    calls: list[tuple[str, str]] = []
    qa_payloads = [
        (
            2,
            {
                "feature_scorecard": {
                    "continue_decision": "continue",
                    "repair_handoff": {
                        "action": "test-case-create",
                        "command": 'beacon test-case create "My Feature" --project-root /tmp/demo --version v1.1.10',
                    },
                }
            },
        ),
        (
            0,
            {
                "feature_scorecard": {
                    "continue_decision": "ready_for_release",
                    "repair_handoff": {
                        "action": "release-check",
                        "command": "beacon gate check release --project-root /tmp/demo --version v1.1.10",
                    },
                }
            },
        ),
    ]

    def _fake_run_auto_qa(project_root: Path, *, feature: str, version: str, extra_args: list[str]):
        calls.append(("qa", feature))
        return qa_payloads.pop(0)

    def _fake_run_beacon_json_command(project_root: Path, command: str):
        calls.append(("handoff", command))
        return 0, {"status": "generated"}

    monkeypatch.setattr(implement_cmd, "_run_auto_qa", _fake_run_auto_qa)
    monkeypatch.setattr(implement_cmd, "_run_beacon_json_command", _fake_run_beacon_json_command)

    exit_code, payload = implement_cmd._run_auto_qa_sequence(  # type: ignore[attr-defined]
        tmp_path,
        feature="My Feature",
        version="v1.1.10",
        extra_args=["--mode", "story-exhaustive"],
        follow_handoff=True,
        max_rounds=3,
    )
    assert exit_code == 0
    assert payload["follow_handoff"] is True
    assert payload["max_rounds"] == 3
    assert len(payload["history"]) == 3
    assert calls[0] == ("qa", "My Feature")
    assert calls[1][0] == "handoff"
    assert calls[2] == ("qa", "My Feature")


def test_implement_team_run_should_forward_team_mode(monkeypatch, tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.3.7", feature="My Feature")
    captured: dict[str, object] = {}

    def _fake_run_implement_stage(**kwargs):
        captured.update(kwargs)
        return 0, {
            "schema_version": "1.0",
            "status": "completed",
            "run_id": "run-team-mode",
            "team_surface": "implement-team",
        }

    monkeypatch.setattr(implement_cmd, "run_implement_stage", _fake_run_implement_stage)

    result = _invoke(
        [
            "implement",
            "team-run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    assert captured["mode"] == "team"
    assert captured["runner"] == "codex-subagents"


def test_implement_run_ralph_should_forward_prompt_boundary_to_controller(monkeypatch, tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.3.7", feature="My Feature")
    captured: dict[str, object] = {}

    def _fake_ralph_controller(**kwargs):
        captured.update(kwargs)
        return 0, {
            "schema_version": "1.0",
            "status": "completed",
            "run_id": "run-ralph-controller",
            "mode": "ralph",
        }

    monkeypatch.setattr(implement_cmd, "_run_ralph_controller", _fake_ralph_controller)

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.3.7",
            "--mode",
            "ralph",
            "--host-prompt",
            "按冻结需求补齐实现顺序和代码范围",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    prompt_boundary = captured["prompt_boundary"]
    assert isinstance(prompt_boundary, dict)
    assert prompt_boundary["classification"] == "in_scope_implementation"
    assert prompt_boundary["blocked"] is False


def test_ralph_summary_should_surface_v140_three_prd_implementation_order(monkeypatch, tmp_path: Path):
    base = _seed_feature_docs(tmp_path, version="v1.4.0", feature="Beacon v1.4.0 lightweight kernel and core surface refactor")
    docs_root = tmp_path / "docs" / "beacon" / "v1.4.0"
    for feature in (
        "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure",
        "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration",
    ):
        (docs_root / "prd" / f"{feature}.md").write_text("# PRD\n", encoding="utf-8")
        (docs_root / "user-story" / f"{feature}.md").write_text("# User Story\n", encoding="utf-8")
        (docs_root / "qa" / "test-cases" / f"{feature}.md").write_text("# Test Cases\n", encoding="utf-8")
    (docs_root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (docs_root / "execution").mkdir(parents=True, exist_ok=True)
    (docs_root / "execution" / "architecture-blueprint.md").write_text("# Blueprint\n", encoding="utf-8")
    (docs_root / ".machine" / "execution").mkdir(parents=True, exist_ok=True)
    for slug in (
        "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor",
        "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure",
        "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration",
    ):
        (docs_root / ".machine" / "execution" / f"{slug}.revision.json").write_text(
            json.dumps({"feature_slug": slug, "revision_id": "R1", "version": "v1.4.0"}, ensure_ascii=False),
            encoding="utf-8",
        )
    (docs_root / ".machine" / "qa").mkdir(parents=True, exist_ok=True)
    for slug in (
        "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor",
        "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure",
        "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration",
    ):
        (docs_root / ".machine" / "qa" / f"{slug}.ac-test-matrix.json").write_text(
            json.dumps({"entries": []}, ensure_ascii=False),
            encoding="utf-8",
        )
        (docs_root / ".machine" / "qa" / f"{slug}.story-scenario-map.json").write_text(
            json.dumps({"scenarios": []}, ensure_ascii=False),
            encoding="utf-8",
        )
        (docs_root / ".machine" / "qa" / f"{slug}.qa9-matrix.json").write_text(
            json.dumps({"entries": []}, ensure_ascii=False),
            encoding="utf-8",
        )

    def _fake_ralph_controller(**kwargs):
        return 0, {
            "schema_version": "1.0",
            "status": "completed",
            "run_id": "run-ralph-controller",
            "mode": "ralph",
            "implementation_order": {
                "status": "analyzed",
                "feature_count": 3,
                "ordered_feature_slugs": [
                    "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor",
                    "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure",
                    "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration",
                ],
                "waves": [
                    {"wave": 1, "parallelizable": False, "features": [{"feature_slug": "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor"}]},
                    {"wave": 2, "parallelizable": False, "features": [{"feature_slug": "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure"}]},
                    {"wave": 3, "parallelizable": False, "features": [{"feature_slug": "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration"}]},
                ],
            },
        }

    monkeypatch.setattr(implement_cmd, "_run_ralph_controller", _fake_ralph_controller)
    _, payload = implement_cmd._run_ralph_controller(  # type: ignore[attr-defined]
        feature="Beacon v1.4.0 lightweight kernel and core surface refactor",
        project_root=tmp_path,
        version="v1.4.0",
        runner="native-single",
        skill=None,
        task_template=None,
        prompt_boundary=None,
        timeout_sec=None,
        auto_switch_branch=None,
        team_runtime=None,
        host_runtime="codex",
        max_rounds=1,
    )
    assert payload["implementation_order"]["ordered_feature_slugs"] == [
        "beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor",
        "beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure",
        "beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration",
    ]


def test_run_auto_qa_sequence_should_not_follow_handoff_when_disabled(monkeypatch, tmp_path: Path):
    calls: list[str] = []

    def _fake_run_auto_qa(project_root: Path, *, feature: str, version: str, extra_args: list[str]):
        calls.append("qa")
        return 2, {
            "feature_scorecard": {
                "continue_decision": "continue",
                "repair_handoff": {
                    "action": "test-case-create",
                    "command": 'beacon test-case create "My Feature" --project-root /tmp/demo --version v1.1.10',
                },
            }
        }

    def _fake_run_beacon_json_command(project_root: Path, command: str):
        calls.append("handoff")
        return 0, {"status": "generated"}

    monkeypatch.setattr(implement_cmd, "_run_auto_qa", _fake_run_auto_qa)
    monkeypatch.setattr(implement_cmd, "_run_beacon_json_command", _fake_run_beacon_json_command)

    exit_code, payload = implement_cmd._run_auto_qa_sequence(  # type: ignore[attr-defined]
        tmp_path,
        feature="My Feature",
        version="v1.1.10",
        extra_args=[],
        follow_handoff=False,
        max_rounds=3,
    )
    assert exit_code == 2
    assert payload["follow_handoff"] is False
    assert calls == ["qa"]


def test_ralph_controller_should_keep_qa_single_round_and_write_round_artifact(monkeypatch, tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.3.2", feature="My Feature")
    calls: list[tuple[str, str]] = []
    call_count = {"count": 0}

    def _fake_run_implement_stage(**kwargs):
        call_count["count"] += 1
        calls.append(("implement", kwargs["feature"]))
        assert kwargs["mode"] == "single"
        assert kwargs["auto_qa"] is True
        assert kwargs["auto_qa_follow_handoff"] is False
        assert kwargs["auto_qa_max_rounds"] == 1
        return 0, {
            "run_id": kwargs["run_id_override"],
            "status": "completed",
            "summary": "runner finished",
            "summary_paths": {"json": "docs/beacon/v1.3.2/.machine/execution/implementation-summary-my-feature.json"},
            "review_quality": {
                "exit_code": 0,
                "payload": {"gate_ready": False},
                "paths": {"json": "docs/beacon/v1.3.2/execution/review-quality-my-feature.json"},
            },
            "auto_qa": {
                "enabled": True,
                "triggered": True,
                "follow_handoff": False,
                "max_rounds": 1,
                "exit_code": 2,
                "payload": {
                    "feature_scorecard_path": ".beacon/qa/features/my-feature/scorecard.json",
                    "feature_scorecard": {
                        "continue_decision": "stop_for_repair",
                        "repair_handoff": {
                            "action": "implement" if call_count["count"] == 1 else "human_review",
                            "command": (
                                'beacon implement run "My Feature" --project /tmp/demo --version v1.3.2 --runner native-single'
                                if call_count["count"] == 1
                                else "manual review required"
                            ),
                            "reason": "fix blocker" if call_count["count"] == 1 else "needs human review",
                        },
                    },
                },
                "history": [
                    {
                        "step": "qa-run",
                        "round": 1,
                        "exit_code": 2,
                    }
                ],
            },
        }

    monkeypatch.setattr(implement_cmd, "run_implement_stage", _fake_run_implement_stage)
    monkeypatch.setattr(implement_cmd, "_run_gate_release_command", lambda *args, **kwargs: (0, {"status": "pass"}))
    monkeypatch.setattr(implement_cmd, "refresh_evidence_manifest", lambda *args, **kwargs: None)

    exit_code, payload = implement_cmd._run_ralph_controller(  # type: ignore[attr-defined]
        feature="My Feature",
        project_root=tmp_path,
        version="v1.3.2",
        runner="native-single",
        skill=None,
        task_template=None,
        prompt_boundary=None,
        timeout_sec=None,
        auto_switch_branch=None,
        team_runtime=None,
        host_runtime="codex",
        max_rounds=3,
    )

    assert exit_code == 0
    assert len(calls) == 2
    ralph = payload["ralph"]
    assert ralph["round_count"] == 2
    assert ralph["next_action"] == "human_review"
    assert ralph["current_blocker"] == "needs human review"
    assert ralph["last_round_ref"].endswith("ralph-round-my-feature-round-002.json")
    assert (tmp_path / ralph["last_round_ref"]).exists()
    assert (tmp_path / "docs/beacon/v1.3.2/.machine/trace/ralph/my-feature/ralph-round-my-feature-round-001.md").exists()
    assert (tmp_path / "docs/beacon/v1.3.2/.machine/trace/ralph/my-feature/ralph-round-my-feature-round-002.md").exists()
    round_one = json.loads((tmp_path / "docs/beacon/v1.3.2/.machine/trace/ralph/my-feature/ralph-round-my-feature-round-001.json").read_text())
    round_two = json.loads((tmp_path / "docs/beacon/v1.3.2/.machine/trace/ralph/my-feature/ralph-round-my-feature-round-002.json").read_text())
    assert round_one["auto_qa"]["max_rounds"] == 1
    assert round_two["auto_qa"]["max_rounds"] == 1


def test_ralph_controller_should_forward_prompt_boundary_to_child_runs(monkeypatch, tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.3.2", feature="My Feature")
    captured: list[dict[str, object]] = []

    def _fake_run_implement_stage(**kwargs):
        captured.append(kwargs)
        return 0, {
            "run_id": kwargs["run_id_override"],
            "status": "handoff_required",
            "request_markdown": ".beacon/implement/run-ralph/request.md",
        }

    monkeypatch.setattr(implement_cmd, "run_implement_stage", _fake_run_implement_stage)
    monkeypatch.setattr(implement_cmd, "refresh_evidence_manifest", lambda *args, **kwargs: None)

    _, payload = implement_cmd._run_ralph_controller(  # type: ignore[attr-defined]
        feature="My Feature",
        project_root=tmp_path,
        version="v1.3.2",
        runner="native-single",
        skill=None,
        task_template=None,
        prompt_boundary={
            "classification": "clarification_within_scope",
            "blocked": False,
            "prompt": "按冻结需求继续实现",
        },
        timeout_sec=None,
        auto_switch_branch=None,
        team_runtime=None,
        host_runtime="codex",
        max_rounds=1,
    )

    assert len(captured) == 1
    assert captured[0]["prompt_boundary"]["classification"] == "clarification_within_scope"
    assert payload["prompt_boundary"]["classification"] == "clarification_within_scope"


def test_implement_v1312_should_default_prompt_boundary_and_semantic_layer_from_runtime_context(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path, version="v1.3.12", feature="My Feature")

    prompt_boundary = evaluate_implement_prompt_boundary(
        tmp_path,
        version="v1.3.12",
        feature="My Feature",
        host_prompt="",
    )
    semantic_layer = load_or_build_semantic_layer(
        tmp_path,
        version="v1.3.12",
        feature="My Feature",
        stage="implement",
        persist=False,
    )

    assert prompt_boundary["required"] is True
    assert prompt_boundary["status"] == "not_provided"
    assert prompt_boundary["blocked"] is False
    assert semantic_layer["artifacts"]["semantic_contract"]
    assert semantic_layer["artifacts"]["semantic_dictionary"]
    assert semantic_layer["artifacts"]["semantic_usage_guidelines"]
    assert semantic_layer["artifacts"]["semantic_review"]
    assert semantic_layer["official_language"]["page_names"]


def test_ralph_controller_should_ignore_text_completion_without_structured_qa_release(monkeypatch, tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.3.2", feature="My Feature")
    calls = {"count": 0}

    def _fake_run_implement_stage(**kwargs):
        calls["count"] += 1
        return 0, {
            "run_id": kwargs["run_id_override"],
            "status": "completed",
            "completed": True,
            "summary": "Task complete. All work is done. Ready for release.",
            "review_quality": {
                "exit_code": 0,
                "payload": {"gate_ready": False},
                "paths": {"json": "docs/beacon/v1.3.2/execution/review-quality-my-feature.json"},
            },
            "auto_qa": {
                "enabled": True,
                "triggered": True,
                "follow_handoff": False,
                "max_rounds": 1,
                "exit_code": 2,
                "payload": {
                    "feature_scorecard_path": ".beacon/qa/features/my-feature/scorecard.json",
                    "feature_scorecard": {
                        "continue_decision": "stop_for_repair",
                        "repair_handoff": {
                            "action": "human_review",
                            "command": "manual review required",
                            "reason": "qa still blocked",
                        },
                    },
                },
                "history": [{"step": "qa-run", "round": 1, "exit_code": 2}],
            },
        }

    monkeypatch.setattr(implement_cmd, "run_implement_stage", _fake_run_implement_stage)
    monkeypatch.setattr(implement_cmd, "refresh_evidence_manifest", lambda *args, **kwargs: None)

    _, payload = implement_cmd._run_ralph_controller(  # type: ignore[attr-defined]
        feature="My Feature",
        project_root=tmp_path,
        version="v1.3.2",
        runner="native-single",
        skill=None,
        task_template=None,
        prompt_boundary=None,
        timeout_sec=None,
        auto_switch_branch=None,
        team_runtime=None,
        host_runtime="codex",
        max_rounds=3,
    )

    assert calls["count"] == 1
    ralph = payload["ralph"]
    assert ralph["stop_state"] == "human_blocked"
    assert ralph["next_action"] == "human_review"
    assert ralph["current_blocker"] == "qa still blocked"
    assert ralph["rounds"][0]["continue_decision"] == "stop_for_repair"
    assert ralph["rounds"][0].get("status") != "exit_detector_triggered"


def test_ralph_controller_should_surface_requirement_completeness_handoff_when_qa_blocks_before_scorecard(monkeypatch, tmp_path: Path):
    _seed_feature_docs(tmp_path, version="v1.3.12", feature="My Feature")

    def _fake_run_implement_stage(**kwargs):
        return 0, {
            "run_id": kwargs["run_id_override"],
            "status": "completed",
            "summary": "runner finished",
            "review_quality": {
                "exit_code": 0,
                "payload": {"gate_ready": False},
                "paths": {"json": "docs/beacon/v1.3.12/execution/review-quality-my-feature.json"},
            },
            "auto_qa": {
                "enabled": True,
                "triggered": True,
                "follow_handoff": False,
                "max_rounds": 1,
                "exit_code": 2,
                "payload": {
                    "status": "blocked",
                    "reason_codes": ["requirement_completeness_blocked"],
                    "requirement_completeness_gate": {
                        "status": "blocked",
                        "blocked": True,
                        "reason_code": "requirement_completeness_blocked",
                        "recommended_command": "beacon-change",
                        "human_loop_handoff": {
                            "action": "human_review",
                            "recommended_command": "beacon-change",
                        },
                    },
                },
                "history": [{"step": "qa-run", "round": 1, "exit_code": 2}],
            },
        }

    monkeypatch.setattr(implement_cmd, "run_implement_stage", _fake_run_implement_stage)
    monkeypatch.setattr(implement_cmd, "refresh_evidence_manifest", lambda *args, **kwargs: None)

    _, payload = implement_cmd._run_ralph_controller(  # type: ignore[attr-defined]
        feature="My Feature",
        project_root=tmp_path,
        version="v1.3.12",
        runner="native-single",
        skill=None,
        task_template=None,
        prompt_boundary=None,
        timeout_sec=None,
        auto_switch_branch=None,
        team_runtime=None,
        host_runtime="codex",
        max_rounds=3,
    )

    ralph = payload["ralph"]
    assert ralph["stop_state"] == "human_blocked"
    assert ralph["next_action"] == "human_review"
    assert ralph["current_blocker"] == "requirement_completeness_blocked"
    assert ralph["recommended_command"] == "beacon-change"


def test_implement_run_should_fail_when_runner_times_out(tmp_path: Path):
    _seed_feature_docs(tmp_path, feature="My Feature")
    script = tmp_path / "runner.py"
    script.write_text(
        (
            "import time\n"
            "time.sleep(2)\n"
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
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "implement",
            "run",
            "My Feature",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.1.4",
            "--runner",
            "fake",
            "--timeout-sec",
            "1",
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "runner_execution_timeout"
