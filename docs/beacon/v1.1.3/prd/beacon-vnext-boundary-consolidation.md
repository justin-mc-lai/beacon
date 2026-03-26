# PRD: Beacon vNext 边界收口、命令收口与 CLI 分层重构（v1.1.3）

## 1. 目标

在 v1.1.3 先完成 Beacon 的文档级收口与架构级收口，形成一套能指导后续代码重构的统一口径，确保：

1. Beacon 的产品定义重新聚焦到需求交付闭环。
2. 命令表面从“混合式命令堆积”转向“分层明确的 CLI”。
3. README 主叙事回到当前版本、当前边界与当前验证方式。
4. 后续实现层收口有可执行的保留 / 迁出 / 废弃清单。
5. 当前阶段是需求草稿阶段，需把“必须先做 / 其次再做”的实施顺序冻结下来，避免实现期发散。

## 2. 背景

当前 Beacon 已经具备较强的主链能力：

`think -> user-story -> prd -> [prototype] -> test-case -> workflow -> auto-test -> gate -> release`

但从当前实现看仍存在四类问题：

1. **命令表面过宽**：当前 `SUPPORTED_SUBCOMMANDS` 共 **40** 个子命令，核心闭环命令与模板型命令、bridge 型命令长期混写。
2. **主源口径未完全收口**：README 已声明 `docs/beacon/<version>/` 为唯一主源，但部分命令与兼容逻辑仍残留 `docs/product/` 双写路径。
3. **NL 路由过宽**：当前 `intent_router` 默认覆盖大量模板型意图，使 Beacon 继续向“什么都接一点”的方向发散。
4. **外部边界重叠风险**：与 `gstack` 的浏览器/角色化工作流、与 `symphony` 的 work scheduler/runner 已出现概念相邻。
5. **版本根目录语义易漂移**：复杂企业项目里，如果一个发布线对应多个 `vX.Y.Z-*` 根目录，版本就会退化为主题容器。
6. **正式交付面与 raw evidence 容易混层**：execution 一旦同时容纳大量 JSON / log / export，会快速淹没人类决策文档。
7. **最小闭环约束缺失时，版本包会退化成按需堆文档**：出现缺 `qa/test-cases` 或缺 `execution/boundaries.md` 的“半闭环版本包”。
8. **runtime 状态容易冒充长期真相**：在 docs-heavy 企业项目中，`.beacon` 往往先过期，而 `docs/beacon/` 才是持续维护的真实交付面。
9. **闭环状态机不是单一真相**：workflow / gate / release 的边界语义仍未完全统一。
10. **implementation 阶段语义模糊**：当前更像元命令对齐点，而不是被清晰定义的阶段职责。
11. **doctor / report / gate 职责还未完全产品化**：诊断、汇总、阻断之间仍存在交叉。
12. **实现阶段缺少顶层 review 回写机制**：当前还不能把“实现中发现规格偏差 -> 回写物料 -> 继续推进”做成正式流程。

## 3. 第一性原则

### 3.1 用户真正购买什么

用户真正购买的不是“更多模板”，而是：

- 需求如何收敛；
- 需求如何变成可审计物料；
- 测试如何绑定到验收标准；
- 什么情况下可以 gate / release；
- 全部过程如何回放、追责、复盘。

### 3.2 Beacon 应解决的核心问题

Beacon 应解决：

1. **需求建模**：think / user-story / prd / prototype / test-case。
2. **证据治理**：auto-test / report / memory / manifest / consistency。
3. **闭环编排**：workflow / resume / status。
4. **放行判断**：gate / release / doctor。

### 3.3 Beacon 不应优先解决的问题

Beacon 不应优先解决：

- PM 框架模板全集；
- 通用多代理调度器；
- 浏览器守护进程 / persistent QA runtime；
- issue tracker daemon / workspace scheduler；
- 生产代码实现与生产部署本身。

## 4. 产品定位

### 4.1 Beacon vNext 定位

> Beacon 是一个 **evidence-first 的需求交付闭环内核**。  
> 它负责版本化需求物料、测试映射、执行证据、gate/release 判定与可审计追踪。

