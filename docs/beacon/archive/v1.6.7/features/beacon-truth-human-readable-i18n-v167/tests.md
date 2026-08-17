---
slug: beacon-truth-human-readable-i18n-v167
version: v1.6.7
status: frozen
revision_id: R1
truth_ref: docs/beacon/archive/v1.6.7/features/beacon-truth-human-readable-i18n-v167/truth.md
---

# Tests: beacon-truth-human-readable-i18n-v167

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-HR-001 | TC-HR-001 | contract | `pytest tests/test_v167_truth_human_readable_i18n.py::test_self_truth_has_l0 -q` | self L0 heading |
| AC-HR-002 | TC-HR-002 | contract | `pytest ...::test_l0_budget_self -q` | self within budget |
| AC-HR-003 | TC-HR-003 | contract | `pytest ...::test_l0_four_questions -q` | four questions cues |
| AC-HR-004 | TC-HR-004 | contract | `pytest ...::test_norms_files_exist -q` | zh+en norms present |
| AC-HR-005 | TC-HR-005 | unit | `pytest ...::test_gate_missing_l0 -q` | reason truth_human_l0_missing |
| AC-HR-006 | TC-HR-006 | unit | `pytest ...::test_l0_not_sufficient_for_ac -q` | L1 still required |
| AC-HR-007 | TC-HR-007 | contract | `pytest ...::test_language_enum -q` | language values |
| AC-HR-008 | TC-HR-008 | contract | `pytest ...::test_bilingual_fixture -q` | dual L0 |
| AC-HR-009 | TC-HR-009 | contract | `pytest ...::test_examples_exist -q` | examples zh+en |
| AC-HR-010 | TC-HR-010 | contract | `beacon goal axis validate -v v1.6.7` | lake on axis |
| AC-HR-012 | TC-HR-012 | negative | `pytest ...::test_humanizer_must_not_drop_ac -q` | AC ids preserved |

## Legal / Illegal

| TC ID | Path | Assertion |
|-------|------|-----------|
| TC-HR-LEGAL-01 | L0+L1 present | freeze may proceed (prose gate) |
| TC-HR-ILLEGAL-01 | no L0 | freeze blocked |
| TC-HR-ILLEGAL-02 | L0 only, empty AC | package invalid |
