"""Truth Integrity Gate (TIG) unit and integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from beacon.utils.feature_package import validate_feature_package
from beacon.utils.truth_integrity import (
    build_truth_integrity_gate,
    verify_closure_via_tig,
)

VERSION = "v1.6.0"
REPO_ROOT = Path(__file__).resolve().parents[1]


def _frontmatter(slug: str, version: str = VERSION) -> str:
    return f"""---
slug: {slug}
version: {version}
status: draft
language: zh
canonical_refs:
  prd: docs/beacon/{version}/features/{slug}/truth.md
  user_story: docs/beacon/{version}/features/{slug}/truth.md
  test_case: docs/beacon/{version}/features/{slug}/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---
"""


def _write_package(
    root: Path,
    slug: str,
    *,
    truth_body: str,
    tests_body: str,
    tasks_body: str,
    evidence_body: str,
    version: str = VERSION,
) -> Path:
    feature_dir = root / "docs/beacon" / version / "features" / slug
    feature_dir.mkdir(parents=True, exist_ok=True)
    (root / "docs/beacon/VERSION").write_text(f"{version}\n", encoding="utf-8")
    (feature_dir / "truth.md").write_text(_frontmatter(slug, version) + truth_body, encoding="utf-8")
    (feature_dir / "tests.md").write_text(tests_body, encoding="utf-8")
    (feature_dir / "tasks.md").write_text(tasks_body, encoding="utf-8")
    (feature_dir / "evidence.md").write_text(evidence_body, encoding="utf-8")
    return feature_dir


def _minimal_good_bodies(slug: str) -> tuple[str, str, str, str]:
    truth = f"""
# {slug}

scope_mode = smoke

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | smoke | GET health returns 200. |
"""
    tests = """
# Tests

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | unit | `beacon doctor --help` | exit 0 |
"""
    tasks = """
# Tasks

- [ ] TASK-001 Implement gate
"""
    evidence = """
# Evidence

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| qa | qa_verdict | tests/test_truth_integrity.py | linked | qa |
"""
    return truth, tests, tasks, evidence


@pytest.fixture()
def good_smoke(tmp_path: Path) -> tuple[Path, str]:
    slug = "good-smoke-scope"
    bodies = _minimal_good_bodies(slug)
    _write_package(tmp_path, slug, truth_body=bodies[0], tests_body=bodies[1], tasks_body=bodies[2], evidence_body=bodies[3])
    return tmp_path, slug


def test_good_smoke_scope_passes_block_mode(good_smoke: tuple[Path, str]) -> None:
    root, slug = good_smoke
    gate = build_truth_integrity_gate(root, version=VERSION, feature=slug, mode="block")
    assert gate["status"] == "pass"
    assert not gate["blocked"]


def test_bad_placeholder_ac_blocks(tmp_path: Path) -> None:
    slug = "bad-placeholder-ac"
    truth, tests, tasks, evidence = _minimal_good_bodies(slug)
    truth = truth.replace("GET health returns 200.", "placeholder AC stub-only closure TBD")
    _write_package(tmp_path, slug, truth_body=truth, tests_body=tests, tasks_body=tasks, evidence_body=evidence)
    gate = build_truth_integrity_gate(tmp_path, version=VERSION, feature=slug, mode="block")
    assert gate["blocked"]
    kinds = {f.get("kind") for f in gate.get("findings", [])}
    assert "placeholder_ac_language" in kinds or "placeholder_acceptance" in kinds


def test_bad_soft_tests_blocks(tmp_path: Path) -> None:
    slug = "bad-soft-tests"
    truth, tests, tasks, evidence = _minimal_good_bodies(slug)
    tests = """
