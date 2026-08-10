from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.1.9"
SLUG = "beacon-closure-control-learning-overlay"
NEXT_VERSION = "v1.1.10"
runner = CliRunner()


def _seed_story_material(root: Path, *, version: str, feature: str) -> None:
    docs = root / "docs" / "beacon" / version
    (docs / "user-story").mkdir(parents=True, exist_ok=True)
    (docs / "prd").mkdir(parents=True, exist_ok=True)
    slug = feature
    (docs / "user-story" / f"{slug}.md").write_text(
        "# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Core | 用户可以完成关键流程 |\n",
        encoding="utf-8",
    )
    (docs / "prd" / f"{slug}.md").write_text("# PRD\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Core | 用户可以完成关键流程 |\n", encoding="utf-8")


def test_v119_should_have_machine_requirement_materials():
    docs = ROOT / "docs" / "beacon" / VERSION / ".machine"
    assert (docs / "user-story" / f"{SLUG}.json").exists()
    assert (docs / "qa" / f"{SLUG}.ac-test-matrix.json").exists()
    assert (docs / "qa" / f"{SLUG}.story-scenario-map.json").exists()
    assert (docs / "execution" / f"{SLUG}.revision.json").exists()



def test_v119_machine_story_and_matrix_should_cover_full_requirement_set():
    story = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "user-story" / f"{SLUG}.json").read_text(encoding="utf-8"))
    matrix = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").read_text(encoding="utf-8"))
    scenario_map = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.story-scenario-map.json").read_text(encoding="utf-8"))
    revision = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"{SLUG}.revision.json").read_text(encoding="utf-8"))

    active_story = next(item for item in story["stories"] if item["revision_id"] == story["current_revision_id"])
    ac_ids = [item["id"] for item in active_story["items"] if item["kind"] == "ac"]
    test_ids = [item["id"] for item in active_story["items"] if item["kind"] == "test"]
    tc_ids = [item["tc_id"] for item in matrix["entries"]]

    assert story["lifecycle_status"] == "frozen"
    assert revision["doc_status"] == "frozen"
    assert len(ac_ids) == 22
    assert len(test_ids) == 22
    assert len(tc_ids) == 22
    assert ac_ids[0] == "AC-001"
    assert ac_ids[-1] == "AC-022"
    assert tc_ids[0] == "TC-001"
    assert tc_ids[-1] == "TC-022"
    assert scenario_map["feature_slug"] == SLUG
    assert isinstance(scenario_map.get("scenarios"), list) and scenario_map["scenarios"]
    families = {item["scenario_family"] for item in scenario_map["scenarios"] if item.get("browser_required")}
    assert "happy" in families or not families


def test_v119_release_docs_should_match_implemented_state():
    summary = (ROOT / "docs" / "beacon" / VERSION / "SUMMARY.md").read_text(encoding="utf-8")
    index = (ROOT / "docs" / "beacon" / VERSION / "execution" / "index.md").read_text(encoding="utf-8")
    release = ROOT / "docs" / "beacon" / VERSION / "release" / f"{VERSION}.md"

    assert release.exists()
    assert "**状态**: Implemented / Verified" in summary
    assert "implemented line" in index
    assert "exploration line" not in index
    assert "v1.1.9 Release Notes" in release.read_text(encoding="utf-8")


def test_test_case_story_scenarios_should_generate_all_features_for_version_prefix(tmp_path: Path):
    _seed_story_material(tmp_path, version="v1.1.8", feature="feature-alpha")
    _seed_story_material(tmp_path, version="v1.1.9", feature="feature-beta")

    result = runner.invoke(
        app,
        [
            "test-case",
            "story-scenarios",
            "--project",
            str(tmp_path),
            "--all-features",
            "--version-prefix",
            "v1.1.",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["generated_count"] == 2
    assert (tmp_path / "docs" / "beacon" / "v1.1.8" / ".machine" / "qa" / "feature-alpha.story-scenario-map.json").exists()
    assert (tmp_path / "docs" / "beacon" / "v1.1.9" / ".machine" / "qa" / "feature-beta.story-scenario-map.json").exists()


def test_all_v11x_features_should_have_story_scenario_maps():
    missing: list[str] = []
    for version_dir in sorted((ROOT / "docs" / "beacon").glob("v1.1.*")):
        user_story_dir = version_dir / "user-story"
        if not user_story_dir.exists():
            continue
        for story in sorted(user_story_dir.glob("*.md")):
            if story.stem == "index":
                continue
            candidates = [
                version_dir / ".machine" / "qa" / f"{story.stem}.story-scenario-map.json",
                version_dir / "qa" / "test-cases" / f"{story.stem}.story-scenario-map.json",
            ]
            if not any(path.exists() for path in candidates):
                missing.append(f"{version_dir.name}:{story.stem}")
    assert not missing, missing


def test_v110_should_have_prd_data_contract_and_phasing_docs():
    base = ROOT / "docs" / "beacon" / NEXT_VERSION
    assert (base / "SUMMARY.md").exists()
    assert (base / "execution" / "index.md").exists()
    assert (base / "prd" / "beacon-qa-confidence-autoresearch-closure.md").exists()
    assert (base / "execution" / "qa-confidence-data-contract.md").exists()
    assert (base / "execution" / "qa-confidence-implementation-phasing.md").exists()
