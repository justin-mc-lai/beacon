# Test Cases: beacon-v1.4.7-change-refreeze-one-shot-requirement-closure

## Overview

**Feature**: `beacon-v1.4.7-change-refreeze-one-shot-requirement-closure`
**Version**: `v1.4.7`
**Status**: `freeze-ready`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-CR47-001 | contract | `python3 -m pytest -q tests/test_v147_change_refreeze_one_shot.py -k "change_refreeze_entry_is_support_only"` | one-shot refreeze is exposed under the change family and does not register a new primary lifecycle stage |
| AC-002 | TC-CR47-002 | contract | `python3 -m pytest -q tests/test_v147_change_refreeze_one_shot.py -k "refreeze_chain_declares_required_truth_surfaces"` | route declares `change / prd / user-story / test-case / requirement_clarity / freeze` coverage |
| AC-003 | TC-CR47-003 | integration | `python3 -m pytest -q tests/test_v147_change_refreeze_one_shot.py -k "refreeze_transaction_records_surface_statuses"` | transaction envelope records touched surfaces, per-surface statuses, truth revision refs, refreeze status, next route, and blocked reason |
| AC-004 | TC-CR47-004 | boundary | `python3 -m pytest -q tests/test_v147_change_refreeze_one_shot.py -k "partial_truth_refresh_fail_closes"` | partial downstream refresh leaves refreeze blocked and explains the stale surface |
| AC-005 | TC-CR47-005 | gate | `python3 -m pytest -q tests/test_v147_change_refreeze_one_shot.py -k "execution_routes_block_until_refreeze_complete"` | implement, QA, and release are blocked until refreeze is complete |
| AC-006 | TC-CR47-006 | docs | `python3 -m pytest -q tests/test_v147_change_refreeze_one_shot.py -k "human_summary_explains_chain_state"` | human summary states changed scope, refreshed surfaces, blockers, and next safe route |
| AC-007 | TC-CR47-007 | regression | `python3 -m pytest -q tests/test_v147_change_refreeze_one_shot.py -k "one_shot_refreeze_does_not_execute_delivery_stages"` | one-shot refreeze does not execute implementation, QA, release, or autonomous truth mutation |

## Required Scenario Families

1. Complete refreeze path
2. Partial PRD-only refresh blocked path
3. Test-case refresh failure path
4. Stale truth barrier blocks implement
5. Operator summary path
6. Support-surface boundary regression

## Boundary and Negative Coverage

- must not create a new public lifecycle stage
- must not bypass `prd -> user-story -> test-case`
- must not treat generated drafts as frozen truth
- must not auto-run implementation, QA, or release

## QA Verification Note

This document defines coverage truth for the implemented package. The executable matrix is backed by `tests/test_v147_change_refreeze_one_shot.py`.
