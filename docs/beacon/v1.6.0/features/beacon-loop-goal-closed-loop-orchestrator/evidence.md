# 证据：Beacon Loop Goal Closed-Loop Orchestrator

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| user-confirmed-architecture | support_advisory | conversation: delivery orchestrator AC-031..039 | accepted-for-change | change |
| change-record | support_advisory | docs/beacon/v1.6.0/change/beacon-loop-goal-closed-loop-orchestrator.md | accepted-for-change | refreeze |
| planner-research | support_advisory | docs/beacon/v1.6.0/research/beacon-loop-goal-closed-loop-orchestrator.md | promoted | truth.define |
| feature-package | requirement_truth | docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md | **frozen** | implement |
| package-tests | test_truth | docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tests.md | authoritative | truth.coverage |
| package-tasks | support_advisory | docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tasks.md | task-intent-indexed | generate |
| package-evidence | support_advisory | docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/evidence.md | evidence-indexed | evaluate |
| parent-feature | requirement_truth | docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md | frozen | dependency |
| planner-review-contract | requirement_truth | docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md | frozen | dependency |
| planner-review-runtime | support_advisory | beacon/utils/planner_review_runtime.py | indexed | generate |
| parent-implementation | support_advisory | packages/beacon-loop/ | extended | qa |
| delivery-orchestrator | support_advisory | packages/beacon-loop/src/delivery/orchestrator.ts; state.ts; eval-chain.ts; truth-fill.ts; review.ts | implemented | qa |
| intent-capture | support_advisory | packages/beacon-loop/src/intent/capture.ts; classify.ts; rules.ts | implemented | qa |
| runner-delivery-integration | support_advisory | packages/beacon-loop/src/runner/run.ts | implemented | qa |
| delivery-tests | support_advisory | packages/beacon-loop/tests/delivery-orchestrator.test.mjs (9 cases, AC-031..039) | implemented | qa |
| parent-test-compat | support_advisory | packages/beacon-loop/tests/beacon-loop.test.mjs (execute-only default migration) | implemented | qa |
| implement-import | support_advisory | run-20260610T091306Z-c638 | imported | qa |

## 决策记录

- 已接受：新建独立 feature `beacon-loop-goal-closed-loop-orchestrator`，扩展 parent runner，不 reopen parent frozen truth。
- 已接受：`scope_mode=full_parity`（delivery orchestrator 层）。
- 已接受：AC-031..AC-039 与 Delivery Loop State Model。
- 已接受：D-009..D-011 显式 defer（并行 review、LLM tie-break、AskUserQuestion UI）。
- 待完成：package refreeze 后进入 Phase E 实现。
- 已完成：Phase E delivery orchestrator 实现（AC-031..AC-039）、npm 35/35 测试、implement evidence import `run-20260610T091306Z-c638`、Beacon QA `run-20260610T172407766304`（TC-031..039 全 pass）。

## Implementation Candidate Evidence

- `beacon-loop goal` 默认 `delivery` mode；`--mode execute-only --feature <slug>` 保留 parent execute-only 路径。
- Delivery state machine：`intent_capture → planner_review → truth_gap_scan → truth_fill? → implement_loop → import_evidence → qa → release → terminal_closed`。
- 修复 `truth_gap_scan → truth_freeze_gate` 非法迁移；frozen truth gate 在 implement_loop 前 fail-closed。
- 新增 `packages/beacon-loop/tests/delivery-orchestrator.test.mjs` 覆盖 TC-031..TC-039。
- parent 回归：`beacon-loop.test.mjs` 通过 `goalDemo()` 注入 execute-only；测试隔离改用 `mkdtempSync` + 串行 test file。

## Verification Commands

```bash
npm --prefix packages/beacon-loop run build
npm --prefix packages/beacon-loop test
pytest -q tests/test_v160_beacon_loop_automation_retirement.py
beacon implement plan beacon-loop-goal-closed-loop-orchestrator --project . --version v1.6.0 --json
beacon qa run beacon-loop-goal-closed-loop-orchestrator --project . --version v1.6.0 --json
```

## 边界

`evidence.md` 是证据索引/read model，不是 final verdict。不得包含 release readiness、QA pass、implementation completion 或 source-of-truth override。
