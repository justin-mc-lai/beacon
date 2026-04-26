from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v134_real_project_validation_assets_should_surface_canonical_board_pack() -> None:
    script = (
        ROOT
        / "skills"
        / "beacon"
        / "beacon-real-project-validation"
        / "scripts"
        / "run_real_project_board_validation.sh"
    )
    script_text = script.read_text(encoding="utf-8")
    assert "portfolio-board.txt" in script_text
    assert "portfolio-board.json" in script_text
    assert "acceptance-record.md" in script_text
    assert "BEACON_RUNTIME_LEDGER_ROOT" in script_text
    assert 'label|project_root|feature|version' in script_text
    assert "workspace-child-repos" in script_text
    assert "discover_git_scopes" in script_text
    assert "specialized-board-acceptance-only" in script_text
    assert "does not replace current-version real-project release proof" in script_text

    command_matrix = (
        ROOT
        / "skills"
        / "beacon"
        / "beacon-real-project-validation"
        / "references"
        / "command-matrix.md"
    ).read_text(encoding="utf-8")
    assert "portfolio-board.txt" in command_matrix
    assert "projection-determinism.json" in command_matrix
    assert "`label|project_root|feature|version`" in command_matrix
    assert "beacon prototype list -p ROOT -v VERSION" in command_matrix
    assert "beacon archive status -p ROOT -v VERSION --feature FEATURE --json" in command_matrix
    assert "beacon gate check release --project-root ROOT --version VERSION --json" in command_matrix
    assert "ROOT/docs/beacon/VERSION/release/VERSION.md" in command_matrix
    assert "current-version real-project release proof" in command_matrix

    template = (
        ROOT
        / "skills"
        / "beacon"
        / "beacon-real-project-validation"
        / "references"
        / "board-acceptance-record-template.md"
    ).read_text(encoding="utf-8")
    assert "canonical_homepage_artifact" in template
    assert "portfolio-board.txt" in template
    assert "projection-determinism.json" in template
    assert "validation_scope: `specialized-board-acceptance-only`" in template
    assert "not_a_substitute_for: `current-version real-project release proof`" in template
    assert "companion current-version release-proof record" in template


def test_v138_real_project_validation_skill_should_distinguish_release_proof_from_board_acceptance() -> None:
    skill_text = (
        ROOT
        / "skills"
        / "beacon"
        / "beacon-real-project-validation"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "current-version real-project release proof" in skill_text
    assert "prototype" in skill_text
    assert "archive" in skill_text
    assert "gate check release" in skill_text
    assert "docs/beacon/<version>/release/<version>.md" in skill_text
    assert "specialized multi-project board acceptance" in skill_text
    assert "cannot replace current-version release proof" in skill_text