### 4.2 与外部系统的边界

| 系统 | 核心职责 | Beacon 关系 |
|------|----------|-------------|
| Beacon | 需求闭环、证据、gate、release | 本体 |
| gstack | 角色化开发流程 + 浏览器 QA runtime | Beacon 可参考其流程设计，但不复制其浏览器/QA 守护进程 |
| symphony | issue tracker 轮询、workspace 生命周期、agent runner | Beacon 可输出 workflow contract，但不承担 scheduler 职责 |

## 5. 范围

### In Scope

1. 产出 Beacon vNext 功能边界文档。
2. 产出覆盖 40 个命令的命令收口清单。
3. 产出根 README 重写草案。
4. 产出 CLI 分层重构方案。
5. 统一 v1.1.3 文档落盘到 `docs/beacon/v1.1.3/`。
6. 给出 retain / migrate / deprecate 的目标方向与兼容策略。
7. 把来自真实企业项目的 4 个文档治理改进点正式纳入 Beacon 需求物料。

### Out of Scope

1. 本版不直接修改 `pyproject.toml` 与运行时版本号。
2. 本版不直接删除现有命令实现。
3. 本版不直接实现 `beacon labs` / `beacon bridge` 新命名空间。
4. 本版不直接替换 `gstack` 浏览器能力或实现 `symphony` 调度能力。
5. 本版不新增新的 PM 模板型命令。
6. 本版不要求与文档同步完成代码实现；当前未实现是需求草稿阶段的正常状态。

## 6. 功能需求

### FR-001 功能边界文档

必须产出 `execution/boundaries.md`，明确：

- Beacon vNext 定位；
- 第一性原则；
- In Scope / Out of Scope；
- core / support / labs / bridge 边界；
- 与 gstack / symphony 的边界；
- `docs/beacon/<version>/` 单一事实源约束。

### FR-002 命令收口清单

必须产出 `execution/command-consolidation-matrix.md`，覆盖当前 40 个子命令，并为每个命令给出：

- 当前角色；
- 建议状态（保留 / 迁出 / 废弃）；
- 目标层级；
- 收口原因；
- 兼容处理方式。

### FR-003 README 重写草案

必须产出 `execution/readme-rewrite-draft.md`，草案仅保留五类信息：

1. 当前版本是什么；
2. 当前能力边界；
3. 当前推荐命令；
4. 当前交付工件；
5. 当前验证命令。

### FR-004 CLI 分层方案

必须产出 `execution/cli-layering-refactor-plan.md`，说明：

- 命令如何分层；
- `command_catalog` 如何按层拆分；
- `cli_factory` 如何按层注册；
- `intent_router` 如何收窄默认意图；
- `labs` / `bridge` 如何迁移出默认叙事。

### FR-005 Core Command Target

文档必须明确 Beacon core 目标命令表面围绕以下能力：

- `think`
- `user-story`
- `prd`
- `prototype`
- `test-case`
- `workflow`
- `auto-test`
- `gate`
- `release`

### FR-006 Support Command Target

文档必须明确 support 层围绕：

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

### FR-007 Labs Command Target

下列模板型命令不应继续作为 Beacon 核心卖点，必须标记为 labs/external pack 候选：

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

### FR-008 Bridge Command Target

下列命令必须标记为 bridge / experimental：

- `run`
- `team`
- `ralph-bridge`

### FR-009 Deprecated Target

下列命令应被纳入废弃/合并路径：

- `prompt`（收敛到 `ask`）
- `save`（收敛到 workflow memory / remember / resume）
- `work`（仅作为 `workflow start` 的兼容别名）

### FR-010 单一事实源

本版新增文档与未来 README 草案不得重新引入 `docs/product/<version>/` 作为人工维护主源。

### FR-012 一个发布线只保留一个正式版本根目录

文档必须正式定义：

