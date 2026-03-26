# PRD: Beacon 原生 implement、revision 生命周期闭环与 story writeback（v1.1.6）

## 1. 背景

Beacon 当前已经具备：

- 主链 workflow：`think → user-story → prd → [prototype] → test-case → implementation → verify → gate`
- workflow lifecycle memory / attempt / stage context
- implement adapter shell
- review spec / quality
- status board
- team collaboration 雏形

问题不在于 Beacon 缺少命令，而在于：

> Beacon 还没有一个“原生实现 + revision 状态机 + item 级回写”的确定性闭环。

当前主要缺口：

1. `implement` 仍以 adapter/handoff 为主，没有默认原生 runner。
2. `user-story` 还是文档生成，不是 machine-backed lifecycle object。
3. `workflow` 有 stage 事件，但没有正式的 draft/frozen/accepted 等对象状态。
4. `review` 会出报告，但不会驱动 story / AC / TC 状态变化。
5. 任意阶段 change/reopen 的行为没有 formal revision contract。
6. `doctor` 与 skill wrapper 还不能系统回答“下一步做什么 / 为什么被 block / 是否 ready”。

## 2. 第一性原理结论

### 2.1 人类真正需要什么
- 能明确看到当前需求是否冻结
- 能知道哪些 story item 已实现 / 已验证 / 已验收
- 能在需求变化时安全重开，而不污染历史闭环记录

### 2.2 机器真正需要什么
- 稳定 revision id
- 稳定 story / item id
- 可回写的 machine truth
- 可推导 next stage 的状态机

### 2.3 Beacon 应负责什么
- 定义 revision / story / item / run 的正式对象模型
- 定义 freeze / implement / verify / accept / reopen 的生命周期语义
- 提供默认原生 implement runner
- 提供 item 级 writeback 机制

### 2.4 Beacon 不应负责什么
- 复制所有外部 runtime 平台能力
- 把每个版本都做成全栈平台复制品
- 以兼容旧设计为由继续维持“implementation 只是外接 adapter”

## 3. 目标

1. **补齐双层生命周期状态机**
2. **实现 revision 化需求重开能力**
3. **提供默认 native implement runner**
4. **实现 user story / AC / test item 的 machine-backed writeback**
5. **支持 multiple agent roles 的 team implement 模式**
6. **保证任意阶段 change/reopen 后可重新闭环**
7. **提供 Navigator Layer（help / doctor / skill routing / scoring）**

## 4. 核心对象模型

## 4.1 Feature

字段建议：
- `feature_slug`
- `version`
- `title`
- `current_revision_id`
- `lifecycle_status`
- `created_at`
- `updated_at`

职责：
- 作为版本内 feature 的稳定根对象
- 指向当前生效 revision

## 4.2 Revision

字段建议：
- `revision_id`
- `feature_slug`
- `source_revision_id`
- `reason`（draft / freeze / change-request / reopen / rewrite）
- `doc_status`
- `delivery_status`
- `baseline_hash`
- `superseded_by`
- `created_at`
- `frozen_at`

职责：
- 承载某一轮正式需求基线
- 支持 supersede / reopen / rewrite

## 4.3 Story

字段建议：
- `story_id`
- `revision_id`
- `title`
- `priority`
- `status`
- `items[]`

职责：
- 作为 revision 内的可交付故事单元
- 绑定一组可回写 item

## 4.4 Story Item

字段建议：
- `id`（如 `AC-001` / `TASK-001` / `TEST-001`）
- `kind`（`ac` / `task` / `test`）
- `text`
- `required`
- `status`
- `implemented_by_run_id`
- `verified_by_run_id`
- `accepted_at`
- `changed_in_revision`

职责：
- 成为 implementation / verify / accept 的直接回写单元

## 4.5 Implementation Run

字段建议：
- `run_id`
- `revision_id`
- `feature_slug`
- `target_story_ids`
- `target_item_ids`
- `runner`（`native-single` / `native-team` / adapter id）
- `status`
- `changed_files`
- `verification`
- `artifact_updates`
- `summary`
- `started_at`
- `completed_at`

职责：
- 记录一次正式实现尝试
- 成为 writeback 的直接来源

## 5. 生命周期状态机

## 5.1 文档/需求生命周期

```text
Draft
→ Refined
→ Frozen
→ Superseded
→ Archived
```

语义：
- `Draft`：允许继续编辑
- `Refined`：需求已补齐，可进入 freeze
- `Frozen`：成为正式实现基线
- `Superseded`：被后续 revision 替代
- `Archived`：完成并归档

## 5.2 实现/交付生命周期

```text
Idle
→ Implementing
→ Implemented
→ Verifying
→ Accepted
→ Released
```

异常与重入：

```text
Blocked
Failed
Reopened
```

## 5.3 生命周期约束

1. 没有 `Frozen revision`，不得进入 implement。
2. implementation 必须绑定 `revision_id`。
3. verify 必须回写 item 状态，不能只产出报告。
4. accept 必须是正式动作，不是隐式推断。
5. reopen 必须产生新 revision，而不是直接污染旧 revision。

## 6. Native Implement 设计目标

## 6.1 为什么必须有默认 native implement

当前 `implement` 若没有 adapter/runner，会进入 `runner_not_configured`。

