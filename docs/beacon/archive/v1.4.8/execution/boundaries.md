# Execution Boundaries (v1.4.8)

## 核心规则

`v1.4.8` 是物料强 gate 与人类面子 skill 原子写回契约的需求冻结线，不是 runtime release 线。

Beacon 主链仍保持：

`prd -> user-story -> test-case -> implement -> qa -> release`

`change/refreeze` 只负责重新闭合 requirement truth；不得自动执行 implement、QA 或 release。

## 物料边界

本版本冻结以下边界：

- 缺失的 required material 必须阻断，不能被解释为 `not needed`
- default seed 不能等同于 approved fact
- side dossier 不能替代 canonical execution host
- support finding 不能直接成为 canonical truth
- toolkit skill 改变项目事实时必须写回 canonical material 或打开 blocking obligation
- gate 输出必须给出缺失材料、漂移字段、open obligation 和修复 route

## Support Surface 边界

Support skills may:

- challenge
- converge
- diagnose
- surface risk
- recommend a governed route
- open or require material obligations

Support skills may not:

- become canonical truth by default
- issue release verdicts by default
- silently replace `change`, `implement`, `qa`, or `release`
- invent a new lifecycle stage
- bypass `change -> prd -> user-story -> test-case -> requirement_clarity -> freeze`

## Toolkit Surface 边界

Toolkit skills may inspect and update project operational facts only when their writeback target is explicit.

For branch/service/worktree facts, canonical writeback targets are:

- `execution/git-workflow-<feature>.md`
- `.machine/execution/git-workflow-<feature>.json`
- `execution/technical-review-contract-<feature>.md`
- `.machine/execution/technical-review-contract-<feature>.json`
- `execution/architecture-blueprint.md`
- `execution/service-slice-map.md`
- canonical metadata contract

If these targets are missing or cannot be updated, the toolkit result must be `writeback_required`, `execution_host_update_required`, or `obligation_opened`; it must not report silent success.

## Delivery Boundary

Implementation may plan only after the frozen R2 requirement package is readable and gates pass.

QA and release remain blocked until:

- runtime implementation exists
- executable tests for the frozen AC matrix exist
- QA evidence is recorded
- blocking artifact update obligations are closed
- release checklist is updated with actual verification results
