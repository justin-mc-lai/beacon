# PRD: Beacon v1.3.9 beacon-friction-intake and sqlite governance queue

**Feature**: `beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue`  
**Version**: `v1.3.9`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/archive/v1.3.9/SUMMARY.md`
- Execution index: `docs/beacon/archive/v1.3.9/execution/index.md`
- Existing PRDs in line:
  - `beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write`
  - `beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility`
  - `beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility`
- Current code anchors:
  - `beacon/utils/memory_friction_evolution.py`
  - `beacon/utils/runtime_projection_store.py`
  - `beacon/utils/runtime_projection.py`
  - `beacon/utils/debug_feedback.py`
- Current analysis anchors:
  - `docs/brainstorms/2026-04-28-beacon-support-skill-should-evolve-memory-friction-evolution-from-per-project-an.md`
  - `.beacon/analysis/memory-friction-evolution-mfe-20260428T073035Z.md`

## 1. 问题

Beacon 当前已经有 `memory-friction-evolution` 工具，也已经有全局 runtime ledger SQLite，但它仍然缺少一个统一、可治理、可长期积累的摩擦录入入口。

现状问题有四个：

1. 入口语义不对
   - `memory-friction-evolution` 更像“分析工具”或“报告生成器”。
   - 它无法自然覆盖两类实际操作：
     - Beacon 源码项目内自动扫描项目摩擦、阻塞、bug
     - 目标开发项目内人工记录一次上下文摩擦，再交给 LLM 分类治理

2. 录入与治理断开
   - 目前更多是项目内分析文件输出。
   - 缺少一个 host-visible 的统一入口，把摩擦写入全局 sqlite 队列，供后续 claim、resolve、review、route 消费。

3. 现有 `debug_issues` 语义不适合直接承接
   - `debug_issues` 是 runtime projection 的当前观察快照。
   - 它不是摩擦 intake 队列，也不承担 claim / resolve / accepted_for_requirement 语义。

4. requirement/change 路由边界不够显式
   - 摩擦被发现，不等于已经进入正式需求。
   - 如果没有显式接受门，frozen requirement truth 会被持续调试噪音污染。

## 2. 目标

### 2.1 主要目标

- 将这条能力线重定义为 `beacon-friction-intake`。
- 把它明确为 Beacon 的摩擦录入入口，而不是主生命周期 stage。
- 支持两种录入模式：
  - `scan`
  - `capture`
- 两种模式都进入全局 sqlite 队列治理。
- 只有在显式接受后，才允许路由到 `beacon-prd` 或 `beacon-change`。

### 2.2 非目标

- 不把 `beacon-friction-intake` 提升为新的主 Beacon stage。
- 不把全局 SQLite 变成第二份项目证据 truth 副本。
- 不让 friction intake 自动改写 frozen requirement truth。
- 不把 `debug_issues` 直接重定义为 friction queue。

### 2.3 Truth 与 Projection 边界

- 目标项目 `.beacon/debug/`、`.beacon/memory/`、`.beacon/analysis/` 继续承担原始证据 truth。
- 全局 SQLite 只承担索引、分类、状态、来源、关系、治理轨迹。
- requirement truth 仍只通过 `beacon-prd` / `beacon-change` 更新。

## 3. 设计原则

### 3.1 One Intake Surface, Two Capture Modes

- `beacon-friction-intake` 是唯一推荐的人类入口。
- 同一入口支持：
  - `scan`：在 Beacon 源码项目中自动扫描项目摩擦、阻塞、bug、重复问题
  - `capture`：在目标开发项目中人工记录一次上下文摩擦，再由 LLM 归一化与分类

### 3.2 Local Truth, Global Queue

- 原始证据留在项目内。
- 全局 SQLite 只承接治理必需的最小索引与队列状态。
- 禁止把 sqlite 扩张成全文证据仓库。

### 3.3 分层治理优先

- 录入层、治理层、requirement/change 层必须分开。
- intake 只负责把摩擦转成可消费队列，不越权写入 requirement truth。

### 3.4 Write / Read Separation

- `scan` / `capture` 负责写入。
- `inbox` / `claim` / `resolve` / `reopen` 负责读取与消费。
- 分析报告是辅助视图，不再是唯一主产物。

### 3.5 No Silent Auto-Routing

- 任何摩擦项在进入 `accepted_for_requirement` 前，都只属于治理队列。
- 未显式接受前，不得自动进入：
  - `prd`
  - `user-story`
  - `test-case`
  - `implement`
  - `qa`
  - `release`

## 4. 范围

### In scope

- 将能力线命名与对外语义收紧为 `beacon-friction-intake`
- 支持 `scan` 与 `capture` 双模式
- LLM 自动完成 summary / class / severity / domain 归类
- dual-write 到项目内产物与全局 runtime ledger sqlite
- 形成可 claim / resolve / reopen / route 的治理队列
- 与 `beacon-prd` / `beacon-change` 建立显式接受后路由边界

### Out of scope

- 自动生成完整 `user-story` / `test-case` / `implement plan`
- 建立新的主 workflow stage
- 一次性重写所有历史 debug/runtime projection 模型
- 将全部历史 friction 文档强制回填

## 5. 功能需求

### FR-001 `beacon-friction-intake` 必须是统一摩擦录入入口

- 新入口对人类语义是“录入摩擦”，不是“生成分析报告”。
- 旧的 `memory-friction-evolution` 应视为底层实现来源或待兼容入口，而不是长期主语义。

### FR-002 必须支持 `scan` 与 `capture` 双模式

- `scan`
  - 适用于 Beacon 源码项目
  - 自动扫描项目摩擦、阻塞、bug、重复出现的问题
- `capture`
  - 适用于目标开发项目
  - 接收人工输入的一次上下文摩擦记录
  - 再由 LLM 做标准化、分类与证据绑定

### FR-003 双模式都必须进入全局 sqlite 队列治理

- 任一 `scan` 或 `capture` 完成后：
  - 项目内分析与证据可继续保留
  - 全局 sqlite 中必须出现对应 friction item 与治理状态
- 若 sqlite 暂时不可用：
  - 项目内 truth 必须继续保留
  - dual-write 失败必须显式记录
  - 后续必须支持恢复语义与重放

### FR-004 分类模型必须可被 Beacon 产品治理直接消费

- 任一 friction item 至少带有：
  - `item_class`
  - `severity`
  - `domain`
  - `queue_status`
  - `source_type`
  - `project_key`
  - `project_root`
  - `summary`
  - `evidence_refs`
  - `first_seen_at`
  - `last_seen_at`
- 最小分类集：
  - `item_class`: `blocking_bug | improvement | optimization_enhancement`
  - `source_type`: `scan | manual_capture`

### FR-005 `debug_issues` 不得直接替代 friction queue

- `debug_issues` 继续服务 runtime projection board / status / doctor。
- friction queue 必须作为独立治理层存在。
- 两者可以引用，但不能混表覆盖。

### FR-006 requirement/change 路由必须显式接受

- 默认状态下，friction item 只进入治理队列。
- 只有被显式推进到 `accepted_for_requirement` 或等价状态时：
  - 才允许进入 `beacon-prd`
  - 或进入 `beacon-change`

## 6. 数据 / 状态 / 集成

### 6.1 建议最小数据模型

- `friction_items`
  - 当前 item 主状态与分类
- `friction_refs`
  - 项目内证据引用
- `friction_events`
  - 追加式治理事件

### 6.2 与现有 runtime ledger 的关系

- 复用 `~/.beacon/runtime-ledger/runtime-ledger.sqlite3`
- 复用现有 sqlite 连接、迁移、WAL、verify、export/rebuild 机制
- 不新增第二个全局 sqlite

### 6.3 双模式统一输出

- `scan` 与 `capture` 都输出到同一治理队列。
- 差异只体现在 `source_type` 与 evidence 生成方式。

### 6.4 状态机

```text
scan/capture
-> classified
-> queued
-> claimed
-> resolved
```

补充分支：

```text
queued
-> discarded

