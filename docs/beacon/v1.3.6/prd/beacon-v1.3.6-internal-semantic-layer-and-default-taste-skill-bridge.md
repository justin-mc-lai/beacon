# PRD：Beacon v1.3.6 内建语义层与默认 Taste Skill 桥接

**Feature**: `beacon-v1.3.6-internal-semantic-layer-and-default-taste-skill-bridge`  
**Version**: `v1.3.6`  
**Date**: `2026-04-22`  
**Status**: `frozen-pending-implementation`  
**Track**: `parallel`  
**Scenario**: `semantic-governance + prototype-implement-augmentation + lifecycle-alignment`  
**Template**: `并行 PRD / capability-convergence`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/v1.3.6/SUMMARY.md`
- Execution index: `docs/beacon/v1.3.6/execution/index.md`
- Architecture blueprint: `docs/beacon/v1.3.6/execution/architecture-blueprint.md`
- Brainstorm source:
  - `docs/brainstorms/2026-04-22-beacon-official-product-language-contract-for-prototype-and-implement-brainstorm.md`
- Capability boundary analysis:
  - `.beacon/analysis/beacon-capability-boundary-semantic-design-skill.md`
  - `docs/beacon/v1.3.6/execution/beacon-toolkit-lighthouse-beacon-capability-boundary-semantic-design-skill.md`
- Current alignment risks:
  - `beacon/cli_factory.py`
  - `beacon/utils/project_skills.py`

## 1. 问题

本并行 PRD 要收敛的不是单个页面文案问题，而是 Beacon 在 `prototype -> implement` 之间缺少稳定、官方、可复用的产品语义真相。

### 1.1 当前问题已在真实看板构建中暴露

Beacon 现有能力已经能做到：

- `prd / user-story / test-case` requirement truth 闭环
- `prototype` requirement-driven wireframe freeze
- `implement` requirement-bound delivery
- `skill registry / profile / orchestration` 外部 skill 受控接入

但在看板与前端表达场景里，仍会暴露三个问题：

1. LLM 进入 `prototype` 或 `implement` 前，没有先拿到一版官方化、面向前台的产品语义。
2. `prototype` 和 `implement` 之间缺少共享语义 contract，前端表达容易回落到内部工程词、临时命名和系统生成感。
3. 外部设计 skill 虽然已可桥接，但还没有被纳入受控生命周期，不足以稳定提升官方感与设计气质。

### 1.2 本质缺口不是“没有设计 skill”，而是“没有内建 semantic layer”

外部 skill 可以增强设计质量，但不能替代 Beacon 内部 requirement compile 的正式真相。

当前真正缺少的是：

```text
prd / user-story / test-case
→ official semantic layer
→ prototype freeze
→ implement delivery
→ qa / release consistency gate
```

如果没有这一层，后续无论是页面生成、前端实现还是 taste review，都只能在局部 prompt 里临时翻译需求，无法形成稳定产品能力。

### 1.3 当前边界还存在两处已知漂移

本次收敛同时冻结两个对齐风险：

1. `cli_factory.py` 顶层 help 仍混用旧主流程叙事，和当前全局 `7+3` 边界不完全一致。
2. `project_skills.py` 的 stage vocabulary 仍偏旧：
   - `implementation`
   - `verify`
   - `review`
   - `delivery`

这与当前 Beacon 人类主链：

```text
prototype
→ implement
→ qa
→ release
```

不完全对齐，后续也不利于接入默认 design bridge skill。

## 2. 目标

### 2.1 主要目标

在 `v1.3.6` 冻结以下能力模型：

```text
requirement truth
→ Beacon internal semantic layer
→ prototype semantic preflight
→ implement semantic/design augmentation
→ qa / release semantic consistency gate
```

并明确：

- `semantic layer` 是 Beacon 内建新增能力
- 设计 skill 通过外部 bridge 接入
- 默认 bridge 仓库是 `https://github.com/Leonxlnx/taste-skill`
- 默认 bridge skill 是 `taste-skill`

### 2.2 明确结果

本线完成后，Beacon 应满足：

