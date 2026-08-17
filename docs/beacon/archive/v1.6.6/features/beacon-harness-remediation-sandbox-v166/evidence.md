---
slug: beacon-harness-remediation-sandbox-v166
version: v1.6.6
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.6/features/beacon-harness-remediation-sandbox-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Evidence Index: Harness Remediation Sandbox v1.6.6

## Evidence Index

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-gen-truth | requirement_truth | docs/beacon/archive/v1.6.6/features/beacon-harness-remediation-sandbox-v166/truth.md | indexed | truth |
| beacon-gen-truth | test_truth | docs/beacon/archive/v1.6.6/features/beacon-harness-remediation-sandbox-v166/tests.md | indexed | truth |
| beacon-pln-review | support_advisory | docs/beacon/archive/v1.6.6/programs/beacon-loop-meta-remediation-v166/planner-review.md | indexed | change |
| beacon-gen-implement | support_advisory | beacon/utils/remediation_sandbox.py | pending | implement |
| beacon-eval-qa | qa_verdict | .beacon/qa/*.remediation-sandbox*.json | pending | qa |

## Upstream Dependencies

| Upstream Feature | Module | Status |
|-----------------|--------|--------|
| beacon-agent-structured-trace-v166 | beacon/utils/agent_trace.py | delivered (Phase 1) |
| beacon-loop-stagnation-detector-v166 | beacon/utils/stagnation_detector.py | truth frozen (Phase 2) |
| beacon-workspace-pool-lease-v165 | beacon/commands/workspace.py | delivered (v1.6.5) |
