from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.1.10"
SLUG = "beacon-qa-confidence-autoresearch-closure"
ARCH_SLUG = "beacon-source-architecture-sync"
ROUTE_SLUG = "beacon-prototype-frontend-route-closure"


def test_v110_should_have_complete_requirement_materials():
    base = ROOT / "docs" / "beacon" / VERSION
    assert (base / "SUMMARY.md").exists()
    assert (base / "user-story" / f"{SLUG}.md").exists()
    assert (base / "prd" / f"{SLUG}.md").exists()
    assert (base / "qa" / "test-cases" / f"{SLUG}.md").exists()
    assert (base / "qa" / "test-cases" / "index.md").exists()
    assert (base / "execution" / "index.md").exists()
    assert (base / "execution" / "architecture-blueprint.md").exists()
    assert (base / "execution" / "boundaries.md").exists()
    assert (base / "execution" / "qa-confidence-data-contract.md").exists()
    assert (base / "execution" / "project-skill-qa-evolution-blueprint.md").exists()
    assert (base / "execution" / "qa-confidence-implementation-phasing.md").exists()
    assert (base / "release" / f"{VERSION}.md").exists()
    assert (base / ".machine" / "execution" / "config.json").exists()
    assert (base / ".machine" / "execution" / "source.json").exists()
    assert (base / ".machine" / "execution" / "git-alignment.json").exists()
    assert (base / ".machine" / "execution" / "delivery-manifest.json").exists()
    assert (base / ".machine" / "execution" / "change-impact.json").exists()
    assert (base / ".machine" / "execution" / "terminal.json").exists()


def test_v110_should_have_parallel_source_architecture_requirement_line():
    base = ROOT / "docs" / "beacon" / VERSION
    assert (base / "user-story" / f"{ARCH_SLUG}.md").exists()
    assert (base / "prd" / f"{ARCH_SLUG}.md").exists()
    assert (base / "qa" / "test-cases" / f"{ARCH_SLUG}.md").exists()

    source_arch = base / "source-architecture"
    assert source_arch.exists()
    expected = {
        "index.md",
        "overall-system-map.md",
        "command-surface-and-module-map.md",
        "lifecycle-memory-and-state.md",
        "skills-prompts-and-project-workflows.md",
        "workflow-and-artifact-flow.md",
        "qa-implement-release-feedback-loop.md",
        "sync-contract.md",
    }
    assert expected <= {path.name for path in source_arch.glob("*.md")}


def test_v110_should_have_parallel_prototype_route_closure_requirement_line():
    base = ROOT / "docs" / "beacon" / VERSION
    assert (base / "user-story" / f"{ROUTE_SLUG}.md").exists()
    assert (base / "prd" / f"{ROUTE_SLUG}.md").exists()
    assert (base / "qa" / "test-cases" / f"{ROUTE_SLUG}.md").exists()
    assert (base / "execution" / "prototype-frontend-route-closure-blueprint.md").exists()


def test_v110_machine_story_and_revision_should_be_frozen():
    story = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "user-story" / f"{SLUG}.json").read_text(encoding="utf-8"))
    revision = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"{SLUG}.revision.json").read_text(encoding="utf-8"))

    active_story = next(item for item in story["stories"] if item["revision_id"] == story["current_revision_id"])
    ac_items = [item for item in active_story["items"] if item["kind"] == "ac"]
    test_items = [item for item in active_story["items"] if item["kind"] == "test"]

    assert story["lifecycle_status"] == "frozen"
    assert revision["doc_status"] == "frozen"
    assert revision["revision_id"] == "R1"
    assert len(ac_items) == 20
    assert len(test_items) == 20
    assert ac_items[0]["id"] == "AC-001"
    assert ac_items[-1]["id"] == "AC-020"


def test_v110_story_scenario_map_should_cover_required_browser_families():
    matrix = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").read_text(encoding="utf-8"))
    scenario_map = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.story-scenario-map.json").read_text(encoding="utf-8"))

    assert len(matrix["entries"]) == 20
    assert scenario_map["families_required"] == ["happy", "negative", "boundary", "recovery", "compatibility"]
    assert len(scenario_map["scenarios"]) >= 40

    browser_families = {
        item["scenario_family"]
        for item in scenario_map["scenarios"]
        if item.get("browser_required")
    }
    assert {"happy", "negative", "boundary", "recovery", "compatibility"} <= browser_families


