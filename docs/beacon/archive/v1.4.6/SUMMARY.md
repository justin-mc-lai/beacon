# Beacon v1.4.6 总览

## 版本状态

- `v1.4.6` 当前主题是：`anti-drift skill contracts and enforced decision surfaces`
- 当前版本状态：`current_runtime_release`
- 当前 runtime/default docs 现为 `v1.4.6`
- `v1.4.6` 是在 `v1.4.5` guidance-first 与 lightweight contract 基线之上，继续把 host-visible skill 行为面收紧成更强的 anti-drift requirement package

## 版本目标

`v1.4.6` 聚焦一条总线：

> 让 Beacon 的 public skill 与 support surface 先在 contract 层更难漂移，再由既有的 truth、evidence、state 与 gate 治理承接后续执行与验收。

## 当前需求包

- PRD
  - `docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
  - `docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
  - `docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-implementation-first-reconciliation-governance.md`
- User Story
  - `docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
  - `docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
  - `docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-implementation-first-reconciliation-governance.md`
- Test Cases
  - `docs/beacon/archive/v1.4.6/qa/test-cases/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
  - `docs/beacon/archive/v1.4.6/qa/test-cases/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
  - `docs/beacon/archive/v1.4.6/qa/test-cases/beacon-v1.4.6-implementation-first-reconciliation-governance.md`

## 正式子线

- `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`
- `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance`
- `beacon-v1.4.6-implementation-first-reconciliation-governance`

## 当前边界判断

- `v1.4.6` 不新增公开一级主命令，也不新增新的公开主生命周期 stage。
- `brainstorm`、`deep`、`ceo-review`、`design-review`、`help`、`status`、`doctor` 仍是 support surfaces，不得成为 truth source 或 gate source。
- `v1.4.6` 的重点不是新增更多 skill，而是冻结更强的 public skill contract anatomy、anti-rationalization、challenge binding 与 machine-checkable enforcement。
- `v1.4.6` 也补充 Beacon automation/jobs 的项目级 feedback loop：nightly QA 必须留下可供下轮和 gated implement 消费的 queue-governed machine state。
- `v1.4.6` 进一步把 project-local automation bootstrap 收口到 `beacon automation init --project-root .`，避免真实项目手工复制 queue / jobs / codex / launchd 资产。
- `v1.4.6` 也冻结一套 shared automation summary schema，让 functional / exception / regression / nightly 等 job 与通知适配器共用同一数据契约。
- `v1.4.6` 同时把多 agent 自动化能力重新收口为 executor tiers，而不是宣称所有 agent 在当前 runtime 下原生等价执行。
- `v1.4.6` 也补上一条 truth recovery 治理：当实现先于 frozen truth 落地时，必须通过 `beacon-change` 承认 drift、回填 truth，并保留 provenance，而不是把 post-hoc writeback 伪装成 truth-first delivery。
- 该版本吸收外部 workflow-skill 思想时，只吸收 contract 和 orchestration 方法，不引入外部 skill pack 作为 Beacon runtime 前提。
- `brainstorm` 可以收敛 framing 与 options，但只有 `change` 可以晋升 requirement truth，供 implement / qa / release 消费。

## 关键验收锚点

- `docs/beacon/global-boundaries.md`
- `docs/beacon/archive/v1.4.6/release/runtime-promotion-changelog.md`
- `docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- `docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- `docs/beacon/archive/v1.4.6/qa/test-cases/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- `docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- `docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- `docs/beacon/archive/v1.4.6/qa/test-cases/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- `docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-implementation-first-reconciliation-governance.md`
- `docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-implementation-first-reconciliation-governance.md`
- `docs/beacon/archive/v1.4.6/qa/test-cases/beacon-v1.4.6-implementation-first-reconciliation-governance.md`
