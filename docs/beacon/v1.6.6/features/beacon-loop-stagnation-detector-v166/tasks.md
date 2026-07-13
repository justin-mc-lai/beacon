---
slug: beacon-loop-stagnation-detector-v166
version: v1.6.6
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.6/features/beacon-loop-stagnation-detector-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Tasks: Loop Stagnation Detector v1.6.6

## Task List

- [ ] TASK-001 truth → `beacon-gen-truth` — freeze truth.md + tests.md + tasks.md + evidence.md
- [ ] TASK-002 implement → `beacon-gen-implement` — create `beacon/utils/stagnation_detector.py` with detect_repeat_failure, detect_repeat_labor, detect_plateau, build_stagnation_report
- [ ] TASK-003 implement → `beacon-gen-implement` — integrate stagnation signal into `beacon/commands/doctor.py` loop-audit
- [ ] TASK-004 implement → `beacon-gen-implement` — create `tests/test_v166_stagnation_detector.py` with 8 test cases
- [ ] TASK-005 qa → `beacon-eval-qa` — run TC-ST-* matrix, accept all AC-001..008
- [ ] TASK-006 release → `beacon-eval-release` — update SUMMARY.md delivery status, release note
