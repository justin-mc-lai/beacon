# PRD: Beacon init 渐进式披露、技术架构主文档与版本演进蓝图（v1.1.8）

## 1. 背景

当前 `beacon init` 已具备：

- 初始化 `docs/beacon/<version>/` 目录
- 初始化 `SUMMARY / release / boundaries / index`
- 初始化 `CLAUDE.md / AGENTS.md` 的 Beacon managed block

这套机制解决的是“项目如何进入 Beacon 体系”。

但它还**没有真正回答项目级技术使用入口的问题**：

1. 新项目（greenfield）初始化后，技术应该先看什么？
2. 二开接手项目（takeover）初始化后，技术如何快速建立系统全貌认知？
3. `AGENTS.md` 主入口里，Beacon 应该如何做渐进式披露，避免 agent/技术一下子掉进细节里？
4. 项目是否应有一份技术架构主文档和版本演进蓝图，作为后续实现、验收、接手的对照面？

### 1.1 必须区分“项目 docs version”和“Beacon runtime version”

这是这条设计线的关键约束之一：

- **项目 docs version**
  - 决定写到哪个 `docs/beacon/<version>/`
  - 应该跟随项目自身的业务/交付版本线

- **Beacon runtime version**
  - 决定 `AGENTS.md / CLAUDE.md` 中 Beacon managed guidance 的版本标记
  - 应该跟随当前安装/使用的 Beacon 工具版本

两者不能混为一谈。

否则会出现错误场景：

- 用户只是想用最新 Beacon `v1.1.8` 初始化一个老项目
- 结果系统错误地在项目里创建了 `docs/beacon/archive/v1.1.8/`
- 但这个 `v1.1.8` 并不是项目自己的业务版本

所以 v1.1.8 必须明确支持：

- `--version`：项目 docs version
- `--runtime-version`：Beacon runtime version

## 2. 第一性原理结论

### 2.1 init 不只是“建目录”

如果 Beacon 要成为长期工作流内核，`init` 的职责不能只停留在：
- 建 docs 目录
- 写 managed block

它还应成为：
- **项目级主入口构建器**
- **技术阅读顺序定义器**
- **架构蓝图初始落盘器**
- **生命周期接管基线初始化器**
- **项目版本线与 Beacon 运行时版本的分离器**

### 2.2 AGENTS.md 主入口需要渐进式披露

当前 `context_files.py` 里的 `build_agents_guidance_body()` 仍偏最小 guidance：
- 用 docs/beacon/<version>
- 优先看 prd/user-story/qa/execution

但对技术和 agent 来说，仍缺少“先看什么、后看什么”的递进式主入口。

Beacon 应明确：

1. `SUMMARY.md` —— 先看整体
2. `execution/index.md` —— 再看导航
3. `execution/architecture-blueprint.md` —— 再看系统结构
4. `prd / user-story / qa` —— 再看需求细节
5. `.machine` —— 最后才看 machine truth

这就是渐进式披露。

### 2.3 项目必须有技术架构主文档

对于技术而言，至少需要两类主文档：

1. **技术架构蓝图**
   - 当前系统长什么样
   - 模块怎么分
   - 数据/服务/依赖/运行时边界是什么

2. **版本演进蓝图**
   - 当前版本相对上一版本新增了什么能力
   - 哪些能力是 planned / implemented / deprecated
   - 未来演进如何递进

### 2.4 init 的最终角色应升级为 Project Lifecycle Onboarding

如果 Beacon 想进一步接管项目开发，`init` 的最终角色不能只是 bootstrap，而应升级为：

> **Project Lifecycle Onboarding**

它初始化的不只是目录和 managed block，还应初始化：

1. **认知入口**
   - 技术/agent 先看什么、后看什么
2. **架构入口**
   - architecture blueprint
   - version evolution blueprint
   - implementation archive index
3. **生命周期接管状态**
   - 当前项目被 Beacon 接管到什么深度
   - 哪些 stage 已启用
   - 下一步建议接管什么

### 2.5 需要“接管级别”概念来表达 Beacon 的接手深度

建议新增：

- `lifecycle_adoption_level`

可参考：

- `0 = context_only`
- `1 = docs_managed`
- `2 = architecture_managed`
- `3 = implementation_managed`
- `4 = qa_gate_managed`
- `5 = full_lifecycle_managed`

这样 Beacon 才能回答：

