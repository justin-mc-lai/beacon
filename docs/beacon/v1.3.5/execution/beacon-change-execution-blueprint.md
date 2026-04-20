# Beacon Change Execution Blueprint (v1.3.5 Draft)

## 1. 文档定位

本文件把 `beacon-change` 从“宿主可见 skill 草案”收口为一份可执行的 change-loop blueprint。

目标不是新增 Beacon 一级主命令，而是明确：

1. `beacon-change` 如何作为宿主路由入口存在
2. 它如何编排 `reopen -> revise -> refresh -> freeze -> implement -> qa -> release`
3. 它和 `7+3` 主链、revision truth、release gate 的边界

规则：

> `beacon-change` 是冻结后需求调整的路由器，不是新的主阶段，不替代 `prd / implement / qa / release`。

## 2. Human Surface

人类可见心智继续保持：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
+ help / status / doctor
+ beacon-change
```

其中：

- `beacon-change` 只在“冻结后需求调整”场景显式出现
- 它不改变主链顺序
- 它的目标是把用户重新送回主链

## 3. Entry Conditions

`beacon-change` 应在以下条件下被推荐或触发：

1. feature 已存在 frozen revision
2. 用户表达以下任一意图：
   - 改需求
   - 补边界
   - 范围调整
   - reopen 后重做
   - hotfix 但先补 requirement truth
   - 重新冻结再交付

不应触发 `beacon-change` 的场景：

1. 新 feature 初次立项
2. 只是问当前状态
3. 只是跑常规 QA / release

## 4. Execution Model

### 4.1 Stage 1: Change Intake

输入：

- `project-root`
- `version`
- `feature`
- change intent

输出：

- `change brief`
- `impact summary`
- `recommended_next_step`

至少归纳：

1. why changed
2. added
3. removed / reduced
4. fixed
5. impacted surfaces
6. recommended mode

### 4.2 Stage 2: Revision Reopen

动作：

- 读取当前 revision state
- 调用 `reopen`
- 生成新的 active revision

产物：

- `previous_revision_id`
- `new_revision_id`
- `reason`

规则：

- 旧 frozen baseline 只能保留，不得被覆盖
- 没有 frozen baseline 时，`beacon-change` 应阻断并回退到 `prd`

### 4.3 Stage 3: Delta Requirement Refresh

动作：

- `prd revise`
- `user-story refresh`
- `test-case refresh`
- `prototype refresh`

目标：

- 把 change brief 编译回完整 requirement truth

规则：

- 不允许只改一个面就直接进入实现
- `prototype` 作为正式 freeze stage，必须跟着 revised truth 刷新

### 4.4 Stage 4: Requirement Re-freeze

动作：

- requirement clarity gate
- `freeze`

产物：

- 新 frozen revision baseline
- requirement clarity report
- re-freeze receipt

阻断条件：

1. PRD / user-story / test-case / prototype 未齐套
2. `冻结交付物` 中列出的必需文件缺失
3. clarity gate 发现 unresolved items

### 4.5 Stage 5: Implement Fix / Hotfix

动作：

- `implement fix`
- 或 `implement hotfix`

要求：

- 绑定最新 revision baseline
- 继承 branch/service/git workflow contract
- 不允许继续沿用旧 baseline 做默认实现

### 4.6 Stage 6: Delta QA / Regression QA

动作：

- `qa delta-run`
- `qa regression-run`

职责分层：

1. `delta-run`
   - 验新变更
2. `regression-run`
   - 验旧承诺未回退

要求：

- QA 必须指向最新 revision truth
- revised baseline 下的 branch/service contract 应可复核

### 4.7 Stage 7: Release Recheck

动作：

- `release recheck`

职责：

1. 判断 revised delivery 是否 ready
2. 判断 hotfix delivery 是否 ready
3. 阻止旧 baseline 的 gate 结果被沿用

## 5. Suggested Command Ladder

建议的宿主推荐顺序：

```text
beacon-change
→ reopen
→ prd revise
→ user-story refresh
→ test-case refresh
→ prototype refresh
→ freeze
→ implement fix
→ qa delta-run
→ qa regression-run
→ release recheck
```

如果用户只说“这版还要改”，应先进入：

```text
beacon-change -> change intake
```

再由系统给出后续 ladder。

## 6. Artifact Contract

### Human-readable

- PRD revise result
- user story refresh result
- test-case refresh result
- prototype refresh summary
- lifecycle state machine
- change brief

### Machine-readable

- revision state
- story state
- requirement clarity state
- QA matrices
- change receipt

### Runtime projection

- runtime ledger / projection store

规则：

> revised delivery 只能建立在同一 revision lineage 的统一 truth 上。

## 7. Routing Contract

### `using-beacon`

应把冻结后需求调整明确路由到 `beacon-change`。

### `beacon-help`

当检测到：

- frozen feature
- user asks how to change scope

应优先建议 `beacon-change`，而不是只返回抽象建议。

### `beacon-status`

应能暴露：

- current revision
- frozen / reopened / re-frozen
- latest delivery type
- whether release gate is based on latest revision

## 8. Blockers and Exit Codes

### 应阻断的条件

1. 当前 feature 尚未冻结，却试图进入 change loop
2. `reopen` 失败
3. delta compile 不完整
4. `freeze` 被 clarity gate 阻断
5. revised baseline 未被 implement / qa / release 消费

### 应回退的方向

- 无 frozen baseline：
  - 回退到 `prd`
- 不清楚当前阶段：
  - 回退到 `status`
- context/material drift：
  - 回退到 `doctor`

## 9. Minimal Implementation Direction

`v1.3.5` 最小实现不要求一次性产品化所有 change-loop 命令，只要求先锁定：

1. 宿主入口：
   - `beacon-change`
2. 文档与状态机：
   - lifecycle state machine
   - change execution blueprint
3. freeze gate：
   - 可校验新增加的冻结交付物
4. routing：
   - `using-beacon` / `help` / `status` 不再忽略 change-loop

## 10. Open Follow-up

1. 把 `beacon-change` 的 intake / prepare / handoff 编排固化为实际内部命令层。
2. 给 `status` 增加 revision-aware board 字段。
3. 给 `release` 增加 delivery type 字段：
   - `initial`
   - `revised`
   - `hotfix`