- 一个发布线应只对应一个正式 `docs/beacon/<version>/` 根目录；
- 版本根目录代表发布单元，不能再同时承担主题容器语义；
- 出现多个并列 `vX.Y.Z-*` 根目录时，应视为需要收口的文档结构漂移。

### FR-013 正式交付文档与 raw evidence 强制分层

文档必须正式定义：

- 人类决策面与机器证据面分层；
- `SUMMARY / boundaries / prd / user-story / qa/test-cases / release / 必要 architecture` 构成正式交付面；
- JSON / log / export / xlsx / screenshot 等 raw evidence 不应继续与正式交付面混层。

### FR-014 每个正式版本包强制满足最小闭环

文档必须明确每个正式版本包至少具备：

- `SUMMARY.md`
- `execution/boundaries.md`
- `prd/`
- `user-story/`
- `qa/test-cases/`
- `release/`

缺任一项，都不应视为完整 Beacon workflow 交付包。

### FR-015 `docs/beacon/` 是长期事实源，`.beacon/` 只是运行时临时状态

文档必须明确：

- 对 docs-heavy 企业项目，长期事实源优先是 `docs/beacon/<version>/`；
- `.beacon/` 中的 gate report、raw command log、runtime state 只作为运行时临时状态；
- 当前版本真相入口优先读取 `SUMMARY / boundaries / qa / release`。

### FR-016 实施阶段必须冻结为“必须先做 / 其次再做”

文档必须明确并记录以下实施顺序：

#### 必须先做
1. 彻底去掉 `docs/product` 主路径语义
2. 把最小闭环变成 `init / doctor / gate / report` 的代码规则
3. 把版本根目录语义做成可检查的治理规则
4. 把 formal docs vs raw evidence 做成明确目录契约
5. 真正收口 CLI surface
6. 真正收口 NL router
7. 把 `docs/beacon > .beacon` 的长期事实源优先级写进状态系统

#### 其次再做
8. 补“代码迁移矩阵”
9. 同步 `README / SKILL / AGENTS / help / reason codes`
10. 再考虑 active version index 之类增强项

### FR-018 Canonical workflow state model 必须唯一

文档必须明确：

- Beacon 只有一套 canonical workflow 主状态机；
- canonical stage model 应收敛为：
  - `think`
  - `user-story`
  - `prd`
  - `prototype`（条件阶段）
  - `test-case`
  - `implementation`（外部执行对齐点）
  - `verify`
  - `gate`

### FR-019 `release` 必须定义为 post-gate action

文档必须明确：

- `release` 不属于 workflow 主状态机；
- `release` 是 gate 通过后的发布/迁移/回滚/组织动作；
- workflow 的终点是 `gate-ready / gate-pass`，而不是 release 本身。

### FR-020 `implementation` 阶段语义必须明确

文档必须明确：

- `implementation` 是外部执行承接/对齐点；
- Beacon 不直接承担业务代码实现；
- `implementation` 的存在是为了在主链中表达“实现已被承接”，而不是把 Beacon 变成执行平台。

### FR-022 顶层 `review spec|quality` 必须新增

文档必须明确 Beacon 应新增顶层：

- `review spec <feature>`
- `review quality <feature>`

### FR-023 `review spec` 必须承接实现阶段的规格回写

文档必须明确：

- `review spec` 在 implementation 之后执行；
- 检查 PRD / User Story / Test Case / Prototype 是否因实现而产生 drift；
- 若存在偏差，应输出需要更新的正式物料与回写建议；
- 这是 Beacon-native 的实现阶段 review，不是 memory 辅助动作。

### FR-024 `review quality` 必须承接 verify 之后的质量审查

文档必须明确：

- `review quality` 在 verify 之后执行；
- 检查是否达到 gate-ready；
- 输出 quality review 结论，供 gate 消费。

### FR-025 Beacon 借 OPSX 的机制，不借 OpenSpec 的 change-folder 结构

文档必须明确：

- Beacon 借鉴的是 OPSX 的“fix artifact then continue”机制；
- Beacon 不引入 OpenSpec 的 `changes/` / delta specs 结构；
- Review 结果继续沉淀在 `docs/beacon/<version>/execution/` 体系内。

