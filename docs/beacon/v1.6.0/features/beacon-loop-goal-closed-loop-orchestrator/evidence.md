# 证据：Beacon Loop Goal Closed-Loop Orchestrator

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| user-confirmed-architecture | support_advisory | conversation: delivery orchestrator AC-031..039 | accepted-for-change | change |
| change-record | support_advisory | docs/beacon/v1.6.0/change/beacon-loop-goal-closed-loop-orchestrator.md | accepted-for-change | refreeze |
| planner-research | support_advisory | docs/beacon/v1.6.0/research/beacon-loop-goal-closed-loop-orchestrator.md | promoted | truth.define |
| feature-package | requirement_truth | docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md | **frozen R10** | implement |
| package-tests | test_truth | docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tests.md | authoritative | truth.coverage |
| package-tasks | support_advisory | docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/tasks.md | task-intent-indexed | generate |
| package-evidence | support_advisory | docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/evidence.md | evidence-indexed | evaluate |
| parent-feature | requirement_truth | docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md | frozen | dependency |
| planner-review-contract | requirement_truth | docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md | frozen | dependency |
| planner-review-runtime | support_advisory | beacon/utils/planner_review_runtime.py | indexed | generate |
| parent-implementation | support_advisory | packages/beacon-loop/ | extended R3 | qa |
| gnhf-work-copy | support_advisory | packages/gnhf/ | cloned fe202c4 | R4 fork |
| r3-backup | support_advisory | packages/beacon-loop.r3-backup-20260610/ | frozen snapshot | R4 reference |
| drill-evidence | support_advisory | /private/tmp/beacon-loop-drill run-20260610214545-infh8c | template-truth + implement blocked | R4 pivot |
| application-boundaries | support_advisory | personal-brain/projects/notes/beacon/application-boundaries.md | compiled truth | R4 architecture |
| delivery-orchestrator | support_advisory | packages/beacon-loop/src/delivery/orchestrator.ts; state.ts; eval-chain.ts; truth-fill.ts; review.ts; review-gate.ts | implemented | qa |
| intent-capture | support_advisory | packages/beacon-loop/src/intent/capture.ts; classify.ts; rules.ts; tiebreak.ts | implemented | qa |
| runner-delivery-integration | support_advisory | packages/beacon-loop/src/runner/run.ts | implemented | qa |
| delivery-tests | support_advisory | packages/beacon-loop/tests/delivery-orchestrator.test.mjs (12 cases, AC-031..039 + AC-040..042) | implemented | qa |
| parent-test-compat | support_advisory | packages/beacon-loop/tests/beacon-loop.test.mjs (execute-only default migration) | implemented | qa |
| implement-import-r1 | support_advisory | run-20260610T091306Z-c638 | imported | qa |
| implement-import-r2 | support_advisory | run-20260610T112829Z-717e | imported | qa |
| writeback-ledger | support_advisory | docs/beacon/v1.6.0/.machine/execution/implementation-writeback-ledger-beacon-loop-goal-closed-loop-orchestrator.json (R1 + R2) | indexed | evaluate |
| test-contract-index | support_advisory | docs/beacon/v1.6.0/.machine/testing/test-contract-index.json (12 TC, TC-042..044) | indexed | evaluate |
| qa-acceptance-envelope | support_advisory | docs/beacon/v1.6.0/.machine/execution/qa-acceptance-beacon-loop-goal-closed-loop-orchestrator.json | indexed | evaluate |
| qa-run-r2 | support_advisory | run-20260610T192844576131 | indexed | evaluate |
| release-gate-artifact | support_advisory | .beacon/release-gate-report.json (stage=release, run_id=run-20260610T192844576131) | indexed | release |
| release-checklist | support_advisory | docs/beacon/v1.6.0/release/checklist-v1.6.0.md | indexed | release |

## 决策记录

