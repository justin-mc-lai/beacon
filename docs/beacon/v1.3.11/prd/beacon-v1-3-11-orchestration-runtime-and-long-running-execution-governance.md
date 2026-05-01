# PRD: Beacon v1.3.11 orchestration runtime and long-running execution governance

**Feature**: `beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance`  
**Version**: `v1.3.11`  
**Date**: `2026-05-01`  
**Status**: `draft`  
**Track**: `main`  
**Scenario**: `runtime_control_plane`  
**Template**: `主 PRD / runtime-control-plane`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Prior version summary: `docs/beacon/v1.3.10/SUMMARY.md`
- Prior version release notes: `docs/beacon/v1.3.10/release/v1.3.10.md`
- Prior metadata governance PRD:
  - `docs/beacon/v1.3.10/prd/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- Prior prototype UX closure PRD:
  - `docs/beacon/v1.3.10/prd/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`
- Brainstorm evidence:
  - `docs/brainstorms/2026-05-01-基于-openai/symphony-elixir-实现源码做只读深挖，重点文件：orchestrator.ex、workflow.ex、workflow_st.md`
  - `docs/brainstorms/2026-05-01-以-beacon-v1.3.10-冻结材料和刚完成的-symphony/elixir-深挖为输入，调研下一版本候选-beacon-v1.3.10-的-orche.md`
- External reference mirror:
  - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/symphony`

## 1. 问题

### 1.1 Beacon 已经有 truth lifecycle，但缺少独立的 execution orchestration runtime

`v1.3.10` 已经把两类能力收口得比较稳定：

1. requirement truth 治理更强
   - `prd / user-story / test-case / prototype / .machine` 的冻结与双写边界更清楚
   - `implement / qa / release` 已能围绕同一套 requirement package 闭环
2. prototype 真相更完整
   - `prototype` 已从结构 freeze 升级为可产出 `ux-prd / DESIGN / state-aware contract / automation priority matrix` 的 UI/UX 类 PRD 编译器

但 Beacon 仍有一个结构性缺口：

> 它很擅长冻结“应该做什么”，但还不够擅长长期调度“正在做的工作”。

当前执行层仍偏命令式：

- 跑一次 `implement`
- 跑一次 `qa`
- 跑一次 `release`

而真实项目越来越多出现以下长任务形态：

- 一个任务需要多轮推进，而不是单轮命令结束
- 一个任务会经历 `continue / retry / repair / escalate / handoff`
- 多个子任务会并行存在，需要统一运行态观察
- `team / ralph / real-project-validation` 需要共享同一套 run 级状态、workspace、证据与恢复逻辑

### 1.2 当前缺口不是 requirement truth 缺口，而是 run-time execution 缺口

这条版本线不是要再发明新的 requirement stage，而是要解决 requirement truth 之外的运行缺口：

1. 缺少统一的 work item 抽象
   - 当前不同子面各自发起实现、验证、回放、修复，缺少统一的调度入口
2. 缺少 run 级隔离
   - 长任务仍容易共享同一工作目录、同一状态文件或同一会话语义
3. 缺少 retry / reconciliation
   - 失败后如何 backoff、何时可恢复、何时需要人工介入，当前没有统一 runtime 规则
4. 缺少 runtime board
   - 人类能看到很多 machine artifacts，但不容易直接看出“当前有哪些 run 在跑、卡在哪、谁需要介入”
5. 缺少 execution contract
   - requirement truth 已经很强，但还没有一套 repo-owned、run-oriented 的执行合同面去约束长任务调度

### 1.3 真实环境触发信号

这条需求不是抽象设想，而是由真实工作暴露出来：

1. `real-project-validation`
   - 已经证明 Beacon 能进入真实项目回溯与验证，但这类工作天然是长任务、多轮回放、多证据采集，不适合继续只用单次命令心智来承载
2. `team`
   - 需要从“协作入口”演进为“多任务运营入口”，否则多个子任务仍只能靠人工心智管理
