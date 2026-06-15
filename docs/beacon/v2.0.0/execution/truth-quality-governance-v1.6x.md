# 需求真相质量治理：v1.6.x 核心问题诊断与根治方案

> authority: support_advisory
> status: draft
> created: 2026-06-14
> branch: worktree-v2-migration-plan
> priority: P0 — v1.6.x 稳定基线的根本性问题
> companion: v1.6-to-v2-migration-roadmap.md

---

## 1. 问题陈述

### 1.1 症状

Beacon v1.6 的需求真相（truth.md）在冻结后仍存在以下问题：

1. **模板占位**：truth.md 中存在 `TBD`、`pending`、`待定`、`TODO` 等占位内容，冻结并未阻止这些占位进入正式真相
2. **凑格式**：为了满足 PRD / user-story / test-case 的模板结构，填充了形式上完整但语义上空洞的内容
3. **意图失真**：没有从用户真实意图和上下文分析中反复提炼，而是从模板结构反向推导填充，导致 truth 不是用户真实需求的确定性表述
4. **冻结虚假安全感**：freeze 通过了，但冻结的是空壳——格式合规 ≠ 内容确定

### 1.2 根因

Beacon 的 truth 生成路径存在一个**结构性缺陷**：

```
当前路径（有缺陷）:
  模板结构 → 填充字段 → 格式检查 → freeze → "真相"

应该的路径:
  用户意图 → 上下文分析 → 确定性表述 → 证据支撑 → 验证无占位 → freeze → 真相
```

问题出在 truth 的**来源**和**质量关卡**两个环节：

- **来源**：truth 生成过程是"模板驱动"而非"意图驱动"。生成器拿到一个模板骨架，逐字段填充，而不是从用户 utterance 出发逐步提炼确定性需求。
- **质量关卡**：freeze gate 检查的是格式完整性和链路闭合性（AC 有无、TC 有无），但不检查**内容确定性**。一个全是 "TBD" 的 AC 可以通过格式检查。

---

## 2. 确定性需求真相的定义

### 2.1 什么是确定性表述

确定性表述满足以下条件：

| 条件 | 说明 | 反例 |
|------|------|------|
| **无占位词** | 不含 TBD/pending/待定/TODO/TBC/待确认 | "AC-003: 性能 TBD" |
| **无空洞模板句** | 不含"需进一步确认"/"视情况而定"/"参考xxx" | "AC-005: 需与团队确认后补充" |
| **可验证** | 每个表述都存在客观的验证手段 | "系统应具有良好的用户体验" |
| **有边界** | 明确什么在范围内、什么不在 | "支持所有格式" |
| **来源可追溯** | 能追溯到具体的用户意图或上下文分析 | 无来源的"行业标准要求" |

### 2.2 什么是确定性 truth.md

一份确定性 truth.md：

- 每个 AC 都是**可独立验证**的确定性陈述
- 不存在任何需要"后续补充"或"待确认"的字段
- 每个需求的来源可追溯到用户意图或上下文分析
- freeze 后的 truth 与用户真实意图之间无语义鸿沟

---

## 3. 治理方案

### 3.1 新增 Truth Integrity Gate — Determinism Check（TIG-DC）

在现有 TIG（Truth Integrity Gate）基础上增加**确定性检查层**：

```
freeze 执行链（增强后）:
  1. TIG-Placeholder   — 检测占位词（TBD/pending/待定/TODO/TBC/待确认）
  2. TIG-TemplateFill  — 检测空洞模板句（"需进一步确认"/"视情况而定"/"参考xxx"）
  3. TIG-Verifiability — 检测不可验证的 AC（无客观验证手段的陈述）
  4. TIG-Boundary      — 检测无边界表述（"支持所有"/"兼容全部"）
  5. TIG-Provenance    — 检测无来源需求（无法追溯到用户意图的 AC）
  6. 现有 TIG 检查继续...
  7. freeze 通过
```

**核心规则**：TIG-DC 任何一项不通过 = freeze 被阻止。这是 fail-closed 语义。

### 3.2 Intent-First Truth Generation Protocol（意图优先真相生成协议）

改造 truth 生成流程，从模板驱动转向意图驱动：

