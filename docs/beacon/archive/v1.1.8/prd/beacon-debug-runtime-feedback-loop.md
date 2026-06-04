# PRD: Beacon Debug 运行时反馈闭环与版本迭代输入（v1.1.8）

## 1. 背景

当前 Beacon 已有 `debug` 能力，主要覆盖：

- prompt / router history 捕获
- `run workflow --mode debug` 的原始事件记录
- `.beacon/state/debug-feedback/*.jsonl` 归档
- debug 事件写入 memory

这套机制解决的是“命令/路由层面怎么 debug”，但**还没有解决真实实践项目里的核心诉求**：

> 当团队在真实项目中深度使用 Beacon skill 和 Beacon 生命周期时，如何把使用过程中的摩擦、卡点、误导、重复动作、缺失能力，实时反馈回 Beacon 源码项目/skill 本身？

用户修正后的目标非常明确：

- 不是只记录 prompt debug；
- 而是要在实践项目中**开启 debug 后，沿着 Beacon skill 生命周期实时产出反馈**；
- 这些反馈要直接沉淀到一个稳定的 `debug` 目录；
- 后续 Beacon 自身做版本规划时，可以直接从这个目录中提炼 vNext 迭代思路。

### 1.1 来自 gstack 源码的直接启发

本地 gstack 源码已经把“工具如何从真实使用中学习”做成显式机制：

- 根 `SKILL.md` 与各技能 preamble 中有 **contributor mode**
- 使用者在体验不是 10/10 时，会直接写 field report 到 `~/.gstack/contributor-logs/`
- `scripts/analytics.ts` 做 skill usage 聚合
- `scripts/eval-watch.ts` 做实时 eval/heartbeat 观察

这说明 gstack 已经把“工具本体也要接收来自实践的反馈”当成正式产品能力。

Beacon 与它的差异是：

- gstack 当前偏 **markdown field report + analytics**
- Beacon 更适合走 **结构化事件 + machine aggregation + issue/idea harvest**

所以 v1.1.8 不是简单模仿 gstack 的 contributor report，而是要把这个理念升级成更适合 Beacon 的 machine-backed 反馈闭环。

## 2. 第一性原理结论

### 2.1 Beacon Debug 的真正职责

Beacon Debug 不应只是“诊断当前命令为什么失败”，还应成为：

- **实践项目使用过程的实时摩擦采集器**
- **Beacon skill / CLI / 生命周期设计缺口的回传通道**
- **版本演进候选需求的原始事实仓**
- **从实践到产品迭代的 bridge 层**

### 2.2 如果没有这层，会发生什么

- 使用 Beacon 时的问题只停留在聊天记录里；
- 后续做版本规划时，需要重新回忆真实痛点；
- 很难知道某个改进到底来自哪个项目、哪个阶段、哪个 skill、哪个具体命令；
- 版本演进容易回到“拍脑袋补功能”，而不是 evidence-first。

## 3. 目标

1. **让 Debug 成为实践项目→Beacon 产品演进的实时反馈通道**
2. **让 Beacon skill 生命周期中的关键摩擦都可结构化记录**
3. **让 Debug 目录可直接作为后续 PRD / US / QA 的输入源**
4. **让 Debug 与项目 workflow/profile/skill 绑定，而不是孤立日志**
5. **保持当前 debug 能力兼容，不破坏已有 prompt/run debug 行为**

## 4. 非目标

1. 不把 Debug 做成通用 APM/日志平台；
2. 不采集无边界的全量 stdout/stderr；
3. 不把 Beacon Debug 变成项目业务日志替代品；
4. 不在 v1.1.8 直接实现自动修复 Beacon 本体；
5. 不要求所有反馈都即时转成正式 PRD。

## 5. 核心设计

## 5.1 Debug 目录从 state 扩展为产品反馈面

当前：
- `.beacon/state/debug-feedback/*.jsonl`

v1.1.8 建议新增 canonical 目录：

```text
.beacon/debug/
  runs/<run_id>/events.jsonl
  runs/<run_id>/summary.json
  issues/<issue_id>.json
  ideas/<date>-<slug>.md
  index.json
```

说明：
- `state/debug-feedback` 保留为底层原始事件兼容面；
- `.beacon/debug/` 成为**实践反馈与产品演进输入的 canonical surface**。

## 5.2 Debug 事件必须带“反馈目标”

每条 debug 事件至少要声明：

- `feedback_target`
  - `beacon-core`
  - `beacon-skill`
  - `project-skill`
  - `workflow-docs`
  - `runner-adapter`

