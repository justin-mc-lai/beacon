# PRD：Beacon v1.3.5 Prototype Wireframe Mode 与 Prototype Surface 重构

**Feature**: `beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor`  
**Version**: `v1.3.5`  
**Date**: `2026-04-20`  
**Status**: `frozen-pending-implementation`  
**Track**: `main`  
**Scenario**: `tooling_surface`  
**Template**: `并行 PRD / tooling-surface`  

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/v1.3.5/SUMMARY.md`
- Execution index: `docs/beacon/v1.3.5/execution/index.md`
- Existing PRDs in line: none
- Design input: `docs/plans/2026-04-20-prototype-wireframe-mode-design.md`
- Downstream target: `docs/beacon/v1.3.6/prd/beacon-v1-3-6-visual-management-console-and-material-viewer.md`

## 1. 问题

本 PRD 是 `v1.3.5` 的主线，用于先补齐 Beacon `prototype` 子能力的结构性缺口，并冻结 Beacon 管理端看板的 wireframe requirement artifact。

### 1.1 当前断层

Beacon 现有 `prototype` 输出仍然残留“HTML 高保真原型”叙事，这与当前阶段真正需要的“需求冻结用草图”不一致。

具体问题已经很明确：

1. 默认输出完整 HTML/CSS/JS，信息量过重。
2. 原型结果容易被误当成最终视觉要求。
3. 页面跳转说明、页面职责、路由结构没有被清晰冻结。
4. 草图产物与 `prd / user-story / test-case` 之间缺少正式映射。
5. 当前 prototype 结果不好看时，团队会把问题误判为“设计不行”，而不是“阶段产物不对”。
6. 现有独立 `wireframe.py` 命令与 `prototype` 并存，导致同一个阶段出现两套入口、两套目录、两套认知。
7. 当前 wireframe 内容仍偏“结构化模板说明器”，没有稳定完成基于 `prd / user-story / test-case` 的业务闭环推理。
8. 人类面与机器面信息揉杂，缺少明确的分层写入边界，导致阅读与机器消费互相污染。
9. Beacon 已存在多写入点（人类可读文档、机器可读产物、SQLite 运行态），但缺少事务化一致机制，存在跨面漂移风险。

### 1.2 为什么不能继续人工兜底

如果继续依赖人工解释“这个 prototype 只是示意，不是最终 UI”，会持续出现三种漂移：

1. 需求漂移：
   - 高保真细节会反向污染 PRD。
2. 设计漂移：
   - 草图阶段被迫讨论颜色、组件、视觉风格。
3. 实现漂移：
   - 实现团队会拿高保真示意产物当交付标准，而不是把它当结构草图。

这不是审美问题，而是 artifact 定位错误。

### 1.3 本线与下游 `v1.3.6` 的边界

`v1.3.5` 先负责把 Beacon 管理端看板所需的页面、路由和状态说明冻结成 wireframe 包；`v1.3.6` 再消费这些产物进入正式产品化实现。

- `v1.3.5` 负责：
  - `prototype` 只应输出什么类型的草图产物
  - 草图包如何组织
  - 草图包如何与 `prd / user-story / test-case` 对齐
  - Beacon 管理端看板的结构草图冻结
- `v1.3.6` 负责：
  - Beacon 管理端成品 UI
  - 页面展示信息与交互收口
  - 项目物料查看器产品化体验

规则：

> `v1.3.5` 先冻结结构，`v1.3.6` 再产品化实现。

## 2. 目标

### 2.1 主要目标

把 Beacon 现有 `prototype` 子能力重构为“只生成需求冻结用 wireframe 草图包”。

这条线要正式关闭的缺口是：

1. 移除“HTML 高保真原型”在 Beacon 中的正式地位。
2. 把 `prototype` 收口为只生成 wireframe 草图。
3. 冻结页面汇总、路由跳转说明、单页草图、状态说明、平台差异说明。
4. 把 wireframe 包纳入 `prd -> user-story -> test-case` 的 requirement 冻结链。
5. 统一 Beacon 的人类原型入口，不再让 `prototype` 与 `wireframe.py` 形成平行分叉。

### 2.2 非目标

本并行 PRD 不承担以下内容：

- 不定义最终视觉设计系统
- 不定义最终实现组件库
- 不要求当前阶段生成好看的高保真页面
- 不把 wireframe 变成在线编辑器
- 不直接重构 Beacon UI 产品本身的页面字段

### 2.3 命令面 / skill 面一致性目标

`prototype` 子能力必须在命令面、文档面和用户认知面保持一致：

- 用户说“生成原型”时，得到的就是 `wireframe freeze artifact`
- Beacon 文档中不再承诺 HTML 高保真原型
- Beacon 不再把 prototype 解释为视觉稿生成器
- 人类极简命令面新增 `prototype`
- Host-visible skill 新增 `beacon-prototype`
- 旧 `wireframe.py` 退出正式主叙事

## 3. 设计原则

### 3.1 Prototype 必须回到 requirement 冻结阶段

Beacon `prototype` 的默认职责不是生成漂亮页面，而是帮助冻结：

- 页面清单
- 页面职责
- 页面布局块
- 路由跳转
- 状态说明
- 平台差异

### 3.2 Wireframe 是 requirement artifact，不是 design artifact

`wireframe` 产物必须被理解为：

- 需求冻结物
- 结构冻结物
- 交互草图
- 页面关系说明

而不是：

- 最终视觉设计稿
- 营销展示页
- 组件精修稿

### 3.3 文档承诺必须有可达入口

既然 `prototype` 会进入版本包叙事，它就必须具备清晰、稳定、可验证的输出规范。

不能再出现：

- 文档说有 prototype
- 实际输出仍是难以冻结的 HTML 页面
- 用户仍需要人工解释这份产物到底该怎么用

### 3.4 默认模式必须服务最小正确闭环

默认输出必须优先服务：

`prd -> user-story -> test-case -> freeze`

而不是优先服务“看起来更完整”。

### 3.5 Beacon 不再承担高保真原型职责

Beacon `prototype` 只负责 requirement freeze，不再承担：

- HTML 高保真原型
- 视觉模拟稿
- 展示型 demo 页面

### 3.6 Wireframe 必须成为正式主链阶段

本线确认 Beacon 的 requirement closure 从：

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

升级为：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
```

