# Boundaries: Beacon v1.1.3 功能边界收口（vNext）

**版本**: v1.1.3  
**日期**: 2026-03-19  
**状态**: Draft / Requirement Materials Only

---

## 1. 一句话定位

> Beacon 是一个 **evidence-first 的需求交付闭环内核**。  
> 它负责把需求收敛为版本化物料，把测试与验收绑定，把执行证据写回，并基于 gate/release 做可审计放行。

---

## 2. 第一性原则

### 2.1 Beacon 真正解决的问题

Beacon 真正应该解决的是：

1. **需求收敛**：从想法到 user-story / PRD / test-case 的结构化收敛；
2. **证据闭环**：从需求到执行证据到 gate/release 的可追溯链路；
3. **版本治理**：所有结论都落到 `docs/beacon/<version>/`；
4. **放行判断**：什么时候可继续、什么时候必须阻断；
5. **可审计性**：为什么 pass，为什么 blocked，都能回放。

### 2.2 Beacon 不应把自己变成什么

Beacon 不应继续膨胀成：

- 通用 PM 方法论模板大全；
- 通用 agent scheduler / issue orchestrator；
- 浏览器守护进程 / browser automation runtime；
- 生产实现与部署平台；
- “什么都接一点”的自然语言超级入口。

---

## 3. 分层边界

## 3.0 闭环状态机语义（新增）

### 3.0.1 Canonical workflow state model
Beacon 的 canonical workflow 主状态机应收敛为：

- `think`
- `user-story`
- `prd`
- `prototype`（条件阶段）
- `test-case`
- `implementation`（外部执行对齐点）
- `verify`
- `gate`

### 3.0.2 Release 不是 workflow 内部阶段
`release` 应被明确为 **post-gate action**：

- `workflow` 负责把需求和证据收口到 `gate-ready / gate-pass`；
- `release` 负责在 gate 之后处理发布、迁移、回滚、窗口和组织动作；
- 因此 `release` 不应继续被混写成 workflow 内部阶段。

### 3.0.3 Implementation 不是 Beacon 自己承担的业务实现
`implementation` 在 Beacon 中应明确为：

- 与外部执行系统的对齐点；
- 表示“实现已经被触发/对齐/承接”；
- 不等同于 Beacon 自己负责业务代码实现。

### 3.0.4 Doctor / Report / Gate 的职责边界
- `doctor`：诊断结构、版本、物料、环境与契约是否成立；
- `report`：汇总已经存在的事实与证据；
- `gate`：基于规则做阻断/放行判断；
- 三者职责不得继续混写。

### 3.0.5 顶层 `review` 是实现阶段的正式回写动作
Beacon 应新增顶层：

- `review spec`
- `review quality`

其职责应明确为：
- `review spec`：在 implementation 后检查是否需要更新 PRD / User Story / Test Case / Prototype；
- `review quality`：在 verify 后检查是否达到 gate-ready；
- `review` 是 Beacon-native 的实现阶段回写机制，用于借鉴 OPSX 的“fix artifact then continue”，而不是引入新的 spec 框架。

## 3.1 Core Workflow Layer（核心主链）

这是 Beacon 的主叙事与主价值层。

**必须围绕以下命令构建：**

- `think`
- `user-story`
- `prd`
- `prototype`
- `test-case`
- `workflow`
- `auto-test`
- `gate`
- `release`

**职责：**

- 形成需求主链；
- 绑定 AC → TC → Evidence；
- 维护 workflow / gate 的闭环；
- 给出是否放行的最终判断。

## 3.2 Support & Governance Layer（支持治理层）

**支撑 core，但不抢主叙事。**

- `status`
- `report`
- `doctor`
- `feedback`
- `remember`
- `recall`
- `resume`
- `version`
- `evolution-summary`
- `init`
- `test-progress`
- `debug`
- `ask`

**职责：**

- 观测、诊断、总结；
- 写回/检索记忆；
- 版本与闭环追踪；
- 自然语言到 core/support 的薄入口。

## 3.3 Labs Layer（模板/分析扩展层）

**有价值，但不应作为 core 内核的一部分。**

- `analyze`
- `api-design`
- `brainstorm`
- `data-dictionary`
- `design`
- `jtbd`
- `kano`
- `moscow`
- `persona`
- `roadmap`
- `ui-spec`
- `wireframe`

**职责：**

- 提供前置研究与模板化分析；
- 作为外置 skill pack 或 `labs` 命名空间；
- 只在显式调用时参与，不占用 core 心智预算。

## 3.4 Bridge / Experimental Layer（桥接实验层）

- `run`
- `team`
- `ralph-bridge`

**职责：**

- 兼容外部编排、长任务、桥接模式；
- 连接 OMC / OMX / 团队运行时；
- 可参考但不替代专门的 orchestrator 系统。

