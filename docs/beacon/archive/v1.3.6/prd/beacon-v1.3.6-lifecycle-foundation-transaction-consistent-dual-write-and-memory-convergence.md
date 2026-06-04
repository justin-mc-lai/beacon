# PRD：Beacon v1.3.6 生命周期基座、事务一致双写与记忆体基座收敛

**Feature**: `beacon-v1.3.6-lifecycle-foundation-transaction-consistent-dual-write-and-memory-convergence`  
**Version**: `v1.3.6`  
**Date**: `2026-04-22`  
**Status**: `planning line`  
**Track**: `parallel`  
**Scenario**: `lifecycle-foundation + memory-foundation-convergence + transactional-consistency`  
**Template**: `并行 PRD / foundation-refactor`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/archive/v1.3.6/SUMMARY.md`
- Execution index: `docs/beacon/archive/v1.3.6/execution/index.md`
- Architecture blueprint: `docs/beacon/archive/v1.3.6/execution/architecture-blueprint.md`
- Existing memory foundation anchor:
  - `docs/beacon/archive/v1.3.6/prd/beacon-v1-3-6-memory-foundation-and-full-scene-evidence-recall.md`
- Current lifecycle/runtime anchors:
  - `beacon/cli_factory.py`
  - `beacon/command_catalog.py`
  - `beacon/commands/workflow.py`
  - `beacon/utils/workflow_memory.py`
  - `beacon/utils/help_support.py`
  - `beacon/commands/status.py`

## 1. 问题

本并行 PRD 要解决的不是单一命令缺陷，而是 Beacon 当前“规范、状态机、记忆体、读模型、LLM 接力”没有收口到同一套 foundation。

### 1.1 上层规范已经升级，但底层状态机仍停留在旧模型

当前 Beacon 已经明确宣布：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
```

同时把：

- `help`
- `status`
- `doctor`

定义为唯一辅助面。

但当前底层 workflow/memory 仍明显保留旧链路：

```text
think
→ user-story
→ prd
→ [prototype]
→ test-case
→ implementation
→ verify
→ gate
```

这意味着：

1. 文档声明与真实生命周期状态机不一致。
2. `next_stage`、closure、blocking reasons 仍会输出旧词汇。
3. `help/status/doctor` 虽然越来越像 lifecycle manager，但其判定基础仍部分依赖旧 vocabulary。

### 1.2 记忆体基座已经存在，但尚未成为生命周期的一部分

Beacon 已有：

- `memory-v1.json`
- `workflow-lifecycle.json`
- `memory-friction-evolution`
- recall / writeback / debug evidence

这些能力说明 Beacon 并非没有 memory foundation。

真正的问题是：

1. lifecycle state 与 evidence memory 仍是并列子系统，不是统一 foundation。
2. stage context pack 还没有由 canonical lifecycle transaction 驱动。
3. memory 还偏向“沉淀结论”，没有完全进入“事务提交和跨面一致性审计”主路径。

### 1.3 人类面与机器面尚未完成正式分层

Beacon 产品边界已经很清楚：

- 人类只应该看最少必要信息
- 机器内部可以保留 team / subagent / projection / recall / transaction 复杂度

但当前仍有三个断层：

1. CLI 对外命令面仍比 `7+3` 更宽，旧面和内部面仍混在一起。
2. 部分 support/read-model 仍暴露 `verify / gate / implementation` 等旧中间语义。
3. 机器内部并未形成“canonical envelope -> 多面单向投影 -> 事务一致提交”的统一写法。

### 1.4 缺少统一的 canonical transaction foundation

`global-boundaries` 已经明确：

- canonical envelope 是唯一提交源
- 必须走 `prepare -> validate -> commit -> publish -> verify`
- human/machine/runtime 多写入点必须强一致

但当前 Beacon 还没有把这件事升级为全生命周期基座。

结果是：

1. `prototype / implement / qa / release` 之间虽然有 requirement binding，但不一定共享同一事务元数据。
2. memory writeback、runtime projection、human docs 之间仍可能出现“局部先写、局部补修”的漂移。
3. LLM 接力可以读上下文，但还没有被强制绑定到统一的 stage transaction contract。

