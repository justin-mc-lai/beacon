# Beacon v1.3.2 QA 迭代浏览器合同

## 目标

把 `qa` 从“测试命令集合”明确收敛成：

> 围绕冻结的 `prd / user-story / test-case`，对目标项目启动真实浏览器环境，按顺序进行多轮迭代，并在每轮引入新的 auto research 增量。

## 当前代码面的真实情况

当前 `qa` 已经具备以下命令面：

- `qa run`
- `qa team-run`
- `qa evolve`
- `qa status`
- `qa import`
- `qa session`
- `qa audit`

并且已经具备：

- `feature-aware` / `story-exhaustive` 执行模式
- `team-mode`
- session 保存
- browser runner family 的部分基础设施

`v1.3.2` 的任务不是重新发明 QA，而是把这些能力讲成一个统一合同。

## 人类主合同

### 推荐执行链

```text
冻结的 prd / user-story / test-case
→ qa run
→ qa evolve
→ 下一轮 qa run
→ repair handoff / Ralph decision
```

### 推荐命令

```bash
beacon qa run "<feature>" --project . --version v1.3.2 --mode story-exhaustive --json
beacon qa evolve "<feature>" --project . --version v1.3.2 --mode story-exhaustive --json
beacon qa team-run "<feature>" --project . --version v1.3.2 --mode story-exhaustive --runtime tmux --json
beacon qa status --project . --json
```

## 输入合同

QA 的正式输入必须固定为：

- 冻结 `prd`
- 冻结 `user-story`
- 冻结 `test-case`
- AC matrix
- story-scenario-map
- QA9 matrix

如果这些输入不完整，就不应声称已经进入正式 browser QA 闭环。

## 执行模式合同

### `feature-aware`

适合：

- 快速 feature 级验收
- 非全量故事穷尽视角

### `story-exhaustive`

适合：

- 正式多轮 browser QA
- 需要 scenario family 覆盖
- 需要 repair handoff 与 Ralph 闭环的场景

`v1.3.2` 推荐把 `story-exhaustive` 作为三模式下的首选 QA 视角。

## 浏览器合同

### Browser execution family

`qa` 必须把以下执行器纳入同一 browser family 叙事：

- `browser-cli`
- `agent-browser`
- `pageagent`
- `browser-use`

必要时兼容：

- `playwright`
- `cypress`

规则：

> 用户关心的是“浏览器验收”，不是某个 runner 的偶然名称。

### Session contract

`qa session` 必须支撑：

- `session_id`
- `origin`
- `runner_type`
- `profile_ref`
- `cookies_ref`
- `storage_state_ref`
- `scope`

这样 browser QA 才能真正围绕目标项目持续演进，而不是每轮重新冷启动。

## 轮次合同

### 每轮至少输出

- round summary
- targeted scenario set
- boundary findings
- structure inference
- evidence pack
- repair handoff 或 continue decision

### 每轮至少新增一种价值

- 新边界
- 新页面状态
- 新异常路径
- 新 coverage closure
- 新 structure inference
- 新 repair handoff

若没有新增价值，该轮不应视为有效进展。

## `qa run` 合同

`qa run` 负责：

- 读取冻结材料
- 按 execution mode 编译场景
- 执行当前轮 browser / verification plan
- 生成 scorecard、coverage、continue decision

它是 QA 的正式执行入口。

## `qa evolve` 合同

`qa evolve` 负责：

- 基于上一轮结果生成 delta-aware rerun plan
- 确定 targeted layers / tc ids / scenario ids
- 生成下一轮执行计划

它不直接执行 QA，而是下一轮实验设计器。

## `qa team-run` 合同

`qa team-run` 负责：

- 在隔离上下文中进入 `qa-team`
- 启动 verifier / repair-handoff-writer 等 team lanes
- 在需要时配合 tmux/HUD 提供可视执行面

## `qa status` 合同

`qa status` 至少应能显示：

- 当前 run id
- 当前 feature
- 当前 execution mode
- evidence done
- continue decision
- coverage / exhaustiveness

在 `v1.3.2` 目标语义里，建议进一步显示：

- 当前 round
- 当前 browser runner family
- 当前 blocker
- 推荐下一步

## 证据合同

每轮 browser QA 至少应支持合理子集的：

- screenshot
- current URL
- action transcript
- DOM / snapshot
- console excerpt
- network summary
- session / profile reference
- result manifest

规则：

> 浏览器探索不是唯一真相，但没有 browser evidence 也不算正式 browser QA。

## 与 Ralph 的衔接

QA 必须成为 Ralph 闭环中的正式输入：

- `qa run` 提供当前轮结论
- `qa evolve` 提供下一轮 delta plan
- `repair handoff` 提供 implement 回流依据
- `status` 提供当前轮次与 blocker

Ralph 不应该自己重新理解 QA；它应消费这些正式输出。

## Guardrails

1. `qa` 不得脱离冻结材料自由扩 scope
2. `qa` 不得把 agent 浏览器探索误当唯一真相
3. `qa` 不得绕过 evidence pack 与 continue decision
4. `qa` 的多轮演进必须带来新价值，而不是无意义重复