3. `ralph`
   - 更适合做决策控制器，而不是直接吞掉所有执行状态
4. `implement / qa / release`
   - 继续保持唯一执行入口是对的，但外侧缺少统一的编排层，会让重复调度逻辑散落在不同命令里
5. Symphony 参考实现
   - `openai/symphony` 明确说明长任务调度要单独建模：
     - `workflow contract`
     - `orchestrator`
     - `workspace isolation`
     - `retry queue`
     - `status dashboard`
   - Beacon 不需要变成 Symphony，但需要吸收“长期运行执行层必须单独存在”的架构结论

### 1.4 为什么现在做

如果 `v1.3.11` 不补这层，后续问题会越来越明显：

1. `team / ralph / validation` 会继续各自维护半套调度逻辑
2. `implement / qa / release` 的执行闭环虽然强，但“闭环前的运行态”仍不可统一运营
3. 多 run 并发时，工作目录、状态、恢复策略、观察面会越来越混乱
4. requirement truth 继续增强，但执行成本仍主要转嫁给人类操作与人工跟踪

所以 `v1.3.11` 的合理主题不是再补一个新的 truth package，而是补：

> **Beacon orchestration runtime**

## 2. 目标

### 2.1 主要目标

在不改动 Beacon 主生命周期的前提下，为 requirement truth 之外的执行面新增统一 orchestration runtime，至少关闭以下缺口：

1. work item 能被统一注册与调度
2. 每个 run 有独立 workspace、状态与证据边界
3. 长任务有 continuation / retry / reconciliation 语义
4. 人类能直接看到当前运行态，而不是只看离散 artifacts
5. `team / ralph / real-project-validation / implement / qa / release` 能消费同一套执行层，而不是各自维护半套

### 2.2 非目标

- 不新增新的一级公开主生命周期 stage
- 不让 orchestration runtime 成为 requirement truth source
- 不让 tracker / queue / runtime board 反向改写 `prd / user-story / test-case / prototype`
- 不把 Beacon 变成 issue-tracker-first 产品
- 不在本版本内引入完整多租户控制平面
- 不在本版本内要求外部项目必须接入 Linear / GitHub Issues 等第三方来源
- 不把 `prototype`、`implement`、`qa`、`release` 的现有 truth 闭环拆掉重写

### 2.3 Truth 与 Execution 边界 / 分层

Beacon 需要明确三层边界，并把这次版本主题正式冻结为一条清晰的运行分层：

1. Requirement Truth Layer
   - `prd`
   - `user-story`
   - `test-case`
   - `prototype`
   - `.machine` requirement materials
2. Orchestration Runtime Layer
   - `work item source`
   - `run scheduler`
   - `workspace isolation`
   - `worker runtime`
   - `retry / reconciliation`
   - `runtime board`
3. Delivery Closure Layer
   - `implement`
   - `qa`
   - `release`
   - `acceptance / evidence manifest / workflow memory`

其中：

- requirement truth 负责定义“该做什么”
- orchestration runtime 负责定义“怎么长期调度去做”
- delivery closure 负责定义“怎么正式验证与放行”

## 3. 设计原则

### 3.1 主生命周期保持不变

Beacon 对人类公开的默认生命周期仍然是：

```text
prd -> user-story -> test-case -> prototype -> implement -> qa -> release
```

`orchestration runtime` 是执行层，不是新的主生命周期 stage。

### 3.2 执行层只能消费 truth，不能反向改写 truth

`work item / run / retry / runtime board` 都只能读取冻结 truth，并产出：

- execution evidence
- drift diagnosis
- repair suggestion
- escalation signal

它们不能直接覆写：

- `prd`
- `user-story`
- `test-case`
- `prototype`

若需要变更 scope，必须路由回 `beacon-change` 或新的 PRD/change loop。

### 3.3 统一调度优先于命令分散调度

长任务调度逻辑不得继续散落在：

