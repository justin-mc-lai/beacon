# Beacon v1.4.0 总览

## 版本状态

- `v1.4.0` 当前主题是：`lightweight kernel and core surface refactor`
- 当前版本不是做“能力删除”，而是做“能力分层、减重、真相收敛”
- 当前版本材料状态：`requirement-freeze-ready / implementation-pending`

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
  - `docs/beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
  - `docs/beacon/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
  - `docs/beacon/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- User Story
  - `docs/beacon/v1.4.0/user-story/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
  - `docs/beacon/v1.4.0/user-story/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
  - `docs/beacon/v1.4.0/user-story/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- Test Cases
  - `docs/beacon/v1.4.0/qa/test-cases/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
  - `docs/beacon/v1.4.0/qa/test-cases/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
  - `docs/beacon/v1.4.0/qa/test-cases/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- Execution
  - `docs/beacon/v1.4.0/execution/index.md`
  - `docs/beacon/v1.4.0/execution/boundaries.md`
  - `docs/beacon/v1.4.0/execution/architecture-blueprint.md`

## 正式子线

- `beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor`
- `beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure`
- `beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration`

## 当前冻结判断

- `beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor`
  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / execution-blueprint-frozen / implementation-pending`
- `beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure`
  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / support-surface-frozen / implementation-pending`
- `beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration`
  - `prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / change-refreeze-frozen / implementation-pending`

## 当前收口结论

- `v1.4.0` 继续坚持 Beacon 主流程：
  - `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`
- `v1.4.0` 不新增公开一级主命令
- `beacon-prd-bootstrap` 继续存在，但只作为 optional support skill
- bootstrap 可以降低 requirement 启动摩擦，但不能伪装成 frozen truth 或绕过主链
- `beacon-prd-bootstrap` 当前已进一步被补强为 unified requirement closure entry 候选，但仍是 support surface，不是主流程替代
- 当前版本 requirement closure 已足以进入待实现阶段，但未声称实现已经完成

## 当前冻结基线

`v1.4.0` 当前作为 requirement freeze 包成立，前提是以下五项同时成立：

1. `docs/beacon/<version>/**/*.md` 继续是唯一 truth root
2. compiled machine contract 继续是单向下游，而不是第二真相源
3. `goal`、`tasks ledger`、bootstrap state artifact 都不得单独定义 completion truth
4. optional skills 的存在与默认可见性已被分层治理
5. support surfaces 只能解释、校准、路由，不得自由改写 canonical truth

## 当前收口判断

- 当前版本已经具备进入实现阶段的 requirement closure：
  - 主内核重构线已冻结
  - `prd-bootstrap` support feature 已冻结
  - `prd-bootstrap unified closure orchestration` change/refreeze 已冻结
  - execution 蓝图已冻结
  - QA coverage contract 已冻结
- 当前版本尚未进入“实现完成”：
  - 未声称源码已完成
  - 未声称测试已执行通过
  - 当前结论是：`implementation-pending`

## 关键验收锚点

- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- `docs/beacon/v1.4.0/user-story/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- `docs/beacon/v1.4.0/qa/test-cases/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`
- `docs/beacon/v1.4.0/execution/architecture-blueprint.md`
- `docs/beacon/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
- `docs/beacon/v1.4.0/user-story/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
- `docs/beacon/v1.4.0/qa/test-cases/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
- `docs/beacon/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- `docs/beacon/v1.4.0/user-story/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- `docs/beacon/v1.4.0/qa/test-cases/beacon-v1.4.0-prd-bootstrap-unified-requirement-closure-orchestration.md`
- `skills/beacon/beacon-prd-bootstrap/SKILL.md`
- `beacon/commands/prd_bootstrap.py`
- `beacon/utils/prd_bootstrap.py`

## 版本主题图

```text
heavy kernel and projection sprawl exists
-> freeze lightweight kernel architecture
-> preserve base capabilities while shrinking default weight
-> re-freeze support capabilities like prd-bootstrap under the same truth discipline
-> enter implementation with one truth root, one contract strategy, and explicit support boundaries
```
