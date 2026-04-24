# PRD：Beacon v1.3.6 记忆基座与全场景证据召回

**Feature**: `beacon-v1.3.6-memory-foundation-and-full-scene-evidence-recall`  
**Version**: `v1.3.6`  
**Date**: `2026-04-21`  
**Status**: `planning line`  
**Track**: `main`  
**Scenario**: `workflow-native-memory-foundation`  
**Template**: `主 PRD / memory-foundation`  
**Source Mirror**: `docs/beacon/v1.3.6/prd/beacon-v1-3-6-memory-foundation-and-full-scene-evidence-recall.md`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/v1.3.6/SUMMARY.md`
- Memory-agent research: `docs/beacon/v1.3.6/research/beacon-oss-sync-memory-agents-absorption-analysis.md`
- Brainstorm draft: `docs/plans/2026-04-21-beacon-v1.3.6-memory-foundation-brainstorm.md`
- Current memory core:
  - `beacon/utils/memory.py`
  - `beacon/utils/workflow_memory.py`
  - `beacon/utils/memory_friction_evolution.py`
  - `beacon/commands/recall.py`

## 1. 问题

### 1.1 Beacon 已有 memory 闭环，但不具备强记忆基座

Beacon 当前已经有三类与记忆相关的能力：

- `memory-v1.json` 为主的 typed memory
- `workflow-lifecycle.json` 为主的阶段生命周期追踪
- `memory-friction-evolution` 为主的记忆/摩擦候选收敛

这说明 Beacon 不是“没有记忆”，而是已经有一套偏 workflow/debug 的记忆闭环。

当前真正的问题是：

1. 原始证据没有正式成为独立真相层。
2. recall 仍偏摘要与词项匹配，不足以支撑复杂接力。
3. memory writeback 有损，很多信息在沉淀时被压成一句 feedback。
4. 需求冻结到交付证据的全链路，缺少统一的跨 artifact 寻址与关联结构。

### 1.2 Beacon 的核心场景正在要求“全场景记忆”，但不是“通用脑”

Beacon 的主价值不是存百科，而是支撑人机协作下的交付闭环：

- 冻结需求时，能够记住为什么这样定义
- 进入实现时，能够接力 requirements、research、prototype、debug evidence
- 进入 QA/release 时，能够回到历史证据定位偏差与漂移

这类“全场景记忆”有两个特点：

1. 必须横跨 `prd / user-story / test-case / prototype / implement / qa / release`
2. 必须仍然受版本、feature、artifact、run、stage 边界约束

所以 Beacon 需要的是：

> workflow-native 的记忆基座

而不是：

> 通用 personal brain / company brain / CRM brain

### 1.3 当前 recall 不足以支撑强可解释接力

当前 Beacon recall 的主要缺口包括：

- 对 raw evidence 的检索弱
- 对 artifact 关系的理解弱
- 对 stage/run/feature 的上下文切片弱
- 返回结果的“为什么命中”解释不够强

结果是：

1. 人类难以快速判断 Beacon 的 recall 是否可信。
2. agent 难以在复杂项目上做稳定接力。
3. 交付证据虽然存在，但难以被重新组织为可操作上下文。

### 1.4 当前 writeback 机制会丢掉重要上下文

`memory-friction-evolution` 当前更接近：

- 候选收敛器
- feedback 压缩器

它还不是：

- evidence-backed memory compiler

如果 Beacon 继续只保存压缩后的结论，就会出现：

- 原始问题样本丢失
- 后续难以重新判断旧结论是否仍然成立
- 同类摩擦是否真的复发，很难被准确比较

### 1.5 没有边界的“记忆增强”会把 Beacon 拉偏

如果只是泛化地说“给 Beacon 增强记忆”，很容易走向下面这些错误：

- 做出第二套 memory silo
- 把宿主 transcript 全量纳入版本 truth
- 引入过重基础设施
- 让 memory 反向劫持 `docs/beacon/<version>/` 的正式地位

这会直接破坏 Beacon 的产品边界。

## 2. 目标

### 2.1 主要目标

`v1.3.6` 需要为 Beacon 增加一层正式的记忆基座，使其能够：

1. 保存原始证据，而不是只保存摘要。
2. 在全工作流阶段里进行强可解释召回。
3. 把 requirement、research、implementation、QA、release 证据连接成可追溯结构。
4. 为人机协作接力生成稳定的 stage context pack。
5. 强化 debug / friction / recurrence 的治理能力。

### 2.2 产品目标

Beacon 的记忆增强必须直接服务以下产品判断：

- 为什么当前需求被冻结成这样
- 当前实现是否仍然遵循冻结真相
- 当前 QA/release 结论依赖哪些证据
- 某类问题是否重复出现，是否已被修复
- 当前接力者最少需要读什么上下文才能继续

### 2.3 非目标

本版本不承担以下内容：

- 把 Beacon 变成通用个人知识脑或公司知识平台
- 引入新的公开一级主命令
- 默认保存完整宿主 transcript 洪流
- 直接引入 Postgres / pgvector 作为必需依赖
- 用 memory 取代 `docs/beacon/<version>/` 的正式 truth 地位

## 3. 方案选择

### 3.1 方案 A：summary-first 增量修补

优点：

- 成本低
- 兼容性最好

缺点：

- 无法解决 raw evidence 缺口
- 只能改善 recall 表面体验，无法补齐记忆基座

### 3.2 方案 B：evidence-first 的 workflow-native 记忆基座

优点：

- 能补齐 Beacon 当前最关键的结构缺口
- 与需求冻结和交付证据主场景一致
- 可以分层、渐进、局部落地

缺点：

- 需要重构 memory 写回和召回路径
- 需要正式冻结 truth/evidence/cache 的边界

### 3.3 方案 C：full brain platform

优点：

- 能力上限高

缺点：

- 过重
- 超出 `v1.3.6`
- 会拉偏 Beacon 的产品语义

### 3.4 选择

本 PRD 选择 **方案 B**。

原则：

> Beacon 要补的是 memory foundation，不是另起一个 brain product。

## 4. 设计原则

### 4.1 Verbatim first，projection second

Beacon 必须先保存原始证据，再生成摘要、索引、graph、context pack。

不能反过来只保留总结。

### 4.2 Workflow-native，而不是 generic brain

所有 memory 结构都必须服务 Beacon 的主工作流，而不是为抽象知识管理而设计。

### 4.3 Truth / Evidence / Index / Cache 分层

Beacon 记忆基座至少需要区分四层：

1. `truth`
   - `docs/beacon/<version>/`
   - 版本化 requirement / QA / release 正式材料
2. `evidence`
   - `.beacon/memory/evidence/`
   - 原始摘录、问题样本、artifact 引用、阶段证据
3. `index / projection`
   - `memory-v1.json`
   - artifact graph
   - recall ranking index
4. `cache / state`
   - stage context pack
   - runtime summarization
   - 允许重建的临时状态

### 4.4 Local-first，deterministic-first

默认优先使用本地 JSON 与确定性索引。

没有足够理由，不引入远程依赖和重型数据库。

### 4.5 Memory can assist, but cannot override truth

memory 可以帮助：

- 解释
- 追溯
- 拼接上下文
- 提示风险

但不能反向覆盖：

- 冻结 PRD
- 冻结 user-story
- 冻结 test-case
- 冻结 release evidence

### 4.6 Recalled context must explain itself

每次 recall 默认都必须能回答：

- 命中了哪条 evidence
- 来自哪个 artifact / run / stage
- 为什么被排在前面

## 5. 范围

### In scope

- 原始证据层
- memory 索引层重构
- artifact graph
- recall 召回增强
- stage context pack
- memory-friction-evolution 写回增强
- recurrence / suppression / freshness 治理
- 与 `implement / qa / release / status / doctor` 的上下文接力

### Out of scope

- 通用 personal brain
- 复杂联系人、公司、日程图谱
- 默认 embedding/向量数据库依赖
- 全 transcript 正式化
- 新的公开一级工作流

## 6. 功能需求

### FR-001 Beacon 必须新增正式的 evidence layer

系统必须在 `.beacon/memory/evidence/` 下新增原始证据层，至少支持以下信息：

- `evidence_id`
- `feature`
- `version`
- `stage`
- `run_id`
- `artifact_ref`
- `source_ref`
- `content_excerpt`
- `content_hash`
- `captured_at`
- `reason_codes`
- `tags`

要求：

- 原始证据可独立存在
- 摘要和 recall 命中结果都必须能回链 evidence

### FR-002 `memory-v1.json` 必须降级为 index / summary plane

`memory-v1.json` 继续保留，负责：

- typed memory index
- summary projection
- recall entry surface
- 兼容旧接口

它不再承担原始真相的唯一承载职责。

### FR-003 Beacon 必须支持 artifact-level memory linking

系统必须支持将以下 artifact 建立稳定关联：

- PRD
- User Story
- Test Case
- Prototype
- Research
- Implementation Summary
- Debug Issue
- QA Artifact
- Release Artifact

关联至少支持：

- `supports`
- `derived_from`
- `contradicts`
- `implements`
- `verifies`
- `blocked_by`
- `supersedes`

### FR-004 Recall 必须支持 stage-aware / artifact-aware / evidence-aware 检索

`beacon recall` 必须能够按以下维度切片与召回：

- `type`
- `stage`
- `feature`
- `version`
- `run_id`
- `artifact_ref`
- `tags`
- `reason_codes`

默认结果必须包含：

- memory 摘要
- evidence refs
- artifact refs
- source session / run / stage

### FR-005 Recall ranking 必须从纯词项匹配升级到混合排序

Beacon 必须至少支持以下混合排序信号：

- keyword match
- tag / reason code overlap
- stage proximity
- artifact backlink
- recency
- evidence density

`v1.3.6` 不强制引入 embedding，但排序不能再只依赖简单词项重叠。

### FR-006 Beacon 必须生成 stage context packs

系统必须能够按 `run_id + stage` 生成与读取 context pack，用于：

- 接力下一阶段
- 让人类快速理解当前上下文
- 为 agent 注入最小必要上下文

context pack 至少需要包含：

- 当前阶段摘要
- 上游 artifact refs
- 当前关键 evidence refs
- 当前 blocker / decision / open risk
- 建议下一步

### FR-007 `memory-friction-evolution` 必须优先写 evidence-backed memory

当系统从 debug / friction / recurrence 中形成记忆候选时，必须优先：

1. 写 evidence
2. 再写 summary memory
3. 最后可选写 feedback projection

不允许只写一句压缩 feedback 就结束。

### FR-008 Beacon 必须支持 recurrence / suppression / freshness 治理

系统必须能够：

- 标记重复出现的问题
- 抑制已经过度处理的重复信号
- 判断某条 evidence 是否 stale
- 区分 `advisory` 与 `truth-supporting`

这层治理必须优先用于：

- debug recurrence
- QA 回归问题
- release blocker 复发

### FR-009 Human-facing memory output 必须默认降噪

默认输出必须先回答：

- 当前为什么走到这里
- 当前最相关的证据是什么
- 当前推荐下一步是什么

而不是默认展开全部内部 memory 细节。

### FR-010 Beacon 公开命令面不得扩张

本版本可以增强：

- `remember`
- `recall`
- `status`
- `doctor`
- `implement / qa / release` 的隐式 context 注入

但不得新增新的公开一级主命令来承载记忆基座。

### FR-011 系统必须兼容现有 memory 与 lifecycle 数据

新记忆基座落地后，必须兼容：

- 现有 `memory-v1.json`
- 现有 legacy projections
- 现有 `workflow-lifecycle.json`
- 现有 `memory-friction-evolution` artifacts

不能要求用户重建项目。

### FR-012 Memory 必须为 release closure 服务

当 Beacon 进入 `qa / release` 阶段时，系统必须能基于 memory foundation 回答：

- 当前 release 结论依赖哪些 requirement truth
- 当前 release blocker 是否是旧问题复发
- 当前 evidence 是否新鲜且与当前 revision 对齐

## 7. 关键场景

### 7.1 场景 A：需求冻结后的实现接力

当实现阶段开始时，Beacon 必须能自动整理：

- 冻结 PRD 关键点
- 对应 user-story / test-case
- 当前 feature 的 research 证据
- 历史实现偏差或旧问题提醒

### 7.2 场景 B：QA 排查为什么又失败

当 QA 失败时，Beacon 必须能快速回答：

- 这是否是旧问题复发
- 相关的旧 debug issue 有哪些
- 哪些 evidence 说明当前改动可能偏离了冻结需求

### 7.3 场景 C：Release 需要收敛证据

当进入 release 阶段时，Beacon 必须能把 requirement、implementation、QA、debug 证据重新投影为 release closure 所需最小证据集合。

### 7.4 场景 D：人类接手项目

新接手者必须能通过一份 stage context pack 和有限 recall 结果，理解：

- 项目在做什么
- 当前为什么卡住
- 接下来该做什么

## 8. 数据与结构建议

### 8.1 最小 evidence envelope

建议最小结构：

```json
{
  "schema_version": "1.0",
  "evidence_id": "ev_...",
  "feature": "beacon-v1.3.6-memory-foundation-and-full-scene-evidence-recall",
  "version": "v1.3.6",
  "stage": "prd",
  "run_id": "run-...",
  "artifact_ref": "docs/beacon/v1.3.6/prd/....md",
  "source_ref": ".beacon/debug/issues/....json",
  "content_excerpt": "....",
  "content_hash": "sha256:....",
  "reason_codes": ["requirement-drift"],
  "tags": ["memory", "freeze"],
  "captured_at": "2026-04-21T00:00:00Z"
}
```

### 8.2 最小 graph projection

建议先使用 deterministic JSON 邻接表，而不是直接上数据库。

### 8.3 Context pack 必须可重建

context pack 可以缓存，但必须能从：

- evidence
- memory index
- workflow lifecycle

重新构建。

## 9. 分阶段落地

### P0：补 evidence layer 与 context pack

交付目标：

- `.beacon/memory/evidence/`
- `memory-v1.json` 指向 evidence
- recall 返回 evidence refs
- stage context pack 强化

### P1：补 artifact graph 与 recall ranking

交付目标：

- artifact graph
- backlink / stage-aware / recency-aware recall
- recurrence / suppression 规则

### P2：补后台维护任务与更强治理

交付目标：

- 可选 deterministic background jobs
- 更成熟的 recurrence/failure ratio/empty-cycle 治理
- 只有必要时再评估 SQLite

## 10. 验收方向

### AC-001 原始证据不再丢失

同一条 memory 或 friction 候选，必须能够回链到原始 evidence，而不是只剩一句 summary。

### AC-002 recall 结果必须可解释

任意 recall 命中结果，必须能说明命中来源、artifact 关系和排序原因。

### AC-003 跨阶段接力必须变短

在 `implement / qa / release` 阶段，系统必须能生成最小 stage context pack，减少人工重读成本。

### AC-004 旧问题复发必须更容易识别

QA/debug/release 阶段必须能借助记忆基座更稳定地识别 recurrence。

### AC-005 Beacon 边界不得漂移

本功能上线后，Beacon 仍然必须保持：

- `docs/beacon/<version>/` 为正式 truth
- 公开主命令面不扩张
- memory 不劫持 requirement/release 真相

## 11. 成功标准

1. Beacon 在冻结到交付阶段具备更强的上下文接力能力。
2. recall 从“能搜到一些摘要”升级到“能解释命中的证据化召回”。
3. `memory-friction-evolution` 的写回不再损失关键证据。
4. 人类与 agent 在复杂项目上的接力成本明显下降。
5. Beacon 仍然保持 workflow-native 边界，没有滑向通用 brain product。
