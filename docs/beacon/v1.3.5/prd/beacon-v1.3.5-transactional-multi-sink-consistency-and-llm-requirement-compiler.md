# PRD：Beacon v1.3.5 事务一致多写与 LLM 需求编译器修复线

**Feature**: `beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler`  
**Version**: `v1.3.5`  
**Date**: `2026-04-20`  
**Status**: `frozen-pending-implementation`  
**Track**: `parallel`  
**Scenario**: `runtime_control_plane + tooling_surface`  
**Template**: `并行 PRD / repair`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/v1.3.5/SUMMARY.md`
- Main PRD: `docs/beacon/v1.3.5/prd/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md`
- 上游诊断结论（当前 line）：
  - 主链职责总体满足；
  - 事务一致多写仍部分满足；
  - LLM 规范输出仍部分满足；
  - `template` 仍偏骨架占位，语义闭环不稳定。

## 1. 问题

本并行 PRD 用于修复 Beacon 在“职责落地”上的两个核心不足：

1. 多写入点事务一致性不完整。
2. `prd` 生成仍偏模板填空，LLM 语义编译不稳定。

### 1.1 多写入点一致性仍存在“部分提交”窗口

Beacon 当前已建立 `canonical -> human/machine/sqlite` 的目标模型，但仍存在以下风险：

- 某些投影写入链路发生失败时，可能出现“部分 sink 已更新、另一个 sink 未更新”的状态。
- 运行态投影（SQLite / PocketBase）与文档面可能短时间不一致。
- 事务失败语义在不同子链路上不完全同形，导致恢复策略不统一。

结果是：

> 边界上写的是“事务一致”，实现上仍有“degraded 可继续”路径，容易形成跨面漂移。

### 1.2 `prd create` 仍偏“模板骨架生成器”

当前 `template` 约束已经有了，但语义填充仍不够稳定，主要问题：

- 对“边界、分层、恢复策略、验收链路”的写入依赖人工补充。
- 对真实输入（global-boundaries / 版本包 / 现有 debug issue / 已有 PRD）的编译不足。
- 输出可读，但 machine 面“为什么这么写”的证据不足。

结果是：

> `template` 只是形式约束，尚未稳定成为 requirement-driven 的语义编译器。

### 1.3 为什么必须在 v1.3.5 同步修复

`v1.3.5` 主线在做 prototype wireframe freeze。如果此时不补齐事务与编译能力：

- 原型闭环会持续面临 human/machine/sqlite 漂移风险；
- 后续 `v1.3.6` 管理端消费的 requirement artifact 质量不稳定；
- `prd -> user-story -> test-case -> prototype -> implement -> qa -> release` 的源头会继续抖动。

## 2. 目标

### 2.1 主要目标

将 Beacon 的“职责约束”落到可执行实现：

1. 多写入点统一走事务提交语义，禁止静默部分成功。
2. `prd` 从模板生成提升为“模板约束 + LLM 语义编译”双层机制。
3. 人类面与机器面输出同源、可追溯、可校验，不再各写各的。

### 2.2 非目标

- 不新增新的公开一级主命令。
- 不把 PocketBase / SQLite 升级为正式交付真相。
- 不要求 v1.3.5 完成全部 UI 产品化实现（仍由后续版本承接）。

## 3. 设计原则

### 3.1 Canonical First

任何多写入都必须先生成 canonical envelope，再从 canonical 单向投影到各 sink。

### 3.2 Transaction First

提交语义固定为：

`prepare -> validate -> stage -> commit -> publish -> verify`

任一 sink 写入失败：

- 默认事务失败；
- 进入显式失败记录；
- freeze / release 不得通过。

### 3.3 Template is Schema, LLM is Compiler

- `template` 只定义结构和必填 contract。
- LLM 负责语义编译与闭环推理。
- 任何未满足 contract 的 LLM 输出必须被结构校验拒绝。

### 3.4 Human/Machine 双面同源

- human 文档与 machine 文档必须来自同一 canonical payload。
- 禁止 human 文档直接反向改写 machine 真相。

### 3.5 Truth Boundary 不动摇

正式真相仍是：

- `docs/beacon/<version>/`
- `.beacon/`

SQLite/PocketBase 只做 projection/control plane。

## 4. 范围

### In scope

- 多写入事务协调器（至少覆盖 prototype 与 runtime projection 相关写入）。
- 事务元数据统一化（`transaction_id/source_hash/projection_seq/committed_at/sink_checksums`）。
- 失败回滚/失败标记/失败阻断的统一策略。
- `prd create` 的 LLM 编译模式与结构校验。
- PRD 机器证据面（编译来源、约束命中、降级原因）落盘。

### Out of scope

- 新增用户可见“事务管理”命令面。
- 将 LLM 模型供应商策略产品化为复杂配置系统。
- 把 PRD 改成自由写作工具。

## 5. 功能需求

### FR-001 多写入统一事务协调器

为 `canonical -> human -> machine -> sqlite` 提供统一事务协调器：

- 固定阶段：prepare/validate/stage/commit/publish/verify。
- 输出统一 `transaction_result`。
- 每次提交都必须带事务元数据。

### FR-002 禁止静默部分提交

当发生 sink 写入失败时，必须满足其一：

1. 全量回滚到提交前状态；或
2. 标记为失败事务并显式阻断 freeze/release。

不允许“部分成功但默认为可用”。

### FR-003 Runtime Projection 失败语义收敛

runtime ledger 写入失败时必须：

- 标记 `status=failed_transaction`（或等价明确失败状态）；
- 记录失败原因与失败 sink；
- 不得伪装成“已一致”。

### FR-004 跨面一致性校验收敛到 gate/review/doctor

`status/review/doctor/gate/release` 必须可读取统一事务状态，并判断：

- human/machine/sqlite 是否一致；
- 是否存在未闭合失败事务；
- 是否允许继续 freeze/release。

### FR-005 `prd create` 增加 LLM 编译模式

`prd create` 应支持：

- `mode=llm`（优先语义编译）；
- `mode=rule`（规则降级）；
- `mode=auto`（默认，按可用性决策）。

### FR-006 模板约束与语义编译解耦

PRD 生成流程必须拆为：

1. Schema/template contract（章节、字段、约束）；
2. LLM semantic compile（内容推理）；
3. Contract validation（硬校验）；
4. Projection（human + machine 落盘）。

### FR-007 PRD 编译证据必须落 machine 面

每次 PRD 生成都应写入 machine 证据，至少包含：

- generator_mode（llm/rule/auto）；
- model 或 fallback 标识；
- source_refs（global boundaries / version summary / existing PRDs / debug issues）；
- constraint_hits；
- open_questions；
- compile_hash。

### FR-008 LLM 输出不达标必须阻断或降级可见

当 LLM 输出未满足 contract：

- 必须自动重试或降级；
- 降级必须带显式 `fallback_reason`；
- freeze-ready 判定必须可识别该降级状态。

### FR-009 并行 lane 输出格式统一

`implement single/team/ralph` 的 requirement traceability 与 delivery summary 必须继续保持同形 contract，避免 lane 间语义漂移。

## 6. 非功能需求

### NFR-001 确定性

同一输入在 rule 模式下输出应稳定可复现；llm 模式必须保留可审计编译证据。

### NFR-002 可恢复

任意投影损坏后，必须能从 `docs/beacon + .beacon` 重建一致状态。

### NFR-003 可观测

事务失败、回滚、降级、重试都必须有可查询事件与证据路径。

## 7. 验收标准

### AC-001 事务一致性

构造单 sink 失败场景时：

- 不出现静默部分成功；
- freeze/release 被阻断；
- 有明确失败事务记录。

### AC-002 跨面一致性

同一事务完成后，human/machine/sqlite 的 `transaction_id/source_hash/projection_seq` 全量一致。

### AC-003 PRD 编译质量

`prd create --mode llm` 生成结果必须覆盖：

- 边界；
- 分层；
- 恢复策略；
- 验收链；
- 风险与缓解；
- 不只是模板占位句。

### AC-004 可审计降级

断开 LLM 能力后，`mode=auto` 进入 rule fallback，并保留 machine 证据与 fallback 原因。

### AC-005 主链闭环不变形

不新增公开一级主命令；人类主面仍维持：

`prd -> user-story -> test-case -> prototype -> implement -> qa -> release (+ help/status/doctor)`。

## 8. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 事务化改造波及面广 | 中-高 | 先从 prototype/runtime projection 两条链路落地统一协调器，再逐步扩展 |
| LLM 输出波动导致 PRD 不稳定 | 高 | 强制 schema 校验 + fallback + compile evidence |
| 团队误把 projection 当 truth | 高 | 在所有状态面持续展示 truth boundary，并在 doctor/gate 增加硬检查 |

## 9. 里程碑

1. M1：事务协调器与失败语义落地（prototype + runtime projection）。
2. M2：PRD LLM 编译模式与 contract 校验落地。
3. M3：gate/review/doctor 收敛统一判定口径并通过真实项目回归。

## 10. 冻结说明

该并行 PRD 作为 `v1.3.5` 的职责修复线冻结，后续实现必须对齐以下判断：

- 主链职责保持不变；
- 事务一致多写从“部分满足”提升到“满足”；
- LLM 规范输出从“部分满足”提升到“满足”；
- 模板仅作为结构约束，语义必须由 requirement-driven 编译产出。
