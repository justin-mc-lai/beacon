from __future__ import annotations

import json
import importlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.commands.qa import _qa_design_truth_verdict
from beacon.utils.requirement_clarity import build_requirement_clarity_gate_payload


runner = CliRunner()
VERSION = "v1.4.9"
FEATURE = "ui-ux-externalization-prototype-adapter-and-version-visualization-contract"
SLUG = "ui-ux-externalization-prototype-adapter-and-version-visualization-contract"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_requirement_docs(root: Path, *, design_binding_required: bool = False, research_truth_bindings: bool = True) -> None:
    binding_line = "design_result_binding_required: true\n" if design_binding_required else ""
    _write(root, "docs/beacon/global-boundaries.md", "# Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# Summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# Execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# Architecture\n")
    _write(root, f"docs/beacon/{VERSION}/source-architecture/index.md", "# Source Architecture\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        (
            "# PRD\n\n"
            f"{binding_line}"
            "## 1. Diagram Truth Layer\n\n"
            "### 1.1 Diagram Types\n"
            "- `branch-flow`\n"
            "- `state-machine`\n"
            "- `decision-priority`\n\n"
            "### 1.2 State Axes\n"
            "- `ui_ux_route`\n"
            "- `adapter_binding`\n\n"
            "## Functional Requirements\n\n"
            "| FR ID | Related AC | Requirement |\n"
            "| --- | --- | --- |\n"
            "| FR-001 | AC-001 | Route UI/UX execution externally. |\n"
            "| FR-002 | AC-002 | Bind accepted design results before implementation. |\n"
        ),
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        (
            "# User Story\n\n"
            "## Acceptance Criteria\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | routing | UI/UX execution routes to ui-ux-dev. |\n"
            "| AC-002 | adapter | Accepted design result is bound to truth. |\n"
        ),
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        (
            "# Test Cases\n\n"
            "## Coverage Matrix\n\n"
            "| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| AC-001 | TC-001 | contract | pytest -q | UI/UX execution routes externally. | .beacon/evidence/tc-001.json |\n"
            "| AC-002 | TC-002 | gate | pytest -q | Missing adapter binding blocks implement. | .beacon/evidence/tc-002.json |\n"
        ),
    )
    truth_binding_block = (
        "Truth bindings:\n\n"
        f"- `prd_refs`: `docs/beacon/{VERSION}/prd/{SLUG}.md`\n"
        f"- `user_story_refs`: `docs/beacon/{VERSION}/user-story/{SLUG}.md`\n"
        f"- `test_case_refs`: `docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md`\n"
        "- `coverage_notes`: AC-001 through AC-002 are covered in the test-case matrix.\n"
        "- `out_of_scope_notes`: projections are not canonical truth.\n"
    ) if research_truth_bindings else ""
    _write(
        root,
        f"docs/beacon/{VERSION}/research/{SLUG}.md",
        (
            "# Research Closure\n\n"
            "## Architecture\n\n"
            "- Beacon governs requirement truth; ui-ux-dev owns UI/UX execution.\n\n"
            "## Business Flow\n\n"
            "- Human accepts UI/UX output, then Beacon binds it to requirement truth.\n\n"
            "## State Machine\n\n"
            "- ui_ux_external_route -> design_result_accepted -> adapter_binding_ready -> implement_ready.\n\n"
            "## PRD / User Story / Test Case Map\n\n"
            "- PRD owns promise, story owns acceptance, test-case owns verification.\n\n"
            f"{truth_binding_block}\n"
            "## Decision Priority\n\n"
            "- Markdown truth beats projection.\n"
        ),
    )