### 1.5 当前缺的不是“再补一个功能”，而是 foundation convergence

Beacon 下一阶段需要的不是继续在旧 foundation 上堆特性，而是收口以下基础设施：

```text
global boundaries
→ versioned requirement materials
→ canonical lifecycle state machine
→ evidence-native memory foundation
→ human/machine/runtime transactional projection
→ help/status/doctor unified read model
```

如果不先做这一层，后续：

- semantic layer
- prototype bridge
- implement lane
- qa/release gate
- management console

都会继续被旧状态机和多源写入漂移拖住。

## 2. 目标

### 2.1 主要目标

在 `v1.3.6` 内，为 Beacon 补齐一套正式的 foundation convergence：

```text
requirement truth
→ canonical lifecycle foundation
→ evidence-native memory foundation
→ canonical transaction envelope
→ human/machine/runtime projections
→ unified support/read model
```

### 2.2 明确结果

本线完成后，Beacon 应满足：

1. 生命周期状态机正式统一到 `prd / user-story / test-case / prototype / implement / qa / release + help/status/doctor`。
2. 旧 `think / implementation / verify / gate` 只作为 legacy alias 或内部迁移语义存在，不再作为 canonical truth。
3. 记忆体基座不再只是 recall 辅助，而是成为生命周期事务、证据召回、阶段接力、反漂移审计的一部分。
4. 所有 human/machine/runtime 写入都由同一 canonical envelope 单向投影生成，并共享事务元数据。
5. LLM 的规划、执行、接力必须绑定 stage context pack 和 transaction contract，而不是裸 prompt 游离运行。
6. 人类默认只看到主链、阻断、下一步、审计结果；机器内部保留细粒度协作和复杂交互。

### 2.3 非目标

本 PRD 不承担：

- 不新增新的公开一级主命令
- 不把 machine transcript 升格为正式 truth
- 不要求用户理解 team/subagent/runtime projection 细节
- 不以 runtime state 取代 `docs/beacon/<version>/` 的正式地位
- 不强依赖远程数据库或重型 infra

## 3. 设计原则

### 3.1 人类极简，机器自由，但提交必须同源

对人类只保留：

- 当前所处 canonical stage
- 阻断原因
- 下一步
- release / drift / consistency 结论

对机器允许：

- 多 agent 协同
- 多 projection sink
- recall / ranking / graph / cache
- runtime orchestration

但所有提交必须共享同一 canonical envelope。

### 3.2 Requirement truth 不能被 runtime 和 memory 反向篡改

正式真相仍然是：

- `docs/beacon/global-boundaries.md`
- `docs/beacon/<version>/`
- 冻结后的 requirement / qa / release materials

memory 可以：

- 解释
- 追溯
- 拼接上下文
- 辅助判断

不能：

- 覆盖 requirement truth
- 代替 release verdict
- 用 runtime state 单独定义“完成”

### 3.3 生命周期状态机必须 canonical first