# Tests

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | integration | integration | directory exists |
"""
    _write_package(tmp_path, slug, truth_body=truth, tests_body=tests, tasks_body=tasks, evidence_body=evidence)
    gate = build_truth_integrity_gate(tmp_path, version=VERSION, feature=slug, mode="block")
    assert gate["blocked"]
    kinds = {f.get("kind") for f in gate.get("findings", [])}
    assert "soft_test_assertion" in kinds or "soft_test_command_only" in str(
        gate.get("feature_package_validation", {})
    )


def test_bad_pending_deferral_blocks(tmp_path: Path) -> None:
    slug = "bad-pending-deferral"
    truth, tests, tasks, evidence = _minimal_good_bodies(slug)
    truth += "\nuser_decision: pending\n| pending | defer item |\n"
    _write_package(tmp_path, slug, truth_body=truth, tests_body=tests, tasks_body=tasks, evidence_body=evidence)
    gate = build_truth_integrity_gate(tmp_path, version=VERSION, feature=slug, mode="block")
    assert gate["blocked"]
    kinds = {f.get("kind") for f in gate.get("findings", [])}
    assert "deferral_pending" in kinds or "pending_deferral" in kinds


def test_bad_fake_delivery_evidence_blocks(tmp_path: Path) -> None:
    slug = "bad-fake-delivery-evidence"
    truth, tests, tasks, evidence = _minimal_good_bodies(slug)
    evidence = evidence + "\nplaceholder evidence for fake closure\n"
    _write_package(tmp_path, slug, truth_body=truth, tests_body=tests, tasks_body=tasks, evidence_body=evidence)
    gate = build_truth_integrity_gate(tmp_path, version=VERSION, feature=slug, mode="block")
    assert gate["blocked"]
    fake = gate.get("fake_delivery", {})
    assert not fake.get("closure_allowed", True) or gate.get("finding_count", 0) > 0


def test_bad_ocean_no_alignment_blocks(tmp_path: Path) -> None:
    slug = "bad-ocean-no-alignment"
    truth, tests, tasks, evidence = _minimal_good_bodies(slug)
    truth = truth.replace("scope_mode = smoke", "scope_mode: ocean\n海级 feature without alignment")
    _write_package(tmp_path, slug, truth_body=truth, tests_body=tests, tasks_body=tasks, evidence_body=evidence)
    gate = build_truth_integrity_gate(tmp_path, version=VERSION, feature=slug, mode="block")
    assert gate["blocked"]
    kinds = {f.get("kind") for f in gate.get("findings", [])}
    assert "alignment_surface_missing" in kinds


def test_prose_ac_validation_passes(tmp_path: Path) -> None:
    slug = "prose-ac-feature"
    truth = _frontmatter(slug) + """
# Prose AC Feature

scope_mode = smoke

## Acceptance

- AC-001: Command exits zero.
"""
    tests, tasks, evidence = _minimal_good_bodies(slug)[1:]
    _write_package(tmp_path, slug, truth_body=truth, tests_body=tests, tasks_body=tasks, evidence_body=evidence)
    validation = validate_feature_package(tmp_path, version=VERSION, feature=slug)
    assert str(validation.get("status")).lower() != "blocked"
    codes = [d.get("code") for d in validation.get("diagnostics", []) if isinstance(d, dict)]
    assert "acceptance_criteria_table_missing" not in codes


def test_verify_closure_aligns_with_tig(good_smoke: tuple[Path, str]) -> None:
    root, slug = good_smoke
    gate = build_truth_integrity_gate(root, version=VERSION, feature=slug, mode="block")
    closure = verify_closure_via_tig(root, version=VERSION, feature=slug)
    assert closure.get("closure_allowed") == gate.get("fake_delivery", {}).get("closure_allowed")


def test_v2_rust_kernel_redesign_audit_passes() -> None:
    gate = build_truth_integrity_gate(
        REPO_ROOT,
        version="v2.0.0",
        feature="beacon-v2-rust-kernel-redesign",
        mode="audit",
    )
    assert gate["status"] in {"pass", "audit_only"}
    assert not gate["blocked"]


def test_tig_feature_package_block_mode() -> None:
    gate = build_truth_integrity_gate(
        REPO_ROOT,
        version=VERSION,
        feature="beacon-truth-integrity-gates-v160",
        mode="block",
    )
    fake = gate.get("fake_delivery", {})
    assert fake.get("closure_allowed", True)
    validation = gate.get("feature_package_validation", {})
    assert str(validation.get("status", "")).lower() != "blocked"