1. 在 `prototype` 之前，先能从 `prd / user-story / test-case` 预生成官方产品语义。
2. `prototype` 与 `implement` 持续复用同一份语义真相，而不是各自临时翻译。
3. `taste-skill` 可作为默认外部设计增强 skill，被 `prototype / implement` 内部受控消费。
4. `qa / release` 可检查语义与设计增强是否和 requirement truth 保持一致。
5. CLI 与 project skill stage 词汇回到当前 `7+3` 全局边界与 `prototype / implement / qa / release` 生命周期。

### 2.3 非目标

本 PRD 不承担：

- 不新增新的公开一级主命令
- 不把 `semantic` 变成独立的人类主流程 stage
- 不把外部 skill 安装动作变成 Beacon 主流程的一部分
- 不把 `taste-skill` 直接升格成 Beacon truth source
- 不在本线内一次性完成全部前端页面视觉升级

## 3. 设计原则

### 3.1 `semantic` 必须内建，不能外包

Beacon 对需求理解的官方产品语义，必须由内部 canonical compile 产出，而不是依赖第三方 skill 或前端实现阶段临时补齐。

### 3.2 外部 design skill 只能做 augmentation，不能做 truth source

`taste-skill` 和其他 design skill 可以增强：

- 页面气质
- 信息架构表达
- 设计系统口径
- taste review

但不能绕过 Beacon 的：

- requirement truth
- canonical envelope
- review / gate / release

### 3.3 人类主面不扩张

对外仍保持：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
```

辅助面仍保持：

- `help`
- `status`
- `doctor`

### 3.4 lifecycle assets 必须单源投影

语义层、设计增强结果、QA 结论都必须由 Beacon canonical 单向投影生成，不允许 human 文档、外部 skill 输出或局部页面代码反向改写真相。

### 3.5 兼容旧 profile，但新语义必须 canonical

`project_skills` 需要兼容历史配置中的旧词汇：

- `implementation`
- `verify`
- `review`
- `delivery`

但内部 canonical stage 应收口为：

- `prototype`
- `implement`
- `qa`
- `release`

## 4. 范围

### In scope

- 定义 Beacon 内建 `semantic layer` 的生命周期位置与产物边界
- 冻结默认 design bridge skill：
  - repo: `https://github.com/Leonxlnx/taste-skill`
  - skill: `taste-skill`
- 明确 `prototype` 的 semantic preflight 和 design augmentation 接入点
- 明确 `implement` 的 semantic/design augmentation 接入点
- 明确 `qa / release` 的 semantic/design consistency gate
- 对齐 `cli_factory.py` 顶层主流程文案
- 对齐 `project_skills.py` 的 canonical stage vocabulary，并兼容 legacy aliases

### Out of scope

- 完整实现 semantic schema 的所有字段
- 完整实现 `taste-skill` discovery / install UX
- 大规模重做现有 prototype 页面内容
- 新增独立 `semantic` 或 `design-skill` 公开主命令

## 5. 能力模型

### 5.1 Beacon internal semantic layer

`semantic layer` 是 requirement compile 的正式中间层，至少负责：

1. 官方页面名、状态名、模块名、动作名预生成
2. 前台禁用词与内部词翻译规则
3. `prototype / implement / qa / release` 可复用的语义 contract
4. 语义变更的受控 writeback 和 anti-drift 检查

建议产物包括：

- `semantic-contract.json`
- `semantic-dictionary.md`
- `semantic-usage-guidelines.md`
- `semantic-review.json`

### 5.2 Prototype semantic preflight

`prototype` 在 freeze 前必须先消费 `semantic layer`，至少用于：

- 页面名称
- 状态标签
- 角色叙事
- 模块标题
- 禁用词替代
- 页面与 AC/TC 的语义映射

### 5.3 Implement design augmentation

`implement` 必须把 `semantic layer` 作为正式输入之一，并允许在内部受控调用默认 design bridge skill，用于：

- 前端页面命名和状态系统约束
- 组件口径 / handoff 文案增强
- taste review / design-to-component 增强