- 已接受：新建独立 feature `beacon-loop-goal-closed-loop-orchestrator`，扩展 parent runner，不 reopen parent frozen truth。
- 已接受：`scope_mode=full_parity`（delivery orchestrator 层）。
- 已接受：AC-031..AC-039 与 Delivery Loop State Model。
- 已接受：AC-031..AC-039 与 Delivery Loop State Model（R1）。
- **R2 撤销**：D-009..D-011 的 accepted defer（用户主权：默认 LLM tie-break + green-light 非打断；并行 review；Beacon lifecycle auto-route）。
- **R2 新增**：AC-040（LLM tie-break green-light）、AC-041（并行 review）、AC-042（lifecycle auto-route，无 AskUser UI）。
- R1 已完成：Phase E delivery orchestrator（AC-031..039）、npm 35/35、QA `run-20260610T172407766304`。
- **R2 refreeze closure**：revision **R2** frozen；`docs/beacon/v1.6.0/change/beacon-loop-goal-closed-loop-orchestrator.md` + truth-cutover refreeze-chain 完成；D-009..D-011 标记 rejected。
- **R2 implement closure**：`beacon implement import-evidence` → `run-20260610T112829Z-717e`；writeback ledger 补录 R2；触及 `tiebreak.ts`、`review-gate.ts`、`review.ts`、`orchestrator.ts`、`cli.ts`、`config/load.ts`、`delivery-orchestrator.test.mjs`。
- **R2 QA closure**：QA artifact `run-20260610T192844576131`；acceptance envelope `qa-acceptance-beacon-loop-goal-closed-loop-orchestrator.json`；matrix 12 AC（AC-031..042）；reconciliation gate cleared（R2 writeback 后 `required=false`）。
- **R2 test-contract closure**：`beacon doctor build-test-contract-index` 重建 index（9→12 TC，含 TC-042..044）；`verify-test-contract-index --strict` 产物归档。
- **R2 release-facing closure**：`beacon release check v1.6.0` 产物；`beacon gate release` → `.beacon/release-gate-report.json`；`beacon release create v1.6.0` → `docs/beacon/v1.6.0/release/checklist-v1.6.0.md`。
- **R3 implement closure**：Phase J AC-043..052；`beacon-loop` harness worker + output-schema + truth-promotion；QA 22/22；R3 frozen。
- **R4 accepted pivot**（2026-06-11）：drill 证明模板 truth_fill 语义空洞 + `--output-schema` CLI gap；主实现迁至 `packages/beacon-run`（gnhf fork）；全迭代 agent + Beacon phase prompt；AC-053..060 + Phase K tasks。
- **R5 implement closure**（2026-06-11）：
  - REV-101（AC-061）：`beacon-run` `buildPhaseHarnessArgs` truth exit 的 `projectRoot` 从 `HarnessContext.projectRoot`（即 `effectiveCwd` = worktree）传递；`runBeaconCommand` cwd 为该路径。TC-063 已 PASS（pnpm test `worktree-harness-project-root`）。
  - REV-102（AC-062）：`requirement_clarity._line_has_inline_marker` 新增 `/todos`、`go-todo-` 域名词汇豁免 + 中文 TODO 上下文豁免。TC-064 pytest 3/3 PASS。
  - REV-103（AC-063）：`buildPhaseHarnessArgs` 当 `scopeMode == "smoke"` 时 truth exit 仅调用 `truth-map resolve`，跳过 `sync-materials`。TC-065 已 PASS。
  - REV-104（AC-064）：`beacon-phase.json` 新增 `phase_promoted` + `last_harness_exit`（失败 reason_code 可见）。TC-066 已 PASS。
  - `examples/go-todo-crud/`：实现完成（go build + go test 7/7 + go test -race PASS）；`go-todo-crud-smoke` truth 提升为 frozen。
- **R6/R8 implement candidate**（2026-06-10，Phase M TASK-096..099）：
  - `packages/beacon-run/src/beacon/harness-checkpoint.ts`：`runTruthPhaseExitHarness` = smoke resolve 或 full_parity sync-materials + `truth_freeze_gate`（clarity + freeze + cutover retry）；`implementPreflightBlocked` 在 generate exit 触发 demote。
  - `packages/beacon-run/src/beacon/truth-frozen.ts`：`isFeatureTruthFrozen` / resolve payload 与 frontmatter 一致性检查。
  - `packages/beacon-run/src/beacon/phase-controller.ts`：generate entry frozen gate；truth/generate demote 至 truth + `truth-promotion.json` freeze_gate 记录。
  - `packages/beacon-run/src/beacon/phase-prompt.ts`：truth allowed harness 含 `freeze`、`truth-cutover run`。
  - `packages/beacon-run/src/beacon/scope-mode.ts`：`minimal_smoke` → `smoke`。
  - 单元测试：`truth-frozen.test.ts`、`harness-checkpoint.test.ts`（freeze_gate）、`phase-controller.test.ts`（TC-068..070）、`scope-mode.test.ts`；`pnpm exec vitest run` → **694 passed**（packages/beacon-run）。
  - **待 evaluator**：`beacon-eval-qa` 覆盖 AC-063 reconcile + AC-068（TC-065/068..070）。