- `team`
- `ralph`
- `real-project-validation`
- `implement`
- `qa`

各自内部。

Beacon 必须优先建立统一 run scheduler，再让这些 surface 接入。

### 3.4 run 级隔离优先于全局共享目录

每个长任务 run 都必须有清晰的：

- workspace boundary
- status boundary
- evidence boundary
- recovery boundary

这是后续并发、多轮回放、跨项目验证能够成立的前提。

### 3.5 观察面优先于日志堆积

`orchestration runtime` 的目标不是再产出一批难读 machine files，而是提供更高信号的运行观察面，至少让人类能快速知道：

- 现在跑了什么
- 哪些卡住了
- 哪些在重试
- 哪些需要人工介入
- 下一步该做什么

## 4. 范围

### In scope

- Beacon 统一 `work item` 抽象
- Beacon 统一 `run` 抽象
- run scheduler 与最小并发/派发/取消/重试语义
- 同版本多个 feature package 的 execution blueprint 共存与按 feature 投影
- 版本内 feature implementation order / wave 分析
- 每 run workspace isolation
- worker runtime 生命周期记录
- retry / reconciliation 机制
- runtime board / 运行观察面
- `team / ralph / real-project-validation / implement / qa / release` 对 orchestration runtime 的接入边界

### Out of scope

- 完整 issue tracker 产品化集成
- 多租户 SaaS control plane
- 任意远程 worker 集群编排
- 替换现有 `implement / qa / release` 真相与 gate 体系
- 让 runtime board 替代 `status / help / doctor`
- 自动将 runtime 推断结果写回 requirement docs

## 5. 功能需求

### FR-001 Beacon 必须定义统一的 work item 模型

Beacon 必须支持统一 work item 模型，用于描述可被 orchestration runtime 调度的执行单元。

每个 work item 至少必须表达：

- `item_id`
- `item_type`
- `feature`
- `version`
- `source_surface`
- `priority`
- `requested_action`
- `truth_refs`
- `status`

最小 `item_type` 至少覆盖：

- `team_task`
- `ralph_step`
- `real_project_validation_case`
- `implement_delivery`
- `qa_repair`
- `release_closure`

### FR-002 Beacon 必须定义统一的 run 模型

每个 work item 被派发后，必须创建 run 级记录。

每个 run 至少必须表达：

- `run_id`
- `item_id`
- `workspace_ref`
- `runtime_mode`
- `status`
- `attempt_seq`
- `started_at`
- `updated_at`
- `next_action`
- `needs_human_intervention`
- `evidence_refs`

run 状态至少支持：

- `queued`
- `running`
- `retry_waiting`
- `blocked`
- `handoff_required`
- `completed`
- `cancelled`

### FR-003 Beacon 必须提供统一 run scheduler

Beacon 必须提供统一 run scheduler，而不是让各 surface 自己调度。

它至少必须支持：

- 入队
- 派发
- 并发限制
- continuation
- 失败重试
- 人工介入挂起
- run 取消

调度决策必须可追踪，不得成为黑盒副作用。

### FR-004 Beacon 必须提供 run 级 workspace isolation

每个 run 必须有独立 workspace 语义。

该能力至少必须支持：

- 生成安全 workspace 路径
- 绑定 run_id 与 workspace
- 在 run 完成或取消时清理/保留策略
- 禁止 run 越界写入不允许目录
- 为真实项目验证与未来 remote worker 预留 worker_host 扩展位

### FR-005 Beacon 必须提供 worker runtime 生命周期记录

每次 run 实际执行时，必须记录 worker runtime 生命周期，至少包括：

- 当前执行 surface
- 当前会话 id
- 当前 turn / step
- 最后状态更新时间
- 最后关键事件
- tokens / runtime metrics（若宿主支持）

该生命周期记录是 runtime board 的直接输入，不得只存在命令行 stdout 中。

### FR-006 Beacon 必须提供 retry / reconciliation 机制

Beacon 必须显式支持：

