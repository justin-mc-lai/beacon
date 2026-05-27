from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.compatibility.registry import registry_by_id, validate_compatibility_registry
from beacon.utils.material_audit import build_material_audit
from beacon.utils.qa_runtime import (
    load_qa_status,
    qa_legacy_admission_path,
    qa_status_path,
    write_qa_status,
)
from beacon.utils.release_scorecard import _resolve_acceptance_truth
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.runtime import write_json
from beacon.utils.story_state import freeze_story_state, sync_story_state_from_docs


VERSION = "v1.4.11"
FEATURE = "QA PRD Legacy Mirror Retirement Contract"
SLUG = "qa-prd-legacy-mirror-retirement-contract"
pytestmark = [pytest.mark.projection_integrity]


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_requirement_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# Global Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# Summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# Execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/boundaries.md", "# Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/execution/project-skill-qa-evolution-blueprint.md", "# Blueprint\n")
    _write(root, f"docs/beacon/{VERSION}/source-architecture/index.md", "# Source Architecture\n")
    _write(root, f"docs/beacon/{VERSION}/research/{SLUG}.md", "# Research\n\n## Architecture\n- Mirror policy.\n\n## Business Flow\n- Current first.\n\n## State Machine\n- registered -> current-only.\n")
    _write(root, f"docs/beacon/{VERSION}/change/{SLUG}.md", "# Change\n")
    _write(root, f"docs/beacon/{VERSION}/release/checklist-{VERSION}.md", "# Release\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        "\n".join(
            [
                "# PRD",
                "",
                "- AC-001 Canonical QA status is the default current QA authority.",
                "- AC-002 Legacy QA status requires explicit compatibility admission.",
                "- AC-003 Release checks cannot pass from legacy-only QA status.",
                "- AC-004 Markdown PRD remains requirement truth.",
                "- AC-005 Current PRD projection drift remains blocking.",
                "- AC-006 Legacy PRD mirror mismatch is compatibility warning.",
                "- AC-007 Mirror policies bind to registry entries.",
                "- AC-008 No unrelated retirement.",
                "",
            ]
        ),
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        "# User Story\n\n## Acceptance Criteria\n"
        + "\n".join(f"- AC-{idx:03d} Criterion {idx}." for idx in range(1, 9))
        + "\n",
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        "# Test Cases\n\n| AC ID | TC ID | Layer | Command | Assertion |\n| --- | --- | --- | --- | --- |\n"
        + "\n".join(f"| AC-{idx:03d} | TC-{idx:03d} | contract | `pytest` | covered |" for idx in range(1, 9))
        + "\n",
    )
    sync_story_state_from_docs(root, VERSION, FEATURE)
    freeze_story_state(root, VERSION, FEATURE)
    freeze_revision_state(root, version=VERSION, feature=FEATURE)


def test_canonical_qa_status_is_default_authority(tmp_path: Path) -> None:
    write_json(tmp_path / ".beacon" / "auto-test-status.json", {"status": "passed", "version": VERSION, "evidence_done": True, "release_ready": True})

    assert load_qa_status(tmp_path) == {}

    write_qa_status(tmp_path, {"status": "passed", "version": VERSION, "evidence_done": True, "release_ready": True})
    status = load_qa_status(tmp_path)

    assert status["status"] == "passed"
    assert status["qa_status_source"] == "canonical"
    assert qa_status_path(tmp_path).exists()


@pytest.mark.compat_contract
@pytest.mark.historical_fixture
def test_legacy_qa_status_requires_explicit_admission(tmp_path: Path) -> None:
    write_json(tmp_path / ".beacon" / "auto-test-status.json", {"status": "passed", "version": VERSION, "evidence_done": True, "release_ready": True})

    status = load_qa_status(tmp_path, allow_legacy=True, admission_reason="test-explicit-admission")

    assert status["qa_status_source"] == "legacy_admitted"
    assert status["compatibility_evidence"]["compat_id"] == "qa-auto-test-status-legacy-mirror"
    assert qa_legacy_admission_path(tmp_path).exists()


@pytest.mark.compat_contract
@pytest.mark.historical_fixture
def test_release_blocks_legacy_only_qa_pass() -> None:
    registry = registry_by_id()
    acceptance = _resolve_acceptance_truth(
        {
            "status": "passed",
            "version": VERSION,
            "evidence_done": True,
            "release_ready": True,
            "qa_status_source": "legacy_admitted",
        },
        {},
        {},
    )

    assert "qa-auto-test-status-legacy-mirror" in registry
    assert acceptance["status"] == "missing"
    assert acceptance["release_ready"] is False
    assert acceptance["legacy_only_qa_blocked"] is True


