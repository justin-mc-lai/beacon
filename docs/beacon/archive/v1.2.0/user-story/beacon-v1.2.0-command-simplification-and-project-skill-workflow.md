# User Story: Beacon v1.2.0 主链简化、项目适配与需求锚定增强

**Feature**: Beacon v1.2.0 - Command Simplification and Project-Skill Workflow Enhancement  
**Version**: v1.2.0  
**Date**: 2026-04-08  
**Status**: Frozen

---

## Epic 概述

作为 Beacon 的使用者和维护者，我希望：

1. 更容易理解和执行 `PRD → user-story → QA` 主链
2. 更容易把这条主链绑定到真实项目的 skill / verify / delivery surface
3. 更容易发现 prototype 与需求之间的漂移

从而让 Beacon 在不扩张核心边界的前提下，变得更易用、更可适配、更少假闭环。

---

## Story 1: 命令简化必须服务主链

### 1.1 作为新用户，我希望一眼看懂 Beacon 的主链入口

**用户角色**: 新用户  
**用户目标**: 快速理解并进入主链

**验收标准**:

- **AC1.1** 默认命令面必须优先暴露与 `PRD → story → QA` 主链最相关的命令
- **AC1.2** `help` 必须基于当前阶段推荐下一步主链动作，而不是只列命令清单
- **AC1.3** `labs` 和低频命令默认隐藏，不抢主链心智
- **AC1.4** 简化命令面不能破坏已有主链命令的向后兼容性

### 1.2 作为高级用户，我希望命令简化不牺牲表达力

**用户角色**: 高级用户  
**用户目标**: 在更少心智负担下继续访问完整能力

**验收标准**:

- **AC2.1** 主链命令保持稳定，不做语义漂移
- **AC2.2** 高级能力可通过显式入口访问，而不是彻底删除
- **AC2.3** 简化后的命令层级必须更清晰地区分 core / support / advanced
- **AC2.4** `help` / `status` 应成为命令路由与阶段导航中心

---

## Story 2: 项目级 skill workflow 必须服务主链落地

### 2.1 作为项目负责人，我希望 Beacon 能更容易发现和绑定项目执行面

**用户角色**: 项目负责人  
**用户目标**: 让项目 skill / profile 更低摩擦接入主链

**验收标准**:

- **AC3.1** 系统应支持根据项目特征推荐合适的 skill/profile 模板
- **AC3.2** 推荐的 skill/profile 必须明确服务于 verify / delivery / debug / pipeline 等项目执行面
- **AC3.3** project skill workflow 不得把项目私有执行逻辑并入 Beacon core
- **AC3.4** 绑定结果必须保留 evidence contract / required cases / capability boundary

### 2.2 作为开发者，我希望能复用项目模板而不是手工搭 workflow

**用户角色**: 开发者  
**用户目标**: 快速拿到项目级 starter packs

**验收标准**:

- **AC4.1** 系统应提供常见项目类型的 skill/profile starter packs
- **AC4.2** starter pack 应明确其适用技术栈和边界
- **AC4.3** starter pack 的目标是缩短项目接入主链的时间，而不是增加新的平台复杂度
- **AC4.4** 模板生成的配置必须可验证、可回滚、可审计

### 2.3 作为 operator，我希望 `skill discover` 走 explainable preview/apply loop

**用户角色**: Operator / Maintainer  
**用户目标**: 在不手工拼配置、不引入黑盒分析的情况下，让项目更快接入主链

**验收标准**:

- **AC4.5** `beacon skill discover` 必须遵循 `detect → recommend → preview → apply`，且默认停在 preview/dry-run
- **AC4.6** discovery 结果必须包含项目特征、推荐模板/skills、评分、理由与证据，而不是只输出模糊分析报告
- **AC4.7** discovery 必须把有界状态写入 `.beacon/state/skill-discovery/<project-or-feature>.json`（或等价契约），且只有显式 apply 才可合并回 `beacon.config.yaml`
- **AC4.8** `help / profile / skill doctor` 必须共用 discovery 结果模型；当项目需要项目级 binding 且尚未完成时，`help` 应显式推荐 `beacon skill discover --project-root .`

---

## Story 3: Prototype 必须继续锚定 PRD 与 Story

### 3.1 作为产品经理，我希望 prototype 不会脱离需求独立漂移

**用户角色**: 产品经理  
**用户目标**: 让 prototype 一直被 `PRD/story` 约束

**验收标准**:

- **AC5.1** 系统必须验证 PRD 中的关键需求点是否在 prototype 中体现
- **AC5.2** 系统必须验证 Story 中的 AC 是否有对应 prototype 页面或状态
- **AC5.3** 若已有 prototype，但 PRD/story 缺少必要 UI 模块信息，系统必须阻断并给出补充模板
- **AC5.4** 若 prototype 存在“有原型无需求”或“有需求无原型”的情况，系统必须显式报告 drift

### 3.2 作为 QA/评审者，我希望 prototype 锚定检查进入正式闭环

**用户角色**: QA / Reviewer  
**用户目标**: 让 prototype 一致性成为正式可检查合同

**验收标准**:

- **AC6.1** prototype 锚定检查结果应进入 review/gate 可消费的 artifact
- **AC6.2** prototype 锚定检查不能替代 `PRD → story → QA` 主链，只能作为其约束补强
- **AC6.3** prototype 覆盖率报告必须能追溯到 PRD/story
- **AC6.4** prototype 检查失败时，系统必须给出明确修复方向

---

## Story 4: v1.2.0 必须明确锚点合同

### 4.1 作为 Beacon 维护者，我希望 v1.2.0 的主目标不再模糊

**用户角色**: Beacon 维护者  
**用户目标**: 防止 `v1.2.0` 变成宽而散的 enhancement release

