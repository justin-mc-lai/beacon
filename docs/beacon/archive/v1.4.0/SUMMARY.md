# Beacon v1.4.0 总览

## 版本状态

- `v1.4.0` 当前主题是：`lightweight kernel and core surface refactor`
- 当前版本不是做“能力删除”，而是做“能力分层、减重、真相收敛”
- 当前版本材料状态：`two-feature-accepted / main-kernel-feature-refrozen-pending-implementation / branch-governance-requirement-frozen / llm-decision-surface-requirement-and-prototype-frozen-pending-implementation`

## 版本目标

`v1.4.0` 当前聚焦两条主线：

1. 收敛 Beacon 内核，解决默认过重问题
   - 保留 frozen truth、gate、implement、qa、host-runtime、learning、meta、memory、archive 基座
   - 收敛 machine contract
   - 强化 change / implement / support human surface
2. 把已有但未被正式冻结的 support capability 收编进当前版本 requirement 包
   - 典型代表：`beacon-prd-bootstrap`
   - 它继续作为 optional support skill 保留
   - 但需要按 `v1.4.0` 轻量内核边界重新规范

## 当前需求包

- PRD
  - `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
  - `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
  - `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
  - `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md`
  - `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`
- User Story
  - `docs/beacon/archive/v1.4.0/user-story/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
  - `docs/beacon/archive/v1.4.0/user-story/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
  - `docs/beacon/archive/v1.4.0/user-story/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
  - `docs/beacon/archive/v1.4.0/user-story/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md`
  - `docs/beacon/archive/v1.4.0/user-story/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`
- Test Cases
  - `docs/beacon/archive/v1.4.0/qa/test-cases/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
  - `docs/beacon/archive/v1.4.0/qa/test-cases/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
  - `docs/beacon/archive/v1.4.0/qa/test-cases/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
  - `docs/beacon/archive/v1.4.0/qa/test-cases/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md`
  - `docs/beacon/archive/v1.4.0/qa/test-cases/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`
- Execution
  - `docs/beacon/archive/v1.4.0/execution/index.md`
  - `docs/beacon/archive/v1.4.0/execution/boundaries.md`
  - `docs/beacon/archive/v1.4.0/execution/architecture-blueprint.md`

## 正式子线

- `beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor`
- `beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure`
- `beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration`
- `beacon-v1.4.0-branch-governance-human-surface-and-implement-gate`
- `beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution`

## 当前冻结判断

- `beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor`
  - `prd-frozen-pending-implementation / story-frozen-pending-implementation / test-case-frozen-pending-implementation / revision-r2-ready`
- `beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure`
  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / support-surface-frozen / implementation-completed / qa-passed / acceptance-accepted`
- `beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration`
  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / change-refreeze-frozen / implementation-completed / qa-passed / acceptance-accepted`
- `beacon-v1.4.0-branch-governance-human-surface-and-implement-gate`
  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / implementation-not-started / qa-not-started`
