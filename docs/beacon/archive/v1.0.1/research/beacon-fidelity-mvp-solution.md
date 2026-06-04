# Brainstorm 收敛方案：Beacon 业务不失真 + 测试全面 + 防假通过 + 最小MVP

> 核心诉求：按用户故事小粒度交付，避免过度设计与信号失真。

## 1. 七维收敛结论

### 用户维度
- 目标用户：PM / 开发 / QA / 发布负责人。
- 共同诉求：不是“流程更多”，而是“结果可追溯、可验证”。

### 场景维度
- 需求评审、开发实现、测试验收、发布决策四个场景必须共享同一事实源。

### 业务维度
- 质量信号必须“可审计”，否则流程成本高于价值。

### 技术维度
- 先最小链路，再智能扩展：Story→AC→TC→Code→Evidence。

### 体验维度
- 一眼看到每个故事：实现了什么、怎么验收、证据在哪里。

### 价值维度
- 降低沟通偏差、减少回归风险、支持持续迭代学习。

### 风险维度
- 最大风险：过度抽象、启发式通过、文档与代码分叉。

---

## 2. 设计理念（不失真、不偏移）

1. **Truth-first**：真实执行证据 > 描述性文本。
2. **Story-first**：所有实现必须挂在用户故事和 AC 上。
3. **MVP-first**：每轮只交付“最小可验证切片”。
4. **Default-strict**：默认严格，放宽必须留痕。
5. **Single-source**：事实源唯一，文档自动生成。

---

## 3. 最小可行执行模型（MVS: Minimum Verifiable Slice）

每个用户故事拆成小切片（Slice），每个切片必须满足：

- 1 个 `story_id`
- 1~N 个 `ac_id`
- 每个 `ac_id` 至少 1 个 `tc_id`
- 至少 1 条 `impl_ref`（commit/PR）
- 至少 1 个 `evidence_ref`（可解析文件）

> 未满足任一项：不得进入 PASS。

---

## 4. 测试全面且防假通过（Gate 最小规则）

## 4.1 全面性（Coverage）
- `story_coverage = implemented_story / planned_story`
- `ac_coverage = tested_ac / total_ac`
- `tc_coverage = executed_tc / total_tc`
- 三项任一 < 100%：本轮仅可标记 partial，不可 release-pass。

## 4.2 防假通过（Anti False-Pass）
- 无真实执行命令/产物：`BLOCK`
- 仅启发式命中（关键词/URL）且无执行证据：`BLOCK`
- evidence 文件不存在或不可解析：`BLOCK`
- 关键动作（login/register/browse/submit-form）缺任一：`FAIL`

## 4.3 最小新增 reason codes
- `traceability_broken`
- `evidence_not_verifiable`
- `heuristic_pass_detected`
- `mvp_scope_drift`

---

## 5. 防过度设计机制（Scope Budget）

每个故事设置 **MVP 预算**：
- 新增模块数 <= 1
- 新增外部依赖 <= 1
- 变更文件数 <= 预设阈值（如 8）
- 非故事 AC 关联改动占比 <= 20%

超预算触发：`mvp_scope_drift`，必须人工确认后继续。

---

## 6. 记忆体接入（可演进）

在现有 memory/lifecycle 基础上新增最小追踪边：
- `story_id -> ac_id`
- `ac_id -> tc_id`
- `ac_id -> impl_ref`
- `tc_id -> evidence_ref`

每轮写回：
- 成功模式（decision）
- 失败模式（insight）
- 下轮建议（decision + tag: next-iteration）

---

## 7. 三阶段落地（推荐）

### P0（本周）
- 接入 anti-false-pass 与 traceability gate
- 强制 evidence 可验证
- 输出 coverage 指标

### P1（下周）
- 增加 MVP 预算检查（scope drift）
- report/status 展示 story/ac/tc 链路健康度

### P2（后续）
- 基于历史失败模式自动生成下轮切片建议
- 做“最小改动优先”排序

---

## 8. 完成定义（Definition of Done）

一个故事完成 = 同时满足：
1. AC 全覆盖并执行通过；
2. 代码改动与 AC 可追溯；
3. 证据可读取、可复核；
4. 无假通过 reason code；
5. 未触发或已批准 `mvp_scope_drift`。