### 5.4 Default external bridge

外部 skill 接入遵循：

```text
skill installation/discovery
→ registry/profile binding
→ capability-bounded orchestration
→ Beacon normalization/writeback
```

默认桥接约束：

- 官方默认 bridge repository: `https://github.com/Leonxlnx/taste-skill`
- 官方默认 bridge skill: `taste-skill`
- 其余 skill 变体只作为可选 profile，不覆盖默认口径

### 5.5 Stage vocabulary alignment

`project_skills` 的内部 canonical stages 收敛为：

| Canonical Stage | Legacy Aliases | 说明 |
| --- | --- | --- |
| `prototype` | `prototype` | 原型语义与低保真结构冻结前增强 |
| `implement` | `implementation` | 正式实现入口 |
| `qa` | `verify`, `review` | 验收、验证、质量复核 |
| `release` | `delivery` | 发布判定与交付收口 |

要求：

- 新配置优先写 canonical stage
- 历史配置 alias 继续可运行
- 输出、校验和帮助信息优先使用 canonical stage

## 6. 功能要求

| FR ID | Requirement | Acceptance |
| --- | --- | --- |
| FR-001 | Beacon 必须把 `semantic layer` 定义为内建 requirement compile 中间层，而不是外部 skill。 | AC-001 |
| FR-002 | `prototype` 必须在 freeze 前消费 `semantic layer`，先生成官方产品语义，再生成 wireframe freeze。 | AC-002 |
| FR-003 | `implement` 必须复用同一份 `semantic layer`，并允许内部调用默认 `taste-skill` 做受控设计增强。 | AC-003 |
| FR-004 | 外部 design skill 的结果必须先归一化为 Beacon evidence / canonical writeback，不能直接成为真相。 | AC-004 |
| FR-005 | `qa / release` 必须支持 semantic/design consistency gate。 | AC-005 |
| FR-006 | `cli_factory.py` 顶层 help 必须与当前 `7+3` 全局边界一致。 | AC-006 |
| FR-007 | `project_skills.py` 必须采用 `prototype / implement / qa / release` canonical stage vocabulary，并兼容 legacy aliases。 | AC-007 |

## 7. 验收标准

- **AC-001 Semantic Built-in**：Beacon 对需求理解的官方产品语义必须被定义为内建能力，不能要求用户安装外部 skill 才成立。
- **AC-002 Prototype Preflight**：`prototype` 语义编译链中必须存在 semantic preflight 概念，且后续输出可追溯到同一份语义 contract。
- **AC-003 Default Taste Bridge**：`implement` 与 `prototype` 的增强方案里，官方默认外部设计 bridge 明确为 `Leonxlnx/taste-skill` 的 `taste-skill`。
- **AC-004 Canonical Writeback**：外部 skill 结果只能经 Beacon 归一化后写回，不能绕过 canonical / review / gate。
- **AC-005 Semantic Consistency Gate**：`qa / release` 需要把 semantic/design consistency 作为正式检查对象。
- **AC-006 Mainline Alignment**：CLI 顶层帮助文本必须回到 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release + help/status/doctor` 语义，不再暴露旧主线叙事。
- **AC-007 Stage Vocabulary Alignment**：project skill 编排内部必须支持 canonical stage 与 legacy alias 的双向对齐，新逻辑与输出优先采用 `prototype / implement / qa / release`。

## 8. 风险

- 语义层若只做文档，不接 lifecycle，会退化成静态词典。
- design skill 若不做 canonical writeback，会形成“外挂式美化”而不是可审计增强。
- stage 归一化若不兼容旧 profile，会破坏既有项目 skill 配置。
- 顶层 help 若继续保留旧主线叙事，会让后续语义层接入继续漂移。

## 9. Release Guard

- 只有当 semantic layer 边界、默认 taste bridge 口径、canonical stage vocabulary 与 CLI 主流程文案四者一致时，本线才能进入 release 评审。
- 若 QA 或 release 发现语义漂移、stage vocabulary 漂移或 canonical writeback 缺失，必须阻断而不是静默降级。
