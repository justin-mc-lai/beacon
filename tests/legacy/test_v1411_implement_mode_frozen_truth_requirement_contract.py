from __future__ import annotations

from pathlib import Path

from beacon.utils.implement_adapters import build_default_task_prompt


FEATURE = "Implement Mode Frozen Truth Requirement Contract"
VERSION = "v1.4.11"
SLUG = "implement-mode-frozen-truth-requirement-contract"


def _prompt(project_root: Path) -> str:
    return build_default_task_prompt(
        feature=FEATURE,
        version=VERSION,
        project_root=project_root,
        source_of_truth_root=f"docs/beacon/{VERSION}",
        feature_slug=SLUG,
        result_file=".beacon/implement/run-001/result.json",
    )


def test_design_truth_injected_when_present(tmp_path: Path) -> None:
    (tmp_path / "DESIGN.md").write_text("# Design Truth\n", encoding="utf-8")

    prompt = _prompt(tmp_path)

    assert "- DESIGN.md (project-level design truth)" in prompt
    assert "Read project-level product/design truth when present:" in prompt


def test_product_truth_injected_when_present(tmp_path: Path) -> None:
    (tmp_path / "PRODUCT.md").write_text("# Product Truth\n", encoding="utf-8")

    prompt = _prompt(tmp_path)

    assert "- PRODUCT.md (project-level product truth)" in prompt
    assert "Read project-level product/design truth when present:" in prompt


def test_missing_project_truth_does_not_block(tmp_path: Path) -> None:
    prompt = _prompt(tmp_path)

    assert "Implement the scoped Beacon feature." in prompt
    assert "Read project-level product/design truth when present:" not in prompt
    assert f"docs/beacon/{VERSION}/prd/{SLUG}.md" in prompt


def test_project_truth_separated_from_frozen_truth(tmp_path: Path) -> None:
    (tmp_path / "PRODUCT.md").write_text("# Product Truth\n", encoding="utf-8")
    (tmp_path / "DESIGN.md").write_text("# Design Truth\n", encoding="utf-8")

    prompt = _prompt(tmp_path)

    frozen_index = prompt.index("Read Beacon source of truth:")
    project_index = prompt.index("Read project-level product/design truth when present:")
    assert frozen_index < project_index
    assert "Project-level truth complements frozen requirement truth" in prompt
    assert "it does not replace PRD, user-story, or test-case truth" in prompt


def test_ac_coverage_matrix_required(tmp_path: Path) -> None:
    prompt = _prompt(tmp_path)

    assert "ac_coverage_matrix" in prompt
    assert "Before QA handoff, AC coverage matrix must list every frozen AC" in prompt


def test_ac_coverage_statuses_required(tmp_path: Path) -> None:
    prompt = _prompt(tmp_path)

    assert "status pass | partial | blocked" in prompt


def test_ac_coverage_evidence_required(tmp_path: Path) -> None:
    prompt = _prompt(tmp_path)

    assert "evidence or blocking_note" in prompt


def test_no_new_public_implement_mode_skill() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    assert not (repo_root / "skills/beacon/beacon-implement-simple").exists()
    assert not (repo_root / "skills/beacon/beacon-implement-team").exists()
    assert not (repo_root / "skills/beacon/beacon-implement-ralph").exists()


def test_scope_stays_default_prompt_only(tmp_path: Path) -> None:
    prompt = _prompt(tmp_path)

    assert "team-worker" not in prompt.lower()
    assert "ralph baseline hash" not in prompt.lower()