**验收标准**:

- **AC7.1** `v1.2.0` 文档必须明确声明 `PRD → story → QA` 是唯一主链锚点
- **AC7.2** 命令简化、项目 skill workflow、prototype anchoring 必须被表达为 subordinate workstreams
- **AC7.3** `v1.2.0` 应新增或明确：
  - `PRD-story-QA anchor contract`
  - `story-QA baseline bundle`
  - `coverage scorecard contract`
- **AC7.4** 所有高级能力面必须证明它们如何服务主链，而不是脱离主链单独扩张

---

## Story 5: QA auto harness 必须受主链约束

### 5.1 作为 Beacon 维护者，我希望 `qa auto harness` 只优化故事型 QA，而不变成通用自迭代平台

**用户角色**: Beacon 维护者  
**用户目标**: 在不破坏主链的前提下，让 QA 质量可以被受控迭代

**验收标准**:

- **AC8.1** `qa auto harness` 必须显式声明其唯一目标是改进 story-native QA，而不是优化 Beacon 任意产品面
- **AC8.2** `qa auto harness` 的输入必须锚定在：
  - `PRD`
  - `user-story`
  - `AC matrix`
  - `scenario map`
  - `QA9 matrix`
  - `coverage / evidence scorecard`
- **AC8.3** `qa auto harness` 只允许修改 bounded QA policy surfaces，例如：
  - story scenario expansion
  - coverage threshold
  - evidence sufficiency
  - continue / stop-for-repair policy
- **AC8.4** `qa auto harness` 明确禁止修改：
  - project-specific execution commands
  - release verdict override
  - arbitrary repo-wide product surfaces
  - memory/knowledge plane as a separate center

### 5.2 作为 QA/评审者，我希望 harness 的每次迭代都有可核验结果

**用户角色**: QA / Reviewer  
**用户目标**: 让 QA 自迭代不是“感觉更好”，而是“证据更强”

**验收标准**:

- **AC9.1** 每次 harness 运行必须输出：
  - changed QA policy surface
  - affected stories / ACs
  - coverage delta
  - evidence closure delta
  - false-complete delta
  - keep/discard verdict
- **AC9.2** harness 成功标准必须继续围绕：
  - PRD-to-story fidelity
  - story coverage
  - AC coverage
  - scenario-family coverage
  - evidence completeness
  - false-complete reduction
- **AC9.3** story-QA baseline bundle 应被定义为 harness 的必要前置条件
- **AC9.4** harness 不能绕过 review / gate，而只能为 review / gate 提供更强输入


---

## Formal AC Matrix

This table is the machine-readable AC anchor for the frozen v1.2.0 requirement package.

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Mainline Command Surface | 默认命令面必须优先暴露 `PRD → story → QA` 主链入口，且不破坏主链向后兼容性 |
| AC-002 | Help Routing | `help / status` 必须成为主链阶段路由中心，而不是只展示命令清单 |
| AC-003 | Advanced Surface Disclosure | 低频或高级能力默认降噪，但仍保留显式入口，不得删除专家路径 |
| AC-004 | Project Skill Recommendation | 系统必须根据项目特征推荐服务于 verify / delivery / debug / pipeline 的 skill/profile |
| AC-005 | Starter Pack Boundary | starter packs 必须声明适用技术栈、边界，并保持 capability / evidence / required-cases 合同 |
| AC-006 | Discover Preview Flow | `beacon skill discover` 必须遵循 `detect → recommend → preview → apply`，且默认停在 preview/dry-run |
| AC-007 | Discover Explainability | discovery 结果必须包含项目特征、推荐模板/skills、评分、理由与证据 |
| AC-008 | Discover Shared State | discovery 必须写出有界状态 artifact，并被 `help / profile / skill doctor` 共用 |
| AC-009 | Prototype Forward Anchor | PRD/story 的关键需求点必须能映射到 prototype 页面或状态 |
| AC-010 | Prototype Reverse Anchor | orphan prototype / orphan requirement / UI 模块缺失必须被显式检测并给出修复方向 |
| AC-011 | Mainline Anchor Contract | `v1.2.0` 文档必须明确 `PRD → story → QA` 是唯一主链锚点，其他工作流均为 subordinate workstreams |
| AC-012 | Story-QA Baseline Bundle | `PRD + story + .machine/user-story + QA markdown + AC matrix + scenario map + QA9 matrix + coverage/evidence scorecard` 必须被定义为固定 bundle |
| AC-013 | QA Auto Harness Inputs | `qa auto harness` 只能消费 baseline bundle，不得自建 benchmark target |
| AC-014 | QA Auto Harness Boundaries | harness 只能迭代 bounded QA policy surfaces，并输出 coverage/evidence/false-complete delta 与 keep/discard verdict |
| AC-015 | Requirement Freeze Closure | 当前 requirement package 必须可生成 machine baseline bundle、完成 freeze，并清晰说明“冻结的是需求包，不是已实现代码” |
| AC-016 | Smart Entry Routing | `ask / help` 必须承担更强的主链命令推荐职责，而不是只做静态说明 |
| AC-017 | Progressive Disclosure | default visible command surface 必须优先主链，advanced / labs surfaces 通过显式 disclosure 暴露 |
| AC-018 | Architecture Guardrails | `v1.2.0` 必须显式保持四层架构边界，并避免把 agent-platform rewrite 变成当前中心 |
| AC-019 | Deferred Generic Discover | 泛化 `beacon discover` 代码分析能力必须被标记为未来 advanced/labs 方向，而不是当前主链冻结交付 |
| AC-020 | Research Convergence | 三份 April 8 深度调研的结论必须被吸收到 versioned requirement package，并映射到 execution / source-architecture / QA contracts |