### FR-021 `doctor / report / gate` 职责边界必须正式化

文档必须明确：

- `doctor`：结构/版本/物料/环境/契约诊断；
- `report`：对既有事实和证据做汇总；
- `gate`：基于规则阻断或放行；
- 三者职责不得继续混写。

### FR-017 当前阶段记录必须明确“需求草稿、未实现正常”

文档必须明确：

- v1.1.3 当前属于 **requirement materials draft**；
- 与 v1.1.2 代码实现仍存在差距是正常现象；
- 当前阶段的验收重点是“问题定义、边界冻结、优先级排序、实施顺序明确”，而不是“功能已完成”。

### FR-011 文档版与运行时版边界

文档必须明确：本次是 v1.1.3 requirement materials draft；是否升级实际包版本，需要后续实现期再统一变更：

- `pyproject.toml`
- `beacon/__init__.py`
- `SKILL.md`
- `AGENTS.md`
- `README.md`

## 7. 非功能要求

### 清晰性
- 每一份文档必须能独立回答“为什么要收口”。

### 可执行性
- 文档必须能直接转化为后续代码重构 backlog。

### 一致性
- 所有新增物料路径统一位于 `docs/beacon/v1.1.3/`。

### 可审计性
- 命令收口矩阵必须覆盖 40 个命令，不能只列举示例。

## 8. 当前阶段记录（新增）

### 8.1 当前阶段
- 当前 `v1.1.3` 仍属于：**需求草稿阶段 / requirement materials draft**
- 当前目标是把代码改造主线与实施优先级冻结下来

### 8.2 为什么“未实现”在当前阶段是正常的
- 文档稿先行，本来就允许实现滞后
- 只要问题、边界、顺序没有冻结，直接进入实现反而会扩大漂移
- 因此 v1.1.3 当前更应该被理解为“实施前收口版”，不是“功能已完成版”

### 8.3 当前阶段的正确验收标准
- 是否明确了必须先做的 7 条主线
- 是否明确了其次再做的 3 条后续项
- 是否把“未实现是正常的”记录进正式需求物料

- 是否明确 workflow / release / implementation / doctor-report-gate 的职责边界

## 9. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 只出文档不做实现，后续再次漂移 | 高 | 在 CLI 分层方案中给出 phased rollout |
| 迁出命令过多引发兼容性阻力 | 高 | 明确保留兼容别名与过渡期 |
| README 草案与当前 runtime 版本冲突 | 中 | 明确标记“草案，不代表已发布包版本” |
| 对 gstack / symphony 的借鉴不清晰 | 中 | 在边界文档中单独设比较章节 |

## 10. 成功指标（目标）

- 默认用户心智中的 Beacon 核心命令表面收敛到 **9 个主链命令 + 10~13 个 support 命令**。
- 默认自然语言路由意图从当前大表面收敛到 **core/support 优先**。
- 新版 README 不再把模板型命令当作主卖点。
- `docs/beacon/<version>/` 继续成为唯一维护主源。
- 企业项目使用 Beacon 时，版本根目录、正式文档分层、最小闭环与长期事实源边界不再漂移。
- workflow / release / implementation / doctor / report / gate 的闭环语义不再互相打架。
- Beacon 在实现阶段具备正式 `review spec|quality` 回写闭环，而不是只依赖 feedback/memory。

## 11. 交付物

- `docs/beacon/v1.1.3/execution/boundaries.md`
- `docs/beacon/v1.1.3/execution/command-consolidation-matrix.md`
- `docs/beacon/v1.1.3/execution/readme-rewrite-draft.md`
- `docs/beacon/v1.1.3/execution/cli-layering-refactor-plan.md`
- `docs/beacon/v1.1.3/user-story/beacon-vnext-boundary-consolidation.md`
- `docs/beacon/v1.1.3/qa/test-cases/beacon-vnext-boundary-consolidation.md`
- `docs/beacon/v1.1.3/qa/test-cases/beacon-vnext-boundary-consolidation.ac-test-matrix.json`
