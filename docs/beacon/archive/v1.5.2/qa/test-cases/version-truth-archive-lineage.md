# Test Cases: version-truth-archive-lineage

## Overview

**Feature**: version-truth-archive-lineage
**Test Type**: ALL
**Version**: v1.5.2
**Generated**: 2026-06-04 10:09
**Requested Mode**: auto
**Effective Mode**: markdown
**Fallback Reason**: N/A
**Memory Context**: N/A
**AC Matrix JSON**: docs/beacon/archive/v1.5.2/.machine/qa/version-truth-archive-lineage.ac-test-matrix.json
**QA9 Matrix JSON**: docs/beacon/archive/v1.5.2/.machine/qa/version-truth-archive-lineage.qa9-matrix.json
**Story Scenario Map JSON**: docs/beacon/archive/v1.5.2/.machine/qa/version-truth-archive-lineage.story-scenario-map.json
**Prototype Plan Present**: False
**Prototype Coverage Present**: False
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-001 | contract | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_catalog_md_is_sole_commit_source -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Catalog parser round-trip; JSON projection derived only. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-001.json` |
| AC-002 | TC-002 | unit | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_active_window_three_versions -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Exactly 3 active roots under `docs/beacon/<v>/`. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-002.json` |
| AC-003 | TC-003 | integration | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_catalog_apply_relocates_archived_tree -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Move to `archive/<v>/`; bounded link rewrite; no delete. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-003.json` |
| AC-004 | TC-004 | integration | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_verify_strict_fails_on_catalog_drift -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Tampered projection or path mismatch → fail closed. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-004.json` |
| AC-005 | TC-005 | contract | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_resolver_uses_active_catalog_only -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Delivery commands ignore archived unless `--include-archived`. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-005.json` |
| AC-006 | TC-006 | unit | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_discover_features_uses_truth_md -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.5.2 discovery finds `features/*/truth.md`. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-006.json` |
| AC-007 | TC-007 | integration | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_archive_lineage_spans_active_and_archive -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Ordered hops with truth paths across roots. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-007.json` |
| AC-008 | TC-008 | integration | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_archive_inventory_active_ac_matrix -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Matrix from active truth AC tables only by default. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-008.json` |
| AC-009 | TC-009 | unit | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_archive_index_regenerated_on_apply -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | INDEX.md matches catalog; not stale after apply. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-009.json` |
| AC-010 | TC-010 | integration | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_catalog_bootstrap_dry_run_and_confirm -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Dry-run previews moves; confirm atomic + verify strict. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-010.json` |
| AC-011 | TC-011 | contract | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_beacon_archive_skill_documents_examples -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Skill contains four verbs + examples A–F boundaries. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-011.json` |
| AC-012 | TC-012 | contract | `python3 -m pytest tests/test_version_truth_archive_lineage.py::test_global_boundaries_section_4_1_present -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | §4.1 + archive/change clarification merged in global-boundaries. | `.beacon/evidence/test-results/version-truth-archive-lineage/{run_id}/TC-012.json` |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 |
| TC-004 | Pending | from AC-004 |
| TC-005 | Pending | from AC-005 |
| TC-006 | Pending | from AC-006 |
| TC-007 | Pending | from AC-007 |
| TC-008 | Pending | from AC-008 |
| TC-009 | Pending | from AC-009 |
| TC-010 | Pending | from AC-010 |
| TC-011 | Pending | from AC-011 |
| TC-012 | Pending | from AC-012 |
