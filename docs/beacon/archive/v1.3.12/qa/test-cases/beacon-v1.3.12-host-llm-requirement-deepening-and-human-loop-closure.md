# Test Cases: Beacon v1.3.12 host-LLM requirement deepening and human-loop closure

## Overview

**Feature**: Beacon v1.3.12 host-LLM requirement deepening and human-loop closure
**Test Type**: ALL
**Version**: v1.3.12
**Generated**: 2026-05-05 18:30
**Requested Mode**: auto
**Effective Mode**: host-or-rule
**Fallback Reason**: capability-dependent
**Memory Context**: v1.3.11 requirement closure + host-native semantic runtime
**AC Matrix JSON**: docs/beacon/archive/v1.3.12/.machine/qa/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.ac-test-matrix.json
**QA9 Matrix JSON**: docs/beacon/archive/v1.3.12/.machine/qa/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.qa9-matrix.json
**Story Scenario Map JSON**: docs/beacon/archive/v1.3.12/.machine/qa/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.story-scenario-map.json
**Prototype Plan Present**: False
**Prototype Coverage Present**: False
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-001 | unit | `python3 -m pytest -q tests/test_v1312_requirement_deepening.py -k "envelope_fields"` | Requirement envelope contains all required deepening dimensions | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-001.json` |
| AC-002 | TC-002 | contract | `python3 -m pytest -q tests/test_v1312_requirement_deepening.py -k "source_truth_refs"` | Every inferred envelope item keeps a traceable source truth reference | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-002.json` |
| AC-003 | TC-003 | unit | `python3 -m pytest -q tests/test_v1312_requirement_deepening.py -k "machine_readable_envelope"` | Envelope is emitted as stable machine-readable artifact | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-003.json` |
| AC-004 | TC-004 | contract | `python3 -m pytest -q tests/test_v1312_requirement_deepening.py -k "no_public_stage_expansion"` | Deepening stays internal to requirement compile and does not create a new public stage | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-004.json` |
| AC-101 | TC-005 | unit | `python3 -m pytest -q tests/test_v1312_story_discovery.py -k "candidate_families"` | Story discovery emits all required candidate families from PRD envelope | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-005.json` |
| AC-102 | TC-006 | contract | `python3 -m pytest -q tests/test_v1312_story_discovery.py -k "candidate_statuses"` | Story candidates preserve explicit already_frozen, missing, deferred, and rejected states | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-006.json` |
| AC-103 | TC-007 | regression | `python3 -m pytest -q tests/test_v1312_story_discovery.py -k "not_just_ac_reprojection"` | Story discovery adds non-trivial candidates beyond current AC restatement | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-007.json` |
| AC-104 | TC-008 | unit | `python3 -m pytest -q tests/test_v1312_story_discovery.py -k "story_writeback_targets"` | Accepted story candidates write back to the correct story sections | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-008.json` |
| AC-201 | TC-009 | unit | `python3 -m pytest -q tests/test_v1312_test_case_expansion.py -k "coverage_families"` | Test-case expansion emits all required risk and boundary coverage families | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-009.json` |
| AC-202 | TC-010 | contract | `python3 -m pytest -q tests/test_v1312_test_case_expansion.py -k "coverage_rationale"` | Every coverage candidate retains traceable rationale and source refs | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-010.json` |
| AC-203 | TC-011 | regression | `python3 -m pytest -q tests/test_v1312_test_case_expansion.py -k "beyond_default_matrix"` | Expanded test cases go beyond default AC to TC projection | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-011.json` |
| AC-204 | TC-012 | unit | `python3 -m pytest -q tests/test_v1312_test_case_expansion.py -k "coverage_writeback"` | Accepted coverage candidates write back into formal QA docs and machine coverage artifacts | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-012.json` |
| AC-301 | TC-013 | integration | `python3 -m pytest -q tests/test_v1312_supplement_protocol.py -k "shared_contract"` | PRD, user-story, and test-case surfaces share one supplement contract | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-013.json` |
| AC-302 | TC-014 | integration | `python3 -m pytest -q tests/test_v1312_supplement_protocol.py -k "stage_routing"` | Accepted supplements route to the correct requirement layer | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-014.json` |
| AC-303 | TC-015 | unit | `python3 -m pytest -q tests/test_v1312_supplement_protocol.py -k "decision_spectrum"` | Human decisions preserve accepted, rejected, and deferred outcomes with reasons | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-015.json` |
| AC-304 | TC-016 | regression | `python3 -m pytest -q tests/test_v1312_supplement_protocol.py -k "no_silent_manual_patch"` | Manual markdown edits without machine decision trail are rejected or surfaced as drift | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-016.json` |
| AC-401 | TC-017 | unit | `python3 -m pytest -q tests/test_v1312_candidate_ledger.py -k "ledger_fields"` | Candidate ledger stores the full required audit field set | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-017.json` |
| AC-402 | TC-018 | integration | `python3 -m pytest -q tests/test_v1312_candidate_ledger.py -k "revision_transaction_binding"` | Accepted candidates bind to revision and transaction identity before re-freeze | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-018.json` |
| AC-403 | TC-019 | integration | `python3 -m pytest -q tests/test_v1312_candidate_ledger.py -k "anti_drift_refreeze"` | Requirement deepening writeback preserves anti-drift auditability and fail-closed behavior | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-019.json` |
| AC-404 | TC-020 | unit | `python3 -m pytest -q tests/test_v1312_candidate_ledger.py -k "queryable_future_rounds"` | Rejected and deferred candidates remain queryable in future requirement rounds | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-020.json` |
| AC-501 | TC-021 | integration | `python3 -m pytest -q tests/test_v1312_delivery_completeness.py -k "read_model_fields"` | Delivery layer can read unresolved gaps, downgrade state, and coverage completeness | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-021.json` |
| AC-502 | TC-022 | contract | `python3 -m pytest -q tests/test_v1312_delivery_completeness.py -k "readiness_verdicts"` | Requirement completeness emits deterministic pass, pass_with_downgrade, and blocked verdicts | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-022.json` |
| AC-503 | TC-023 | integration | `python3 -m pytest -q tests/test_v1312_delivery_completeness.py -k "deterministic_blocking"` | High-severity gaps and unacceptable downgrade states block readiness with explicit reasons | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-023.json` |
| AC-504 | TC-024 | contract | `python3 -m pytest -q tests/test_v1312_delivery_completeness.py -k "no_delivery_truth_rewrite"` | Delivery surfaces can read completeness but cannot bypass requirement truth ownership | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-024.json` |
| AC-601 | TC-028 | contract | `python3 -m pytest -q tests/test_v1312_acceptance_kit.py -k "unified_acceptance_contract"` | Acceptance Kit v1 is emitted as a shared machine-readable contract for all requirement surfaces | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-028.json` |
| AC-602 | TC-029 | contract | `python3 -m pytest -q tests/test_v1312_acceptance_kit.py -k "layered_verdict_ladder"` | Acceptance Kit v1 emits the five verdict layers and enforces fail-fast ordering | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-029.json` |
| AC-701 | TC-030 | integration | `python3 -m pytest -q tests/test_v1312_board_projection.py -k "gate_projection_and_jumpback"` | status / board surfaces expose gate card points and jump-back links to supplement items | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-030.json` |
| AC-702 | TC-031 | integration | `python3 -m pytest -q tests/test_v1312_real_project_proof.py -k "shared_acceptance_proof"` | real-project-validation, release proof, and regression checks consume the same Acceptance Kit evidence chain | `.beacon/evidence/test-results/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure/TC-031.json` |

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
| TC-028 | Pending | from AC-601 |
| TC-029 | Pending | from AC-602 |
| TC-030 | Pending | from AC-701 |
| TC-031 | Pending | from AC-702 |

---

## Freeze Gate Notes

- 当前 test-case 包已经达到 requirement freeze 所需粒度：
  - AC 与 TC 一一绑定
  - `story discovery / supplement protocol / candidate ledger / completeness verdict` 都进入可执行断言面
  - `blocked / pass_with_downgrade / pass` 三类 readiness 语义已经成为正式验收对象
- 当前文档不宣称测试已执行通过；它声明的是：
  - 后续实现必须遵守这套 coverage contract
  - 如果 machine completeness verdict 与这里的 gate 语义不一致，requirement freeze 必须视为失效

## Diagram Truth

- `branch-flow`
  - 覆盖补料候选从 `brainstorm` 回流到 `user-story / test-case`，以及必要时进入 `change`
  - 覆盖 `prototype -> implement -> qa -> release` 的验收分支与回退分支
- `decision-priority`
  - 覆盖 `accepted / rejected / deferred` 的候选处理顺序
  - 覆盖 `pass / pass_with_downgrade / blocked` 的 delivery 判定顺序
  - 覆盖当候选优先级与交付优先级冲突时的显式记录