## 3.5 Deprecated / Merge Layer（废弃/合并层）

- `prompt` → 合并进 `ask`
- `save` → 合并进 workflow memory / remember / resume
- `work` → 保留兼容别名，长期废弃

---

## 4. In Scope（Beacon 负责）

1. 需求主链文档生成与版本化治理；
2. AC → TC → Evidence 的映射与校验；
3. workflow / resume / status 的闭环状态维护；
4. gate / release 的规则阻断与放行；
5. doctor / report / memory 的支持性治理；
6. `docs/beacon/<version>/` 下的可审计交付物。

## 5. Out of Scope（Beacon 不直接负责）

1. 直接写业务代码；
2. 直接修生产事故；
3. 数据库迁移与生产部署执行本身；
4. 浏览器守护进程与 persistent QA runtime；
5. issue tracker 轮询、workspace 调度与 agent scheduler；
6. 在 core 内维护完整 PM 框架模板全集。

---

## 6. 与 gstack / symphony 的边界

## 6.1 与 gstack 的边界

`gstack` 的启发：

- 用少量高价值工作流替代大而全命令集；
- 把真正困难的问题集中到一个硬系统（浏览器 daemon + QA runtime）；
- README 主叙事非常聚焦：Think → Plan → Build → Review → Test → Ship。

**Beacon 应借鉴其收口方式，但不复制其职责。**

Beacon 不负责：

- persistent Chromium daemon；
- `/browse` 这类浏览器原生命令；
- “角色化开发团队”作为主产品。

Beacon 更适合做：

- 规格治理；
- 证据治理；
- gate / release contract；
- 版本化交付主链。

## 6.2 与 symphony 的边界

`symphony` 的定位非常清楚：

- poll issue tracker；
- 为 issue 创建 workspace；
- 启动 coding agent session；
- 管理 retries / observability / reconciliation。

**这是一类 work scheduler / runner。**

Beacon 不应与之正面重叠，不应把 `team/run/bridge` 扩展成核心卖点。  
若 Beacon 需要协同该类系统，应该输出：

- workflow contract；
- gate contract；
- docs/evidence artifacts；
- reason codes / release profile。

---

## 7. 来自 rolo 实战高强度使用的文档治理边界

rolo 这类复杂多服务仓库证明，Beacon 在企业项目里最容易被高强度使用的，不是“模板生成”，而是“版本化交付真相管理”。

因此 v1.1.3 必须把以下 4 点正式下沉为 Beacon 自身的边界要求：

### 7.1 一个发布线只保留一个正式版本根目录

- 一个发布线应只对应一个正式 `docs/beacon/<version>/` 根目录；
- 版本根目录代表发布单元，而不是主题容器；
- 多个并列 `vX.Y.Z-*` 根目录会破坏版本语义，应视为需要收口的结构漂移。

### 7.2 正式交付文档与 raw evidence 强制分层

- 人类决策面只应包含：`SUMMARY / boundaries / prd / user-story / qa/test-cases / release / 必要 architecture`；
- JSON / log / export / xlsx / screenshot 等 raw evidence 必须与正式交付面分层；
- Beacon 不应让执行目录被机器证据淹没，导致“当前版本怎么做、怎么验收、怎么发布”难以快速定位。

### 7.3 每个正式版本包强制满足最小闭环

每个正式版本包至少必须具备：

- `SUMMARY.md`
- `execution/boundaries.md`
- `prd/`
- `user-story/`
- `qa/test-cases/`
- `release/`

缺任一项，都不应视为完整 Beacon workflow 交付包。

### 7.4 `docs/beacon/` 是长期事实源，`.beacon/` 只是运行时临时状态

- 对 docs-heavy 企业项目，长期事实源必须优先读取 `docs/beacon/<version>/`；
- `.beacon/` 的 gate report、raw command log、runtime state 仅是运行时临时状态；
- Beacon 必须明确：当前版本真相入口优先是 `SUMMARY / boundaries / qa / release`，而不是易过期的本地 runtime 快照。

---

## 8. Source of Truth 边界

v1.1.3 继续坚持：

- `docs/beacon/<version>/` 是唯一维护主源；
- `docs/product/<version>/` 不能重新成为人工双写主源；
- 新版 README 也不得再把双写说成当前推荐方案；
- 对企业项目，还必须进一步明确：`docs/beacon/<version>/` 是长期事实源，`.beacon/` 只作为运行时临时状态。

---

## 9. 版本边界

本稿定义的是：

- **v1.1.3 requirement materials draft**

本稿尚未声明：

- 包版本已经升级；
- CLI 实现已完成重构；
- README 已正式替换；
- `SUPPORTED_SUBCOMMANDS` 已完成代码层收口。

即：**先统一边界，再进入实现。**
