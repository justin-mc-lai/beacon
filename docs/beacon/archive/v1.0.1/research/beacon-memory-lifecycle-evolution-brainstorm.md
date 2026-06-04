# Brainstorm：Beacon 迭代生命周期接入记忆体与可演进闭环（v1.0.1）

- 日期：2026-03-03
- 目标：让「用户故事 → 代码实现 → 测试验收」形成可追踪、可复用、可演进的记忆链路

## 0. 现状（基于当前实现）

已具备能力：

- 记忆条目：`.beacon/memory/{project-insights,decisions,vocabulary}.json`
- 生命周期事件：`.beacon/memory/workflow-lifecycle.json`
- 阶段注入/回写：`write_stage_context` + `record_stage_writeback`
- 反馈同化：`feedback sync` → `feedback_memory_assimilated`

主要缺口：

1. 记忆闭环仅覆盖 `think/user-story/prd/test-case`，对 `implementation/verify/release` 不完整
2. 用户故事、代码提交、测试证据缺少统一 ID 图谱绑定
3. 记忆回写内容偏摘要，结构化追踪字段不足（AC/TC/commit/test_run）

---

## 1) 用户维度（谁最受益）

- PM：希望每次迭代都能看到需求演进脉络（为什么改）
- 开发：希望知道“这段代码对应哪个故事/AC”
- QA：希望知道“这个测试结果验证了哪个 AC/TC”
- 发布负责人：希望 gate 报告有可审计证据链

结论：核心用户是 PM+Dev+QA 协作团队，目标是“协作记忆而非个人记忆”。

---

## 2) 场景维度（何时触发记忆）

关键触发点：

1. Story 创建/变更
2. 代码提交/合并
3. 测试执行/回归
4. 缺陷修复与复测
5. 版本复盘

建议：每个触发点都产出一条 `trace event`，自动写入记忆与生命周期。

---

## 3) 业务维度（为什么值得做）

- 降低“换人即失忆”成本
- 减少重复讨论与重复踩坑
- 提升发布信号可信度（从“看起来通过”变成“证据可追溯通过”）

可量化指标：

- AC 覆盖可追踪率（目标 >95%）
- 缺陷复发率（目标下降）
- 需求回溯时间（目标下降）

---

## 4) 技术维度（核心设计）

## 4.1 统一追踪 ID 体系（建议）

- `feature_id`（如 `F-v1.0.1-ui-false-pass`）
- `story_id`（US-xxx）
- `ac_id`（AC-xxx）
- `tc_id`（TC-xxx）
- `impl_id`（commit sha / PR id）
- `verify_run_id`（测试运行批次）

## 4.2 追踪关系图（新增文件）

新增：`.beacon/memory/traceability.jsonl`（或 `traceability-graph.json`）

每条边：

- `story_id -> ac_id`
- `ac_id -> tc_id`
- `tc_id -> evidence_ref`
- `ac_id -> impl_id`
- `impl_id -> verify_run_id`

## 4.3 生命周期扩展（现有基础上增强）

当前 `WORKFLOW_STAGES` 扩展为：

- `think, user-story, prd, test-case, implementation, verify, release`

并保证每阶段都有：

- `stage_started`
- `stage_context_injected`
- `stage_finished`
- `memory_writeback`

---

## 5) 体验维度（团队如何使用）

目标体验：

- 一条命令可看“从故事到代码到测试”的链路
- 任一失败能定位到具体 AC/TC/证据缺口

建议新增查询视图：

- `beacon recall trace --feature <id>`：输出链路图
- `beacon report --machine` 增加 `traceability_metrics`

---

## 6) 价值维度（形成核心迭代演进）

形成“记忆驱动迭代”闭环：

1. **Recall**：迭代开始前注入历史记忆
2. **Plan**：用户故事/PRD 绑定上轮反馈
3. **Build**：代码提交关联 story/ac
4. **Verify**：测试结果关联 tc/ac/evidence
5. **Learn**：反馈同化为 insight/decision
6. **Evolve**：生成下一轮建议与风险清单

---

## 7) 风险维度（可能失败点与应对）

| 风险 | 影响 | 应对 |
|------|------|------|
| 开发嫌麻烦，不填关联 ID | 链路断裂 | 自动从 commit message / PR template 抽取 |
| 历史数据不完整 | 统计失真 | 允许 `unknown`，并逐轮补齐 |
| 事件太多导致噪音 | 难以阅读 | 分层存储（raw event + summary memory） |
| 指标好看但无真实价值 | 形式化 | 强制 gate 使用 trace 指标参与判定 |

---

## 收敛方案（建议 v1.0.2 起分步落地）

### P0（先打通链路）

1. 扩展生命周期阶段到 implementation/verify/release
2. 写入统一追踪字段（story_id/ac_id/tc_id/impl_id/run_id）
3. 在 gate 增加 `traceability_broken` 检查

### P1（增强可观测）

1. 新增 `traceability.jsonl`
2. `report/status/resume` 输出 trace 指标
3. 增加 `beacon recall trace` 查询

### P2（形成演进引擎）

1. 基于历史缺陷/失败原因自动生成下一轮改进建议
2. 引入记忆置信度衰减与“被证伪”标记

---

## 最小验收标准

- 每个 AC 至少关联一个 TC 与一个实现证据（commit/PR）
- 每个 TC 至少关联一个执行证据（artifact）
- Gate 报告可列出断链节点并阻断发布
- 复盘时可自动生成“本轮决策 -> 下轮动作”建议
