---
slug: beacon-loop-goal-v166
version: v1.6.6
status: draft
revision_id: R6
language: zh
truth_ref: docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Evidence Index: Loop Goal Orchestrator v1.6.6

## Evidence Index

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-gen-truth | requirement_truth | docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/truth.md | indexed | truth |
| beacon-gen-truth | test_truth | docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/tests.md | indexed | truth |
| beacon-pln-review | support_advisory | docs/beacon/archive/v1.6.6/programs/beacon-loop-meta-remediation-v166/planner-review.md | indexed | change |
| beacon-gen-implement | support_advisory | beacon/utils/loop_goal_state.py | linked | implement |
| beacon-gen-implement | support_advisory | .agents/skills/beacon-loop-goal/SKILL.md | linked | implement |
| beacon-gen-implement | support_advisory | skills/beacon/beacon-loop-goal/SKILL.md | linked | implement |
| beacon-gen-implement | support_advisory | beacon/utils/agent_surface.py | linked | implement |
| beacon-gen-implement | support_advisory | beacon/utils/agent_eval_kit.py | linked | implement |
| beacon-gen-implement | support_advisory | fixtures/agent-eval/v161/live/beacon-loop-goal.prompt.txt | linked | implement |
| beacon-gen-implement | support_advisory | docs/beacon/archive/v1.6.6/execution/implementation-summary-beacon-loop-goal-v166-r2.md | linked | implement |
| beacon-eval-qa | qa_verdict | .beacon/qa/features/beacon-loop-goal-v166/scorecard.json; .beacon/qa/status.json; .beacon/evidence/auto-test/run-20260715T135541350657/summary.json | passed | qa |
| beacon-gen-change | requirement_truth | docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/truth.md; docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/tests.md | R3 review-routing refreeze target | refreeze |
| beacon-gen-implement | support_advisory | skills/beacon/beacon-loop-goal/SKILL.md; .agents/skills/beacon-loop-goal/SKILL.md; beacon/utils/loop_goal_state.py; tests/test_v166_loop_goal.py; docs/beacon/archive/v1.6.6/execution/implementation-summary-beacon-loop-goal-v166-r3.md | R3 implemented, formal QA still evaluator-owned | implement |
| beacon-pln-review | support_advisory | .beacon/state/planner-review/beacon-loop-goal-v166/pln-review-20260715t122003z.json | R4 accepted for change | change |
| beacon-gen-change | requirement_truth | docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/truth.md; docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/tests.md; docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/tasks.md; docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/evidence.md | R4 standard execution flow refreeze target | refreeze |

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

## Public Skill Inventory (38 host-visible)

`beacon-loop-goal` is the 38th public host-visible skill and is counted as a governor skill. It orchestrates the other 37 public skills; it does not self-orchestrate.

| Harness | Count | Skills Orchestrated |
|---------|-------|-------------------|
| Planner | 7 | beacon-pln-brainstorm, beacon-pln-friction, beacon-pln-program, beacon-pln-program-auto, beacon-pln-program-interactive, beacon-pln-review, beacon-pln-source |
| Generator | 11 | beacon-gen-truth, beacon-gen-truth-init, beacon-gen-change, beacon-gen-refreeze, beacon-gen-implement, beacon-gen-prototype, beacon-gen-design, beacon-gen-design-explore, beacon-gen-design-init, beacon-gen-design-polish, beacon-gen-design-system |
| Evaluator | 5 | beacon-eval-agent, beacon-eval-qa, beacon-eval-qa-deep, beacon-eval-real-project, beacon-eval-release |
| Governor | 15 | beacon-gov-router, beacon-gov-status, beacon-gov-help, beacon-gov-doctor, beacon-gov-debug, beacon-gov-archive, beacon-gov-automation, beacon-gov-branch, beacon-gov-extract, beacon-gov-hooks, beacon-gov-learn, beacon-gov-library, beacon-gov-lighthouse, beacon-gov-metadata, beacon-loop-goal |

## R4 Standard Execution Flow Evidence

- Planner review runtime: `.beacon/state/planner-review/beacon-loop-goal-v166/pln-review-20260715t122003z.json`
- Highest severity: `P1`
- Recommended route: `beacon-gen-change`
- User decision: accepted to write Standard Execution Flow into v1.6.6 canonical package surfaces, then refreeze.
- Scope: loop-goal must fail closed before implement unless canonical refreeze is committed, feature worktree has reconciled/stashed stale local refreeze, canonical baseline commit is merged, verification bundle is complete, and workspace admission passes.

## R5 Truth-on-main Closure Evidence

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-gen-change | requirement_truth | docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/truth.md (+ tests/tasks/evidence) | R5 draft reopen | refreeze |
| beacon-gen-implement | support_advisory | beacon/utils/git_alignment.py; change_refreeze.py; freeze.py; reopen.py; workspace_admission.py | partial CLI gate landed pre-R5; file write + CLI precheck still open for implement | implement |
| beacon-gen-implement | support_advisory | tests/test_v166_truth_canonical_branch.py | landed for AC-022/024/026 partial | implement |
| beacon-loop-goal | support_advisory | skills/beacon/beacon-loop-goal/SKILL.md Step 2 truth_canonical check | landed | implement |

### R5 Accepted Scope

- Close remaining soft gaps so requirement truth cannot be authored or frozen outside `truth_canonical`.
- Make standard_execution_precheck evidence CLI-owned.
- Keep governor routing-only; do not make loop-goal execute git itself.

## R6 Human-gate Redefinition Evidence

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-gen-change | requirement_truth | docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/{truth,tests,tasks,evidence}.md | R6 draft (AC-014 rewrite + AC-027..030) | refreeze |
| user confirmation | decision | chat: confirm Phase A/B/C human-gate set | accepted | change |
| beacon-gen-implement | support_advisory | loop_goal_state.record_review_decision; status loop-goal --resume; SKILL.md | queued for post-freeze implement | implement |

### R6 Accepted Scope

- Default human stops: `release_gate` + review blocking (`P0` | `user_decision_required` | drift routes only).
- Standalone P1 → advisory continue into `standard_execution_precheck` with severity/continue audit.
- Same-session skill continue + `beacon status loop-goal --resume`.
- Observability: human_stops_per_run / stop_reason / p1_continue_count (/ pseudo_stall when detectable).
- AC-007 unchanged: release never auto-decide.
