# PRD: Beacon v1.3.11 PRD freeze anti-drift and machine-mirror reconciliation

**Feature**: `beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation`  
**Version**: `v1.3.11`  
**Date**: `2026-05-01`  
**Status**: `draft`  
**Track**: `parallel`  
**Scenario**: `requirement_package_governance`  
**Template**: `并行 PRD / anti-drift-governance`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/v1.3.11/SUMMARY.md`
- Upstream runtime PRD: `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`
- Change document: `docs/beacon/v1.3.11/change/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`

## 1. 问题

`v1.3.11` 已经暴露出一条真实 requirement gap：

- human PRD markdown 在正式修订后可以变新
- `.beacon/prd` 与 `docs/beacon/<version>/.machine/prd` 仍可能停留在旧 projection
- `validate` 只知道 markdown contract，`audit` 又只查 legacy mirror

结果是：

- 需求冻结会出现 human / machine 漂移
- 操作者容易以为“validate pass 就等于 freeze 完整”
- 后续 `freeze / implement / qa / release` 可能站在旧 machine truth 上继续推进

## 2. 目标

### 2.1 主要目标

为 `PRD freeze` 增加正式 anti-drift 闭环，使 Beacon 能：

1. 把当前 markdown 作为可重投影 truth
2. 统一 reconcile human 与 machine mirror
3. 扩展 audit 到 full mirror 审计
4. 明确 transaction latest / supersedes 语义
5. 在 stale mirror 出现时 fail-closed，并提供恢复路径

### 2.2 非目标

- 不新增新的一级公开主命令
- 不把 `doctor sync-materials` 重新提升为正常 PRD revise 主路径
- 不让 repair fallback 替代正常 reconcile

### 2.3 Truth 与 Execution 边界 / 分层

本线必须明确 requirement 分层：

1. human truth：`docs/beacon/<version>/prd/*.md`
2. machine mirror：`.beacon/prd/*.json` 与 `docs/beacon/<version>/.machine/prd/*`
3. repair / execution support：`doctor` 与 change-loop support surface

其中：

- truth 可以被正式修订
- machine mirror 必须可重投影
- repair 只负责恢复，不负责定义 truth

## 3. 设计原则

### 3.1 markdown 可编辑，但 mirror 不能静默滞后

人类可以修订 PRD，但 machine mirror 不允许继续静默保留旧版本。

### 3.2 reconcile 属于正常主路径，repair 属于异常路径

`reconcile` 是正常 requirement refresh 动作；`doctor` repair 只在损坏或缺失时使用。

### 3.3 stale mirror 必须可见、可审计、可恢复

系统必须显式暴露 stale mirror，而不是让其在 gate 前继续潜伏。

## 4. 范围

### In scope

- PRD reconcile contract
- full mirror audit
- transaction latest / supersedes 语义
- stale mirror detection
- doctor fallback boundary

### Out of scope

- 多租户 PRD control plane
- 数据库化 requirement source of truth
- 自动改写 user-story / test-case / prototype

## 5. 功能需求

### FR-001 PRD markdown 必须支持重投影

Beacon 必须允许当前 `PRD markdown` 作为 authoritative truth 被重新投影到 machine mirror。

### FR-002 audit 必须覆盖 full mirror

Beacon 必须把 PRD audit 扩展到：

- `docs/beacon/<version>/prd/*.md`
- `.beacon/prd/*.json`
- `docs/beacon/<version>/.machine/prd/*.canonical.json`
- `docs/beacon/<version>/.machine/prd/*.compile.json`

### FR-003 transaction 必须支持 latest / supersedes

Beacon 必须让多次 PRD transaction 之间存在当前 active pointer 与 superseded 关系。

### FR-004 stale mirror 必须 fail-closed

当 human truth 与 machine mirror 漂移时，系统必须明确阻断后续 freeze / implement / qa / release。

### FR-005 doctor fallback 必须可恢复

当 machine sink 缺失、损坏或不可信时，`doctor` fallback 必须给出明确恢复步骤，并允许回到正常验收路径。

## 6. 数据 / 状态 / 集成

### 6.1 Truth 来源

- `docs/beacon/<version>/prd/*.md`
- `.beacon/prd/*.json`
- `docs/beacon/<version>/.machine/prd/*`

### 6.2 Mirror 状态层

- PRD canonical envelope
- compile payload
- legacy machine mirror
- transaction lineage

### 6.3 恢复面

- `doctor sync-materials`
- `doctor repair-package`
- `doctor verify-materials`

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| human 改了 markdown 但 machine 继续旧版本 | 高 | 引入 reconcile 和 full mirror audit |
| repair surface 挤占主路径 | 中 | 明确区分 reconcile 与 doctor fallback 边界 |
| 历史 transaction 混淆当前 truth | 高 | 增加 latest / supersedes 语义 |

## 8. 验收标准

### AC-001 PRD 可重投影

human markdown 修订后，Beacon 能在不手工 patch JSON 的前提下重新生成 machine mirror。

### AC-002 audit 能定位 mirror 漂移

系统能明确指出 stale mirror 是发生在 legacy mirror、canonical、compile，还是多个 sink 同时失配。

### AC-003 transaction 当前性可判断

系统能判断谁是当前 active transaction，谁已经 superseded。

### AC-004 stale mirror 会阻断主链

当 stale mirror 已被识别时，freeze / implement / qa / release 不会继续通过。

### AC-005 doctor fallback 可回主链

repair 完成后，系统能重新回到 `validate -> audit -> freeze readiness` 路径。