def test_v110_parallel_source_architecture_feature_should_have_machine_materials():
    story = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "user-story" / f"{ARCH_SLUG}.json").read_text(encoding="utf-8"))
    revision = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"{ARCH_SLUG}.revision.json").read_text(encoding="utf-8"))
    matrix = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{ARCH_SLUG}.ac-test-matrix.json").read_text(encoding="utf-8"))
    scenario_map = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{ARCH_SLUG}.story-scenario-map.json").read_text(encoding="utf-8"))

    active_story = next(item for item in story["stories"] if item["revision_id"] == story["current_revision_id"])
    ac_items = [item for item in active_story["items"] if item["kind"] == "ac"]
    test_items = [item for item in active_story["items"] if item["kind"] == "test"]

    assert story["lifecycle_status"] == "frozen"
    assert revision["doc_status"] == "frozen"
    assert len(ac_items) == 15
    assert len(test_items) == 15
    assert len(matrix["entries"]) == 15
    assert len(scenario_map["scenarios"]) >= 15


def test_v110_parallel_prototype_route_closure_feature_should_have_machine_materials():
    story = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "user-story" / f"{ROUTE_SLUG}.json").read_text(encoding="utf-8"))
    revision = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "execution" / f"{ROUTE_SLUG}.revision.json").read_text(encoding="utf-8"))
    matrix = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{ROUTE_SLUG}.ac-test-matrix.json").read_text(encoding="utf-8"))
    scenario_map = json.loads((ROOT / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{ROUTE_SLUG}.story-scenario-map.json").read_text(encoding="utf-8"))
    active_story = next(item for item in story["stories"] if item["revision_id"] == story["current_revision_id"])
    ac_items = [item for item in active_story["items"] if item["kind"] == "ac"]

    assert story["lifecycle_status"] == "frozen"
    assert revision["doc_status"] == "frozen"
    assert len(ac_items) == 11
    assert len(matrix["entries"]) == 11
    assert len(scenario_map["scenarios"]) >= 11


def test_v110_docs_should_express_anchor_and_feedback_model():
    summary = (ROOT / "docs" / "beacon" / VERSION / "SUMMARY.md").read_text(encoding="utf-8")
    qa_doc = (ROOT / "docs" / "beacon" / VERSION / "qa" / "test-cases" / f"{SLUG}.md").read_text(encoding="utf-8")
    release = (ROOT / "docs" / "beacon" / VERSION / "release" / f"{VERSION}.md").read_text(encoding="utf-8")
    blueprint = (ROOT / "docs" / "beacon" / VERSION / "execution" / "project-skill-qa-evolution-blueprint.md").read_text(encoding="utf-8")
    route_blueprint = (ROOT / "docs" / "beacon" / VERSION / "execution" / "prototype-frontend-route-closure-blueprint.md").read_text(encoding="utf-8")
    arch_prd = (ROOT / "docs" / "beacon" / VERSION / "prd" / f"{ARCH_SLUG}.md").read_text(encoding="utf-8")
    route_prd = (ROOT / "docs" / "beacon" / VERSION / "prd" / f"{ROUTE_SLUG}.md").read_text(encoding="utf-8")
    sync_contract = (ROOT / "docs" / "beacon" / VERSION / "source-architecture" / "sync-contract.md").read_text(encoding="utf-8")
    qa_prd = (ROOT / "docs" / "beacon" / VERSION / "prd" / f"{SLUG}.md").read_text(encoding="utf-8")
    phasing = (ROOT / "docs" / "beacon" / VERSION / "execution" / "qa-confidence-implementation-phasing.md").read_text(encoding="utf-8")
    source_qa = (ROOT / "docs" / "beacon" / VERSION / "qa" / "test-cases" / f"{ARCH_SLUG}.md").read_text(encoding="utf-8")
    route_qa = (ROOT / "docs" / "beacon" / VERSION / "qa" / "test-cases" / f"{ROUTE_SLUG}.md").read_text(encoding="utf-8")

    assert "Implemented / Verified" in summary
    assert "runtime-closed" in summary
    assert "Anchor-A" in qa_doc
    assert "TC-036" in qa_doc
    assert "project-specific skill/profile/orchestration" in blueprint
    assert "browser QA session/auth persistence" in blueprint
    assert "technical implementation archive" in blueprint
    assert "route closure an explicit contract" in route_blueprint
    assert "route-closure-contract.json" in route_prd
    assert "implementation-map.json" in route_prd
    assert "TC-010 | miniapp" in route_qa
    assert "FR-016 `qa run <feature>` must consume project workflow truth" in qa_prd
    assert "FR-018 Machine refresh must preserve human-authored QA requirement docs" in qa_prd
    assert "Phase 2.5 — Move project workflow into the QA mainline" in phasing
    assert "Phase 5.5 — Materials and doc-integrity closure" in phasing
    assert "source-architecture/" in summary
    assert "beacon-source-architecture-sync" in arch_prd
    assert "beacon-prototype-frontend-route-closure" in summary
    assert "must update source architecture docs" in sync_contract
    assert "TC-016 | formal-audit" in source_qa
    assert "Implemented / Verified" in release
    assert "test-case gate" in release
    assert "runtime implementation now exists for `closure_outcome`" in release