resolved
-> reopened

claimed
-> accepted_for_requirement
-> beacon-prd / beacon-change
```

### 6.5 恢复语义

- sqlite 不可用时，必须保留项目内 truth，并允许后续恢复后 replay。
- 已关闭项若因新证据漂移重新成立，必须支持 reopen。

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 继续沿用 `memory-friction-evolution` 旧语义，导致入口被误解为分析工具 | 高 | 对外统一命名为 `beacon-friction-intake`，把分析降为内部机制 |
| `scan` 与 `capture` 分裂成两套流程 | 高 | 统一进入同一 sqlite 队列，只保留 `source_type` 差异 |
| `debug_issues` 与 friction queue 混层 | 高 | 保持 projection 快照与治理队列分层 |
| 全局 sqlite 存储过多原始正文，形成第二份 truth | 高 | 仅存最小治理索引与 evidence refs |
| 自动路由 requirement，污染 frozen truth | 高 | 只允许显式 accepted 后进入 `beacon-prd` / `beacon-change` |

## 8. 验收标准

### AC-001 统一入口语义成立

- Beacon 存在明确的 `beacon-friction-intake` 能力定义。
- 人类能理解它是“摩擦录入入口”，而不是“分析报告工具”。

### AC-002 双模式录入成立

- Beacon 源码项目中可以执行 `scan` 来抽取项目摩擦、阻塞、bug。
- 目标开发项目中可以执行 `capture` 来记录一次人工上下文摩擦。

### AC-003 sqlite 治理队列成立

- 任一 `scan` 或 `capture` 完成后，都能在全局 sqlite 中看到对应 queue item。
- dual-write 失败时有明确诊断与恢复路径。

### AC-004 requirement/change 路由保持显式

- 新摩擦默认只进入治理队列。
- 只有显式 accepted 后，才会进入 `beacon-prd` 或 `beacon-change`。

### AC-005 项目内原始证据不丢失

- 全局 sqlite 可重建时，项目内 `.beacon/debug/`、`.beacon/memory/`、`.beacon/analysis/` 仍能作为原始 truth 驱动恢复。

## 9. 成功指标

- Beacon 可以跨项目持续沉淀摩擦，而不再只能回看零散分析文件。
- Beacon 可以明确区分“阻塞 bug / 改进 / 优化增强”并统一排队治理。
- Beacon 的产品改进线索只在显式接受后进入 requirement/change，避免持续调试噪音污染主线。

## 10. 与主 PRD 的关系

- 本并行 PRD 不重新定义 Beacon 主生命周期。
- 它补的是 Beacon 支持面中的“摩擦录入与治理入口”。
- 它为 `beacon-prd` / `beacon-change` 提供前置 intake 队列，但不替代正式 requirement surface。
