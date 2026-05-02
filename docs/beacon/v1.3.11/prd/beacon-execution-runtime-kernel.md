# PRD：beacon-execution-runtime-kernel

**Feature**: `beacon-execution-runtime-kernel`  
**Version**: `v1.3.11`  
**Date**: `2026-05-01`  
**Status**: `draft`  
**Track**: `parallel`  
**Scenario**: `runtime_control_plane`  
**Semantic Label**: `运行态投影治理`  

target_audience: Beacon operator、交付负责人、运行态宿主维护者
primary_use_cases: 判断 feature 实现顺序, 管理运行队列, 处理恢复路径, 校验宿主与工作区一致性
operator_mental_state: 需要先判断当前运行态、阻塞原因与下一步动作，再决定是否继续、停止、重试或回修
usage_environment: 桌面优先的本地执行控制台、版本交付审阅与恢复处理环境
brand_tone: formal, restrained, precise, operational
density_preference: workbench-medium
design_preset: apple-inspired-design-md

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/v1.3.11/SUMMARY.md`
- Execution index: `docs/beacon/v1.3.11/execution/index.md`
- Main runtime anchor PRD:
  - `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- Existing freeze safety PRD:
  - `docs/beacon/v1.3.11/prd/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- External reference mirrors:
  - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/symphony`
  - `/Users/apple/Developer/Personal/oss-sync/agents/agent-systems/vibe-kanban`

## 1. 问题

### 1.1 当前断层

Beacon 已经能稳定冻结 requirement truth，但长任务执行层仍然分散在 `implement / qa / release / team / ralph / real-project-validation` 等 surface 内部。

当前缺口集中在四点：

- 缺少统一的 `work item -> run -> workspace -> evidence` 运行模型
- 缺少 authoritative runtime state，导致并发、恢复、重试仍依赖人工心智
- 缺少 feature 级自动实现顺序分析，多个 feature 容易共享版本容器但缺少稳定编排
- 缺少稳定的恢复面，run 中断、workspace 漂移、状态残留后不能确定性回收

### 1.2 触发信号

- `v1.3.11` 已经证明 requirement freeze anti-drift 必须 fail-closed，执行层如果仍是松散脚本，会重新把漂移引回实现面
- 当前 `implementation-delivery-host` 已开始承载同版本多 feature baseline，但还没有升级为真正的 runtime host
- 真实项目验证已经要求 Beacon 能从 requirement truth 走到长任务运行与恢复，而不是停留在单轮命令
- `symphony` 证明 runtime kernel 必须独立建模，`vibe-kanban` 证明执行工作台必须建立在稳定 runtime 之上

### 1.3 为什么现在做

如果不先收敛 kernel，再做 operator board，只会把现有离散状态做成更华丽的展示层，无法真正承担长任务执行能力。

## 2. 目标

### 2.1 主要目标

- 为 Beacon 新增统一的 execution runtime kernel
- 把 run-oriented 能力从具体命令面中抽离为共享宿主
- 让同版本多个 feature 可以稳定共存、共享版本级 baseline host、并自动分析实现顺序
- 为后续 `beacon board` / desktop launcher 提供稳定状态读模型和操作 contract

### 2.2 非目标

- 不新增新的公开主生命周期 stage
- 不让 runtime kernel 反向改写 `prd / user-story / test-case / prototype`
- 不在本 feature 内直接实现完整桌面 UI
- 不在本 feature 内绑定某个第三方 issue tracker 为唯一入口
- 不把 Beacon 变成通用 CI/CD 编排器或分布式 job system

## 3. 设计原则

### 3.1 Truth First, Runtime Second

- requirement truth 仍是唯一 scope 来源
- runtime kernel 只能消费冻结 requirement package 和 change loop 结果
- 若发现 scope 不完整，必须阻断并回路由到 `beacon-change` 或 requirement chain

### 3.2 Single Authoritative Runtime State