- **R10 implement closure**（2026-06-12，Phase N TASK-101..103）：
  - AC-069：`packages/beacon-run/e2e/e2e-go-todo-worktree.test.ts` + `packages/beacon-loop/tests/beacon-loop.test.mjs` TC-071（dry-run；live opt-in `BEACON_RUN_E2E_GO_TODO=1`）。
  - AC-070：`docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md` + `packages/beacon-loop/src/spine/show.ts` + TC-072。
  - AC-071：`packages/beacon-run/src/core/stop-when-gate.ts` + `--stop-check-cmd` + TC-073 / vitest `stop-when-exec-gate`。
  - `beacon implement import-evidence` → `run-20260612T110636Z-c038`；writeback ledger 补录 **R10**。
  - `beacon implement plan` → `plan-beacon-loop-goal-closed-loop-orchestrator-r10`（revision **R10**）。
- **R10 QA closure**：QA artifact `run-20260612T182801183358`；38/38 AC、41/41 scenario（TC-071..073 PASS）。
- **R10 release-facing closure**：
  - `implementation-first-reconciliation` refreeze complete（`-reconciliation.json` status=completed）。
  - `beacon doctor build/verify-test-contract-index` + `sync-technical-review-contract --revision-id R10`。
  - `beacon release check v1.6.0` 产物归档；`beacon release create v1.6.0` → `docs/beacon/v1.6.0/release/checklist-v1.6.0.md`。
  - **注意**：`beacon gate release` 是 **v1.6.0 全版本 runtime promotion** 门禁（terminal.json / formal package 等），不是本 feature v1.6.1 止血 patch 的 feature release 路径。

## Implementation Candidate Evidence

- `beacon-loop goal` 默认 `delivery` mode；`--mode execute-only --feature <slug>` 保留 parent execute-only 路径。
- Delivery state machine：`intent_capture → planner_review → truth_gap_scan → truth_fill（条件分支）→ implement_loop → import_evidence → qa → release → terminal_closed`。
- 修复 `truth_gap_scan → truth_freeze_gate` 非法迁移；frozen truth gate 在 implement_loop 前 fail-closed。
- 新增 `packages/beacon-loop/tests/delivery-orchestrator.test.mjs` 覆盖 TC-031..TC-039。
- parent 回归：`beacon-loop.test.mjs` 通过 `goalDemo()` 注入 execute-only；测试隔离改用 `mkdtempSync` + 串行 test file。
- R2：`packages/beacon-loop/src/intent/tiebreak.ts` 默认 green-light continue；`intent-tiebreak.json` 落盘；ambiguous 默认不再进入 `user_decision_pending`（`--strict-interrupt` opt-in）。
- R2：`packages/beacon-loop/src/delivery/review-gate.ts` P0 hard stop / P1 green-light；`recommended_route` 驱动下一 delivery state。
- R2：`packages/beacon-loop/src/delivery/review.ts` parallel fixture + `--execution-mode parallel_subagent_review`。
- R2：测试扩展 TC-042（LLM tie-break）、TC-043（parallel review）、TC-044（lifecycle auto-route）；npm test 38/38（packages/beacon-loop）。

## Verification Commands

```bash
npm --prefix packages/beacon-loop run build
npm --prefix packages/beacon-loop test
pytest -q tests/test_v160_beacon_loop_automation_retirement.py
beacon implement import-evidence beacon-loop-goal-closed-loop-orchestrator --project . --version v1.6.0 \
  --source-ref docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/evidence.md \
  --changed-file packages/beacon-loop/src/intent/tiebreak.ts \
  --summary-ref docs/beacon/v1.6.0/execution/implementation-plan-beacon-loop-goal-closed-loop-orchestrator.md \
  --approved-by operator --json
beacon qa run beacon-loop-goal-closed-loop-orchestrator --project . --version v1.6.0 --json
beacon doctor build-test-contract-index beacon-loop-goal-closed-loop-orchestrator --project-root . --version v1.6.0 --json
beacon release check v1.6.0 --project . --json
beacon release create v1.6.0 --project .
# R10 Phase N smoke
npm --prefix packages/beacon-loop test -- --test-name-pattern "TC-071|TC-072|TC-073"
cd packages/beacon-run && pnpm exec vitest run src/core/orchestrator.test.ts -t stop-when
# R5 verification
cd packages/beacon-run && pnpm exec vitest run
# R6/R8 verification (truth_freeze_gate)
cd packages/beacon-run && pnpm exec vitest run src/beacon/truth-frozen.test.ts src/beacon/harness-checkpoint.test.ts src/beacon/phase-controller.test.ts src/beacon/scope-mode.test.ts
python3 -m pytest tests/test_requirement_clarity_domain_vocab_r5.py -q
cd examples/go-todo-crud && go build ./... && go test ./... && go test -race ./...
```

## 边界

`evidence.md` 是证据索引/read model，不是 final verdict。不得包含 release readiness、QA pass、implementation completion 或 source-of-truth override。