这样才能区分：
- 是 Beacon 核心能力缺口；
- 还是某个项目 skill 的流程问题；
- 还是文档/导航/帮助信息误导。

## 5.3 实践项目中的实时反馈事件

建议事件 schema 至少包含：

- `ts`
- `run_id`
- `project_name`
- `project_root`
- `feature_slug`
- `workflow_stage`
- `beacon_command`
- `skill_id`
- `profile_id`
- `feedback_target`
- `severity`
- `reason_code`
- `expected`
- `actual`
- `friction_summary`
- `workaround`
- `artifact_refs[]`
- `source_refs[]`
- `suggested_capability`
- `candidate_doc_slug`

## 5.4 生命周期阶段必须可追踪

Debug 不应脱离 Beacon lifecycle，至少要覆盖：

- think
- user-story
- prd
- prototype
- freeze
- implement
- verify
- review-quality
- review-accept
- release

重点不是“都记录一句话”，而是：

> 哪个阶段最卡、为什么卡、Beacon 应该补什么能力。

## 5.5 实时反馈不只记录失败，也记录高摩擦成功

因为很多真实问题不是“失败”，而是：

- 明明成功了，但步骤过长；
- 需要用户重复给同一类上下文；
- help / doctor 给错了下一步；
- skill 要靠人工拼装而不是自动编排；
- 文档物料与执行面之间来回切换成本太高。

所以事件应支持：

- `severity = blocker | high | medium | low`
- `result = failed | degraded | succeeded-with-friction | improved`

## 5.6 从 Debug 目录自动汇聚迭代候选

新增建议聚合物：

- `issues/<issue_id>.json`
- `ideas/<date>-<slug>.md`
- `index.json`

聚合逻辑：
- 同类 friction 聚合为 issue；
- 高频 issue 自动升格为 candidate idea；
- 供 Beacon 版本规划直接读取。

## 6. 命令面建议

### 6.1 保留现有命令
- `beacon debug enable`
- `beacon debug disable`
- `beacon debug status`
- `beacon debug watch`
- `beacon debug sync-prompts`
- `beacon debug capture`

### 6.2 新增建议命令
- `beacon debug project-feed <feature>`
- `beacon debug issue list`
- `beacon debug issue show <issue_id>`
- `beacon debug harvest`
- `beacon debug export-ideas`

## 7. 功能需求

### FR-001 Debug 必须支持实践项目实时反馈
当实践项目开启 Beacon debug 后，使用 Beacon skill 生命周期过程中必须持续记录结构化反馈，而不是只记录 prompt/router 事件。

### FR-002 Debug 必须与 skill/profile/stage 绑定
每条反馈必须知道：
- 用的是哪个 skill
- 属于哪个 profile
- 卡在哪个 lifecycle stage
- 对应哪个 feature/run

### FR-003 Debug 目录必须能直接服务版本迭代
`.beacon/debug/` 中的聚合 issue / idea 必须可直接作为后续 Beacon 自身版本 PRD 输入，不应只是原始日志堆积。

### FR-004 Debug 要支持“成功但高摩擦”场景
不允许只记录失败；高摩擦成功同样应成为迭代输入。

### FR-005 Debug 事件必须标注反馈目标
必须明确该反馈是：
- Beacon core
- Beacon skill
- 项目 skill
- workflow docs
- runner adapter

### FR-006 Debug 输出必须包含建议能力方向
事件或聚合 issue 至少要能给出：
- `suggested_capability`
- `candidate_doc_slug`
- `candidate_version_line`

### FR-007 Debug 不得污染业务日志
Debug 采集要聚焦 Beacon 使用摩擦，不得退化成项目业务日志全量复制。

### FR-008 Debug 与 report / help / doctor 联动
- `help` 可提示当前 debug 是否开启
- `doctor` 可提示当前项目是否存在高频 Beacon friction
- `report` 可汇总 debug 统计，用于版本演进评审

### FR-009 v1.1.8 为设计线，先冻结语义
当前只定义结构、目录、字段、命令与闭环，不宣称已编码实现。

## 8. 验收语义

### Pass
- Debug 被正式定义为实践反馈→产品演进输入层；
- 目录、事件、聚合、命令、lifecycle 绑定都明确；
- 可以直接支撑 Beacon 版本迭代 planning。

### Fail
- 仍然只把 Debug 当成 prompt/router 调试；
- 无法支持实践项目中实时采集 Beacon 自身能力缺口；
- 没有可供版本规划消费的 debug 目录产物。

### Blocked
- Debug 目录、事件字段或聚合语义仍存在关键冲突。