- backoff retry
- stale run detection
- work item eligibility re-check
- blocked -> repair -> resume
- abandoned run reconciliation

尤其对 `real-project-validation` 和 `qa repair`，必须允许失败后进入明确的恢复状态，而不是只能重新手工跑整条命令。

### FR-007 Beacon 必须提供 runtime board

Beacon 必须提供人类可读的运行面板，至少展示：

- 当前 running runs
- retry queue
- blocked / handoff_required runs
- 当前 stage 分布
- 当前需要人工介入项
- 每个 run 的 next action

runtime board 必须优先呈现运行态判断，而不是原始 machine noise。

### FR-008 Beacon 必须提供 delivery closure bridge

orchestration runtime 必须能桥接到现有：

- `implement`
- `qa`
- `release`

但桥接方式必须满足：

1. `implement / qa / release` 仍是唯一正式执行与闭环入口
2. 调度层只能在外侧编排与记录运行态
3. 最终 acceptance / gate / release 结果仍落到当前 delivery kernel

### FR-009 `team` 必须优先接入 orchestration runtime

`team` 在本版本中必须被定义为 orchestration runtime 的首批消费方之一。

目标不是替换 `team`，而是让其：

- 以 work item 形式派发任务
- 以 run 形式观察任务
- 以 runtime board 形式管理整体运行态

### FR-010 `ralph` 必须作为 controller 而不是直接执行器接入

`ralph` 在本版本中必须被明确定位为：

- 决策层
- 升级/继续/修复/暂停控制器

而不是直接持有所有执行态。

换言之：

- `ralph` 决定 `what next`
- orchestration runtime 决定 `how it runs`

### FR-011 `real-project-validation` 必须接入 run 级隔离

`real-project-validation` 在本版本中必须成为另一条首批消费方。

它至少必须支持：

- validation case -> work item
- per-case run creation
- per-run workspace
- failure -> retry / repair
- 统一 runtime board 可见

### FR-012 orchestration runtime 不得反向写 requirement truth

Beacon 必须明确阻断以下行为：

- run state 自动改写 PRD
- runtime inference 自动改写 user-story/test-case
- execution board 自动改写 prototype truth
- tracker / run queue 取代 requirement package 成为 source of truth

若运行时发现需求变化，系统只能输出：

- change recommendation
- repair recommendation
- escalation recommendation

### FR-013 同版本多个 feature package 的 execution blueprint 投影必须可并存

当同一版本下存在多个 feature package 时，Beacon 必须保证：

- `execution/architecture-blueprint.md` 不再只能容纳单一 feature 的 implementation projection
- 系统必须存在版本级 `implementation-delivery-host` 作为同版本多 feature baseline 的统一宿主视图
- blueprint 中的 managed projection 至少能按 `feature_slug` 独立投影与独立校验
- `implement plan / implement run / release gate` 只校验当前 feature 对应的 projection block
- 后续 feature 的 implementation baseline materialization 不得覆盖前一 feature 已存在的 projection block

该能力的目标不是让 blueprint 升格为新的 truth source，而是让它成为：

- 版本级 human-readable execution mirror
- feature-aware projection host
- version-level baseline host projection surface
- 多 feature 并行/串行 delivery 的稳定观察面

### FR-014 Beacon 必须提供版本内 feature implementation order 分析

当同一版本下存在多个 feature package 时，Beacon 必须能够生成稳定的 implementation ordering 结果，用于指导：

- 哪些 feature 可并行推进
- 哪些 feature 必须串行推进
- 哪些 feature 依赖前置 feature 完成后才能进入下一 wave

该能力至少必须支持以下排序信号：

- 显式 feature dependency（如 `depends_on_features`）
- writable/direct delivery service 冲突
- 版本级 baseline host 中已登记的 `target_branch / writable_services / baseline_ref`
- 当前 revision / technical review / implementation progress 的时间与状态信号

排序结果至少必须表达：

