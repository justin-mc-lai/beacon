from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
PACKAGED = ROOT / "skills" / "beacon"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_beacon_truth_skill_exists_in_packaged_surface_as_v160_generator() -> None:
    text = _read(PACKAGED / "beacon-gen-truth" / "SKILL.md")
    assert text.startswith("---\n")
    assert "name: beacon-gen-truth" in text
    assert "Beacon v1.6.0 共享 Preamble" in text
    assert "HARD GATE:" in text
    assert "你正在运行 generator skill" in text
    assert "beacon-truth` -> `beacon-gen-truth" in text


def test_beacon_truth_preserves_distinct_change_and_refreeze_routes() -> None:
    change = _read(PACKAGED / "beacon-gen-change" / "SKILL.md")
    refreeze = _read(PACKAGED / "beacon-gen-refreeze" / "SKILL.md")
    bootstrap = _read(PACKAGED / "beacon-gen-truth-init" / "SKILL.md")
    assert "beacon-change` -> `beacon-gen-change" in change
    assert "beacon-change-refreeze` -> `beacon-gen-refreeze" in refreeze
    assert "beacon-prd-bootstrap` -> `beacon-gen-truth-init" in bootstrap
    assert "禁止自证完成" in change


def test_beacon_truth_is_resolver_first_and_package_authoritative() -> None:
    text = _read(PACKAGED / "beacon-gen-truth" / "SKILL.md")
    root_skill = _read(PACKAGED / "SKILL.md")
    assert "resolver-selected truth" in text
    assert "docs/beacon/<version>/research/<feature-slug>.md" in text
    assert "beacon truth-map resolve <feature> --project . --version <version> --json" in root_skill
    assert "docs/beacon/<version>/features/<slug>/{truth,tests,tasks,evidence}.md" in root_skill


def test_legacy_truth_skills_are_removed_from_v160_packaged_surface() -> None:
    for old_name in ("beacon-prd", "beacon-user-story", "beacon-test-case", "beacon-truth"):
        assert not (PACKAGED / old_name / "SKILL.md").exists()


def test_root_and_brainstorm_prefer_truth_mode_lifecycle_language() -> None:
    root_skill = _read(PACKAGED / "SKILL.md")
    assert "plan -> truth -> generate -> evaluate -> release" in root_skill
    assert "`beacon-gen-truth`" in root_skill
    assert "Old host-visible aliases" in root_skill

    brainstorm = _read(PACKAGED / "beacon-pln-brainstorm" / "SKILL.md")
    assert "你正在运行 planner skill" in brainstorm
    assert "route recommendation" in brainstorm


def test_beacon_truth_does_not_inflate_support_or_gate_surfaces() -> None:
    text = _read(PACKAGED / "beacon-gen-truth" / "SKILL.md").lower()
    assert "禁止自证完成" in text
    assert "禁止给 qa/release verdict" in text
    assert "fake-runner" in text
    evaluator = _read(PACKAGED / "beacon-eval-qa" / "SKILL.md").lower()
    assert "禁止改写 requirement truth" in evaluator


def test_validate_feature_package_cli_for_truth_skill_lifecycle_package() -> None:
    result = CliRunner().invoke(
        app,
        [
            "validate-feature-package",
            "beacon-truth-skill-lifecycle-rename",
            "--project",
            str(ROOT),
            "--version",
            "v1.5.2",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["truth_source_model"] == "feature_package_authoritative"
    assert payload["source_paths"]["truth"].endswith("/features/beacon-truth-skill-lifecycle-rename/truth.md")
