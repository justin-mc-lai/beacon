---
slug: beacon-loop-goal-v166
version: v1.6.6
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.6/features/beacon-loop-goal-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Evidence Index: Loop Goal Orchestrator v1.6.6

## Evidence Index

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-gen-truth | requirement_truth | docs/beacon/v1.6.6/features/beacon-loop-goal-v166/truth.md | indexed | truth |
| beacon-gen-truth | test_truth | docs/beacon/v1.6.6/features/beacon-loop-goal-v166/tests.md | indexed | truth |
| beacon-pln-review | support_advisory | docs/beacon/v1.6.6/programs/beacon-loop-meta-remediation-v166/planner-review.md | indexed | change |
| beacon-gen-implement | support_advisory | beacon/utils/loop_goal_state.py | pending | implement |
| beacon-gen-implement | support_advisory | .agents/skills/beacon-loop-goal/SKILL.md | pending | implement |
| beacon-eval-qa | qa_verdict | .beacon/qa/*.loop-goal*.json | pending | qa |

## Upstream Dependencies

| Upstream Feature | Module / Skill | Status |
|-----------------|---------------|--------|
| beacon-agent-structured-trace-v166 | beacon/utils/agent_trace.py | delivered (Phase 1) |
| beacon-loop-stagnation-detector-v166 | beacon/utils/stagnation_detector.py | truth frozen (Phase 2) |
| beacon-harness-remediation-sandbox-v166 | beacon/utils/remediation_sandbox.py | truth frozen (Phase 3) |
| Governance precheck | beacon/utils/program_plan_runtime.py | delivered (v1.6.6) |
| beacon-loop-pattern-registry-v165 | beacon/utils/loop_patterns.py | delivered (v1.6.5) |
| beacon-loop-failure-mode-catalog-v165 | beacon/utils/loop_failure_catalog.py | delivered (v1.6.5) |
| beacon-loop-token-budget-v165 | beacon/utils/loop_budget.py | delivered (v1.6.5) |
| beacon-loop-readiness-audit-v165 | beacon/utils/loop_readiness.py | delivered (v1.6.5) |
| beacon-workspace-pool-lease-v165 | beacon/commands/workspace.py | delivered (v1.6.5) |

## Orchestrated Skills (36 existing)

| Harness | Count | Skills Orchestrated |
|---------|-------|-------------------|
| Planner | 7 | beacon-pln-brainstorm, beacon-pln-friction, beacon-pln-program, beacon-pln-program-auto, beacon-pln-program-interactive, beacon-pln-review, beacon-pln-source |
| Generator | 11 | beacon-gen-truth, beacon-gen-truth-init, beacon-gen-change, beacon-gen-refreeze, beacon-gen-implement, beacon-gen-prototype, beacon-gen-design, beacon-gen-design-explore, beacon-gen-design-init, beacon-gen-design-polish, beacon-gen-design-system |
| Evaluator | 5 | beacon-eval-agent, beacon-eval-qa, beacon-eval-qa-deep, beacon-eval-real-project, beacon-eval-release |
| Governor | 13 | beacon-gov-router, beacon-gov-status, beacon-gov-help, beacon-gov-doctor, beacon-gov-debug, beacon-gov-archive, beacon-gov-automation, beacon-gov-branch, beacon-gov-extract, beacon-gov-hooks, beacon-gov-learn, beacon-gov-library, beacon-gov-lighthouse, beacon-gov-metadata |
