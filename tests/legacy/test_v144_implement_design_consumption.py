from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.story_state import freeze_story_state, sync_story_state_from_docs
from beacon.utils.technical_review_contract import materialize_technical_review_contract
from tests.legacy.test_v144_prototype_projection import FEATURE, SLUG, VERSION, _prepare_requirement_package


runner = CliRunner()


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


def _write_runner_script(path: Path) -> None:
    path.write_text(
        (
            "import json, sys, pathlib\n"
            "request_file = pathlib.Path(sys.argv[1])\n"
            "result_file = pathlib.Path(sys.argv[2])\n"
            "payload = json.loads(request_file.read_text())\n"
            "result_file.parent.mkdir(parents=True, exist_ok=True)\n"
            "result_file.write_text(json.dumps({\n"
            "  'schema_version': '1.0',\n"
            "  'run_id': payload['run_id'],\n"
            "  'status': 'completed',\n"
            "  'summary': 'implemented with governed design truth',\n"
            "  'changed_files': ['beacon/commands/implement.py'],\n"
            "  'verification': [{'command': 'pytest -q tests/test_v144_implement_design_consumption.py', 'status': 'passed'}]\n"
            "}, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')\n"
        ),
        encoding="utf-8",
    )


def _write_fake_runner_config(root: Path) -> None:
    (root / "beacon.config.yaml").write_text(
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


def _prepare_implement_ready_requirement_package(root: Path) -> None:
    _init_git_repo(root)
    _prepare_requirement_package(root, design_preset="operator-console")
    prd = (
        f"# PRD: {FEATURE}\n\n"
        "## 1. Overview\n\n"
        f"- version: `{VERSION}`\n"
        f"- feature: `{FEATURE}`\n"
        "- status: `frozen`\n"
        "- design_preset: operator-console\n"
        "- prototype_freeze_required: true\n"
        "- ui_visualization_required: true\n"
        "- target_audience: Product owner and implementation operator\n"
        "- primary_use_cases: freeze UX truth, align implement and qa, review hierarchy\n"
        "- operator_mental_state: needs quick and confident delivery decisions\n"
        "- usage_environment: desktop-first workbench review and handoff\n"
        "- brand_tone: quiet, precise, operational\n"
        "- density_preference: workbench-medium\n\n"
        "## 2. Scope\n\n"
        "- In scope: implement consumes prototype design truth, template preset, and anti-AI interaction baseline.\n"
        "- Out of scope: introducing a new public design command or external runtime dependency.\n\n"
        "## 3. Functional Requirements\n\n"
        "| FR ID | Related AC | Requirement |\n"
        "| --- | --- | --- |\n"
        "| FR-001 | AC-001 | Prototype emits governed template truth for implementation. |\n"
        "| FR-002 | AC-002 | Implement request, summary, and QA handoff consume the same design truth. |\n\n"
        "## 4. Acceptance Traceability\n\n"
        "| AC ID | Theme | Description |\n"
        "| --- | --- | --- |\n"
        "| AC-001 | design-truth | Prototype design assets expose the selected template and anti-AI baseline. |\n"
        "| AC-002 | implement-consumption | Implement consumes the same template and interaction baseline truth. |\n"
    )
    story = (
        f"# User Story: {FEATURE}\n\n"
        "## Story\n\n"
        "As an implementation operator, I want implement to consume prototype design truth so implementation does not reinvent the product surface.\n\n"
        "## Acceptance Criteria\n\n"
        "| AC ID | Theme | Description |\n"
        "| --- | --- | --- |\n"
        "| AC-001 | design-truth | Prototype design assets expose the selected template and anti-AI baseline. |\n"
        "| AC-002 | implement-consumption | Implement consumes the same template and interaction baseline truth. |\n\n"
        "## Metadata\n\n"
        f"- version: `{VERSION}`\n"
        f"- feature: `{FEATURE}`\n"
        "- status: `frozen`\n"
    )
    test_case = (
        f"# Test Cases: {FEATURE}\n\n"
        "## Coverage Matrix\n\n"
        "| TC ID | AC ID | Scenario | Layer | Expected |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| TC-001 | AC-001 | Prototype emits style-preset and design-lint-rules | integration | design truth is available. |\n"
        "| TC-002 | AC-002 | Implement consumes design truth in request, summary, and handoff | integration | same canonical preset and anti-AI contract are present. |\n\n"
        "## Metadata\n\n"
        f"- version: `{VERSION}`\n"
        f"- feature: `{FEATURE}`\n"
        "- status: `frozen`\n"
    )
    for rel, content in (
        (f"docs/beacon/{VERSION}/prd/{SLUG}.md", prd),
        (f"docs/beacon/{VERSION}/user-story/{SLUG}.md", story),
        (f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md", test_case),
    ):
        (root / rel).write_text(content, encoding="utf-8")
    sync_story_state_from_docs(root, VERSION, FEATURE)
    freeze_story_state(root, VERSION, FEATURE)
    sync_story_state_from_docs(root, VERSION, FEATURE)
    for rel in (
        f"docs/beacon/{VERSION}/execution/boundaries.md",
        f"docs/beacon/{VERSION}/execution/project-skill-qa-evolution-blueprint.md",
        f"docs/beacon/{VERSION}/source-architecture/index.md",
        f"docs/beacon/{VERSION}/release/index.md",
    ):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Required Beacon material\n", encoding="utf-8")
    revision_state = freeze_revision_state(root, version=VERSION, feature=FEATURE)
    materialize_technical_review_contract(
        root,
        version=VERSION,
        feature=FEATURE,
        revision_id=str(revision_state.get("revision_id", "R1") or "R1"),
        force_refresh=True,
        contract_overrides={
            "review_status": "approved",
            "approved_by": "Beacon Tests",
        },
        source="test.v144.implement-design-consumption",
    )


def test_v144_implement_consumes_same_design_truth(tmp_path: Path) -> None:
    _prepare_implement_ready_requirement_package(tmp_path)
    create = _invoke(["prototype", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert create.exit_code == 0, create.stdout
    plan = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert plan.exit_code == 0, plan.stdout

    runner_script = tmp_path / "runner.py"
    _write_runner_script(runner_script)
    _write_fake_runner_config(tmp_path)

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
            "fake",
            "--json",
            "--no-auto-review-spec",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["status"] == "completed"
    assert payload["design_truth"]["status"] == "ready"
    assert payload["design_truth"]["design_preset"] == "operator-console"
    assert payload["design_truth"]["canonical_design_preset"] == "operator-console"
    assert payload["design_truth"]["preset_source"] == "vercel"
    assert payload["design_truth"]["anti_ai_ui_contract"]["minimum_touch_target"] == "44x44"
    assert "focus-visible must exist for keyboard users" in payload["design_truth"]["interaction_discipline_rules"]
    assert "design-artifacts/style-preset.json" in payload["design_truth"]["allowed_inputs"]
    assert "design-artifacts/design-lint-rules.json" in payload["design_truth"]["allowed_inputs"]

    request_path = tmp_path / payload["request_path"]
    request_payload = json.loads(request_path.read_text(encoding="utf-8"))
    assert request_payload["design_truth"]["refs"]["style_preset"] == f"docs/beacon/{VERSION}/prototype/{SLUG}/design-artifacts/style-preset.json"
    assert request_payload["design_truth"]["refs"]["design_lint_rules"] == f"docs/beacon/{VERSION}/prototype/{SLUG}/design-artifacts/design-lint-rules.json"
    assert "Reuse Beacon prototype design truth" in request_payload["task_prompt"]
    assert f"docs/beacon/{VERSION}/prototype/{SLUG}/design-artifacts/style-preset.json" in request_payload["task_prompt"]

    summary_path = tmp_path / f"docs/beacon/{VERSION}/.machine/execution/implementation-summary-{SLUG}.json"
    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary_payload["design_truth"]["canonical_design_preset"] == "operator-console"
    assert summary_payload["design_truth"]["refs"]["design_lint_rules"] in summary_payload["traceability_refs"]

    handoff_path = tmp_path / summary_payload["implement_to_qa_handoff"]
    handoff_payload = json.loads(handoff_path.read_text(encoding="utf-8"))
    assert handoff_payload["design_truth"]["canonical_design_preset"] == "operator-console"
    assert handoff_payload["design_truth"]["anti_ai_ui_contract"]["focus_visibility_policy"] == "required"
