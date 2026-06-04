# Beacon v1.1.6 安全实现方案

## 1. 当前判断

v1.1.6 当前属于：

- **需求包已成形**
- **运行时代码尚未跟上**
- **可以进入实现**
- **不能直接视为可发布版本**

已确认事实：

1. `resolve_target_version(..., "auto")` 当前已经会选到 `v1.1.6`
2. runtime 管理口径仍停在 `v1.1.4`
3. `doctor verify-materials --version v1.1.6` 已通过
4. `doctor verify-delivery --version v1.1.6` 未通过
5. `gate check release --version v1.1.6` 未通过

结论：

- `v1.1.6` 已经足够支撑安全实现设计；
- 但当前仍是 requirement-materials-only 状态；
- 首轮实现必须是 **交付结构重构**，不是功能扩张。

## 2. 不变约束

实现 `v1.1.6` 时必须保持以下约束不变：

1. Beacon 仍是 **delivery kernel**，不是 runtime orchestrator。
2. `doctor` / `gate` / `report` / `status` / `review` / `workflow` 的核心职责不变。
3. `.beacon/` 继续只代表 runtime internal surface，不升级为正式交付面。
4. `docs/beacon/<version>/` 继续是 source of truth，只调整 human / machine 分层。
5. `v1.1.4` 及更早版本 contract 不得回归。
6. `eval-lab` 不进入首轮主线实现，不做整仓自治或自修改。

## 3. 可安全实现的范围

### 可以先做

- human primary surface 收口
- `.machine` 机器面路径迁移
- `doctor` 破坏性修复器
- LLM / skill prompt 合同

### 只能做最小骨架

- eval benchmark 定义
- keep/discard ledger
- drift-auditor skeleton

### 当前不要做

- 新 runner / orchestration 能力
- 全仓自动研究 / 自动修改
- 把 Beacon 演进为 agent lab
- 长期双写兼容方案

## 4. 风险识别

## 4.1 版本选择风险

当前 `auto` 已经选到 `v1.1.6`，但 runtime 口径仍是 `v1.1.4`。  
如果不先处理版本选择策略，后续命令可能把“未实现版本”当成默认目标。

## 4.2 路径耦合风险

现有代码大量把 machine artifacts 写死在：

- `docs/beacon/<version>/execution/*.json`
- `docs/beacon/<version>/qa/test-cases/*.json`

因此 `v1.1.6` 实现不是单点改动，而是一次受控的路径与消费面重构。

## 4.3 行为回归风险

`status` / `report` / `gate` / `doctor` / `review` / `workflow` 目前都依赖旧路径。  
如果直接切写入路径而不先补读取兼容层，会破坏现有闭环能力。

## 5. 安全实施顺序

### Phase 0: 冻结版本选择

先明确：

- 未闭环版本是否允许被 `auto` 选中
- `v1.1.6` 在何种条件下才能成为默认目标

目标：

- 避免 runtime 在实现未完成前误读 `v1.1.6`

### Phase 1: 提取统一路径层

新增统一 artifact path resolver，例如：

- `beacon/utils/artifact_paths.py`

职责：

- 统一解析 human surface 路径
- 统一解析 machine surface 路径
- 针对 `<= v1.1.4` 返回旧结构
- 针对 `>= v1.1.6` 返回新结构

目标：

- 先消除分散硬编码
- 不改变现有命令语义

### Phase 2: 先改读取，不改写入

先让以下消费者同时支持旧路径与 `.machine`：

- `doctor`
- `gate`
- `report`
- `status`
- `review`
- `material_audit`
- `coverage`

目标：

- 新旧结构都能被消费
- Beacon 核心判断逻辑不变

### Phase 3: 实现 doctor 迁移器

按照 `v1.1.6` 规范，由 `doctor` 执行正式修复：

1. execution JSON -> `.machine/execution/`
2. QA JSON -> `.machine/qa/`
3. 补 `execution/index.md`
4. 补 `qa/test-cases/index.md`
5. 修 `SUMMARY.md`
6. 修 `release/<version>.md`

目标：

- 迁移行为集中到单一入口
- 不在各子命令中加入隐式迁移

### Phase 4: 再切生产者写入路径

更新写入方：

- `workflow`
- `test-case`
- `report`
- 必要时 `auto-test`

原则：

- human markdown 写人类主入口
- machine JSON 写 `.machine`
- `.beacon` 只保留 runtime/raw evidence

### Phase 5: 接入 prompt / skill 合同

把以下规范接进 Beacon 的上下文与提示词体系：

- human-first reading order
- progressive disclosure
- clarification gate
- no compatibility-first
- no overdesign

该阶段只调整工作法，不改变 Beacon 的产品边界。

### Phase 6: eval-lab 只做最小骨架

仅允许：

- benchmark 定义
- keep/discard 账本
- drift-audit skeleton

不允许：

- 自动修改整仓
- agent swarm 编排扩张
- 新 runtime 平台化能力

## 6. 首批受影响模块

优先梳理以下代码面：

- `beacon/commands/workflow.py`
- `beacon/commands/gate.py`
- `beacon/commands/doctor.py`
- `beacon/commands/report.py`
- `beacon/commands/status.py`
- `beacon/commands/review.py`
- `beacon/commands/test_case.py`
- `beacon/utils/material_audit.py`
- `beacon/utils/coverage.py`

这些模块是风险最高的，因为它们当前直接依赖旧 execution / QA JSON 路径。

## 7. 必须先补的回归测试

在进入结构迁移前，应先锁住以下行为：

1. `v1.1.4` 旧路径 contract 不变
2. `status/report/gate/doctor/review` 对旧结构继续可用
3. 新路径 resolver 行为可测试
4. `doctor repair` 可把旧包迁移到 `.machine`
5. `v1.1.6` 不再把 machine JSON 当 human primary surface
6. `v1.1.6` 不默认双写旧路径

## 8. 最终结论

`v1.1.6` 已经具备实现条件，但必须按“读兼容优先、迁移集中、写路径后切、eval-lab 后置”的顺序推进。  

只要遵守本文约束，`v1.1.6` 的实现会改变 **交付结构**，不会改变 Beacon 的 **本质功能**。
