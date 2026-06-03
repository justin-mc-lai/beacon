from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
PACKAGED = ROOT / "skills" / "beacon"
AGENTS = ROOT / ".agents" / "skills"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_beacon_truth_skill_exists_in_packaged_and_agent_surfaces() -> None:
    for root in (PACKAGED, AGENTS):
        text = _read(root / "beacon-truth" / "SKILL.md")
        assert text.startswith("---\n")
        assert "name: beacon-truth" in text
        assert "truth.define" in text
        assert "truth.acceptance" in text
        assert "truth.coverage" in text


def test_beacon_truth_preserves_distinct_modes_and_change_route() -> None:
    for root in (PACKAGED, AGENTS):
        text = _read(root / "beacon-truth" / "SKILL.md")
        assert "truth.define" in text
        assert "truth.acceptance" in text
        assert "truth.coverage" in text
        assert "truth.change" in text
        assert "freeform truth surface" in text


def test_beacon_truth_is_resolver_first_and_package_authoritative() -> None:
    for root in (PACKAGED, AGENTS):
        text = _read(root / "beacon-truth" / "SKILL.md")
        assert "beacon truth-map resolve <feature> --project . --version v1.5.2 --json" in text
        assert "features/<slug>/truth.md" in text
        assert "features/<slug>/tests.md" in text
        assert "markdown feature package" in text.lower()


def test_legacy_truth_skills_are_marked_compatibility_aliases() -> None:
    for root in (PACKAGED, AGENTS):
        assert "compatibility alias" in _read(root / "beacon-prd" / "SKILL.md")
        assert "truth.define" in _read(root / "beacon-prd" / "SKILL.md")
        assert "compatibility alias" in _read(root / "beacon-user-story" / "SKILL.md")
        assert "truth.acceptance" in _read(root / "beacon-user-story" / "SKILL.md")
        assert "compatibility alias" in _read(root / "beacon-test-case" / "SKILL.md")
        assert "truth.coverage" in _read(root / "beacon-test-case" / "SKILL.md")


def test_root_and_brainstorm_prefer_truth_mode_lifecycle_language() -> None:
    root_skill = _read(PACKAGED / "SKILL.md")
    assert "truth.define -> truth.acceptance -> truth.coverage" in root_skill
    assert "`beacon-truth`" in root_skill
    assert "compatibility aliases" in root_skill

    for root in (PACKAGED, AGENTS):
        brainstorm = _read(root / "beacon-brainstorm" / "SKILL.md")
        assert "truth.define -> truth.acceptance -> truth.coverage" in brainstorm
        assert "`beacon-truth`" in brainstorm


def test_beacon_truth_does_not_inflate_support_or_gate_surfaces() -> None:
    for root in (PACKAGED, AGENTS):
        text = _read(root / "beacon-truth" / "SKILL.md").lower()
        assert "not a truth authority" in text
        assert "not a gate source" in text
        assert "not a new lifecycle stage" in text
        assert "does not execute qa" in text
        assert "does not issue release verdicts" in text


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