- scheduler、retry、workspace、run status、operator action 必须依赖同一权威运行态
- 不允许每个 surface 各写一套“自己的当前状态”

### 3.3 Workspace Isolation Before Parallelism

- 并发能力建立在 run 级隔离之上
- 每个 run 至少有清晰的 `workspace boundary / evidence boundary / recovery boundary / writable scope`

### 3.4 Host-Driven Ordering

- 同版本多 feature 的实现顺序不能再依赖人工猜测
- 必须以版本级 baseline host 为宿主，统一分析 `depends_on_features / writable_services / direct delivery services / branch target`

### 3.5 Recovery Is a First-Class Capability

- stop、retry、continue、repair、reconcile 不是附属逻辑，而是 kernel 的正式 contract

### 3.6 Fail-Closed Before Surface Convenience

- 任一 surface 只要依赖 runtime state，就必须先服从 admission、ordering、workspace、evidence 的 fail-closed 约束
- 不允许为了 UI 连续性或单轮命令便利而绕过 host 校验

## 4. 范围

### In scope

- runtime kernel 领域模型
- version-level baseline host 与 host-driven implementation ordering
- work item admission / run scheduling / retry / recovery / reconcile
- workspace lifecycle 与 evidence binding
- operator-facing runtime read model
- 为后续 workbench 暴露启动、继续、停止、重试等稳定 contract

### Out of scope

- 复杂视觉设计、跨端 desktop 包装、marketing 式控制台页面
- 第三方团队协作、租户隔离、云端多租户治理
- 直接替换 Beacon 现有 requirement lifecycle

## 5. 功能需求

### FR-001 Runtime Domain Model

Beacon 必须正式建模以下运行实体，并统一挂到 `v1.3.11` 版本材料与 machine mirrors：

- `WorkItem`
- `Run`
- `Workspace`
- `AgentSession`
- `RetryEntry`
- `ExecutionHost`
- `OperatorAction`

每个实体至少具备：

- `version`
- `feature_slug`
- `revision_id`
- `status`
- `transaction/source hash`
- `evidence refs`

### FR-002 Version-Level Baseline Host

Beacon 必须把现有 `implementation-delivery-host` 升级为稳定宿主，至少承担：

- 注册当前版本全部 feature baseline
- 记录 `feature_slug / revision_id / baseline_ref / writable_services / depends_on_features / target_branch`
- 提供当前版本的 `ordered_feature_slugs / waves / reason_codes`
- 阻断同版本 feature 因共享单一容器而相互覆盖 baseline

### FR-003 Host-Driven Implementation Ordering

Beacon 必须能根据以下输入自动分析实现顺序：

- feature 依赖关系
- writable service 冲突
- direct delivery service overlap
- branch/worktree target
- blocked feature state

输出至少包含：

- `ordered_feature_slugs`
- `waves`
- `depends_on_features`
- `conflict_reason_codes`
- `manual_intervention_required`

### FR-004 Run Scheduler And Recovery Contract

Kernel 必须提供统一的 run 调度与恢复语义：

- `queued`
- `admitted`
- `running`
- `blocked`
- `needs_review`
- `retry_scheduled`
- `stopped`
- `completed`
- `failed`

并支持至少以下动作：

- `start`
- `continue`
- `stop`
- `retry`
- `reconcile`
- `repair-handoff`

### FR-005 Workspace And Evidence Isolation

每个 run 必须有可确定性定位的：

- workspace root
- writable service scope
- baseline binding
- evidence output root
- recovery metadata

若 workspace 与 baseline host、feature host 或 service scope 不一致，kernel 必须 fail-closed。

### FR-006 Runtime Read Model

Kernel 必须产出供 operator workbench 消费的正式 read model，至少包含：

- active runs
- blocked runs
- retry queue
- feature ordering
- baseline host state
- recovery alerts
- latest operator-relevant events