- `ordered_feature_slugs`
- `waves`
- 每个 feature 的 `depends_on_features`
- `parallelizable`
- `reason_code`

并且至少必须投影到版本级：

- change payload / change markdown
- release-facing version planning surface

### FR-015 Beacon 必须维护版本级 implementation delivery host

当同一版本下存在多个 feature package 时，Beacon 必须维护稳定的版本级 baseline host，至少用于：

- 注册该版本已存在的 feature baseline
- 给 `implement / release / change` 提供统一读取面
- 作为同版本多 feature 串并行分析的优先输入源

该 host 至少必须注册：

- `feature_slug`
- `revision_id`
- `baseline_ref`
- `writable_services`
- `depends_on_features`
- `target_branch`

并且必须满足：

- host 由 canonical baseline envelope 单向投影生成，而不是人工手写维护
- host block 可投影到 `execution/architecture-blueprint.md`
- 重新 materialize 某个 feature baseline 时，host registry 必须同步刷新，但不得破坏其他 feature 的已注册记录

## 6. 数据 / 状态 / 集成

### 6.1 Truth 来源

本版本要求 orchestration runtime 只消费以下 truth 来源：

- `docs/beacon/<version>/prd/`
- `docs/beacon/<version>/user-story/`
- `docs/beacon/<version>/qa/test-cases/`
- `docs/beacon/<version>/prototype/`
- `docs/beacon/<version>/.machine/`
- `.beacon/metadata/`

### 6.2 Runtime 状态层

建议的最小 runtime 状态层至少包括：

- `.beacon/runs/`
- `.beacon/state/orchestration/`
- `.beacon/runtime/board/`

其中至少应能投影：

- work item 列表
- run 状态
- workspace 引用
- retry 队列
- handoff / escalation 状态

### 6.3 兼容与集成

本版本允许 orchestration runtime 先只依赖 Beacon 现有本地状态与宿主运行态。

SQLite、PocketBase、外部 tracker adapter 可以作为兼容层或后续扩展位，但不应成为本版本必须交付的唯一路径。

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 执行层范围膨胀成新平台 | 高 | 明确只做最小 orchestration runtime，不做多租户平台 |
| 调度层反向污染 truth | 高 | 把 runtime 层写权限限制在 `.beacon/state` 与 run artifacts，不直接写 requirement docs |
| `team / ralph / validation` 各自继续造轮子 | 中 | 先冻结统一 work item / run / scheduler 契约，再让各 surface 接入 |
| board 成为 machine noise 展示墙 | 中 | 以 next action / blocked / retry / human intervention 为主，不直接暴露内部噪声 |
| 多 run 并发导致 workspace 污染 | 高 | 强制 run 级 workspace isolation 与路径安全 |

## 8. 验收标准

### AC-001 Beacon 能统一注册并派发至少三类长任务

至少以下三类 work item 必须能用统一模型注册并进入 run scheduler：

- `team_task`
- `ralph_step`
- `real_project_validation_case`

### AC-002 每个 run 都有独立 workspace 与状态记录

对于同一版本下并发或串行的多个 run，系统必须能证明：

- workspace 不混用
- run 状态独立
- 证据引用独立

### AC-003 失败任务存在明确 retry / repair 语义

对于至少一条 `real-project-validation` 或 `qa repair` run，系统必须能证明：

- 失败后不会直接静默丢失
- 可进入 `retry_waiting` 或 `blocked`
- 有明确恢复动作或人工介入语义

### AC-004 runtime board 能直接回答“现在发生了什么”

runtime board 至少必须能让人类直接判断：

- 当前有哪些 run 在跑
- 哪些 run 卡住了
- 哪些在重试
- 哪些需要人工介入
- 下一步该做什么

### AC-005 `implement / qa / release` 与 orchestration runtime 边界稳定

系统必须证明：

- `implement / qa / release` 仍是唯一正式闭环入口
- orchestration runtime 只做调度、状态、证据与桥接
- runtime 不反向改写 requirement truth

