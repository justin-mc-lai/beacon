# Test Cases: beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance

## Overview

**Feature**: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`  
**Test Type**: `contract + integration + regression`  
**Version**: `v1.4.2`  
**Status**: `freeze-ready`  
**Primary Truth**: `docs/beacon/v1.4.2/prd/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`  
**Upstream User Story**: `docs/beacon/v1.4.2/user-story/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`  
**Global Boundary Truth**: `docs/beacon/global-boundaries.md`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-US001-001 | contract | `python3 -m pytest -q tests/test_v142_test_contract_index.py -k "index_shape" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Test Contract Index exposes identity, truth refs, runtime/docs lines, lane membership, AC/TC/test/evidence mapping, status, and reason codes | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US001-001.json` |
| AC-002 | TC-US002-001 | contract | `python3 -m pytest -q tests/test_v142_test_contract_lanes.py -k "canonical_lanes" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Canonical lanes include feature release-facing, current runtime contract, generated surface sync, compatibility contract, legacy snapshot, and browser runtime admission | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US002-001.json` |
| AC-003 | TC-US003-001 | regression | `python3 -m pytest -q tests/test_v142_test_contract_index.py -k "release_facing_mapping_required" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Release-facing tests without AC/TC/evidence mapping are blocked unless classified as generated-surface contract checks | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US003-001.json` |
| AC-004 | TC-US004-001 | integration | `python3 -m pytest -q tests/test_v142_doctor_test_contract_governance.py -k "doctor_build_and_verify" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Doctor support surface builds and verifies test contract index without adding a public lifecycle stage | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US004-001.json` |
| AC-005 | TC-US005-001 | contract | `python3 -m pytest -q tests/test_v142_qa_lane_order.py -k "qa_first_principles_order" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | QA lane execution preserves AC order, evidence pack, coverage current/gap, continue decision, blocker stop, repair handoff, help resume, and backfill | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US005-001.json` |
| AC-006 | TC-US006-001 | integration | `python3 -m pytest -q tests/test_v142_release_test_contract_governance.py -k "release_consumes_lane_status" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Release scorecard and strict gate consume lane status and block missing, stale, failed, or unclassified release-facing evidence | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US006-001.json` |
| AC-007 | TC-US007-001 | regression | `python3 -m pytest -q tests/test_v142_generated_surface_lane.py -k "generated_surface_sync_blocks_drift" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Generated skill, metadata, command, context, and agent surfaces are lane-classified and block delivery when drift affects truth or routing | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US007-001.json` |
| AC-008 | TC-US008-001 | regression | `python3 -m pytest -q tests/test_v142_legacy_snapshot_classification.py -k "legacy_snapshot_not_release_blocker_by_default" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Historical snapshot failures route to legacy snapshot or test evolution backlog unless promoted to active compatibility contract | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US008-001.json` |
| AC-009 | TC-US009-001 | contract | `python3 -m pytest -q tests/test_v142_skill_delivery_guidance.py -k "skill_guides_contract_lane_verification" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Beacon skills instruct agents to use contract-lane verification and avoid unclassified full-suite release claims | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US009-001.json` |
| AC-010 | TC-US010-001 | regression | `python3 -m pytest -q tests/test_v142_deep_delta_adoption.py -k "deep_delta_routes_to_test_case_or_qa" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Deep test deltas route through test-case or supplemental QA; deep remains support-only and does not execute QA | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US010-001.json` |
| AC-011 | TC-US011-001 | regression | `python3 -m pytest -q tests/test_v142_planning_line_safety.py -k "v142_does_not_promote_runtime" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Freezing v1.4.2 requirement materials does not change current runtime release line, docs default line, or package version | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US011-001.json` |
| AC-012 | TC-US012-001 | integration | `python3 -m pytest -q tests/test_v142_test_contract_recovery.py -k "blocked_governance_has_repair_route" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Test contract governance blockers include reason codes and repair or resume routes through existing support surfaces | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US012-001.json` |
| AC-013 | TC-US013-001 | integration | `python3 -m pytest -q tests/test_v142_browser_runtime_admission.py -k "protected_surface_requires_session_admission" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Protected browser surfaces require session/runner admission before execution and prefer attached-session paths before bare Playwright | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US013-001.json` |
| AC-014 | TC-US014-001 | regression | `python3 -m pytest -q tests/test_v142_browser_evidence_authenticity.py -k "placeholder_transcript_is_not_browser_closure" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Browser-capable QA closure requires authentic browser evidence; transcript-only placeholder artifacts are insufficient | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US014-001.json` |
| AC-015 | TC-US015-001 | contract | `python3 -m pytest -q tests/test_v142_browser_runner_priority.py -k "protected_surface_runner_priority" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Protected-surface runner priority is represented as `web-access -> attached agent-browser -> playwright attach/CDP -> bare Playwright` | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US015-001.json` |
| AC-016 | TC-US016-001 | integration | `python3 -m pytest -q tests/test_v142_browser_runtime_admission.py -k "missing_session_bridge_yields_blocked_or_skip" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Missing session bridge on protected live surfaces yields `skip` or `blocked` reasoned outcomes rather than false product failures | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US016-001.json` |
| AC-017 | TC-US017-001 | contract | `python3 -m pytest -q tests/test_v142_browser_runner_learning.py -k "runner_learning_note_contract" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | QA writes reusable runner/admission learning notes with reason, fallback, next preferred runner, and expiry semantics | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US017-001.json` |
| AC-018 | TC-US018-001 | integration | `python3 -m pytest -q tests/test_v142_browser_lane_traceability.py -k "browser_admission_and_evidence_participate_in_lane_reasoning" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Browser-runtime admission and browser evidence obligations participate in lane/status reasoning alongside AC/TC/evidence mapping | `.beacon/evidence/test-results/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance/TC-US018-001.json` |

