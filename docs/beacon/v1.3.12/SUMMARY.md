# Beacon v1.3.12 总览

## 版本状态

- `v1.3.12` 当前从 `v1.3.11` 的 requirement package closure 向前推进，主题不再是补新的主生命周期，而是把 `prd / user-story / test-case` 做成可持续深挖的人机协作需求闭环。
- 当前版本首先冻结一条主线：
  - `host-llm requirement deepening and human-loop closure`
- 当前版本材料状态：`requirement-freeze-ready`

## 版本目标

`v1.3.12` 当前聚焦解决一组要求更高、但仍留在现有 Beacon 边界内的 requirement gap：

1. requirement package 已经能闭环，但深挖仍偏弱
   - `prd -> user-story -> test-case` 已能形成 formal package
   - 但 `user-story / test-case` 仍更多依赖结构抽取与规则投影
   - 对角色差异、状态机、边界、异常、风险、回退路径的主动挖掘不足
2. host-native LLM 已经存在，但没有被系统化用于 requirement deepening
   - `prd / user-story / test-case / prototype` 已具备 host-native semantic runtime 基础
   - 但 requirement compile 还没有被正式提升为“持续深挖 + 人类补齐 + 可回写 formal truth”的协作闭环
3. 人类面 subskill 还没有成为稳定的 requirement补齐入口
   - `beacon-prd / beacon-user-story / beacon-test-case` 已是公开入口
   - 但三者之间缺少统一的 gap register、补问协议、深挖证据与增量冻结语义
4. 缺少统一的收敛编排 contract
   - `brainstorm / change / help` 之间需要明确字段与路由规则
   - 否则 PRD 驱动的持续深挖仍会停留在“建议可见”而非“链路可执行”

## 当前需求包

- PRD
  - `docs/beacon/v1.3.12/prd/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md`
- User Story
  - `docs/beacon/v1.3.12/user-story/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md`
- Test Cases
  - `docs/beacon/v1.3.12/qa/test-cases/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md`
- Human runbook
  - `docs/beacon/v1.3.12/execution/beacon-v1.3.12-one-page-runbook.md`

## 正式子线

- `beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure`

## 当前冻结判断

- `beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure`：`prd-freeze-ready / story-freeze-ready / test-case-freeze-ready / machine-contract-seeded / implementation-pending`

## 当前收口结论

- `v1.3.12` 不改变 Beacon 的公开主生命周期，仍保持：
  - `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`
- `v1.3.12` 不新增公开一级主命令，仍以：
  - `beacon-prd`
  - `beacon-user-story`
  - `beacon-test-case`
  作为 requirement 人类主面
- 当前主张不是“让 LLM 取代 requirement truth”，而是：
  - 用 host-native LLM 深挖 requirement gap
  - 让人类通过现有 subskill 补齐缺口
  - 把补齐结果重新冻结进 `prd / user-story / test-case`
- 当前主张不是改变 `implement / qa / release`，而是提升它们上游 requirement package 的信息密度与可验收性

## 当前冻结基线

`v1.3.12` 当前可以作为 requirement freeze 包收口的前提是以下五项同时成立：

1. `prd / user-story / test-case` 三份文档对同一 feature 使用同一 slug、同一 revision 语义、同一 completeness 口径
2. `accepted / rejected / deferred` 的人机补齐决策必须留下 machine-readable decision trail
3. `story discovery / coverage expansion / completeness verdict` 必须各自存在最小 `.machine` 合同
4. `prototype / implement / qa / release` 只能读取 requirement completeness，不得改写 requirement truth
5. host downgrade 可以存在，但必须显式记录，且不得伪装为与 host deepening 等价

## 当前收口判断

- 当前版本已经具备“需求物料可冻结”的最低闭环：
  - PRD 定义了 deepening contract 与 freeze 决策
  - User Story 定义了角色、状态、异常、治理、补齐协议与 completeness read model
  - Test Cases 定义了 AC 到 executable coverage 的映射与 readiness blocking 语义
  - `.machine` 最小合同已被指定为同版本 requirement package 的消费面
- 当前版本尚未进入“实现完成”：
  - 未声称源码已实现
  - 未声称执行测试已通过
  - 当前冻结结论仅针对 requirement package，可作为后续 `prototype / implement / qa` 的正式指导物料

## 关键验收锚点

- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.3.11/SUMMARY.md`
- `docs/beacon/v1.3.11/execution/index.md`
- `docs/beacon/v1.3.12/prd/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md`
- `docs/beacon/v1.3.12/user-story/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md`
- `docs/beacon/v1.3.12/qa/test-cases/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md`
- `docs/beacon/v1.3.12/execution/requirement-convergence-contract.md`
- `skills/beacon/beacon-prd/SKILL.md`
- `skills/beacon/beacon-user-story/SKILL.md`
- `skills/beacon/beacon-test-case/SKILL.md`
- `beacon/commands/prd.py`
- `beacon/commands/user_story.py`
- `beacon/commands/test_case.py`
- `beacon/utils/requirement_parsing.py`
- `beacon/utils/semantic_runtime.py`

## 版本主题图

```text
formal requirement package exists
-> deep requirement mining still weak
-> host-native semantic runtime already exists
-> use host LLM to deepen PRD truth
-> derive richer story / test-case candidates
-> expose gaps through current human subskills
-> human supplements missing facts
-> updated truth re-freezes into prd / user-story / test-case
-> implement / qa / release consume denser requirement closure
```