def test_v149_prototype_create_should_route_to_ui_ux_dev_not_generate(tmp_path: Path) -> None:
    _seed_requirement_docs(tmp_path)

    result = _invoke(["prototype", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "prototype_generation_externalized"
    assert payload["ui_ux_execution_owner"] == "ui-ux-dev"
    assert "ui-ux-dev-review" in payload["recommended_command"]
    assert not (tmp_path / f"docs/beacon/{VERSION}/prototype/{SLUG}/wireframe-summary.md").exists()


def test_v149_prototype_adapt_should_write_truth_binding(tmp_path: Path) -> None:
    _seed_requirement_docs(tmp_path, design_binding_required=True)

    result = _invoke(
        [
            "prototype",
            "adapt",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--design-result-ref",
            "docs/ui-ux-dev/accepted.md",
            "--accepted-by",
            "codex-test",
            "--summary",
            "accepted operator console design",
            "--screen-intent",
            "operator reviews version closure",
            "--state-visibility",
            "adapter_binding_ready is visible",
            "--interaction-handoff",
            "implementation follows accepted handoff only",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "ready"
    assert payload["adapter_role"] == "design-result-adapter"
    binding_path = tmp_path / payload["paths"]["binding_json"]
    markdown_path = tmp_path / payload["paths"]["binding_md"]
    assert binding_path.exists()
    assert markdown_path.exists()
    assert payload["truth_bindings"]["prd_refs"] == f"docs/beacon/{VERSION}/prd/{SLUG}.md"
    assert payload["truth_bindings"]["user_story_refs"] == f"docs/beacon/{VERSION}/user-story/{SLUG}.md"
    assert payload["truth_bindings"]["test_case_refs"] == f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md"


def test_v149_implement_should_block_when_required_adapter_binding_missing(tmp_path: Path, monkeypatch) -> None:
    implement_module = importlib.import_module("beacon.commands.implement")._legacy_cli

    _seed_requirement_docs(tmp_path, design_binding_required=True)
    monkeypatch.setattr(implement_module, "build_requirement_package_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(implement_module, "_requirement_closure_preflight", lambda *_args, **_kwargs: {"blocked": False, "status": "pass"})
    monkeypatch.setattr(implement_module, "_automation_runtime_preflight", lambda *_args, **_kwargs: {"blocked": False, "status": "pass"})
    monkeypatch.setattr(implement_module, "evaluate_takeover_baseline_gate", lambda *_args, **_kwargs: {"status": "pass"})
    monkeypatch.setattr(implement_module, "_run_branch_preflight", lambda **_kwargs: {"blocked": False, "current_branch": "beacon/v1.4.9"})
    monkeypatch.setattr(implement_module, "implementation_plan_supported", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(implement_module, "resolve_adapter", lambda *_args, **_kwargs: ("fake", {"adapter_type": "command", "command": "true", "args": []}))
    monkeypatch.setattr(implement_module, "detect_adapter", lambda *_args, **_kwargs: (True, []))

    code, payload = implement_module.run_implement_stage(
        feature=FEATURE,
        project_root=tmp_path,
        version=VERSION,
        runner="fake",
        mode="single",
    )

    assert code == 2
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "design_result_adapter_binding_missing"
    assert payload["design_truth"]["source_surface"] == "prototype-adapter"
    assert "prototype adapt" in payload["recommended_command"]


def test_v149_qa_should_skip_optional_adapter_binding_when_not_applicable(tmp_path: Path) -> None:
    _seed_requirement_docs(tmp_path)

    verdict = _qa_design_truth_verdict(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        handoff={
            "design_truth": {
                "status": "not_applicable",
                "source_surface": "prototype-adapter",
                "mode": "design-result-adapter",
                "required": False,
                "refs": {},
            }
        },
    )

    assert verdict["status"] == "not_applicable"
    assert verdict["blocked"] is False
    assert verdict["reason_codes"] == []


def test_v149_requirement_clarity_should_block_projection_without_truth_bindings(tmp_path: Path) -> None:
    _seed_requirement_docs(tmp_path, research_truth_bindings=False)

    payload = build_requirement_clarity_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["blocked"] is True
    kinds = {item["kind"] for item in payload["findings"]}
    assert "version_projection_truth_binding_missing" in kinds
    contract = payload["version_projection_truth_contract"]
    assert contract["required"] is True
    assert "prd_refs" in contract["missing_fields"]


def test_v149_design_review_should_route_ready_verdict_to_ui_ux_dev(tmp_path: Path) -> None:
    _seed_requirement_docs(tmp_path)
    marker = "ui_visualization_required: true\nprototype_freeze_required: true\n"
    for rel in (
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
    ):
        path = tmp_path / rel
        path.write_text(marker + path.read_text(encoding="utf-8"), encoding="utf-8")

    result = _invoke(["review", "design", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    txn = payload["support_surface_transaction"]
    assert txn["decision"] == "ready_for_prototype"
    assert txn["next_route"]["target_surface"] == "ui-ux-dev"
    assert "ui-ux-dev-review" in txn["next_route"]["command"]
    assert "prototype adapt" in txn["next_route"]["writeback_command"]
