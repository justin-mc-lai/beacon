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