```
Phase 1: Intent Capture（意图捕获）
  输入: 用户 utterance / 上下文 / 历史需求
  输出: 意图清单（每个意图是确定性陈述，非模板字段）
  规则: 不允许在这一步引用模板结构

Phase 2: Intent Verification（意图验证）
  输入: 意图清单
  输出: 用户确认的意图（或修正后的意图）
  规则: 必须获得用户显式确认，不可自动通过

Phase 3: Structured Truth Derivation（结构化真相推导）
  输入: 确认后的意图清单
  输出: truth.md（从意图推导，不是从模板填充）
  规则: 每个字段的内容必须能追溯到至少一个意图

Phase 4: Determinism Verification（确定性验证）
  输入: truth.md
  输出: TIG-DC 检查结果
  规则: 全部通过才能进入 freeze

Phase 5: Freeze（冻结）
  输入: 通过 TIG-DC 的 truth.md
  输出: frozen truth
  规则: 冻结后不可修改（只能 refreeze）
```

### 3.3 占位词黑名单（Placeholder Blacklist）

定义一个持续维护的占位词黑名单，freeze gate 硬检查：

```json
{
  "placeholder_patterns": [
    {"pattern": "\\bTBD\\b", "severity": "block"},
    {"pattern": "\\bpending\\b", "severity": "block", "case_insensitive": true},
    {"pattern": "待定", "severity": "block"},
    {"pattern": "待确认", "severity": "block"},
    {"pattern": "\\bTODO\\b", "severity": "block"},
    {"pattern": "\\bTBC\\b", "severity": "block"},
    {"pattern": "需进一步确认", "severity": "block"},
    {"pattern": "视情况而定", "severity": "block"},
    {"pattern": "参考.*补充", "severity": "block"},
    {"pattern": "后续补充", "severity": "block"},
    {"pattern": "待.*确认", "severity": "block"},
    {"pattern": "需与.*确认", "severity": "block"}
  ],
  "hollow_template_patterns": [
    {"pattern": "具有良好的?", "severity": "warn"},
    {"pattern": "支持所有", "severity": "block"},
    {"pattern": "兼容全部", "severity": "block"},
    {"pattern": "根据实际情况", "severity": "block"},
    {"pattern": "按照.*规范", "severity": "warn"}
  ],
  "verifiability_heuristics": [
    {"rule": "AC 不含可量化标准且非纯存在性断言", "severity": "warn"},
    {"rule": "AC 含'良好'/'合理'/'适当'/'足够'等主观词", "severity": "warn"}
  ]
}
```

**severity 说明**：
- `block`：freeze 直接阻止
- `warn`：不阻止 freeze，但写入 gate report 要求 refreeze 前解决

### 3.4 Provenance Chain（来源追溯链）

每个 AC 必须能追溯到来源。在 truth.md 的 frontmatter 中增加 `provenance` 字段：

```yaml
---
feature: beacon-truth-quality-governance
version: v1.6.1
status: draft
provenance:
  - ac_id: AC-001
    source_type: user_intent        # user_intent | context_analysis | constraint_derivation
    source_ref: "用户陈述：'需求真相冻结后不应存在占位内容'"
  - ac_id: AC-002
    source_type: context_analysis
    source_ref: "v1.6.0 冻结的 truth.md 中 3 处 TBD，2 处 pending"
  - ac_id: AC-003
    source_type: constraint_derivation
    source_ref: "global-boundaries.md Section 2: truth/acceptance/gate 标准不可降级"
---
```

**规则**：
- `source_type` 只允许三种：`user_intent`（用户直接陈述）、`context_analysis`（从上下文分析推导）、`constraint_derivation`（从约束推导）
- 不允许 `template_fill`（从模板填充）作为 source_type
- freeze gate 检查：每个 AC 必须有 provenance 条目

---

## 4. 实施路径（v1.6.x 稳定迭代内）

### 4.1 Phase A：TIG-DC 实现（v1.6.1）

| 任务 | 说明 | 难度 |
|------|------|------|
| 定义占位词黑名单 JSON | `beacon/artifact-language-policy.json` 扩展或新建 `truth-quality-policy.json` | EASY |
| 实现 `check_placeholder_content` | 扫描 truth.md 中占位词，返回 `{ac_id, pattern, line}` 列表 | MEDIUM |
| 实现 `check_hollow_template` | 扫描空洞模板句模式 | MEDIUM |
| 实现 `check_verifiability` | 启发式检测不可验证 AC（主观词、无量词标准） | MEDIUM |
| 实现 `check_provenance` | 验证 frontmatter provenance 字段完整性 | EASY |
| 集成到 `freeze.py` gate 链 | 在现有 TIG 之后、freeze 之前执行 | EASY |
| 添加 `beacon doctor verify-truth-quality` | 独立运行 TIG-DC，不依赖 freeze | EASY |
| 测试 | 对 v1.6.0 已冻结 truth.md 执行，应检出实际占位 | EASY |