这里的 `prototype` 等于 `wireframe freeze`，它不是设计附属动作，而是 requirement freeze 的正式阶段。

### 3.7 新增 `prototype` 必须是唯一正式原型入口

如果 Beacon 人类极简命令面新增 `prototype`，则必须满足：

- 只有这一条公开原型入口
- 不再保留 `wireframe.py` 作为平行入口
- 不再允许 HTML prototype 与 wireframe 各走各路

规则：

> 要么没有公开原型阶段；要加，就只能加一个统一入口。

### 3.8 人机隔离与多写入点一致性必须是默认能力

`prototype` 既要可读，也要可算，但不能混写。

必须采用三层语义模型：

1. Canonical 语义层（机器唯一真相）：
   - 结构化 canonical envelope（页面、状态流、组件、映射关系）。
2. Human 视图层（人类可读投影）：
   - 由 canonical 渲染出的 Markdown/摘要，禁止手工反写 canonical。
3. Runtime 索引层（SQLite / 投影加速）：
   - 只做查询聚合，不改写 requirement 正式真相。

规则：

- 同一语义先写 canonical，再原子投影到多写入点。
- 任一写入失败，必须整体回滚或标记为未提交。
- 所有写入面都带同一 `projection_seq / source_hash`，防止漂移。

## 4. 范围

### In scope

- 人类极简命令面新增 `prototype`
- Host-visible `beacon-prototype` 子 skill
- `prototype` 收口为 `wireframe`
- `prototype` 输出结构重构
- `wireframe.py` 退役与删除
- 页面汇总文档规范
- 路由跳转说明规范
- 单页草图 Markdown 规范
- 状态变化说明规范
- 平台差异说明规范
- `freeze/review/status` 对 wireframe 的识别
- 与 PRD / user-story / test-case 的映射说明
- 人机分层写入规范（human / machine / sqlite）
- multi-sink 事务型提交与一致性校验
- 跨写入面的 anti-drift 指纹比对

### Out of scope

- 高保真视觉设计生成
- HTML 原型输出
- 自动生成最终前端代码
- 引入外部设计平台作为硬依赖
- 替代后续设计与实现规范

## 5. 功能需求

### FR-001 `prototype` 只保留 `wireframe` 草图模式

当用户执行：

- `beacon prototype plan`
- `beacon prototype create`
- `beacon prototype review`
- `beacon prototype freeze`
- `beacon prototype status`

系统都必须以 `wireframe` 作为唯一正式语义。

要求：

- manifest 中必须显式记录 `prototype_mode: "wireframe"`
- status/review/freeze 必须可识别该模式

