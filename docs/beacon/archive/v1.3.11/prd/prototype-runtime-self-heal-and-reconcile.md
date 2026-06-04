# PRD：prototype-runtime-self-heal-and-reconcile

**Feature**: `prototype-runtime-self-heal-and-reconcile`  
**Version**: `v1.3.11`  
**Date**: `2026-05-04`  
**Status**: `draft`  
**Track**: `parallel`  
**Scenario**: `prototype_runtime_governance`  
**Semantic Label**: `原型运行时自愈与重投影闭环`  

target_audience: Beacon prototype maintainer、requirement owner、runtime operator
primary_use_cases: 修复 prototype bundle truth 漂移,执行 nondestructive reconcile,判断 freeze drift 类型并自动给出 repair 路径
operator_mental_state: 需要先判断当前 prototype bundle 是否可继续 freeze，还是必须 reconcile、repair 或 recreate
usage_environment: 桌面优先的本地 requirement freeze、prototype review、runtime gate 与真实项目验证环境
brand_tone: formal, restrained, precise, operational
density_preference: workbench-medium
design_preset: apple-inspired-design-md

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/archive/v1.3.11/SUMMARY.md`
- Execution index: `docs/beacon/archive/v1.3.11/execution/index.md`
- Upstream PRDs:
  - `docs/beacon/archive/v1.3.11/prd/prototype-design-intelligence-and-governed-rendering-separation.md`
  - `docs/beacon/archive/v1.3.11/prd/beacon-execution-runtime-kernel.md`
- Related changes:
  - `docs/beacon/archive/v1.3.11/change/prototype-runtime-self-heal-and-reconcile.md`
  - `docs/beacon/archive/v1.3.11/change/beacon-operator-workbench-and-board-launcher.md`
  - `docs/beacon/archive/v1.3.11/change/beacon-execution-runtime-kernel.md`

## 1. 问题

### 1.1 当前断层

Beacon 当前 prototype runtime 已具备 `create / review / freeze / status` 四个基本 surface，但 bundle 真相仍存在三层断裂：

- `review` 实际读取 `prototype-plan.json`，但 host 经常只看到 `manifest` 或 human-edited source
- `freeze` 遇到 source drift 只有硬阻断，没有 `metadata-only repair / reconcile / nondestructive refresh`
- `create` 仍是高风险 destructive projection，可能覆盖已收窄的人类页面与正式可见语义

结果是：

- host LLM 需要输出“先不要盲目重跑 create、先补字段、再 freeze”的人工诊断话术
- runtime 自身无法对 `stale plan truth / sink drift / transaction drift` 做正式收口
- 真实项目 prototype refresh 需要手工 patch 多个 JSON 才能重新 freeze

### 1.2 触发信号

- 真实项目 `shopxo_canada` 在 `third-party-capability-governance` 上已经暴露：`prototype-brief` 正确，但 `plan / manifest / canonical-envelope` 未同步
- 当前 `review` 与 `freeze` 的恢复路径都要求人工判断是否重跑 `create`
- `prototype-design-intelligence-and-governed-rendering-separation` 已收紧了输出治理，但 runtime 层还没有自愈能力

### 1.3 为什么现在做

若不把 prototype runtime 的 reconcile/self-heal 收口为正式 requirement line，后续任意 feature 都会继续出现：

- source truth 修正后 bundle 仍旧旧骨架
- review 只失败，不说明 canonical repair path
- freeze 因 transaction/source drift 被迫手工 patch
- host-native runtime 能力被 bundle repair 摩擦抵消

## 2. 目标

### 2.1 主要目标

- 为 prototype runtime 建立正式的 `self-heal and reconcile` 闭环
- 统一 prototype canonical truth source，消除 `plan / manifest / canonical-envelope` 多头漂移
- 让 `freeze` 能区分 drift 类型并提供正式 repair path
- 让 `status / gate / board / implement-readiness` 能消费统一 reason codes，而不是依赖 host 解释

### 2.2 非目标

- 不把 prototype 变成自由编辑器
- 不在本 feature 中重做所有现有 prototype bundle
- 不允许 reconcile 反向改写 `prd / user-story / test-case`
- 不把 `doctor` fallback 替代正常 reconcile path

## 3. 设计原则

### 3.1 Canonical Truth Must Be Single

- prototype runtime 必须只有一个正式 canonical truth source
- `plan / manifest / canonical-envelope / freeze` 都只能是从 canonical truth 投影出来的 sink
- review、freeze、status 不得各自选择不同 truth

### 3.2 Reconcile Before Recreate

- 发现 drift 时，系统必须优先判断是否可以 `reconcile`
- 仅当 canonical truth 自身不可恢复或 projection contract 已失效时，才允许 destructive `recreate`

### 3.3 Human Narrowing Must Be Preserved

- 已冻结的 production-visible human copy 与 pages narrowing 必须被视为正式受保护资产
- 非 destructive refresh 不得覆盖 `pages/*.md`、`preview.html`、已收窄的 production copy

### 3.4 Drift Must Be Typed

- drift 必须至少分为：
  - `source-drift`
  - `metadata-only-drift`
  - `sink-drift`
  - `transaction-header-drift`
  - `canonical-truth-missing`
- 不允许所有失败都退化成“regenerate and review before freeze”

### 3.5 Repair Path Must Be Executable

- runtime 不能只给错误提示
- 必须返回正式 `reason_code / diagnosis / next_action / repair_path`
- operator 不应再依赖 host 自行推理修复步骤

## 4. 范围

### In scope

- prototype canonical truth contract
- prototype reconcile surface
- nondestructive refresh / projection repair
- freeze drift classification and repair routing
- status / gate / review 的 shared reason codes
- transaction/source header 的自动对齐

### Out of scope

- 新的主生命周期 stage
- 高保真设计器
- 任意人工编辑自动并回 runtime truth
- 与 prototype 无关的 PRD / user-story / test-case machine mirror 问题

## 5. 功能需求

### FR-001 Prototype Canonical Truth Contract

Beacon 必须明确 prototype runtime 的单一 canonical truth source，并定义以下 sink 只能从该真相单向投影：

- `prototype-plan.json`
- `manifest.json`
- `canonical-envelope.json`
- `freeze.json`
- `design-artifacts/*`

若多个 sink 之间存在信息不一致，系统必须以 canonical truth 为准并标记 drift。

### FR-002 Prototype Reconcile Surface

Beacon 必须提供正式 `prototype reconcile` 或等价内部 surface，用于：

- 读取 canonical truth
- 重投影 `plan / manifest / canonical-envelope / freeze metadata`
- 更新 source_fingerprints、transaction headers、sink fingerprints
- 保留受保护的人类页面与 production-visible copy

### FR-003 Nondestructive Refresh Contract

Beacon 必须提供 `nondestructive refresh` 语义。该语义至少满足：

- 默认不覆盖 `pages/*.md`
- 默认不覆盖已存在的 `preview.html` / `preview-dark.html`
- 默认不改写已冻结的 production-visible copy
- 只更新结构化 machine sink 与需要对齐的 metadata

### FR-004 Drift Classification

Beacon 必须在 `review / freeze / status / gate` 中统一输出 drift 分类：

- `source-drift`
- `metadata-only-drift`
- `sink-drift`
- `transaction-header-drift`
- `canonical-truth-missing`
- `destructive-recreate-required`

每类 drift 必须具备：

- `reason_code`
- `diagnosis`
- `repair_path`
- `next_action`

### FR-005 Freeze Repair Path

当 `freeze` 发现 drift 时，系统必须遵循以下逻辑：

1. 先判断是否属于 `metadata-only-drift` 或 `transaction-header-drift`
2. 若可修复，则先执行 reconcile/repair，再继续 freeze
3. 若属于 `sink-drift`，先重投影 machine sink，再重跑 review
4. 仅当属于 `destructive-recreate-required` 时，才允许 operator 重新 create

`freeze` 不得继续把所有 drift 都归约成单一 regenerate 提示。

### FR-006 Shared Reason Codes

以下 surface 必须共享 prototype drift reason codes：

- `prototype review`
- `prototype freeze`
- `prototype status`
- `gate`
- `implement-readiness`
- `real-project-validation`

禁止不同 surface 为同一 drift 各自产生不同错误语义。

### FR-007 Host Friction Elimination

当 prototype bundle 进入可 repair 的 drift 状态时，runtime 必须直接给出正式 repair action，而不是依赖 host LLM 输出分析型人工提示。

至少要消除以下 host 摩擦类型：

- “先不要盲目重跑 create”
- “先补 review 真正读取的字段”
- “手工 patch 多个 JSON 再 freeze”

### FR-008 Traceability And Audit

每次 reconcile / repair / freeze 都必须写入可审计信息，至少包含：

- `feature`
- `version`
- `source_hash`
- `projection_seq`
- `transaction_id`
- `repair_action`
- `drift_type`
- `sink_checksums`

status 与 audit 必须可区分：

- 正常 create
- nondestructive reconcile
- metadata repair
- destructive recreate

## 6. 边界 / 分层 / 恢复策略

### 6.1 边界

- requirement truth 定义 prototype scope
- prototype canonical truth 定义 bundle authoritative source
- reconcile 负责 projection 修复
- freeze 负责正式冻结
- doctor 仅处理损坏材料或异常 fallback

### 6.2 分层

固定为四层：

1. Requirement Truth Layer
2. Prototype Canonical Truth Layer
3. Projection Sink Layer
4. Freeze / Audit / Read-Model Layer

### 6.3 恢复策略

- `metadata-only-drift`：自动修 transaction/source header
- `sink-drift`：执行 nondestructive reconcile 后重跑 review
- `canonical-truth-missing`：阻断并要求 repair / doctor fallback
- `destructive-recreate-required`：明确提示 recreate 原因与会覆盖的范围

## 7. 验收锚点

- runtime 不再要求 host LLM 解释应该先 patch 哪些结构化文件
- `prototype review` 与 `freeze` 对同一 bundle 看到一致 canonical truth
- `freeze` 对 metadata-only drift 可直接 repair，不再硬阻断人工 patch
- `status` 能明确给出 drift 类型、next action 与 repair path
- 真实项目 prototype refresh 可通过 reconcile 完成冻结，不依赖 destructive create

## 7.1 风险与缓解

- 风险：canonical truth 选择错误会把错误 sink 重新投影为新基线。缓解：review、status、freeze 统一只读取正式 canonical truth，并在 reconcile 前输出 truth source 与 drift diagnosis。
- 风险：reconcile 误覆盖人类已收窄页面会把正式可见语义刷回旧骨架。缓解：nondestructive refresh 默认禁止改写 `pages/*.md`、`preview.html`、`preview-dark.html`。
- 风险：surface 各自输出不同 drift 语义会导致 operator 误判。缓解：review、freeze、status、gate 共享同一套 `reason_code / diagnosis / next_action / repair_path`。

## 8. 验收标准

- `prototype status` 必须对 `v1.3.11+` 输出正式 `drift_type / reason_code / diagnosis / next_action / repair_path`
- `prototype reconcile` 必须可在不覆盖 `pages/*.md`、`preview.html`、`preview-dark.html` 的前提下修复 machine sink 与 transaction metadata
- `prototype freeze` 遇到 `metadata-only-drift / transaction-header-drift / sink-drift` 时，必须先执行 repair/reconcile 路径，再决定是否继续 freeze
- `prototype gate` 必须透传 `prototype_sink_drift / prototype_source_drift / prototype_transaction_header_drift / prototype_metadata_drift / prototype_canonical_truth_missing / prototype_destructive_recreate_required`
- `doctor verify-materials --strict`、`qa run`、prototype 相关聚焦测试必须能通过 requirement package contract 与 runtime drift contract 验证

## 9. 依赖与影响

### Dependencies

- `prototype-design-intelligence-and-governed-rendering-separation`
- `beacon-execution-runtime-kernel`

### Impact

- `beacon/utils/prototype_utils.py`
- `beacon/commands/prototype.py`
- `beacon/commands/gate.py`
- `beacon-real-project-validation`
- prototype bundle machine mirrors

## 10. 下一步

本 PRD 冻结后，下一阶段应继续进入：

1. `beacon-user-story v1.3.11`
2. `beacon-test-case v1.3.11`
3. `beacon-implement v1.3.11`

不在本 PRD 内直接声明实现完成。
