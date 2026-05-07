# Test Cases: Beacon v1.4.0 PRD bootstrap safe requirement bootstrap and freeze closure

## Overview

**Feature**: Beacon v1.4.0 PRD bootstrap safe requirement bootstrap and freeze closure
**Test Type**: ALL
**Version**: v1.4.0
**Generated**: 2026-05-06 21:10
**Requested Mode**: auto
**Effective Mode**: requirement-freeze
**Fallback Reason**: bootstrap-contract-freeze-before-implementation
**Primary Truth**: docs/beacon/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md
**Upstream User Story**: docs/beacon/v1.4.0/user-story/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md
**Global Boundary Truth**: docs/beacon/global-boundaries.md
**AC Matrix JSON**: docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.ac-test-matrix.json
**QA9 Matrix JSON**: docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.qa9-matrix.json
**Story Scenario Map JSON**: docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.story-scenario-map.json

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-001 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_surface.py -k "optional_support_skill_tier"` | `beacon-prd-bootstrap` remains an optional support skill rather than a public mainline command | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-001.json` |
| AC-002 | TC-002 | regression | `python3 -m pytest -q tests/test_v140_prd_bootstrap_surface.py -k "not_new_lifecycle_stage"` | bootstrap is not exposed as a new lifecycle stage | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-002.json` |
| AC-003 | TC-003 | regression | `python3 -m pytest -q tests/test_v140_prd_bootstrap_surface.py -k "not_mainline_replacement"` | bootstrap does not replace formal `prd / user-story / test-case` semantics | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-003.json` |
| AC-004 | TC-004 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_surface.py -k "lightweight_kernel_alignment"` | bootstrap aligns with `v1.4.0` lightweight kernel boundaries | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-004.json` |
| AC-101 | TC-005 | integration | `python3 -m pytest -q tests/test_v140_prd_bootstrap_generation.py -k "three_doc_bootstrap"` | one run can generate PRD, user-story, and test-case draft docs | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-005.json` |
| AC-102 | TC-006 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_generation.py -k "writes_to_canonical_paths"` | generated docs target canonical `docs/beacon/<version>/` paths | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-006.json` |
| AC-103 | TC-007 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_generation.py -k "shared_generation_identity"` | the three docs share feature slug, version, and generation identity | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-007.json` |
| AC-104 | TC-008 | regression | `python3 -m pytest -q tests/test_v140_prd_bootstrap_generation.py -k "no_side_truth_tree"` | bootstrap does not create an alternate truth tree outside the canonical version package | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-008.json` |
| AC-201 | TC-009 | integration | `python3 -m pytest -q tests/test_v140_prd_bootstrap_safety.py -k "strict_context_verify_default"` | bootstrap runs strict context verification by default | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-009.json` |
| AC-202 | TC-010 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_safety.py -k "dry_run_default"` | default execution is dry-run and does not write requirement docs | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-010.json` |
| AC-203 | TC-011 | integration | `python3 -m pytest -q tests/test_v140_prd_bootstrap_safety.py -k "no_overwrite_default"` | existing docs block apply by default unless overwrite is explicitly allowed | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-011.json` |
| AC-204 | TC-012 | regression | `python3 -m pytest -q tests/test_v140_prd_bootstrap_safety.py -k "fail_closed_on_any_safety_failure"` | context, quality, consistency, or lock failure all fail closed | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-012.json` |
| AC-301 | TC-013 | integration | `python3 -m pytest -q tests/test_v140_prd_bootstrap_apply.py -k "lock_protection"` | a bootstrap lock prevents concurrent write conflicts | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-013.json` |
| AC-302 | TC-014 | integration | `python3 -m pytest -q tests/test_v140_prd_bootstrap_apply.py -k "atomic_write_no_partial_docs"` | apply writes are atomic and do not leave partial requirement docs on failure | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-014.json` |
| AC-303 | TC-015 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_apply.py -k "state_artifact_written"` | every run writes a state artifact for audit | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-015.json` |
| AC-304 | TC-016 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_apply.py -k "rollback_manifest_present"` | apply results include a rollback manifest | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-016.json` |
| AC-401 | TC-017 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_status.py -k "bootstrap_generated_status"` | generated docs explicitly carry bootstrap-generated semantics | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-017.json` |
| AC-402 | TC-018 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_status.py -k "review_required_status"` | generated docs explicitly carry review-required semantics | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-018.json` |
| AC-403 | TC-019 | regression | `python3 -m pytest -q tests/test_v140_prd_bootstrap_status.py -k "not_yet_frozen_or_implement_ready"` | generated docs are not mislabeled as frozen or implementation-ready by default | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-019.json` |
| AC-404 | TC-020 | integration | `python3 -m pytest -q tests/test_v140_prd_bootstrap_status.py -k "routes_to_review_refreeze"` | support output routes the operator toward review and refreeze | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-020.json` |
| AC-501 | TC-021 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_traceability.py -k "shared_metadata_fields"` | all three docs share required metadata fields | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-021.json` |
| AC-502 | TC-022 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_traceability.py -k "minimal_ac_tc_traceability"` | user-story and test-case retain minimal AC/TC traceability | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-022.json` |
| AC-503 | TC-023 | regression | `python3 -m pytest -q tests/test_v140_prd_bootstrap_traceability.py -k "v140_format_alignment"` | generated docs align with `v1.4.0` document format and status conventions | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-023.json` |
| AC-504 | TC-024 | integration | `python3 -m pytest -q tests/test_v140_prd_bootstrap_traceability.py -k "downstream_surfaces_can_read_contract"` | review, refreeze, and gate surfaces can read the minimal bootstrap structure | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-024.json` |
| AC-601 | TC-025 | unit | `python3 -m pytest -q tests/test_v140_prd_bootstrap_quality.py -k "placeholder_threshold_blocks"` | placeholder threshold violations block the run | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-025.json` |
| AC-602 | TC-026 | contract | `python3 -m pytest -q tests/test_v140_prd_bootstrap_quality.py -k "ac_mapping_must_be_complete"` | incomplete AC coverage between user-story and test-case blocks the run | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-026.json` |
| AC-603 | TC-027 | integration | `python3 -m pytest -q tests/test_v140_prd_bootstrap_quality.py -k "overwrite_risk_single_recovery_command"` | overwrite risk blocks and returns one recovery command | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-027.json` |
| AC-604 | TC-028 | regression | `python3 -m pytest -q tests/test_v140_prd_bootstrap_quality.py -k "state_artifact_not_truth_source"` | state and quality artifacts remain audit evidence, not truth sources | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-028.json` |
| AC-701 | TC-029 | integration | `python3 -m pytest -q tests/test_v140_prd_bootstrap_guidance.py -k "current_status_visible"` | output clearly shows the current bootstrap status | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-029.json` |
| AC-702 | TC-030 | integration | `python3 -m pytest -q tests/test_v140_prd_bootstrap_guidance.py -k "blocked_reason_visible"` | blocked runs clearly surface the blocked reason | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-030.json` |
| AC-703 | TC-031 | integration | `python3 -m pytest -q tests/test_v140_prd_bootstrap_guidance.py -k "recommended_next_command_visible"` | output contains a recommended next command | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-031.json` |
| AC-704 | TC-032 | regression | `python3 -m pytest -q tests/test_v140_prd_bootstrap_guidance.py -k "freeze_gap_visible"` | output explains what still blocks entry into the freeze mainline | `.beacon/evidence/test-results/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure/TC-032.json` |

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
| TC-025 | Pending | from AC-601 |
| TC-026 | Pending | from AC-602 |
| TC-027 | Pending | from AC-603 |
| TC-028 | Pending | from AC-604 |
| TC-029 | Pending | from AC-701 |
| TC-030 | Pending | from AC-702 |
| TC-031 | Pending | from AC-703 |
| TC-032 | Pending | from AC-704 |

---

## Freeze Gate Notes

- 当前 QA 包把 `beacon-prd-bootstrap` 从“已有 skill/命令”提升为 `v1.4.0` 的正式 requirement feature。
- 本 feature 的验收重点不是 bootstrap 是否存在，而是：
  - 是否保持 optional support 定位
  - 是否继续 fail-closed
  - 是否清楚区分 draft 与 frozen truth
  - 是否能顺畅路由回正式 freeze 主链
- 当前文档不宣称测试已执行通过，只声明后续实现必须满足这些 coverage contract。

## Diagram Truth

- `branch-flow`
  - `intent -> bootstrap draft -> review/refreeze -> frozen requirement package`
  - `blocked bootstrap -> explain reason -> recommend next command`
- `decision-priority`
  - `frozen truth > bootstrap draft > state artifact`
  - `safety gate > convenience`
  - `mainline lifecycle > optional bootstrap surface`