## Execution Results

| Test ID | Result | Notes |
| --- | --- | --- |
| TC-US001-001 | Pending | Implementation pending |
| TC-US002-001 | Pending | Implementation pending |
| TC-US003-001 | Pending | Implementation pending |
| TC-US004-001 | Pending | Implementation pending |
| TC-US005-001 | Pending | Implementation pending |
| TC-US006-001 | Pending | Implementation pending |
| TC-US007-001 | Pending | Implementation pending |
| TC-US008-001 | Pending | Implementation pending |
| TC-US009-001 | Pending | Implementation pending |
| TC-US010-001 | Pending | Implementation pending |
| TC-US011-001 | Pending | Implementation pending |
| TC-US012-001 | Pending | Implementation pending |
| TC-US013-001 | Pending | Implementation pending |
| TC-US014-001 | Pending | Implementation pending |
| TC-US015-001 | Pending | Implementation pending |
| TC-US016-001 | Pending | Implementation pending |
| TC-US017-001 | Pending | Implementation pending |
| TC-US018-001 | Pending | Implementation pending |

## Freeze Gate Notes

- Current test-case package defines requirement coverage for test contract governance but does not claim implementation or QA completion.
- The matrix intentionally uses future `tests/test_v142_*` targets as implementation obligations.
- The release-facing lane must not be considered passed until these tests exist, execute, and produce evidence through QA.
- Browser-capable QA must not be considered closed by task transcripts or placeholder runner reports alone; authentic browser evidence and protected-surface admission classification are explicit gate conditions.

## Diagram Truth

- `branch-flow`
  - `feature evolves -> contract layer identified -> test contract index -> browser admission -> lane-aware QA -> release scorecard`
  - `deep delta -> test-case adoption -> supplemental QA -> release evidence`
  - `legacy failure -> legacy_snapshot or compatibility_contract classification -> release decision`
  - `protected live surface -> session bridge check -> attached runner available? -> execute | skip | blocked`
- `decision-priority`
  - `global boundaries > frozen truth > test contract index > browser admission truth > runtime projection > full-suite text output`
  - `release-facing lane > unclassified full-suite output`
  - `authentic browser evidence > placeholder transcript`
  - `generated surface sync > stale skill guidance`
- `state-machine`
  - `unindexed -> indexed -> lane_verified -> evidence_collected -> release_consumed`
  - `protected_surface_detected -> admission_checked -> attached_runner_selected | blocked_no_bridge | degraded_last_resort`
  - `unclassified_failure -> classified_blocker | legacy_snapshot | compatibility_contract | test_evolution_backlog`
