---
slug: beacon-loop-stagnation-detector-v166
version: v1.6.6
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.6/features/beacon-loop-stagnation-detector-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Evidence Index: Loop Stagnation Detector v1.6.6

## Evidence Index

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-gen-truth | requirement_truth | docs/beacon/v1.6.6/features/beacon-loop-stagnation-detector-v166/truth.md | indexed | truth |
| beacon-gen-truth | test_truth | docs/beacon/v1.6.6/features/beacon-loop-stagnation-detector-v166/tests.md | indexed | truth |
| beacon-pln-review | support_advisory | docs/beacon/v1.6.6/programs/beacon-loop-meta-remediation-v166/planner-review.md | indexed | change |
| beacon-gen-implement | support_advisory | beacon/utils/stagnation_detector.py | pending | implement |
| beacon-eval-qa | qa_verdict | .beacon/qa/*.stagnation-detector*.json | pending | qa |

## Upstream Dependencies

| Upstream Feature | Module | Status |
|-----------------|--------|--------|
| beacon-agent-structured-trace-v166 | beacon/utils/agent_trace.py | delivered (Phase 1) |
| beacon-loop-pattern-registry-v165 | beacon/utils/loop_patterns.py | delivered (v1.6.5) |
| beacon-loop-failure-mode-catalog-v165 | beacon/utils/loop_failure_catalog.py | delivered (v1.6.5) |
| beacon-loop-token-budget-v165 | beacon/utils/loop_budget.py | delivered (v1.6.5) |
