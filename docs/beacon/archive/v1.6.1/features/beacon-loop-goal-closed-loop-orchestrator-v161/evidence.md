# 证据：Beacon Loop Goal Closed-Loop Orchestrator v1.6.1

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| planner-research | support_advisory | docs/beacon/archive/v1.6.1/research/beacon-loop-goal-closed-loop-orchestrator.md | promoted | change |
| feature-package | requirement_truth | docs/beacon/archive/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md | frozen R1 | implement |
| package-tests | test_truth | docs/beacon/archive/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/tests.md | authoritative | truth.coverage |
| upstream-loop-v160 | requirement_truth | docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md | frozen R10 | dependency |
| upstream-program-plan | requirement_truth | docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md | frozen R4 | dependency |
| operator-guide | support_advisory | docs/beacon/archive/v1.6.1/execution/long-task-operator-guide.md | present | operator |
| upstream-agent-eval | requirement_truth | docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md | frozen R2 | dependency |

## 决策记录

- 用户确认路线 **A**：v1.6.1 + **pre-main**；不在 v1.6.0 docs line 上开 R11。
- UD-001..007 锁定于 research closure（pln-review-20260616t023732z）。
- v1.6.0 R10 保持 frozen；v1.6.1 delta 在本 package AC-072..075。

## Gate 证据（R1 freeze — 2026-06-15）

| gate | command | status | notes |
|------|---------|--------|-------|
| truth-map | `beacon truth-map rebuild-machine … -v v1.6.1` | written | package registered |
| TIG | `beacon doctor verify-truth-integrity … --mode block` | pass | upstream AC delegated in tests |
| refreeze-chain | `beacon change … --refreeze-chain` | blocked:revision_not_frozen | 新 feature 首冻 |
| freeze R1 | `beacon freeze … --version v1.6.1` | frozen | 与 agent-eval R1 同路径 |

## Boundary

`evidence.md` 为索引/read model。Loop 不得承载 formal QA/release verdict authority。
