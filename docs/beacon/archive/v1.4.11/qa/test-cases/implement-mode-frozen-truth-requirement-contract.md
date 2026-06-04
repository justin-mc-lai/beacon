# Test Cases: Implement Mode Frozen Truth Requirement Contract

**Feature**: `implement-mode-frozen-truth-requirement-contract`
**Version**: `v1.4.11`
**Status**: `refreeze-input`
**Date**: `2026-05-29`

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-IMPL-TRUTH-001 | prompt | `python3 -m pytest -q tests/test_v1411_implement_mode_frozen_truth_requirement_contract.py -k "design_truth_injected_when_present"` | Prompt includes `DESIGN.md` as project-level design truth when the file exists. | `.beacon/evidence/test-results/implement-mode-frozen-truth-requirement-contract/TC-IMPL-TRUTH-001.json` |
| AC-002 | TC-IMPL-TRUTH-002 | prompt | `python3 -m pytest -q tests/test_v1411_implement_mode_frozen_truth_requirement_contract.py -k "product_truth_injected_when_present"` | Prompt includes `PRODUCT.md` as project-level product truth when the file exists. | `.beacon/evidence/test-results/implement-mode-frozen-truth-requirement-contract/TC-IMPL-TRUTH-002.json` |
| AC-003 | TC-IMPL-TRUTH-003 | prompt | `python3 -m pytest -q tests/test_v1411_implement_mode_frozen_truth_requirement_contract.py -k "missing_project_truth_does_not_block"` | Prompt generation succeeds when `DESIGN.md` and `PRODUCT.md` are absent. | `.beacon/evidence/test-results/implement-mode-frozen-truth-requirement-contract/TC-IMPL-TRUTH-003.json` |
| AC-004 | TC-IMPL-TRUTH-004 | prompt | `python3 -m pytest -q tests/test_v1411_implement_mode_frozen_truth_requirement_contract.py -k "project_truth_separated_from_frozen_truth"` | Prompt separates project-level product/design truth from frozen PRD/user-story/test-case truth. | `.beacon/evidence/test-results/implement-mode-frozen-truth-requirement-contract/TC-IMPL-TRUTH-004.json` |
| AC-005 | TC-IMPL-TRUTH-005 | prompt | `python3 -m pytest -q tests/test_v1411_implement_mode_frozen_truth_requirement_contract.py -k "ac_coverage_matrix_required"` | Prompt requires AC coverage matrix before QA handoff. | `.beacon/evidence/test-results/implement-mode-frozen-truth-requirement-contract/TC-IMPL-TRUTH-005.json` |
| AC-006 | TC-IMPL-TRUTH-006 | prompt | `python3 -m pytest -q tests/test_v1411_implement_mode_frozen_truth_requirement_contract.py -k "ac_coverage_statuses_required"` | Prompt requires `pass`, `partial`, and `blocked` statuses. | `.beacon/evidence/test-results/implement-mode-frozen-truth-requirement-contract/TC-IMPL-TRUTH-006.json` |
| AC-007 | TC-IMPL-TRUTH-007 | prompt | `python3 -m pytest -q tests/test_v1411_implement_mode_frozen_truth_requirement_contract.py -k "ac_coverage_evidence_required"` | Prompt requires evidence or blocking note per AC row. | `.beacon/evidence/test-results/implement-mode-frozen-truth-requirement-contract/TC-IMPL-TRUTH-007.json` |
| AC-008 | TC-IMPL-TRUTH-008 | boundary | `python3 -m pytest -q tests/test_v1411_implement_mode_frozen_truth_requirement_contract.py -k "no_new_public_implement_mode_skill"` | No new public implement mode skill is introduced for simple, team, or ralph. | `.beacon/evidence/test-results/implement-mode-frozen-truth-requirement-contract/TC-IMPL-TRUTH-008.json` |
| AC-009 | TC-IMPL-TRUTH-009 | regression | `python3 -m pytest -q tests/test_v1411_implement_mode_frozen_truth_requirement_contract.py` | Regression suite covers project truth injection and AC coverage matrix wording. | `.beacon/evidence/test-results/implement-mode-frozen-truth-requirement-contract/TC-IMPL-TRUTH-009.json` |
| AC-010 | TC-IMPL-TRUTH-010 | scope | `python3 -m pytest -q tests/test_v1411_implement_mode_frozen_truth_requirement_contract.py -k "scope_stays_default_prompt_only"` | Tests and implementation stay anchored to default prompt injection, not team-worker or ralph hash mechanisms. | `.beacon/evidence/test-results/implement-mode-frozen-truth-requirement-contract/TC-IMPL-TRUTH-010.json` |

## Explicit Non Coverage

- These tests do not execute team-mode sub-agent worker injection.
- These tests do not enforce ralph baseline hash verification.
- These tests do not create or overwrite `PRODUCT.md` or `DESIGN.md`.
- These tests do not claim QA acceptance or release readiness by themselves.
