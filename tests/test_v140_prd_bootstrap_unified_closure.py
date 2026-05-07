from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path) -> Path:
    base = root / "docs" / "beacon" / "v1.4.0"
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text("# v1.4.0\n", encoding="utf-8")
    return base


def test_v140_prd_bootstrap_empty_package_should_emit_draft_generated_verdict(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Unified Closure",
            "--desc",
            "补齐 requirement package 并判断是否可以进入待实现",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--skip-context-verify",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["package_state"] == "empty"
    assert payload["closure_verdict"] == "draft_generated"
    assert payload["readiness_verdict"] == "supplement_required"
    assert payload["generated_layers"] == ["prd", "user_story", "test_case"]
    assert (tmp_path / payload["state_path"]).exists()


def test_v140_prd_bootstrap_prd_only_should_fill_missing_layers_and_be_ready(tmp_path: Path) -> None:
    base = _seed_docs(tmp_path)
    (base / "prd" / "unified-closure.md").write_text(
        (
            "# PRD: Unified Closure\n\n"
            "## 1. Overview\n\n"
            "- version: `v1.4.0`\n"
            "- feature: `Unified Closure`\n"
            "- status: `draft`\n"
            "- 需求描述: 补齐 requirement package 并判断是否可以进入待实现\n\n"
            "## 2. Scope\n\n"
            "- In scope: 需求闭环补齐。\n"
            "- Out of scope: 无关重构。\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Unified Closure",
            "--desc",
            "补齐 requirement package 并判断是否可以进入待实现",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--skip-context-verify",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["package_state"] == "prd_only"
    assert payload["missing_layers"] == ["user_story", "test_case"]
    assert payload["generated_layers"] == ["user_story", "test_case"]
    assert payload["reverse_derived_layers"] == []
    assert payload["closure_verdict"] == "freeze_ready"
    assert payload["readiness_verdict"] == "implementation_pending"
    assert payload["closure_analysis"]["ok"] is True


def test_v140_prd_bootstrap_prd_only_with_incomplete_truth_should_require_supplement(tmp_path: Path) -> None:
    base = _seed_docs(tmp_path)
    (base / "prd" / "unified-closure.md").write_text(
        (
            "# PRD: Unified Closure\n\n"
            "- version: `v1.4.0`\n"
            "- feature: `Unified Closure`\n"
            "- status: `draft`\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Unified Closure",
            "--desc",
            "补齐 requirement package 并判断是否可以进入待实现",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--skip-context-verify",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["package_state"] == "prd_only"
    assert payload["closure_verdict"] == "supplement_required"
    assert payload["readiness_verdict"] == "supplement_required"
    assert "goal_defined" in payload["closure_analysis"]["missing_evidence"]
    assert "scope_defined" in payload["closure_analysis"]["missing_evidence"]


def test_v140_prd_bootstrap_user_story_only_should_mark_reverse_derived_truth(tmp_path: Path) -> None:
    base = _seed_docs(tmp_path)
    (base / "user-story" / "unified-closure.md").write_text(
        (
            "# User Story: Unified Closure\n\n"
            "## Acceptance Criteria\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | happy-path | 系统可以完成补齐。 |\n\n"
            "## Metadata\n\n"
            "- version: `v1.4.0`\n"
            "- feature: `Unified Closure`\n"
            "- status: `draft`\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Unified Closure",
            "--desc",
            "补齐 requirement package 并判断是否可以进入待实现",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--skip-context-verify",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["package_state"] == "user_story_only"
    assert payload["reverse_derived_layers"]
    assert payload["reverse_derived_layers"][0]["layer"] == "prd"
    assert payload["closure_verdict"] == "supplement_required"
    assert payload["readiness_verdict"] == "supplement_required"
    assert payload["supplement_tasks"]


def test_v140_prd_bootstrap_full_inconsistent_should_block_with_drift_digest(tmp_path: Path) -> None:
    base = _seed_docs(tmp_path)
    (base / "prd" / "unified-closure.md").write_text("# PRD: Unified Closure\n", encoding="utf-8")
    (base / "user-story" / "unified-closure.md").write_text(
        (
            "# User Story: Unified Closure\n\n"
            "## Acceptance Criteria\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | happy-path | A |\n"
        ),
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / "unified-closure.md").write_text(
        (
            "# Test Cases: Unified Closure\n\n"
            "## Coverage Matrix\n\n"
            "| TC ID | AC ID | Scenario | Layer | Expected |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| TC-001 | AC-002 | mismatch | unit | B |\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Unified Closure",
            "--desc",
            "补齐 requirement package 并判断是否可以进入待实现",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--skip-context-verify",
            "--json",
        ]
    )

    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["package_state"] == "full_inconsistent"
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "truth_drift_detected"
    assert payload["drift_digest"]
    assert payload["readiness_verdict"] == "drift_repair_required"


def test_v140_prd_bootstrap_unit_full_inconsistent_should_expose_beacon_change_repair_route(tmp_path: Path) -> None:
    base = _seed_docs(tmp_path)
    (base / "prd" / "unified-closure.md").write_text("# PRD: Unified Closure\n", encoding="utf-8")
    (base / "user-story" / "unified-closure.md").write_text(
        (
            "# User Story: Unified Closure\n\n"
            "## Acceptance Criteria\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | happy-path | A |\n"
        ),
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / "unified-closure.md").write_text(
        (
            "# Test Cases: Unified Closure\n\n"
            "## Coverage Matrix\n\n"
            "| TC ID | AC ID | Scenario | Layer | Expected |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| TC-001 | AC-002 | mismatch | unit | B |\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Unified Closure",
            "--desc",
            "补齐 requirement package 并判断是否可以进入待实现",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--skip-context-verify",
            "--json",
        ]
    )

    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "truth_drift_detected"
    assert payload["recommended_command"] == "beacon-change"


def test_v140_prd_bootstrap_prd_test_case_should_require_truth_review(tmp_path: Path) -> None:
    base = _seed_docs(tmp_path)
    (base / "prd" / "unified-closure.md").write_text(
        (
            "# PRD: Unified Closure\n\n"
            "## 1. Overview\n\n"
            "- version: `v1.4.0`\n"
            "- feature: `Unified Closure`\n"
            "- status: `draft`\n\n"
            "## 2. Scope\n\n"
            "- In scope: 需求闭环补齐。\n"
        ),
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / "unified-closure.md").write_text(
        (
            "# Test Cases: Unified Closure\n\n"
            "## Coverage Matrix\n\n"
            "| TC ID | AC ID | Scenario | Layer | Expected |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| TC-001 | AC-001 | happy | unit | ok |\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Unified Closure",
            "--desc",
            "补齐 requirement package 并判断是否可以进入待实现",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--skip-context-verify",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["package_state"] == "prd_test_case"
    assert payload["generated_layers"] == ["user_story"]
    assert payload["reverse_derived_layers"][0]["layer"] == "user_story"
    assert payload["closure_verdict"] == "supplement_required"


def test_v140_prd_bootstrap_full_consistent_should_stay_ready(tmp_path: Path) -> None:
    base = _seed_docs(tmp_path)
    (base / "prd" / "unified-closure.md").write_text(
        (
            "# PRD: Unified Closure\n\n"
            "## 1. Overview\n\n"
            "- version: `v1.4.0`\n"
            "- feature: `Unified Closure`\n"
            "- status: `freeze-ready`\n\n"
            "## 2. Scope\n\n"
            "- In scope: 需求闭环补齐。\n"
        ),
        encoding="utf-8",
    )
    (base / "user-story" / "unified-closure.md").write_text(
        (
            "# User Story: Unified Closure\n\n"
            "## Story\n\n"
            "作为用户，我希望补齐 requirement package。\n\n"
            "## Acceptance Criteria\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | happy-path | 系统可以完成补齐。 |\n"
        ),
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / "unified-closure.md").write_text(
        (
            "# Test Cases: Unified Closure\n\n"
            "## Coverage Matrix\n\n"
            "| TC ID | AC ID | Scenario | Layer | Expected |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| TC-001 | AC-001 | happy | unit | ok |\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Unified Closure",
            "--desc",
            "补齐 requirement package 并判断是否可以进入待实现",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--skip-context-verify",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["package_state"] == "full_consistent"
    assert payload["generated_layers"] == []
    assert payload["closure_verdict"] == "freeze_ready"
    assert payload["readiness_verdict"] == "implementation_pending"


def test_v140_test_case_create_should_preserve_explicit_matrix_command_for_repair_route(tmp_path: Path) -> None:
    base = _seed_docs(tmp_path)
    (base / "prd" / "unified-closure.md").write_text(
        (
            "# PRD: Unified Closure\n\n"
            "## 1. Overview\n\n"
            "- version: `v1.4.0`\n"
            "- feature: `Unified Closure`\n"
            "- status: `freeze-ready`\n\n"
            "## 2. Scope\n\n"
            "- In scope: 需求闭环补齐。\n"
        ),
        encoding="utf-8",
    )
    (base / "user-story" / "unified-closure.md").write_text(
        (
            "# User Story: Unified Closure\n\n"
            "## Acceptance Criteria\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-303 | repair-route | 系统必须给出 repair route，而不是静默重写。 |\n"
        ),
        encoding="utf-8",
    )
    (base / "qa" / "test-cases" / "unified-closure.md").write_text(
        (
            "# Test Cases: Unified Closure\n\n"
            "## Executable AC Test Matrix\n\n"
            "| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| AC-303 | TC-015 | unit | `python3 -m pytest -q -k unit --junitxml \"${BEACON_JUNIT_PATH:-.beacon/junit.xml}\"` | 系统必须给出 repair route，而不是静默重写。 | `.beacon/evidence/test-results/unified-closure/TC-015.json` |\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "test-case",
            "create",
            "Unified Closure",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    qa9_matrix = json.loads((tmp_path / payload["qa9_matrix_path"]).read_text(encoding="utf-8"))
    tc_015 = next(item for item in qa9_matrix["entries"] if item["tc_id"] == "TC-015")
    assert tc_015["layer"] == "unit"
    assert tc_015["command"].startswith("python3 -m pytest -q -k unit")


def test_v140_prd_bootstrap_apply_should_write_missing_layers_when_overwrite_allowed(tmp_path: Path) -> None:
    base = _seed_docs(tmp_path)
    (base / "prd" / "unified-closure.md").write_text(
        (
            "# PRD: Unified Closure\n\n"
            "## 1. Overview\n\n"
            "- version: `v1.4.0`\n"
            "- feature: `Unified Closure`\n"
            "- status: `draft`\n\n"
            "## 2. Scope\n\n"
            "- In scope: 需求闭环补齐。\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Unified Closure",
            "--desc",
            "补齐 requirement package 并判断是否可以进入待实现",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--skip-context-verify",
            "--apply",
            "--allow-overwrite",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "applied"
    assert (base / "user-story" / "unified-closure.md").exists()
    assert (base / "qa" / "test-cases" / "unified-closure.md").exists()
    assert payload["write_actions"]
    assert any(action["target"] == "user_story" for action in payload["write_actions"])


def test_v140_prd_bootstrap_human_output_should_show_state_and_verdicts(tmp_path: Path) -> None:
    base = _seed_docs(tmp_path)
    (base / "user-story" / "unified-closure.md").write_text(
        (
            "# User Story: Unified Closure\n\n"
            "## Acceptance Criteria\n\n"
            "| AC ID | Theme | Description |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | happy-path | 系统可以完成补齐。 |\n"
        ),
        encoding="utf-8",
    )

    result = _invoke(
        [
            "prd-bootstrap",
            "run",
            "Unified Closure",
            "--desc",
            "补齐 requirement package 并判断是否可以进入待实现",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.4.0",
            "--skip-context-verify",
        ]
    )

    assert result.exit_code == 0, result.stdout
    assert "package_state" in result.stdout
    assert "closure_verdict" in result.stdout
    assert "readiness_verdict" in result.stdout
    assert "closure_ok" in result.stdout
    assert "reverse_derived" in result.stdout
    assert "next_command" in result.stdout