### AC-006 同版本多个 feature 的 blueprint 投影不会相互覆盖

对于同一版本下至少两个 feature package，系统必须能证明：

- `execution/architecture-blueprint.md` 中可同时存在两个以上 feature-aware projection block
- 重新 materialize 某一 feature baseline 后，不会删除或覆盖其他 feature 的 projection block
- `implement` 与 `release` 的 gate 只校验当前 feature 对应的 block，而不会误把其他 feature 的 block 当成 drift

### AC-007 系统能自动给出版本内 feature 的推荐实现顺序

对于同一版本下至少三个 feature package，系统必须能证明：

- 至少能把“共享 writable/direct delivery service 的 feature”自动串行化
- 至少能把“无服务冲突、无显式依赖的 feature”归入同一并行 wave
- 输出中能明确表达 `depends_on_features / wave / reason_code`
- 结果至少在版本级 change/release 观察面中可读，而不是只能藏在内部状态文件

### AC-008 系统维护版本级 baseline host 作为同版本多 feature 的唯一宿主视图

对于同一版本下至少两个 feature package，系统必须能证明：

- 存在版本级 `implementation-delivery-host`
- host 至少登记 `feature_slug / revision_id / baseline_ref / writable_services / depends_on_features / target_branch`
- host 由 canonical baseline envelope 单向投影生成，而不是独立手填
- host 与 blueprint 中的版本级投影块保持一致

### AC-009 implementation ordering 优先读取 baseline host

对于同一版本下至少三个 feature package，系统必须能证明：

- implementation ordering 优先读取 baseline host，而不是只依赖 technical review contract
- 当部分 feature 尚未形成完整 technical review contract 时，系统仍能基于 host registry 给出稳定的串并行建议
- 对显式 `depends_on_features` 与共享 writable service 冲突，输出能明确区分 `reason_code`

## 9. 成功指标

- 主指标：需要人工重新手工拼接长任务上下文的次数显著下降
- 辅指标：对于 `team / ralph / real-project-validation`，run 级恢复与继续推进时间缩短
- 版本级指标：同版本多 feature 交付时，不再因 blueprint projection 覆盖导致 implement/release gate 漂移
- 排序指标：版本操作者无需手工维护 feature 串并行顺序表，即可获得可解释的 implementation wave 建议

## 10. 依赖与开放问题

- 需要后续在 `user-story` 阶段明确 `work item` 与 `run` 的最小字段集合
- 需要后续决定 runtime board 是扩展 `status --board` 还是独立 support surface
- 需要后续决定 remote worker / ssh worker 是否进入 `v1.3.11` 主线还是保留为扩展位
- 需要后续决定 `implement / qa / release` 哪些子路径优先接入 orchestration runtime

## 11. Diagram Truth Layer

### 11.1 Diagram Types

- `branch-flow`
- `state-machine`
- `decision-priority`

### 11.2 State Axes

- `runtime_item_axis`
- `team_task`
- `ralph_step`
- `real_project_validation_case`
- `implement_delivery`
- `qa_repair`
- `release_closure`
- `run_status_axis`
- `queued`
- `running`
- `retry_waiting`
- `blocked`
- `handoff_required`
- `completed`
- `cancelled`
- `workspace_axis`
- `isolated_workspace`
- `shared_workspace_blocked`
- `recovery_axis`
- `retry_path_explicit`
- `repair_resume_explicit`
- `human_intervention_explicit`
- `delivery_bridge_axis`
- `truth_read_only`
- `runtime_bridge_only`
- `release_gate_preserved`

### 11.3 Propagation Contract

- Diagram truth must stay explicit through freeze readiness, implementation planning, and QA coverage.
- State axes must not be silently compressed into one implicit status field.

---

**Created**: 2026-05-01  
**Version**: v1.3.11  
**Status**: draft  
**Memory Context**: Symphony execution-layer research + Beacon v1.3.10 release closure