### FR-001A 人类主链新增 `prototype` 阶段

Beacon 的人类主链应明确升级为：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
```

要求：

- `prototype` 的语义明确等于 `wireframe freeze`
- 它位于 `test-case` 与 `implement` 之间
- `implement / qa` 不得绕开 `prototype` 直接把页面结构冻结责任吞掉

### FR-001B 必须新增 `beacon-prototype` host-visible 子 skill

Beacon 对外 skill 面必须新增：

- `beacon-prototype`

要求：

- 它是 Beacon 原型阶段的唯一 host-visible 路由
- 它默认解释 `prototype = requirement-driven wireframe freeze`
- 它不得继续沿用 HTML 高保真原型叙事

### FR-001C `wireframe.py` 必须退出正式实现面

现有独立 `wireframe.py` 必须退役。

要求：

- 不再作为正式主流程命令保留
- 不再继续向 `docs/product/...` 输出通用模板
- `wireframe.py` 直接删除，不保留兼容迁移壳层

### FR-002 必须移除 HTML 高保真原型能力与要求

版本文档、命令叙事、子 skill 语义都必须同步调整：

- 不再要求 prototype 产出 HTML 页面
- 不再保留 HTML 作为兼容模式
- 不再把视觉完成度作为 prototype 阶段目标
- 不再把 Beacon 作为高保真原型生成器

说明：

> Beacon 中直接删除 HTML 高保真原型方向，而不是只降级其地位。

### FR-003 Wireframe 输出必须形成冻结包

`wireframe` 模式下的标准输出至少包含：

- `wireframe-summary.md`
- `wireframe-manifest.json`
- `navigation-map.md`
- `navigation-map.json`
- `pages/*.md`
- `freeze.json`
- `prototype-review.json`

要求：

- 所有文件均可版本化
- 所有文件均适合 review
- 所有文件均适合 freeze
- 不依赖 `index.html` 才能成立

### FR-004 `wireframe-summary.md` 必须承担页面汇总职责

汇总文档至少要冻结：

- 页面清单
- 页面名称
- 页面 ID
- 支持平台
- 优先级
- 页面状态
- 页面职责摘要
- 与 PRD / user-story 的关联

### FR-005 `navigation-map` 必须冻结路由与跳转逻辑

必须同时提供：

- 人类可读的跳转图
- 结构化的跳转清单

至少要表达：

- 页面入口
- 页面出口
- 主路径跳转
- 次路径跳转
- 返回路径
- 死路和终点页

### FR-006 单页草图必须使用 Markdown + ASCII 结构

每个页面草图至少包含：

1. 页面定位
2. 页面目标用户
3. 页面回答的问题
4. ASCII 布局草图
5. 元素清单
6. 跳转入口与出口
7. 状态变化

这份单页草图必须优先服务“结构冻结”，而不是“视觉展示”。

### FR-007 必须支持平台差异说明

Wireframe 包必须能标注不同平台变体，例如：

- Web
- PC
- App
- 小程序

即使当前只支持 Web，也必须保留平台差异标注机制，避免未来再次回到 HTML 单平台假设。

### FR-008 必须与 `prd / user-story / test-case` 形成对齐面

Wireframe 包必须显式支持以下映射：

- 该页面来自哪条 PRD 承诺
- 该页面承载哪些 user story
- 该页面对应哪些 test case 场景

要求：

- 不是自由发挥式草图
- 而是 requirement-driven wireframe

### FR-009 `freeze/review/status` 必须围绕 wireframe 语义工作

`prototype freeze` 不应再默认冻结 HTML 页面，而应默认冻结：

- 页面结构
- 页面职责
- 路由逻辑
- 状态说明
- 平台差异

`prototype review` 和 `prototype status` 也必须围绕这些结构性产物工作。

### FR-010 版本文档与 skill 文档必须同步更新

本线落地时，以下文档叙事必须一致：

- `docs/beacon/v1.3.5/*`
- `skills/beacon/SKILL.md`
- 新增 `skills/beacon/beacon-prototype/SKILL.md`

要求：

- 都明确 `prototype` 是主链 requirement freeze 阶段
- 都明确默认 mode 为 `wireframe`
- 都明确 `wireframe.py` 已退役

### FR-011 必须从真实 requirement 生成“闭环型”线框内容

`prototype` 不能只输出固定模板描述，必须用 LLM 对真实 `prd / user-story / test-case` 做闭环推理。

每个页面必须可回答：

- 该页承接哪条业务目标
- 核心状态如何流转（含异常分支）
- 该页包含哪些组件与数据槽位
- 该页动作如何映射到测试场景

要求：

- 模板骨架固定，内容语义动态推理。
- 推理结果必须通过规则校验后才可冻结。

### FR-012 必须冻结页面状态流转（State Flow），而不只是页面跳转

除 `navigation-map` 外，必须新增并冻结：

- `state-flow-map.json`
- `state-flow-map.md`

至少包含：

- 状态节点（state id / label）
- 触发条件（event / guard）
- 迁移边（from -> to）
- 异常回退路径（fallback / recover）
- 与 test-case 场景映射（test refs）

### FR-013 必须冻结页面组件契约（Component Contract）

每个页面必须产出组件说明，至少包含：

- component_id
- 组件职责
- 数据来源（字段或查询）
- 用户动作（interaction）
- 关联状态（state refs）
- 关联 AC / TC / user-story refs

建议输出：

- `component-catalog.json`
- `component-catalog.md`

### FR-014 多写入点必须支持事务型一致提交

`prototype` 写入至少涉及三类目标：

1. 人类面（`wireframe-summary.md`, `pages/*.md` 等）
2. 机器面（`*.json` canonical / map / manifest）
3. Runtime 索引面（SQLite / projection）

要求：

- 以 canonical envelope 作为唯一提交源。
- 采用 `prepare -> validate -> commit -> publish` 提交流程。
- 任一 sink 失败则回滚，或标记事务失败并阻止 freeze。
- 每次提交写入统一事务元数据：
  - `projection_seq`
  - `source_hash`
  - `transaction_id`
  - `committed_at`
  - `sink_checksums`

### FR-015 人机隔离必须在目录与语义层同时成立

要求：

- 人类可读层与机器可读层目录分离，不混排。
- 人类文档禁止承载机器专用字段噪音。
- 机器文档禁止依赖人类描述进行反向解析。
- `status/review` 必须同时报告：
  - human_view_status
  - machine_contract_status
  - sqlite_projection_status
  - drift_status

## 6. 数据 / 状态 / 集成

### 6.1 输入源与 canonical 语义层

wireframe 生成输入应包括：

- feature 名称
- docs version
- 对应 PRD 内容
- 对应 user-story 内容
- 对应 test-case 内容
- 页面/路由补充说明
- 当前 prototype manifest

canonical 输出（机器唯一真相）应包含：

- `prototype-plan.json`
- `page-specs/*.json`
- `navigation-map.json`
- `state-flow-map.json`
- `component-catalog.json`
- `route-closure-contract.json`
- `source-map.json`
- `manifest.json`

### 6.2 三写入点与事务提交

三写入点定义：

1. Human readable sink：
   - `wireframe-summary.md`
   - `navigation-map.md`
   - `state-flow-map.md`
   - `component-catalog.md`
   - `pages/*.md`
2. Machine readable sink：
   - canonical json artifacts
3. Runtime projection sink：
   - SQLite 索引与 projection 镜像

事务流程：

1. `prepare`
   - 读取 requirement 输入并生成 canonical candidate
2. `validate`
   - 校验路由闭环、状态闭环、组件映射完整度
3. `commit`
   - 原子写入 machine sink，并记录事务元数据
4. `publish`
   - 从 canonical 渲染 human sink，并同步 sqlite sink
5. `verify`
   - 校验三面 `source_hash / projection_seq` 一致

### 6.3 输出物

- wireframe summary
- navigation map
- state flow map
- component catalog
- single-page wireframes
- freeze artifacts
- prototype review result
- manifest with mode metadata

### 6.4 演进接口

后续可以继续扩展：

- 对外导出给设计工具的中间格式
- 更适合实现侧消费的页面草图 contract
- 结构化 page spec

但不得重新引入 HTML 高保真原型作为 Beacon 内部标准输出。

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| HTML 模式遗留叙事继续污染默认认知 | 高 | 文档、命令示例、manifest 与实现统一改为 wireframe only |
| 新增 `prototype` 与全局 6 段主流程边界冲突 | 高 | 在 `v1.3.5` 中把它升级为正式 boundary delta，并同步更新 Beacon 全局边界 |
| `prototype` 与 `wireframe.py` 双入口并存 | 高 | 移除 `wireframe.py`，统一 `beacon-prototype` 子 skill 与 `prototype` 命令 |
| wireframe 过于抽象，无法落到实现 | 中 | 强制输出页面清单、跳转、元素、状态、PRD/story/case 映射 |
| 团队继续把视觉细节拉进 prototype 阶段 | 高 | 明确 wireframe 只冻结结构和交互，不冻结视觉 |
| review/freeze 仍以旧 HTML 资产为中心 | 中 | 删除旧 HTML 原型路径，`status/review/freeze` 统一围绕 wireframe artifact 工作 |
| 人类面与机器面混写导致审阅困难 | 高 | 人机目录与字段严格分层，禁止双向污染 |
| 多写入点提交成功率不一致导致漂移 | 高 | 引入事务型多 sink 提交与统一指纹校验 |
| LLM 推理内容与 test-case 不一致 | 高 | 强制 AC/TC 覆盖映射校验，未通过即阻断 freeze |

## 8. 验收标准

### AC-001 `prototype` 不再产出 HTML 高保真原型

用户执行 prototype 相关命令时，得到的必须是 wireframe 语义，而不是 HTML 原型语义。

### AC-005 `prototype` 成为正式人类阶段

人类工作流能够明确表达：

```text
prd -> user-story -> test-case -> prototype -> implement -> qa -> release
```

且 `prototype` 被正式理解为 wireframe freeze，而不是可有可无的设计附件。

### AC-006 `beacon-prototype` 成为唯一 host-visible 原型 skill

Beacon 的对外 skill 面中存在 `beacon-prototype`，并以它承担原型阶段的统一路由。

### AC-007 `wireframe.py` 退出正式流程

仓库内不再存在一个与 `prototype` 平行竞争的人类公开 wireframe 入口；`wireframe.py` 必须被直接删除，不保留兼容迁移壳层。

### AC-002 Wireframe 包可独立完成页面冻结

至少基于一条真实 PRD，能够冻结：

- 页面清单
- 页面职责
- 页面路由
- 页面草图
- 页面状态

不依赖 HTML 页面也能完成需求冻结。

### AC-003 Wireframe 包可接到 user-story / test-case

任一页面都能回答：

- 来自哪条 PRD 承诺
- 对应哪条 user story
- 需要覆盖哪些 test case

### AC-004 与下游产品线不漂移

对于 `v1.3.6` 的 Beacon 管理端主 PRD：

- wireframe 包可以清晰表达其页面结构
- 不会反向篡改主 PRD 的产品定义
- 只承担结构冻结职责

### AC-008 页面状态流必须可验证

`state-flow-map` 必须可回答：

- 每个关键状态如何进入与退出
- 异常时如何回退
- 每条迁移对应哪些 test-case

且 `prototype review` 对状态流缺失必须阻断。

### AC-009 页面组件说明必须可实现接力

每页必须存在组件契约并可映射：

- 组件 -> 状态
- 组件 -> 用户动作
- 组件 -> AC / TC

缺失映射时，`freeze` 不得通过。

### AC-010 三写入点一致性必须可审计

同一轮生成后，human / machine / sqlite 三面必须具备相同：

- `source_hash`
- `projection_seq`
- `transaction_id`

任一面不一致，`status` 必须显示 `drift`，`release` 不得判定通过。

## 9. 成功指标

- 主指标：
  - Beacon `prototype` 被团队统一理解为 requirement wireframe，而不是高保真原型生成器。
- 辅指标：
  - 页面冻结讨论显著减少对颜色、样式、组件细节的无效争论，更多回到页面职责、路由、状态和 requirement 映射。
  - 从 `prd -> user-story -> test-case -> wireframe` 的映射缺口率持续下降。
  - 三写入点一致性检查通过率稳定在 100%（以事务批次计）。

## 10. 与下游产品线的关系

- 下游主线锚点：`beacon-v1-3-6-visual-management-console-and-material-viewer`
- 本 PRD补强的能力：
  - 让下游主 PRD中的页面定义能通过 wireframe 包被稳定冻结和 review
- 回写下游主 PRD的内容：
  - `v1.3.6` 主 PRD应补充“页面实现回链 `v1.3.5` wireframe artifact”这一要求
- 回写 Beacon 全局边界的内容：
  - Beacon 人类主链应升级为包含 `prototype` 的正式 requirement freeze 闭环
- 保持独立冻结的内容：
  - `prototype` wireframe only 规范
  - wireframe 包结构
  - PRD / user-story / test-case 对齐 contract

---

**Created**: 2026-04-20  
**Version**: `v1.3.5`  
**Status**: `frozen-pending-implementation`  
**Memory Context**: N/A