- `beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution`
  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / prototype-frozen / implementation-not-started / qa-not-started`

## 当前收口结论

- `v1.4.0` 继续坚持 Beacon 主链：
  - `prd -> user-story -> test-case -> implement -> qa -> release`
- `prototype` 改为条件触发层：
  - 仅当 feature 存在真实 UX/UI surface 或 route/state/interaction handoff 需求时，才进入 `test-case -> prototype -> implement`
- `v1.4.0` 不新增公开一级主命令
- `beacon-prd-bootstrap` 继续存在，但只作为 optional support skill
- 新增 branch governance requirement 子线，目标是在不扩张主流程的前提下补齐人类面 git workflow / implement gate 治理缺口
- 新增 llm decision surface 子线，目标是在不扩张主流程的前提下，把既有 ask / learning / diagram / semantic 能力收敛成正式 decision surface
- 主内核重构线已按 `beacon-change` 回路重新补齐“版本号/版本元信息漂移治理” requirement，并重新冻结到待实现
- bootstrap 可以降低 requirement 启动摩擦，但不能伪装成 frozen truth 或绕过主链
- `beacon-prd-bootstrap` 当前已进一步被补强为 unified requirement closure entry 候选，但仍是 support surface，不是主流程替代
- 当前版本有两条 support 子线已形成 implementation / QA / acceptance 证据链
- 主内核重构线、branch governance 子线与 llm decision surface 子线当前都处于 requirement 已冻结、待实现状态
- branch governance 新子线当前 requirement package 已冻结，尚未进入 implementation / QA execution
- llm decision surface 新子线当前 requirement package 已冻结；由于该 feature 具备真实 route/state/interaction handoff 需求，prototype 已被条件触发并完成冻结，当前待进入 implementation / QA execution

## 当前冻结基线

`v1.4.0` 当前作为 requirement freeze 包成立，前提是以下五项同时成立：

1. `docs/beacon/<version>/**/*.md` 继续是唯一 truth root
2. compiled machine contract 继续是单向下游，而不是第二真相源
3. `goal`、`tasks ledger`、bootstrap state artifact 都不得单独定义 completion truth
4. optional skills 的存在与默认可见性已被分层治理
5. support surfaces 只能解释、校准、路由，不得自由改写 canonical truth

## 当前收口判断

- 当前版本已经完成两条 requirement 子线的正式实现闭环：
  - `prd-bootstrap` safe bootstrap/freeze closure 已实现并验收
  - `prd-bootstrap unified closure orchestration` 已实现并验收
- 当前版本有两条 requirement 子线处于冻结待实现：
  - 主内核重构线已补齐版本漂移治理 requirement，并完成 R2 冻结
  - branch governance 子线 requirement package 已冻结，尚未进入 implementation / QA execution
- 当前版本新增一条 requirement-frozen / prototype-frozen 子线：
  - llm decision surface 子线已完成 PRD / story / test-case / prototype 冻结，当前待进入 implementation
- 当前版本尚未进入“版本发布完成”：
  - release scorecard 仍未到 `release_ready`
  - release gate 仍有版本级阻断需要收口
  - 当前结论是：`mixed feature state / release-pending`

## 当前真实状态

- 截至 `2026-05-07`，两条 bootstrap feature 的 machine acceptance transaction 都已写回
- 两条 bootstrap feature 的 `artifact-update-obligations` 都已 `open_count=0`
- 两条 bootstrap feature 的 `Acceptance Kit v1` 四层 verdict 都是：
  - `skill-contract=pass`
  - `scenario-suite=pass`
  - `trace-scorecard=pass`
  - `real-project-proof=pass`
- 主内核重构线当前已因 requirement 变更进入 `R2`，并新增版本表面漂移治理待实现项
- 版本级仍不应直接宣称发布完成，当前主要差项同时包括 release governance 与未完成 feature implementation

## 当前版本级阻断

- `release scorecard v1.4.0` 仍显示 `release_ready=false`
- 当前主要版本级阻断来自 release gate / evidence governance，以及主内核与 branch governance 两条 feature 的实现未闭环
- 当前主要版本级阻断来自 release gate / evidence governance，以及主内核、branch governance 与 llm decision surface 三条 feature 的后续交付未闭环
- 因此本版本当前应被表述为：
  - `two feature packages accepted`
  - `main kernel feature requirement-refrozen to pending implementation`
  - `branch-governance feature requirement-frozen`
  - `llm-decision-surface feature requirement-frozen / prototype-frozen / pending-implementation`
  - `version release still pending final governance closure`

## 关键验收锚点

- `docs/beacon/global-boundaries.md`
- `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- `docs/beacon/archive/v1.4.0/user-story/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- `docs/beacon/archive/v1.4.0/qa/test-cases/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- `docs/beacon/archive/v1.4.0/execution/architecture-blueprint.md`
- `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
- `docs/beacon/archive/v1.4.0/user-story/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
- `docs/beacon/archive/v1.4.0/qa/test-cases/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
- `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- `docs/beacon/archive/v1.4.0/user-story/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- `docs/beacon/archive/v1.4.0/qa/test-cases/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md`
- `docs/beacon/archive/v1.4.0/user-story/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md`
- `docs/beacon/archive/v1.4.0/qa/test-cases/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md`
- `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`
- `docs/beacon/archive/v1.4.0/user-story/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`
- `docs/beacon/archive/v1.4.0/qa/test-cases/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`
- `skills/beacon/beacon-prd-bootstrap/SKILL.md`
- `beacon/commands/prd_bootstrap.py`
- `beacon/utils/prd_bootstrap.py`

## 研究与对标

- 与 **OpenSpec**、**GitHub Spec Kit** 的结构层对比，及 Beacon **可交付设计**（极简人类面、完备交付闭环、职责分层）：[`research/beacon-openspec-speckit-comparison-and-deliverable-design.md`](./research/beacon-openspec-speckit-comparison-and-deliverable-design.md)
- **Spec Kit 多 Agent / Trae skills** 安装机制与 Beacon **宿主材质化**对齐（为何 Trae 人类面看不到子技能、建议 `beacon doctor` 侧实现要点）：[`research/beacon-agent-surface-speckit-trae-alignment.md`](./research/beacon-agent-surface-speckit-trae-alignment.md)
- **OpenSpec 归档**（主 spec、delta 变更包、`archive` 合并语义）与 Beacon **版本演进中的「实现真相」缺口**：[`research/openspec-archive-vs-beacon-version-evolution.md`](./research/openspec-archive-vs-beacon-version-evolution.md)

## 版本主题图

```text
heavy kernel and projection sprawl exists
-> freeze lightweight kernel architecture
-> preserve base capabilities while shrinking default weight
-> re-freeze support capabilities like prd-bootstrap under the same truth discipline
-> enter implementation with one truth root, one contract strategy, and explicit support boundaries
```
