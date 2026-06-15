from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.revision_state import freeze_revision_state, reopen_revision_state
from beacon.utils.story_state import freeze_story_state, reopen_story_state

VERSION = "v1.4.7"
FEATURE = "feature refreeze"
SLUG = "feature-refreeze"

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


def _seed_docs(root: Path, *, include_test_case: bool = True) -> None:
    _init_git_repo(root)
    docs = root / "docs" / "beacon" / VERSION
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (docs / "change").mkdir(parents=True, exist_ok=True)
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (docs / "execution").mkdir(parents=True, exist_ok=True)
    (docs / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (docs / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (docs / "change" / f"{SLUG}.md").write_text("# Change\n- reason: refreeze\n", encoding="utf-8")
    (docs / "prd" / f"{SLUG}.md").write_text(
        "# PRD\n\n## Acceptance\n- AC-001 Refreeze preserves the full truth chain.\n",
        encoding="utf-8",
    )
    (docs / "user-story" / f"{SLUG}.md").write_text(
        "# User Story\n\n## Story\nAs an operator, I want refreeze.\n\n## Acceptance Criteria\n- AC-001 Refreeze preserves the full truth chain.\n",
        encoding="utf-8",
    )
    if include_test_case:
        (docs / "qa" / "test-cases" / f"{SLUG}.md").write_text(
            "# Test Cases\n\n| AC ID | TC ID | Layer | Command | Assertion |\n| --- | --- | --- | --- | --- |\n| AC-001 | TC-US001-001 | contract | pytest | refreeze preserves chain |\n",
            encoding="utf-8",
        )
    freeze_revision_state(root, version=VERSION, feature=FEATURE)
    freeze_story_state(root, VERSION, FEATURE)


def _seed_feature_package_docs(root: Path, *, version: str = "v0.0.1") -> None:
    _init_git_repo(root)
    slug = "feature-package-refreeze"
    feature_dir = root / "docs" / "beacon" / version / "features" / slug
    (root / "docs" / "beacon").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (root / "docs" / "beacon" / version / "SUMMARY.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / version / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (root / "docs" / "beacon" / version / "execution").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / version / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    feature_dir.mkdir(parents=True, exist_ok=True)
    (feature_dir / "truth.md").write_text(
        "\n".join(
            [
                "---",
                f"slug: {slug}",
                f"version: {version}",
                "status: frozen",
                "language: zh",
                "canonical_refs:",
                f"  prd: docs/beacon/{version}/features/{slug}/truth.md",
                f"  user_story: docs/beacon/{version}/features/{slug}/truth.md",
                f"  test_case: docs/beacon/{version}/features/{slug}/tests.md",
                "parser_contract: beacon-feature-package-v1",
                "truth_source_model: feature_package_authoritative",
                "---",
                "",
                "# Feature Truth",
                "",
                "## Acceptance Criteria",
                "",
                "| AC ID | Theme | Description |",
                "|---|---|---|",
                "| AC-001 | package-refreeze | Package truth refreezes without legacy mirrors. |",
            ]
        ),
        encoding="utf-8",
    )
    (feature_dir / "tests.md").write_text(
        "\n".join(
            [
                "# Tests",
                "",
                "| AC ID | TC ID | Layer | Command | Assertion |",
                "|---|---|---|---|---|",
                "| AC-001 | TC-001 | contract | `pytest` | package refreeze does not require legacy triptych |",
            ]
        ),
        encoding="utf-8",
    )
    (feature_dir / "tasks.md").write_text("# Tasks\n\n- [x] `TASK-001` Package refreeze proof\n", encoding="utf-8")
    (feature_dir / "evidence.md").write_text(
        "\n".join(
            [
                "# Evidence",
                "",
                "| Surface | Authority | Path | Status | Owner |",
                "|---|---|---|---|---|",
                f"| feature-package | requirement_truth | docs/beacon/{version}/features/{slug}/truth.md | frozen | change |",
            ]
        ),
        encoding="utf-8",
    )
    freeze_revision_state(root, version=version, feature="feature package refreeze")
    freeze_story_state(root, version, "feature package refreeze")


def test_change_refreeze_entry_is_support_only(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    result = _invoke(
        [
            "change",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--reason",
            "accepted truth change",
            "--refreeze-chain",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["refreeze_status"] == "complete"
    assert payload["next_route"]["target_surface"] == "beacon-implement"
    assert payload["delivery_execution"] == {
        "implement_executed": False,
        "qa_executed": False,
        "release_executed": False,
    }


def test_refreeze_chain_declares_required_truth_surfaces(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    result = _invoke(["change", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--refreeze-chain", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["touched_surfaces"] == [
        "change",
        "prd",
        "user-story",
        "test-case",
        "requirement_clarity",
        "freeze",
    ]


def test_refreeze_transaction_records_surface_statuses(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    result = _invoke(["change", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--refreeze-chain", "--json"])
    payload = json.loads(result.stdout)
    assert set(payload["surface_statuses"]) == {
        "change",
        "prd",
        "user-story",
        "test-case",
        "requirement_clarity",
        "freeze",
    }
    assert all(payload["surface_statuses"][surface]["status"] == "present" for surface in ["change", "prd", "user-story", "test-case"])
    assert payload["surface_statuses"]["requirement_clarity"]["status"] == "passed"
    assert payload["surface_statuses"]["freeze"]["status"] == "complete"
    assert payload["truth_revision_before"]["revision_id"] == "R1"
    assert payload["truth_revision_after"]["revision_id"] == "R2"
    assert payload["artifacts"]["machine_path"].endswith(f"{SLUG}.refreeze-transaction.json")
    assert payload["artifacts"]["human_path"].endswith(f"{SLUG}.refreeze-summary.md")


def test_refreeze_chain_closes_existing_reopened_revision(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    reopen_revision_state(tmp_path, version=VERSION, feature=FEATURE, reason="accepted change")
    reopen_story_state(tmp_path, VERSION, FEATURE, reason="accepted change")

    result = _invoke(["change", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--refreeze-chain", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["truth_revision_before"]["revision_id"] == "R2"
    assert payload["truth_revision_before"]["doc_status"] == "draft"
    assert payload["truth_revision_after"]["revision_id"] == "R2"
    assert payload["truth_revision_after"]["doc_status"] == "frozen"
    assert payload["next_route"]["target_surface"] == "beacon-implement"


def test_partial_truth_refresh_fail_closes(tmp_path: Path) -> None:
    _seed_docs(tmp_path, include_test_case=False)
    result = _invoke(["change", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--refreeze-chain", "--json"])
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["refreeze_status"] == "blocked"
    assert payload["blocked_reason"] == "missing_requirement_surfaces"
    assert payload["missing_surfaces"] == ["test-case"]
    assert payload["next_route"]["target_surface"] == "beacon-change"


def test_feature_package_refreeze_uses_package_surfaces_for_project_docs_version(tmp_path: Path) -> None:
    version = "v0.0.1"
    feature = "feature package refreeze"
    _seed_feature_package_docs(tmp_path, version=version)
    result = _invoke(["change", feature, "--project", str(tmp_path), "--version", version, "--refreeze-chain", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["refreeze_status"] == "complete"
    assert payload["touched_surfaces"] == [
        "change",
        "truth",
        "tests",
        "tasks",
        "evidence",
        "requirement_clarity",
        "freeze",
        "feature_package_validation",
    ]
    assert "prd" not in payload["surface_statuses"]
    assert "user-story" not in payload["surface_statuses"]
    assert "test-case" not in payload["surface_statuses"]


def test_execution_routes_block_until_refreeze_complete(tmp_path: Path) -> None:
    _seed_docs(tmp_path, include_test_case=False)
    result = _invoke(["change", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--refreeze-chain", "--json"])
    payload = json.loads(result.stdout)
    assert payload["refreeze_status"] == "blocked"
    assert payload["next_route"]["target_surface"] != "beacon-implement"


def test_human_summary_explains_chain_state(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    result = _invoke(["change", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--refreeze-chain", "--json"])
    payload = json.loads(result.stdout)
    summary = tmp_path / payload["artifacts"]["human_path"]
    text = summary.read_text(encoding="utf-8")
    assert "Surface Statuses" in text
    assert "refreeze_status: `complete`" in text
    assert "Partial refresh keeps the feature blocked." in text


def test_one_shot_refreeze_does_not_execute_delivery_stages(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    result = _invoke(["change", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--refreeze-chain", "--json"])
    payload = json.loads(result.stdout)
    assert payload["delivery_execution"]["implement_executed"] is False
    assert payload["delivery_execution"]["qa_executed"] is False
    assert payload["delivery_execution"]["release_executed"] is False


def test_change_skill_exposes_one_shot_refreeze_operator_route() -> None:
    root = Path(__file__).resolve().parents[1]
    for path in [
        root / "skills" / "beacon" / "beacon-gen-refreeze" / "SKILL.md",
        root / ".agents" / "skills" / "beacon-gen-refreeze" / "SKILL.md",
    ]:
        text = path.read_text(encoding="utf-8")
        assert "`beacon change ... --refreeze-chain`" in text
        assert "change -> prd -> user-story -> test-case -> requirement_clarity -> freeze" in text