这意味着 Beacon 仍然依赖外部实现环境才能闭环。

v1.1.6 的目标是：

> 即使没有外部 runner，Beacon 也必须能自己跑通 implementation 主链。

## 6.2 默认 runner

至少定义：

- `native-single`
- `native-team`

## 6.3 `native-single`

适用于：
- 小改动
- 单故事
- 低 blast radius
- 低协作成本

职责：
- 读取 frozen revision 文档与 machine state
- 选中未完成 items
- 单 agent 实现
- 产出 changed files / summary / verification
- 自动 writeback

## 6.4 `native-team`

适用于：
- 多 story
- 高复杂度
- 高风险变更
- 需要 review / test 并行协作

最小角色集：
- **Planner / Orchestrator**
- **Implementer**
- **Reviewer**
- **Tester**

可扩展角色：
- Architect
- Writer / Writeback agent

## 7. Writeback 设计目标

## 7.1 implement writeback

implement 完成后至少更新：
- `TASK-*`
- 被覆盖的 `AC-*`
- `implemented_by_run_id`
- changed files summary

## 7.2 verify writeback

verify 完成后至少更新：
- `TEST-*`
- `AC-*` 的 verified 状态
- failed items 的阻塞原因

## 7.3 accept writeback

accept 完成后至少更新：
- `accepted_at`
- `accepted_by`
- story status / revision delivery status

## 7.4 human / machine 双面输出

- `docs/beacon/<version>/user-story/*.md`：人类主读
- `docs/beacon/<version>/.machine/user-story/*.json`：机器真相

Markdown 是 projection，machine JSON 是状态真相。

## 8. 任意阶段重改需求 / 重写实现

## 8.1 原则

不要 reopen 当前 revision 本体，而是：

> **创建一个新 revision，旧 revision 保留历史。**

## 8.2 场景覆盖

### 场景 A：在 frozen 后改需求
- `R1` 已 frozen
- 用户提出新变更
- 创建 `R2`
- `R1 → superseded`
- `R2 → refined / frozen / implement`

### 场景 B：在 implementing 中途改需求
- 当前 run 绑定 `R1`
- 变更请求进入
- 创建 `R2`
- 当前 run 标记被 supersede
- `R2` 重新闭环

### 场景 C：在 verify / accepted 后发现需求错误
- 保留 `R1` 历史
- 创建 `R2`
- 新 revision 重新 refined / freeze / implement / verify / accept

## 8.3 OpenSpec 式重入语义在 Beacon 中的落点

Beacon 需要做到：
- 任意阶段可以提交 change request
- 变化通过 revision 进入，而不是直接篡改 frozen baseline
- `status / workflow continue / review / gate` 都能识别“当前生效 revision”

## 9. 命令面目标

建议新增或增强：

### 9.1 生命周期命令
- `beacon freeze <feature>`
- `beacon reopen <feature>`
- `beacon review accept <feature>`

### 9.2 implement 命令增强
- `beacon implement run <feature> --runner native-single`
- `beacon implement run <feature> --runner native-team`

### 9.3 writeback / 状态可视化
- `beacon status --board`
- `beacon review spec`
- `beacon review quality`
- writeback 可以作为隐式动作，也可以后续补显式命令

## 10. Navigator Layer

### 10.1 `beacon help`

应新增 stage-aware 的 `beacon help`，输出：
- current stage / revision / doc_status / delivery_status
- next step action / reason / command
- scores：`test_score / closure_score / readiness_score / quality_score`

### 10.2 升级版 `doctor`

`doctor` 不应只做诊断，还应支持 advise 语义：
- 为什么现在不能继续
- 当前 blocked 在哪一层
- 应该先修什么、再做什么

### 10.3 Skill / Prompt Routing

Beacon skill 与 prompt contract 应当：
- 未 freeze 前阻止直接 implement
- change request 存在时优先建议 reopen
- 通过 `status → help → doctor → action` 顺序做路由

### 10.4 评分体系

建议冻结 4 个评分：
- `test_score`
- `closure_score`
- `readiness_score`
- `quality_score`

## 10. 成功标准

1. 没有外部 adapter 时，Beacon 仍可原生完成 implementation。
2. story / AC / test item 有稳定 id 与 machine-backed state。
3. 生命周期具备 `draft / refined / frozen / implementing / verifying / accepted` 正式状态。
4. 任意阶段变更都能通过新 revision 重入，不污染历史闭环。
5. status board 能看见：
   - 当前 revision
   - item 覆盖率
   - acceptance closure
   - blocked reason

## 11. 成功标准

- 不复制 DeerFlow 全栈平台广度
- 不复制 GSD 2 全量 runtime 与 UI
- 不在 v1.1.6 引入 release 自动化扩张
- 不以长期兼容旧实现模型为目标

## 12. 非目标

v1.1.6 的本质不是“新增 implement 子命令”，而是：

> 让 Beacon 拥有 **原生实现能力 + revision 化生命周期 + item 级 writeback + 任意阶段可重入闭环** 的正式交付能力。


## 13. 一句话结论

v1.1.6 的本质不是“新增 implement 子命令”，而是：

> 让 Beacon 拥有 **原生实现能力 + revision 化生命周期 + item 级 writeback + 任意阶段可重入闭环 + stage-aware navigator layer** 的正式交付能力。