Beacon 真实状态机必须收口为：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
```

并把：

- `help`
- `status`
- `doctor`

作为 read-model / diagnosis / recovery surfaces。

### 3.4 一切多面写入都必须走事务提交

所有关键提交必须遵循：

```text
prepare
→ validate
→ commit
→ publish
→ verify
```

任一 sink 失败时：

- 要么整体回滚
- 要么保留失败事务并阻断 freeze / qa / release

### 3.5 记忆体基座必须 evidence-first，而不是 summary-first

memory foundation 必须先保留：

- raw evidence
- artifact linkage
- stage/run binding
- transaction metadata

再生成：

- summary
- graph
- ranking
- stage context pack

### 3.6 读模型必须只解释 canonical truth

`help/status/doctor` 的作用是：

- 解释当前状态
- 指出阻断
- 给出下一步
- 检查一致性

而不是再定义一套与 canonical lifecycle 并行的伪状态机。

## 4. 目标架构

### 4.1 Foundation layers

Beacon foundation 收口为五层：

1. `truth layer`
   - `docs/beacon/global-boundaries.md`
   - `docs/beacon/<version>/`
   - frozen requirement / qa / release materials
2. `lifecycle foundation`
   - canonical stages
   - stage transitions
   - closure rules
   - blocker model
3. `memory foundation`
   - evidence store
   - artifact graph
   - recall index
   - stage context pack
4. `transaction foundation`
   - canonical envelope
   - commit journal
   - sink projection receipts
   - anti-drift verification
5. `read model`
   - help/status/doctor
   - qa scorecard
   - release scorecard
   - management console projections

### 4.2 Canonical lifecycle state machine

统一后的 state machine 至少包含：

- `prd`
- `user-story`
- `test-case`
- `prototype`
- `implement`
- `qa`
- `release`

legacy aliases 映射规则：

- `think` → 不再是 canonical stage；仅作为 greenfield planning helper
- `implementation` → `implement`
- `verify` → `qa`
- `gate` / `review` / `delivery` → `release`

### 4.3 Canonical transaction envelope

每次正式写入至少包含：

- `transaction_id`
- `source_hash`
- `projection_seq`
- `feature`
- `version`
- `stage`
- `source_artifacts`
- `evidence_refs`
- `sink_checksums`
- `committed_at`
- `commit_status`

所有 sink 必须由这个 envelope 单向投影生成。

### 4.4 Memory-lifecycle convergence

memory foundation 与 lifecycle foundation 的连接点包括：

1. 每个 canonical stage 进入前生成 stage context pack。
2. 每次 stage 完成后写入 structured evidence receipt。
3. 每次 transaction publish 后刷新 recall index 和 artifact graph。
4. `help/status/doctor/qa/release` 读取同一份 transaction-backed memory summary。

### 4.5 Human/machine/runtime projections

投影面至少分为：

1. `human-readable`
   - Markdown docs
   - human execution notes
   - compact status explanation
2. `machine-readable`
   - JSON contracts
   - transaction journals
   - evidence receipts
3. `runtime/read-model`
   - sqlite / projections
   - console summary
   - query indexes

规则：

- human 面不能反向改写 machine 真相
- machine 面不能脱离 requirement truth 自行升级为正式结论
- runtime 面不能绕过 transaction verification 直接被判定为最终 truth

## 5. Functional Requirements

### FR-001 生命周期 canonical 化

Beacon 必须把生命周期 canonical stages 统一为：

```text
prd -> user-story -> test-case -> prototype -> implement -> qa -> release
```

并让 workflow progress、next_stage、closure、blocking reasons 全量使用该词汇。

### FR-002 legacy vocabulary 兼容迁移

系统必须兼容旧状态与旧 profile 中的：

- `think`
- `implementation`
- `verify`
- `review`
- `gate`
- `delivery`

但对外解释和新写入必须映射为 canonical vocabulary。

### FR-003 lifecycle memory 收口

`workflow-lifecycle`、typed memory、memory-friction-evolution、recall evidence 必须被重组到同一 memory foundation contract，而不是各自独立沉淀。

### FR-004 stage context pack 正式化

每个 canonical stage 都必须具备 machine-first 的 stage context pack，至少包含：

- requirement refs
- latest evidence refs
- blockers
- open questions
- decision trace
- transaction lineage

人类默认只看到其摘要和下一步。

### FR-005 canonical envelope 单源提交

Beacon 的 requirement/material/memory/runtime 关键写入必须统一走 canonical envelope，禁止多源并写。

### FR-006 事务一致双写

human/machine/runtime 三类 sink 必须在同一 transaction 中完成：

- human docs / summaries
- machine contracts / journals
- runtime projections / indexes

任一失败时必须阻断闭环，不允许静默漂移。

### FR-007 anti-drift 审计

`status / doctor / qa / release` 必须能够检查并报告：

- lifecycle vocabulary drift
- human/machine mismatch
- memory/projection mismatch
- stale context pack
- sink checksum mismatch

### FR-008 LLM lifecycle binding

LLM 参与的规划、执行、修复、接力必须绑定：

- canonical stage
- stage context pack
- required source refs
- transaction lineage

禁止裸 prompt 直接改写正式 materials。

### FR-009 support/read-model convergence

`help/status/doctor` 必须共享统一 read model，并只解释 canonical lifecycle 和 transaction-backed truth。

### FR-010 release-grade consistency gate

`qa / release` 必须将以下内容升级为正式 gate：

- requirement traceability
- lifecycle closure
- memory evidence completeness
- sink consistency
- transaction verification

## 6. 范围

### In scope

- 生命周期 canonical stage 收口
- workflow / workflow_memory / help_support / status 词汇统一
- transaction envelope 与 sink receipt
- memory foundation 与 lifecycle foundation 的连接
- stage context pack 正式化
- anti-drift 审计与 release gate 扩展
- 对人类面的最小化解释策略

### Out of scope

- 替换整个 management console 产品线
- 新增独立 memory SaaS 或知识平台
- 对外暴露 team/subagent 新主命令
- 一次性清洗所有历史版本包

## 7. 迁移计划

### Phase 0: 规范冻结

- 冻结 canonical lifecycle vocabulary
- 冻结 legacy alias mapping
- 冻结 transaction envelope 字段
- 冻结 memory-lifecycle convergence boundary

### Phase 1: 状态机收口

- 改造 `workflow.py`
- 改造 `workflow_memory.py`
- 改造 progress/closure/next_stage 输出
- 把旧状态统一映射到 canonical stages

### Phase 2: 支持面收口

- 改造 `help_support.py`
- 改造 `status.py`
- 改造 `doctor` 相关 consistency checks
- 把 support/read-model 收口到 canonical lifecycle 和 transaction truth

### Phase 3: 事务一致双写

- 引入 canonical transaction journal
- 引入 sink receipts / checksums
- human/machine/runtime 三面统一提交
- 失败回滚或失败阻断

### Phase 4: 记忆体基座融合

- typed memory 与 lifecycle event 建立统一 lineage
- recall index 接入 transaction/evidence receipts
- stage context pack 从 memory foundation 自动编译
- friction/evolution 写回保留 raw evidence linkage

### Phase 5: QA / release gate 升级

- 引入 lifecycle drift checks
- 引入 transaction consistency checks
- 引入 stage context freshness checks
- release scorecard 纳入 foundation verdict

## 8. 验收标准

- `AC-001` lifecycle canonical stages 对外统一为 `prd / user-story / test-case / prototype / implement / qa / release`
- `AC-002` 旧 `implementation / verify / gate / review / delivery` 配置和历史状态可被兼容映射
- `AC-003` workflow progress、next_stage、blocking reason、help/status 输出不再使用旧 canonical 词汇
- `AC-004` 每次正式 lifecycle 写入都生成 canonical transaction envelope 和 sink receipts
- `AC-005` human/machine/runtime 三类 sink 任一失败时系统阻断并留下失败事务，不允许静默通过
- `AC-006` memory foundation 至少能为每个 canonical stage 生成 stage context pack，并保留 raw evidence linkage
- `AC-007` `help / status / doctor / qa / release` 能检查跨面一致性和 anti-drift 结果
- `AC-008` 人类默认界面只暴露最少必要 lifecycle 信息，机器内部复杂度不进入主流程心智面

## 9. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 旧状态机依赖太深，迁移时引发回归 | 高 | 先冻结 alias mapping，再逐层替换 next_stage / closure 输出 |
| memory 与 lifecycle 过早强耦合导致实现过重 | 中 | 先打通 transaction lineage，再逐步扩大 recall 与 graph 范围 |
| 多 sink 强一致实现复杂 | 高 | 先以 journal + receipt + checksum 落地，避免直接引入重 infra |
| 人类面再次膨胀 | 中 | 继续把 machine-only 结构限制在 `.beacon` 与 read model 内部 |

## 10. 与记忆体主 PRD 的关系

- 主锚点仍是 `beacon-v1-3-6-memory-foundation-and-full-scene-evidence-recall`
- 本并行 PRD 不替代记忆体主 PRD，而是补齐它缺失的 lifecycle foundation 与 transaction foundation
- 最终目标不是“双基座分裂”，而是形成：

```text
生命周期基座
+ 记忆体基座
+ LLM stage planning
+ 人机事务一致双写
= Beacon foundation convergence
```

## 11. Release Guard

- 仅当 canonical lifecycle、transaction consistency、memory evidence completeness 三项同时通过时，方可进入 release readiness 结论。