> 这个项目只是“初始化过”，还是已经进入 Beacon 生命周期接管。

## 3. 目标

1. **让 init 为项目生成更强的技术主入口**
2. **让 AGENTS.md / CLAUDE.md 中的 Beacon guidance 具备渐进式披露能力**
3. **让 greenfield / takeover 两类项目都能得到合适的技术架构主文档**
4. **让版本演进蓝图成为后续实现/接手/复盘的稳定对照面**
5. **保持 init 与 doctor/context 管理兼容，不破坏已有 managed block 机制**
6. **让 init 成为 Beacon 生命周期接管项目开发的正式起点**

## 4. 非目标

1. 不要求 init 自动逆向出完整架构图；
2. 不要求 v1.1.8 自动分析所有代码依赖并填满蓝图；
3. 不把 AGENTS.md 变成超长百科全书；
4. 不替代项目真实架构设计评审；
5. 不在 v1.1.8 宣称 greenfield/takeover 自动识别都已实现。

## 5. 核心设计

## 5.1 init 模式区分

建议 `init` 支持：

- `--project-mode greenfield`
- `--project-mode takeover`

## 5.1.1 版本语义分离

建议 `init` 支持：

- `--version <docs_version>`
- `--runtime-version <beacon_runtime_version>`

默认规则：

- `--version auto`
  - 解析项目已有 `docs/beacon/` 的最新项目版本线
- `--runtime-version`
  - 默认使用当前 Beacon toolkit version

例如：

```bash
python3 -m beacon.main init \
  --project /path/to/project \
  --version auto \
  --runtime-version v1.1.8 \
  --project-mode takeover \
  --apply
```

其含义应是：

- 文档落到项目自己的版本线
- context guidance 使用 Beacon `v1.1.8`

## 5.1.2 版本解析与导航必须全链路使用双解析器

除了 `init`，v1.1.8 还必须把版本语义推进到运行期：

- `resolve_docs_version()`
  - 只负责解析项目 docs line
  - `auto` 优先读取 `.beacon/state/project-onboarding.json.docs_version`

- `resolve_runtime_version()`
  - 只负责解析 Beacon runtime line
  - 默认跟随当前 Beacon toolkit version

兼容别名：

- `resolve_target_version()`
  - 仍保留
  - 但内部必须等价于 `resolve_docs_version()`

这样才能确保：

- 后续 `status/help/workflow/...` 不会再因为误扫到某个 runtime 同名目录而漂移
- docs line 与 runtime line 可以独立演进

## 5.1.3 status / help / doctor 必须显式输出双版本

以下导航面必须同时展示：

- `docs_version`
- `runtime_version`
- `context_managed_version`

原因是 Beacon 需要回答：

- 当前我在操作哪条项目 docs 线？
- 当前我运行的是哪条 Beacon runtime 线？
- 当前项目的 managed context marker 写入的是哪条线？

## 5.1.4 doctor 必须有版本分离漂移检查

doctor 需要新增至少以下能力：

- 检查 onboarding 中 `docs_version` / `runtime_version` 是否完整
- 检查 context managed marker 是否与 runtime 线一致
- 检查是否出现“runtime 同名 docs root”误建
- 检查 docs line 与 runtime line 是否再次被混用

这类问题应作为兼容性诊断的一等问题，而不是只靠人工发现

### Greenfield
适合：
- 新项目
- 初次引入 Beacon

重点文档：
- architecture blueprint skeleton
- version evolution blueprint skeleton
- AGENTS 渐进式披露主入口

### Takeover
适合：
- 老项目二开
- 团队接手维护

重点文档：
- architecture current-state doc
- bounded context / service map
- known debt / constraints
- version evolution timeline

## 5.2 新增技术主文档

建议 init 后至少生成：

```text
docs/beacon/<version>/execution/
├── architecture-blueprint.md
├── version-evolution-blueprint.md
├── project-lifecycle-onboarding.md
├── implementation-archive-index.md
└── boundaries.md
```

### `architecture-blueprint.md`
至少包含：
- 系统定位
- 分层结构
- 模块/服务图
- 数据流 / 调用链
- 外部依赖
- 数据库/缓存/队列
- 部署环境
- 边界与约束

### `version-evolution-blueprint.md`
至少包含：
- 当前版本定位
- 与前一版本差异
- planned / implemented / deprecated capability map
- 演进顺序
- 接下来的关键里程碑