@pytest.mark.current_contract
def test_markdown_prd_remains_requirement_truth(tmp_path: Path) -> None:
    _seed_requirement_docs(tmp_path)
    write_json(tmp_path / ".beacon" / "prd" / f"{SLUG}.json", {"markdown": "# stale legacy mirror\n"})

    audit = build_material_audit(tmp_path, version=VERSION, strict=True, feature=SLUG)

    compat_check = next(item for item in audit["checks"] if item["name"] == "prd_compat_mirror_sync")
    assert compat_check["status"] == "warn"
    assert compat_check["details"]["warning_by_feature"][SLUG]["compat_mirror_stale"]["role"] == "compat_mirror"


@pytest.mark.current_contract
def test_current_prd_projection_drift_still_blocks(tmp_path: Path) -> None:
    _seed_requirement_docs(tmp_path)
    write_json(tmp_path / "docs" / "beacon" / VERSION / ".machine" / "prd" / f"{SLUG}.canonical.json", {"markdown_hash": "stale"})

    audit = build_material_audit(tmp_path, version=VERSION, strict=True, feature=SLUG)
    mirror_check = next(item for item in audit["checks"] if item["name"] == "prd_machine_mirror_sync")

    assert mirror_check["status"] == "warn"
    assert "canonical_machine_mirror_sync" in mirror_check["details"]["drift_by_feature"][SLUG]


@pytest.mark.compat_contract
@pytest.mark.historical_fixture
def test_legacy_prd_mirror_stale_is_compat_warning(tmp_path: Path) -> None:
    registry = registry_by_id()
    _seed_requirement_docs(tmp_path)
    write_json(tmp_path / ".beacon" / "prd" / f"{SLUG}.json", {"markdown_hash": "stale"})

    audit = build_material_audit(tmp_path, version=VERSION, strict=True, feature=SLUG)
    mirror_check = next(item for item in audit["checks"] if item["name"] == "prd_machine_mirror_sync")
    compat_check = next(item for item in audit["checks"] if item["name"] == "prd_compat_mirror_sync")

    assert "prd-legacy-machine-mirror" in registry
    blocking_drift = mirror_check["details"]["drift_by_feature"].get(SLUG, {})
    assert "compat_mirror_stale" not in blocking_drift
    assert "legacy_machine_mirror_sync" not in blocking_drift
    assert compat_check["status"] == "warn"
    assert "compat_mirror_stale" in compat_check["details"]["warning_by_feature"][SLUG]


@pytest.mark.compat_contract
def test_mirror_policies_bind_to_compat_registry() -> None:
    registry = registry_by_id()
    assert registry["qa-auto-test-status-legacy-mirror"]["retirement_route"] == "qa-prd-legacy-mirror-retirement-contract"
    assert registry["prd-legacy-machine-mirror"]["retirement_route"] == "qa-prd-legacy-mirror-retirement-contract"

    result = validate_compatibility_registry(required_ids={"qa-auto-test-status-legacy-mirror", "prd-legacy-machine-mirror"})
    assert result["status"] == "pass"


@pytest.mark.compat_contract
@pytest.mark.historical_fixture
def test_no_unrelated_legacy_retirement_in_mirror_policy_slice(tmp_path: Path) -> None:
    registry = registry_by_id()
    write_json(tmp_path / ".beacon" / "auto-test-status.json", {"status": "passed"})
    write_json(tmp_path / ".beacon" / "prd" / f"{SLUG}.json", {"markdown": "legacy"})

    assert "qa-auto-test-status-legacy-mirror" in registry
    assert "prd-legacy-machine-mirror" in registry
    assert (tmp_path / ".beacon" / "auto-test-status.json").exists()
    assert (tmp_path / ".beacon" / "prd" / f"{SLUG}.json").exists()

    from beacon.adapters import browser_runner_common
    from beacon.utils import intent_router, memory, prototype_utils

    assert callable(prototype_utils.evaluate_prototype_status)
    assert callable(browser_runner_common.write_runner_artifacts)
    assert callable(memory._migrate_legacy_to_v1_if_needed)
    assert callable(intent_router.detect_intent)
