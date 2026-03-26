# Beacon v1.1.6 Help / Doctor / Navigator / Skill Routing Contract

## 1. 为什么 v1.1.6 还必须补 Navigator Layer

v1.1.6 已经定义了：

- 原生 implement runner
- revision 生命周期
- story item writeback
- reopen / rewrite 语义
- native-team 多角色实现模式

但如果缺少导航层，系统仍然会卡在同一个问题上：

> 用户和 agent 都不知道“现在在哪一阶段、下一步该做什么、为什么不能继续、是否已经足够 ready”。

因此 v1.1.6 还必须正式补一层：

- `beacon help`
- 升级后的 `beacon doctor`
- stage-aware skill / prompt routing contract
- test / closure / readiness / quality scoring

## 2. 角色分工

### 2.1 `status`
负责提供原始、可计算的事实信号：
- current stage
- next_stage
- revision_id
- coverage.story / coverage.ac / coverage.tc
- gate status
- closure_complete

### 2.2 `help`
负责把状态翻译成“下一步建议”：
- 现在在哪一阶段
- 下一步推荐动作是什么
- 推荐命令是什么
- 为什么是这个动作

### 2.3 `doctor`
负责做“诊断 + 阻塞解释 + 修复建议”：
- 为什么现在不能继续
- 是环境、物料、生命周期还是测试层出问题
- 应该先修什么，再做什么

### 2.4 `skill / prompt routing`
负责让 agent 在执行前先判阶段，而不是直接猜命令：
- 先看 `status`
- 再走 `help`
- 如果 blocked 再走 `doctor`
- 最后才选择 `freeze / reopen / implement / review / verify`

## 3. `beacon help` 的正式职责

建议新增：

```bash
beacon help --project-root . --version v1.1.6 --feature <feature>
beacon help --project-root . --version v1.1.6 --feature <feature> --json
```

### 3.1 必须输出的最小字段

- `feature`
- `version`
- `revision_id`
- `current_stage`
- `doc_status`
- `delivery_status`
- `blocked`
- `blocking_reasons[]`
- `next_step.action`
- `next_step.reason`
- `next_step.command`
- `scores.test_score`
- `scores.closure_score`
- `scores.readiness_score`
- `scores.quality_score`

### 3.2 人类可读输出要求

Beacon Help 不应输出命令树，而应输出：

- 当前 feature / revision / stage
- 当前评分
- 推荐下一步
- 阻塞原因
- 推荐命令

### 3.3 JSON 输出要求

JSON 输出应成为 skill / agent / automation 的正式输入面。

## 4. 升级后的 `doctor` 职责

当前 doctor 主要偏 diagnostics。

v1.1.6 目标中，doctor 应分成两层语义：

### 4.1 diagnose（保留现有能力）
- runtime diagnostics
- context diagnostics
- package / docs / version diagnostics
- repair-package / setup-context / verify-context

### 4.2 advise（新增目标能力）
建议新增：

```bash
beacon doctor advise --project-root . --version v1.1.6 --feature <feature>
```

输出：
- 当前 blocked 吗？
- blocked 在哪一层？
- 最优修复路径是什么？
- 修复之后推荐什么命令？
- 当前评分是多少？

### 4.3 doctor 的职责边界

- `help` 负责 next step suggestion
- `doctor` 负责 blocked reason diagnosis
- `status` 负责 raw metrics

三者不能互相完全替代。

## 5. 评分体系（Scoring Contract）

v1.1.6 至少应定义 4 个评分。

### 5.1 `test_score`
用于表示测试充分性。

建议输入：
- AC coverage
- TC execution rate
- verify pass ratio
- blocked tests penalty

### 5.2 `closure_score`
用于表示闭环完成度。

建议输入：
- feature object exists
- active revision exists
- revision frozen
- implementation complete
- writeback complete
- verify complete
- accept complete

### 5.3 `readiness_score`
用于表示是否适合进入下一阶段。

建议输入：
- target stage 所需前提是否齐全
- 是否存在 critical blockers
- 是否已 freeze
- 是否已完成必要 review / verify

### 5.4 `quality_score`
用于表示质量风险水平。

建议输入：
- review spec result
- review quality result
- drift
- scope break / overbuild risk
- failing verification signals

## 6. 阶段感知导航规则

### 6.1 Draft / Refined
应优先建议：
- 继续补齐 user story / prd / test-case
- 若条件满足，执行 `freeze`

### 6.2 Frozen
应优先建议：
- 进入 `implement run --runner native-*`
- 或在复杂场景下进入 `native-team`

### 6.3 Implementing
应优先建议：
- 查看当前 implementation run 与 writeback 进度
- 若需求变更，优先 `reopen`
- 若实现完成，进入 verify / review

### 6.4 Verifying
应优先建议：
- review quality
- 修复 failing AC / TC
- 若 verify 通过，再进入 accept

### 6.5 Accepted
应优先建议：
- 进入 release 检查
- 若发现需求变化，优先 `reopen` 生成新 revision

## 7. Skill / Prompt Routing Contract

Beacon skill 需要从“CLI wrapper”升级为“stage-aware navigator skill”。

### 7.1 When to Use
除了 requirement generation，还应触发于：
- 用户问“下一步做什么”
- 用户问“为什么不能继续”
- 用户要开始实现但当前 revision 还未 freeze
- 用户要 reopen / rewrite / 变更需求
- 用户要判断是否 ready for implement / verify / accept

### 7.2 Lifecycle Routing Rules

如果：
- **没有 frozen revision** → 推荐 `beacon freeze`
- **active revision 已 superseded** → 推荐转向 active revision
- **verify 未通过** → 不允许进入 accept
- **change request 存在** → 推荐 `beacon reopen`
- **current stage 不明** → 优先 `beacon status --board` + `beacon help --json`

### 7.3 Clarification Gate

skill/prompt 必须约束 agent：
- 未 freeze 前不得直接进入 implement
- revision 不明确时不得直接继续 verify
- 存在 change request 时不得覆盖当前 frozen baseline
- 不得跳过 help/status 直接猜下一步

### 7.4 Next Step Protocol

建议固定顺序：

1. `beacon status --board`
2. `beacon help --json`
3. 若 blocked → `beacon doctor --json` 或 `beacon doctor advise`
4. 再执行 `freeze / reopen / implement / review / verify / accept`

### 7.5 Scoring Interpretation

建议 skill/prompt 采用如下解释规则：
- `test_score < 60` → 不建议 accept
- `closure_score < 80` → 闭环不完整
- `readiness_score < 70` → 不建议进入下一阶段
- `quality_score < 70` → 先做 review/fix

## 8. 建议命令面补充

```bash
beacon help --project-root . --version v1.1.6 --feature <feature>
beacon help --project-root . --version v1.1.6 --feature <feature> --json

beacon doctor advise --project-root . --version v1.1.6 --feature <feature>
```

保留现有：
- `beacon doctor`
- `beacon status`
- `beacon implement`
- `beacon review`

## 9. 结果目标

v1.1.6 完成后，Beacon 应不仅能闭环执行，还能闭环导航：

- 知道当前在哪
- 知道下一步做什么
- 知道为什么不能继续
- 知道测试与闭环质量如何
- 知道何时应 freeze / reopen / implement / verify / accept

## 10. 一句话总结

v1.1.6 的 Navigator Layer 目标是：

> **把 Beacon 从“会跑命令的 workflow kernel”升级成“能解释阶段、能建议下一步、能说明阻塞原因、能输出质量评分”的闭环导航内核。**