### `implementation-archive-index.md`
至少包含：
- 当前版本下的 implement 技术归档入口索引
- 按 feature 列出 technical-implementation docs

### `project-lifecycle-onboarding.md`
至少包含：
- `docs_version`
- `runtime_version`
- 当前项目模式（greenfield / takeover）
- 当前接管级别
- 已启用的 Beacon stage
- 推荐阅读顺序
- 推荐下一步
- 对人和对 agent 的主入口说明

## 5.3 AGENTS.md 中的渐进式披露

`build_agents_guidance_body()` 应从“最小命令提示”升级为主入口阅读顺序提示，至少明确：

- 先看 `SUMMARY.md`
- 再看 `execution/index.md`
- 再看 `execution/architecture-blueprint.md`
- 再看 `prd / user-story / qa`
- 最后看 `.machine`

并区分：
- 初始项目阅读方式
- 接手项目阅读方式

## 5.4 init 必须落盘生命周期接管状态

建议新增：

```text
.beacon/state/project-onboarding.json
```

最小字段：

- `project_mode`
- `lifecycle_adoption_level`
- `docs_version`
- `runtime_version`
- `architecture_blueprint_ready`
- `version_blueprint_ready`
- `implementation_archive_enabled`
- `qa_managed`
- `gate_managed`
- `next_recommended_stage`

## 5.5 技术架构蓝图必须可递进演进

不能每个版本重写成孤岛。

建议结构：
- 当前版 blueprint
- 上一版对照
- capability delta
- 演进时间线

这能让技术接手时快速知道：
- 这版到底比上一版多了什么
- 哪些东西还只是 planned

## 5.6 init 未来应支持递进式模式，而不是一次性命令

从长期看，init 至少应兼容这些使用姿态：

- 轻量初始化：只建基础骨架
- 架构增强初始化：补 architecture / evolution / onboarding
- takeover 初始化：补 current-state / debt / service map / timeline
- 生命周期接管初始化：补 adoption state 与阶段启用状态

## 6. 功能需求

### FR-001 init 支持项目模式语义

init 设计上必须支持 greenfield / takeover 两类模式。

### FR-002 init 必须区分 docs version 与 runtime version

设计上必须支持：

- `--version` 只控制项目文档版本线
- `--runtime-version` 只控制 Beacon managed runtime guidance 版本

### FR-003 init 生成技术架构蓝图主文档

至少生成：
- `execution/architecture-blueprint.md`
- `execution/version-evolution-blueprint.md`

### FR-004 init 生成 implement 技术归档索引

至少生成：
- `execution/implementation-archive-index.md`

### FR-005 init 生成 lifecycle onboarding 文档

至少生成：
- `execution/project-lifecycle-onboarding.md`

### FR-006 AGENTS 主入口补齐渐进式披露

managed AGENTS block 必须明确技术/agent 的推荐阅读顺序。

### FR-007 AGENTS 主入口区分 greenfield / takeover

同一套 Beacon guidance 中应给出两类项目的不同入口建议。

### FR-008 architecture blueprint 必须适合技术查看

文档必须是技术可消费的，不是纯产品描述。

### FR-009 version blueprint 必须表达递进版本演进

能够对照当前版 / 上一版 / 下一版方向。

### FR-010 init 必须表达 lifecycle adoption level

设计上必须支持接管级别语义，而不是只表达“是否 init 过”。

### FR-011 init 必须落盘 project onboarding state

至少支持：
- `.beacon/state/project-onboarding.json`

### FR-012 status/help/doctor 输出双版本上下文

至少应显式输出：

- `docs_version`
- `runtime_version`
- `context_managed_version`

### FR-013 doctor 增加版本分离漂移检查

至少支持：

- `docs_runtime_separation_integrity`
- runtime 同名 docs root 可疑检测

### FR-014 当前版本先冻结设计语义

v1.1.8 当前只冻结 init 的增强设计，不宣称已实现。

## 7. 验收语义

### Pass
- init 的主入口、渐进式披露、技术架构主文档、版本演进蓝图都定义清晰
- greenfield/takeover 两类场景都有明确语义
- 能服务技术接手与版本递进对照

### Fail
- init 仍停留在建目录/写 managed block
- 没有技术主文档和主入口阅读顺序
- 无法支撑接手项目场景

### Blocked
- init 模式语义、AGENTS guidance、architecture blueprint 结构仍存在关键冲突
