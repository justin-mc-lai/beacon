# Test Cases: prototype-runtime-self-heal-and-reconcile

## Overview

**Feature**: prototype-runtime-self-heal-and-reconcile
**Test Type**: ALL
**Version**: v1.3.11
**Generated**: 2026-05-04 11:30
**Requested Mode**: auto
**Effective Mode**: rule
**Fallback Reason**: llm_unavailable
**Memory Context**: N/A
**AC Matrix JSON**: docs/beacon/archive/v1.3.11/.machine/qa/prototype-runtime-self-heal-and-reconcile.ac-test-matrix.json
**QA9 Matrix JSON**: docs/beacon/archive/v1.3.11/.machine/qa/prototype-runtime-self-heal-and-reconcile.qa9-matrix.json
**Story Scenario Map JSON**: docs/beacon/archive/v1.3.11/.machine/qa/prototype-runtime-self-heal-and-reconcile.story-scenario-map.json
**Prototype Plan Present**: False
**Prototype Coverage Present**: False
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-001 | unit | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "canonical_truth_source"` | Canonical truth source is single and authoritative | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-001.json` |
| AC-002 | TC-002 | unit | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "no_multi_truth_read"` | Review, freeze, status, and gate consume the same canonical truth | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-002.json` |
| AC-003 | TC-003 | unit | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "sink_drift_detection"` | Sink drift is detected when plan, manifest, envelope, or freeze diverge | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-003.json` |
| AC-004 | TC-004 | contract | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "truth_traceability"` | Canonical truth and sink projections retain traceability fields | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-004.json` |
| AC-101 | TC-005 | interface | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "reconcile_surface"` | Reconcile surface is callable from the formal prototype runtime | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-005.json` |
| AC-102 | TC-006 | integration | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "sink_reprojection"` | Reconcile reprojects plan, manifest, canonical envelope, and freeze metadata | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-006.json` |
| AC-103 | TC-007 | unit | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "fingerprint_refresh"` | Reconcile refreshes source fingerprints, sink fingerprints, and transaction headers | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-007.json` |
| AC-104 | TC-008 | exception | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "no_requirement_writeback"` | Reconcile does not write back into prd, user-story, or test-case truth | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-008.json` |
| AC-201 | TC-009 | regression | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "pages_protected"` | Nondestructive refresh preserves pages markdown | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-009.json` |
| AC-202 | TC-010 | regression | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "preview_protected"` | Nondestructive refresh preserves existing preview assets | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-010.json` |
| AC-203 | TC-011 | regression | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "production_copy_protected"` | Nondestructive refresh preserves frozen production-visible copy | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-011.json` |
| AC-204 | TC-012 | integration | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "machine_sink_only"` | Nondestructive refresh updates machine sinks and metadata only | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-012.json` |
| AC-301 | TC-013 | unit | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "drift_types"` | Runtime classifies all required drift types | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-013.json` |
| AC-302 | TC-014 | integration | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "repair_first"` | Freeze routes metadata-only and transaction-header drift to repair before freeze | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-014.json` |
| AC-303 | TC-015 | integration | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "reprojection_before_review"` | Sink drift triggers reprojection before review rerun | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-015.json` |
| AC-304 | TC-016 | exception | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "recreate_explicit"` | Destructive recreate is only allowed when required and emits explicit scope notice | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-016.json` |
| AC-401 | TC-017 | contract | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "shared_reason_codes"` | Prototype drift reason codes are shared across all required surfaces | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-017.json` |
| AC-402 | TC-018 | integration | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "shared_diagnosis"` | Diagnosis, next action, and repair path remain consistent across surfaces | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-018.json` |
| AC-403 | TC-019 | regression | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "no_surface_local_drift_copy"` | Surfaces do not emit incompatible local drift wording | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-019.json` |
| AC-404 | TC-020 | contract | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "audit_ready"` | Reason code outputs are consumable by audit, board, and status read models | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-020.json` |
| AC-501 | TC-021 | functional | `python3 -m beacon.adapters.browser_use_runner --mode functional --fallback-cmd "python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k host_friction_elimination"` | Runtime returns repair actions directly for repairable drift | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-021.json` |
| AC-502 | TC-022 | regression | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "no_manual_json_playbook"` | Manual JSON patching is not the default operator path | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-022.json` |
| AC-503 | TC-023 | interface | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "executable_next_action"` | Each drift maps to reconcile, repair, review, freeze, or recreate | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-023.json` |
| AC-504 | TC-024 | smoke | `python3 -m pytest -q tests/test_v136_prototype_runtime_reconcile.py -k "real_project_closure"` | Real-project prototype refresh closes through formal runtime repair flow | `.beacon/evidence/test-results/prototype-runtime-self-heal-and-reconcile/TC-024.json` |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 |
| TC-004 | Pending | from AC-004 |
| TC-005 | Pending | from AC-101 |
| TC-006 | Pending | from AC-102 |
| TC-007 | Pending | from AC-103 |
| TC-008 | Pending | from AC-104 |
| TC-009 | Pending | from AC-201 |
| TC-010 | Pending | from AC-202 |
| TC-011 | Pending | from AC-203 |
| TC-012 | Pending | from AC-204 |
| TC-013 | Pending | from AC-301 |
| TC-014 | Pending | from AC-302 |
| TC-015 | Pending | from AC-303 |
| TC-016 | Pending | from AC-304 |
| TC-017 | Pending | from AC-401 |
| TC-018 | Pending | from AC-402 |
| TC-019 | Pending | from AC-403 |
| TC-020 | Pending | from AC-404 |
| TC-021 | Pending | from AC-501 |
| TC-022 | Pending | from AC-502 |
| TC-023 | Pending | from AC-503 |
| TC-024 | Pending | from AC-504 |