该 read model 必须是 board 的唯一运行态来源之一，不允许 UI 自己推导隐式真相。

### FR-007 Runtime Admission And Drift Reason Codes

Kernel 必须为以下阻断或恢复场景提供稳定的 `reason_code / diagnosis / repair_path`：

- baseline host stale
- ordering stale
- workspace drift
- writable scope conflict
- blocked dependency
- retry orphan
- evidence sink missing

每个 reason code 必须能被 `status / board / release / qa / implement` 共用，禁止不同 surface 各自产生一套错误语义。

### FR-008 Cross-Surface Runtime Contract

以下 surface 必须共享同一 runtime host contract，而不是各自维护分散状态：

- `implement`
- `qa`
- `release`
- `team`
- `ralph`
- `real-project-validation`
- `board`

共享 contract 至少统一：

- run status enum
- ordered feature waves
- admission gate result
- workspace binding
- evidence sink state
- repair path metadata

## 6. 边界 / 分层 / 恢复策略

### 6.1 边界

- requirement documents 定义 scope，不定义 runtime side effect
- runtime kernel 负责调度与状态，不负责修改 requirement truth
- workbench 负责观察与操作，不负责自己维护真相

### 6.2 分层

推荐固定为四层：

1. Requirement Truth Layer
2. Runtime Kernel Layer
3. Operator Read Model Layer
4. Delivery Closure Layer

其中：

- Layer 1 冻结承诺
- Layer 2 调度执行
- Layer 3 面向 board/CLI/desktop 暴露可消费状态
- Layer 4 承担 implement/qa/release 的正式放行

### 6.3 恢复策略

针对以下失败类型必须有确定性恢复路径：

- run interrupted
- workspace drifted
- stale baseline host
- ordering projection stale
- evidence sink missing
- retry queue orphaned

恢复顺序必须优先：

1. 校验 frozen truth
2. 校验 baseline host
3. reconcile machine/runtime projection
4. 再允许 continue 或 retry

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 只把旧命令状态包装成新名词，没有真正 kernel | 高 | 强制 domain model、host、ordering、run state、recovery contract 全部落到 machine mirrors |
| 多 feature 仍共享单一版本容器并互相覆盖 | 高 | version-level baseline host 成为唯一宿主，并增加 feature-aware projection 校验 |
| runtime kernel 反向侵入 requirement truth | 高 | gate 层 fail-closed，scope drift 一律回 `beacon-change` |
| workspace 与 evidence 隔离不完整 | 中 | run admission 前校验 workspace root、writable scope、baseline binding |
| 后续 board 直接绕过 kernel 自己拼状态 | 中 | read model contract 固定，UI 仅消费 contract |

## 8. 验收标准

## 9. Diagram Truth Layer

### 9.1 Diagram Types

- `branch-flow`
- `state-machine`
- `decision-priority`

### 9.2 Branch Flow

1. `frozen truth ready -> baseline host registered -> ordering projected -> run admitted -> workspace bound -> execution starts`
2. `frozen truth missing or stale -> admission blocked -> route to beacon-change / doctor / reconcile`
3. `workspace drift or evidence sink missing -> recovery diagnostics raised -> reconcile before continue/retry`
4. `dependency conflict or writable scope conflict -> ordering blocked -> manual intervention required`
5. `run failed but recovery path valid -> retry scheduled or repair-handoff issued -> operator resumes after reconcile`

### 9.3 State Machine

- `queued -> admitted -> running -> completed`
- `queued -> blocked`
- `admitted -> blocked`
- `running -> needs_review`
- `running -> retry_scheduled`
- `running -> stopped`
- `running -> failed`
- `blocked -> queued` after reconcile succeeds
- `retry_scheduled -> queued`
- `needs_review -> completed`
- `needs_review -> retry_scheduled`
- `stopped -> queued` via explicit continue
- `failed -> retry_scheduled`

Illegal transitions that must stay blocked:

- `failed -> running`
- `blocked -> running`
- `queued -> completed`
- `stopped -> completed`

### 9.4 Decision Priority

当多个条件同时出现时，kernel 必须按以下优先级决策：

1. `frozen truth / baseline hash / requirement package` 不一致优先阻断
2. `baseline host stale / ordering stale` 次级阻断
3. `workspace binding / writable scope / evidence sink` 校验失败阻断 continue/retry
4. `dependency conflict / branch conflict` 阻断 admission 与 wave 排序
5. 只有在以上都通过后，才允许 `start / continue / retry / repair-handoff`

### 9.5 State Axes

- `feature_host_axis`
- `baseline_host_registered`
- `baseline_host_stale`
- `ordering_axis`
- `ordered`
- `conflicted`
- `manual_intervention_required`
- `run_status_axis`
- `queued`
- `admitted`
- `running`
- `blocked`
- `needs_review`
- `retry_scheduled`
- `stopped`
- `completed`
- `failed`
- `workspace_axis`
- `workspace_bound`
- `workspace_drifted`
- `evidence_axis`
- `evidence_ready`
- `evidence_sink_missing`
- `recovery_axis`
- `reconcile_required`
- `retry_path_explicit`
- `repair_handoff_explicit`
- `truth_boundary_axis`
- `truth_read_only`
- `runtime_contract_only`
- `release_gate_preserved`

### 9.6 Propagation Contract

- Diagram truth must propagate into freeze readiness, implementation ordering, scheduler transitions, recovery diagnostics, and QA coverage.
- State axes must remain explicit in runtime host, read model, and operator actions; they cannot be collapsed into one opaque status string.

---

**Created**: 2026-05-01  
**Version**: v1.3.11  
**Status**: draft  
**Memory Context**: Beacon orchestration runtime kernel and operator workbench evolution

### AC-001 Runtime Domain Model Frozen

- `WorkItem / Run / Workspace / RetryEntry / ExecutionHost / OperatorAction` 均有正式 machine projection

### AC-002 Multi-Feature Baseline Host Stable

- 同版本多个 feature 共存时，不会因 shared blueprint container 覆盖彼此 baseline

### AC-003 Ordering Analysis Available

- Beacon 能输出 feature 实现顺序、wave 分组、冲突理由，并可被 release / board / status 消费

### AC-004 Recovery Path Fail-Closed

- baseline host、workspace、ordering、evidence 任一关键状态漂移时，continue/retry 会被阻断并给出 repair path

### AC-005 Shared Runtime Contract

- `implement / qa / release / team / ralph / real-project-validation` 至少能共享同一套 runtime host contract，而不是继续维护完全独立状态

### AC-006 Workbench-Ready Read Model

- operator workbench 不需要自行扫描散落 artifacts，就能读取 kernel 暴露的运行态总览

### AC-007 Shared Reason Code Contract

- drift、blocked、stale、orphan、conflict 类场景均有稳定 reason code，并被 `status / board / release / qa / implement` 复用

### AC-008 Cross-Surface Host Consistency

- `implement / qa / release / team / ralph / real-project-validation / board` 对同一 run 的状态、排序、workspace、evidence 解释一致

## 9. 成功指标

- 主指标：同版本多 feature 实现编排不再依赖人工记忆
- 主指标：run 中断后的恢复路径明确且可重放
- 辅指标：`status/board/release` 对当前运行态的解释一致
- 辅指标：真实项目长任务从“单轮命令心智”升级为“可持续编排心智”

## 10. 与主 PRD 的关系

- 主线锚点：`beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance`
- 本并行线负责把主线里的“runtime”从概念主题收敛到可实现 kernel contract
- 后续 `user-story / test-case / implement / qa` 都应以本 feature 作为 execution substrate
- workbench 类能力必须建立在本 feature 完成后，不能倒挂

---

**Created**: 2026-05-01  
**Version**: v1.3.11  
**Status**: draft