### 4.2 Phase B：Intent-First Protocol 落地（v1.6.2）

| 任务 | 说明 | 难度 |
|------|------|------|
| `beacon gen-truth` 增加 intent-first 模式 | `--intent-first` flag 切换生成协议 | MEDIUM |
| 意图捕获 prompt 模板 | 替代当前模板填充式 truth 生成 | MEDIUM |
| provenance 字段生成 | 在 truth 生成过程中自动记录来源 | MEDIUM |
| 用户确认交互 | 意图清单输出后要求用户显式确认 | EASY |
| 端到端验证 | 从用户 utterance 到冻结 truth 的完整链路 | HARD |

### 4.3 Phase C：存量 truth 清洗（v1.6.x 持续）

| 任务 | 说明 |
|------|------|
| 对 v1.6.0 已冻结 truth.md 运行 TIG-DC | 生成问题清单 |
| 逐 feature 补充 provenance | 追溯每个 AC 的真实来源 |
| 清洗占位内容 | 将 TBD/pending 替换为确定性表述或降级为 research |
| refreeze | 清洗后重新冻结 |

---

## 5. 与 v2 迁移的关系

本治理方案与 v2 迁移的关系：

1. **TIG-DC 是 v2 gate 引擎的前置输入**：v2 P3 阶段移植 gate.py 时，TIG-DC 逻辑必须已稳定。否则 v2 gate 会复刻"冻结空壳"的缺陷。
2. **Intent-first protocol 影响 orchestrator 设计**：v2 orchestrator 的 `goal` 入口应直接采用 intent-first 协议，而不是先实现模板驱动再改造。
3. **provenance 字段是 v2 DB 的必要 schema**：`feature_packages` 表应包含 `provenance_json` 列，在 P1 schema 对齐时加入。
4. **占位词黑名单是跨版本共享契约**：与 reason_codes 一样，占位词黑名单应作为独立 JSON 文件，Python 和 Rust 两边从同一份源读取。

**关键原则**：v1.6.x 的 truth 质量治理必须先于 v2 的 gate 移植。如果 v1.6 的 truth 仍然是空壳，v2 的 gate 只会更快地冻结空壳。

---

## 6. 验收标准

### Phase A (v1.6.1)

- [ ] `beacon doctor verify-truth-quality` 对任意 truth.md 能检出占位词
- [ ] `beacon freeze` 在存在占位词时被阻止（fail-closed）
- [ ] 对 v1.6.0 已冻结 truth.md 运行 TIG-DC，输出具体问题清单
- [ ] TIG-DC 测试覆盖：占位词检测、空洞模板检测、不可验证 AC 检测

### Phase B (v1.6.2)

- [ ] `beacon gen-truth --intent-first` 生成的 truth.md 无占位词
- [ ] 生成的 truth.md 每个AC有 provenance 来源
- [ ] 从用户 utterance 到冻结 truth 的端到端链路可演示

### Phase C (持续)

- [ ] v1.6.0 所有 feature truth.md 占位内容清零
- [ ] 所有 AC 有 provenance 来源
- [ ] refreeze 后 gate 全绿

---

## 7. 核心洞察

> **冻结不是目的，确定性才是。**
> 
> Beacon 的 truth 系统的核心价值不在于"有一份格式完整的文档"，而在于"每一个需求陈述都是确定性的、可验证的、可追溯到用户真实意图的"。
> 
> 模板填充产生的是形式真相，不是实质真相。只有从用户意图出发、经过上下文分析验证、不含任何占位和空洞的确定性表述，才配得上"truth"这个名字。
> 
> 这个问题不在 v2 Rust 重写的范围内——它是方法论层面的。Rust 可以让空壳冻结得更快，但不能让空壳变成真相。v1.6.x 必须先解决这个问题，v2 才能站在确定性的地基上构建。
