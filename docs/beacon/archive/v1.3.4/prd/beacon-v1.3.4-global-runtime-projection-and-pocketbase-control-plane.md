# PRD：Beacon v1.3.4 Beacon Runtime Ledger 与 Beacon 管理看板

**Feature**: `beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane`  
**Version**: `v1.3.4`  
**Date**: `2026-04-18`  
**Status**: `planning line`

## 1. 问题

Beacon 当前在“单项目 requirement 闭环”和“项目本地运行态证据”上已经足够强，但机器级全局管理仍是空白：

1. `docs/beacon/<version>/` 承担版本化 requirement / release 真相。
2. `.beacon/` 承担项目内运行态、证据、HUD、debug、team/ralph 等本地状态。
3. 机器人读面当前大量依赖本地 markdown / json / runtime 文件，适合项目内闭环，但不适合跨项目统一检索、索引、看板和异常总览。

结合目标实践项目，问题已经很明确：

### 1.1 `slow_uni_bmtop` 暴露的摩擦

- 它是典型单仓项目。
- 本地 `docs/beacon` 与 `.beacon/` 已经很丰富。
- 真正缺的不是更多本地状态文件，而是跨项目 run 历史、健康态、失败态和进度聚合。

### 1.2 `rolo` 暴露的摩擦

- 它是多服务 workspace，根目录不是单一 git repo。
- root 级别有 `docs/beacon/` 与 `.beacon/`，但实际交付散布在多个 child repo。
- 同一次需求推进可能同时关联多个服务、多个 branch、多个 repo root。
- 这意味着 Beacon 不能继续隐含地假设“一个项目等于一个 git repo”。

### 1.3 当前缺口的本质

当前最缺的不是第二套正式真相面，而是：

- 项目注册表
- git scope 注册表
- run 跟踪
- 进度聚合
- 异常观测
- 跨项目可视化
- 可备份的机器级观察面

同时又必须满足一个硬约束：

> 即使 SQLite / PocketBase 全部丢失，项目也必须仍可从 `docs/beacon` 和 `.beacon` 继续开始。

同时必须明确：

- `omc`
- `omx`
- 其他 Beacon 外兼容运行时

不属于本版本的 Beacon 正式投影对象，也不进入 `Beacon 管理看板` 展示边界。

### 1.4 真实环境最新摩擦输入（2026-04-18）

本次 `v1.3.4` 主线规划，已经结合 4 个真实项目 / 源码项目的 `.beacon` 状态做过一次外场扫描：

- `rolo`
  - 存在最新 `debug/index.json`
  - 最新 run 为 `debug-rolo-v118`
  - 已出现最新 runtime friction，但尚未稳定物化为 `debug/issues/*.json`
- `slow_uni_bmtop`
  - 存在 `debug/index.json` 与 `debug/issues/beacon-core--runtime_feedback.json`
  - 最新 issue 不是新增阻塞，而是历史 acceptance 经验沉淀
- `shopxo_canada`
  - 有 `.beacon` 运行态与 team/handoff 证据
  - 但没有 `debug/index.json` 与 `debug/issues/*.json`
- `beacon`
  - Beacon 源码项目本身必须被纳入看板
  - 它不是系统外部工具，而是 `v1.3.4` 的自迭代、自演进、自验收对象
  - 看板需要能正确表达其当前版本线、并行 PRD、doctor/qa/release 进度与治理状态

这组真实环境输入，明确暴露出 `v1.3.4` 必须正面吸收的 3 条 Beacon 自身摩擦：

1. `rolo` 多服务项目 discovery 摩擦
   - Beacon 不能继续按“仓根单语言 / 单服务”做默认推断。
   - `multi_repo_workspace` 必须优先吸收 `beacon.config.yaml`、既有 `project_skills/profile/registry`、child repo 证据和服务角色采样。
2. 分支 / worktree 解析摩擦
   - Beacon 不能仅按通用 feature 分支命名猜测当前执行分支。
   - 对 `rolo` 这类 workspace，必须优先使用“用户显式指定 + git worktree 实证 + 本地 truth 绑定”。
3. debug repair lane 缺口
   - runtime friction 已经在真实项目反复出现，但缺少正式的人类可达 repair lane，把 issue 稳定转成 `analyze / research / fix / verify` 的闭环对象。

这意味着 `v1.3.4` 不只是“加一个 SQLite + PocketBase 看板”，还必须补齐：

- 多服务 discovery 纠偏
- branch/worktree 解析稳定性
- debug issue intake 与 repair lane
- projection 多写确定性与预校验防漂移

## 2. 目标

`v1.3.4` 的目标是为 Beacon 增加一层机器内部全局运行态投影层，并用 PocketBase 提供人类可读的可视化管理能力。

本版本正式命名应收口为：

- `Beacon Runtime Ledger`
  - 机器内部 SQLite 投影账本
- `Beacon 管理看板`
  - PocketBase 承载的人类管理与观察面

### 2.1 真相层不变

以下内容仍是正式真相：

- `docs/beacon/<version>/`
- `.beacon/`
- 目标项目继承的 `AGENTS.md` / `CLAUDE.md`

SQLite 与 PocketBase 都不得成为正式 release / delivery truth。

### 2.2 建立机器内部全局运行态数据库

SQLite 必须承担以下职责：

- 跨项目注册
- run 追踪
- 进度聚合
- 异常观测
- 关键 artifact 引用索引
- 健康快照

同时必须支持把 Beacon 现有生命周期与 runtime 状态统一投影为：

- 项目管理信息
- 生命周期阶段信息
- 实现阶段 runtime 信息
- git / worktree 规范信息
- host session 引用信息

### 2.3 建立 PocketBase 控制面

PocketBase 必须承担以下职责：

- 可视化后台
- 集合管理与查询
- REST API / realtime 订阅
- 数据导出与备份运维

这层可视化的正式命名应收口为：

- `Beacon 管理看板`

它必须优先展示人类可读的项目管理信息，而不是默认暴露机器交互洪流。

### 2.4 正式支持两类项目

`v1.3.4` 必须正式支持：

- `single_repo`
- `multi_repo_workspace`

其中 `rolo` 必须被视为核心验证对象，而不是边缘特例。

### 2.5 明确断库重建合同

如果 SQLite 状态缺失、损坏或不可用，Beacon 仍应允许从本地项目材料恢复到可继续推进的状态。

### 2.6 生命周期主轴优先于 runtime 细节

`Beacon 管理看板` 的第一层必须按 Beacon 生命周期展示：

- 需求阶段：
  - `prd`
  - `user-story`
  - `test-case`
- 实现阶段：
  - `implement`
  - `qa`
  - `release`

并且必须承认 Beacon 的立项根本不是“有这几个命令”，而是：

```text
prd
→ user-story
→ test-case
→ acceptance
```

也就是说：

- `prd` 定义承诺面
- `user-story` 定义 acceptance criteria
- `test-case` 定义验收场景
- `implement / qa / release` 只能沿这条链闭环，不得反向改写 requirement truth

`single / team / ralph` 只能作为实现阶段的 runtime 下钻信息，而不是生命周期主轴。

### 2.7 支持双层视图

系统必须同时支持：

- CEO 视图：
  - 多项目推进程度
  - 当前交付内容
  - 当前立项工作
  - 当前 blocker
- 项目负责人视图：
  - 当前版本线
  - 主 PRD / 并行 PRD
  - 需求物料补齐情况
  - implement / qa 当前运行态
  - git / worktree 规范
  - session / runtime 引用

### 2.8 冻结 Projection 多写确定性

`v1.3.4` 必须把“Beacon 本地 truth -> SQLite -> PocketBase”定义成正式的确定性投影链，而不是松散同步：

```text
docs/beacon + .beacon + git/worktree
→ normalized projection envelope
→ preflight / drift check
→ SQLite transaction
→ PocketBase projection sync
```

冻结要求：

- 不允许从人类输入或启发式结果直接写 PocketBase。
- 不允许 SQLite 与 PocketBase 各自独立解释同一份 truth。
- 同一份 truth snapshot 必须生成同一份 projection envelope。
- 如果 branch / worktree / version / session 绑定不确定，必须先返回 `unknown / partial / conflicted`，而不是静默写错。

## 3. 设计原则

### 3.1 Projection，不是 Truth

全局数据库和 PocketBase 都只能是投影层。

它们可以持有：

- 索引
- 聚合状态
- 时间线
- 观察指标
- 管理元数据

它们不能持有：

- requirement 真相
- release 真相
- formal acceptance 真相
- 取代本地证据链的最终判断

### 3.2 不扩张人类命令面

`v1.3.4` 不能因为引入 SQLite / PocketBase，就新增新的公开一级主命令。

人类主流程仍是：

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

辅助面仍收敛在：

- `help`
- `status`
- `doctor`

### 3.3 机器复杂度默认内收

project discovery、registry sync、health projection、PocketBase sync、backup 等都应是机器内部复杂度，不应让人类长期承担。

### 3.4 多项目态优先于单一仓假设

从 `rolo` 可以明确得出：

> Beacon project 不等于 git repo。

因此 `project registry` 必须高于 `git scope registry`。

### 3.5 可丢失、可重建优先于强耦合

如果 projection 层比 truth layer 更难恢复，就说明设计方向错了。

正确目标应是：

```text
local truth exists
→ projection can always be rebuilt
```

### 3.6 生命周期优先

`Beacon 管理看板` 必须优先回答：

- 现在处于需求阶段还是实现阶段
- requirement materials 是否补齐
- 当前是否已进入 implement / qa / release

而不是优先回答：

- 当前跑了几个 worker
- tmux pane 是什么
- 内部调度细节如何

### 3.7 双层可见性

人类可见面必须分为：

- 总览层：极简项目管理信息
- 详情层：runtime / git / evidence / session 下钻

规则：

> CEO 看阶段与进度；项目负责人看详情与约束；机器细节不默认外露。

### 3.8 子 skill 通过生命周期映射展示

看板不应把 Beacon 子 skill 当作主导航目录展示，而应通过生命周期映射给出推荐动作：

- 需求阶段：
  - `beacon-prd`
  - `beacon-user-story`
  - `beacon-test-case`
- 实现阶段：
  - `beacon-implement`
  - `beacon-qa`
  - `beacon-release`
- 支持观察层：
  - `beacon-help`
  - `beacon-status`
  - `beacon-doctor`

### 3.9 多写必须确定性且可解释

`v1.3.4` 的投影写链必须满足：

- 同一输入快照，多次执行得到相同结构化 projection 结果。
- 每次写入都能回答“这条状态从哪里来、为何可信、为何覆盖上一条记录”。
- 每条聚合状态都必须能回溯到具体 truth ref、git ref 或 runtime ref。

换句话说：

> 允许延迟，不允许静默漂移；允许不确定，不允许伪确定。

### 3.10 预校验先于落 SQLite / PocketBase

对以下高风险字段，必须先做 preflight，再允许进入 projection write：

- branch / commit / worktree
- project_kind 与 git_scope 归属
- docs line 与 runtime line
- run 与 host session 关联
- material completeness 与 lifecycle stage 推断

如果 preflight 冲突，系统只能：

- 拒绝写入
- 降级写入 `partial`
- 保留 `conflicted` 标记

不能：

- 静默猜测
- 用低优先级推断覆盖高优先级证据

### 3.11 Source Priority 必须被正式冻结

对分支、scope、feature、session 等容易漂移的字段，`v1.3.4` 必须冻结统一优先级：

1. 用户显式指定
2. git worktree / branch / commit 实证
3. `beacon.config.yaml` / project-local registry
4. `docs/beacon` 与 `.beacon` 已落盘绑定
5. runtime inference / heuristics

只有更高优先级来源，才允许覆盖更低优先级来源。

## 4. 范围

### In scope

- 机器内部全局 SQLite 运行态库
- PocketBase 管理与可视化层
- 跨项目 project registry
- 多 git scope 建模
- feature package / version package 建模
- run / run events / artifact refs / health snapshots 建模
- 生命周期阶段与 requirement completeness 建模
- CEO 总览视图与项目负责人详情视图
- `single / team / ralph` runtime 下钻
- git 分支 / worktree 规范治理记录
- Beacon-observed Codex / Claude session 引用
- 基于本地 truth 的重建与回填机制
- 真实环境 debug/index / debug/issues / debug/runs intake
- projection 多写确定性与 preflight 漂移校验
- 多服务 workspace discovery 纠偏与 branch 解析稳定化

### Out of scope

- 把正式交付材料迁移到数据库
- 把 PocketBase 变成 requirement 编辑器
- 用全局状态覆盖本地 `.beacon` 状态
- 引入新的公开 `db` / `pocketbase` / `registry` 一级命令
- 让 Beacon 成为跨宿主桥接控制器
- 把 `omc` / `omx` / 外部兼容运行时纳入正式投影或总览

## 5. 功能需求

### FR-001 建立 Project Registry

系统必须能够注册一台机器上的 Beacon 项目，并记录至少以下字段：

- `project_key`
- `display_name`
- `workspace_root`
- `project_root`
- `docs_root`
- `state_root`
- `project_kind`
- `beacon_runtime_version`
- `last_seen_at`

### FR-002 正式区分 `single_repo` 与 `multi_repo_workspace`

Project registry 必须显式区分：

- `single_repo`
- `multi_repo_workspace`

并且不得把 workspace root 是否是 git repo 作为唯一判定标准。

### FR-003 建立 Git Scope Registry

系统必须为一个 project 关联多个 git scope，并记录至少以下信息：

- `repo_root`
- `repo_name`
- `branch`
- `commit`
- `dirty`
- `role`

这项能力必须足以覆盖 `rolo` 的多服务 workspace。

### FR-004 建立 Feature / Package Registry

系统必须能够识别并注册一个项目下的 feature package / version package，并允许至少表达：

- `version_line`
- `feature_package`
- `themed_package`

这样才能同时兼容：

- `slow_uni_bmtop` 的版本线
- `rolo` 的主题/能力包式目录

### FR-005 建立 Run Registry

系统必须记录关键运行态 run，并至少覆盖：

- `run_id`
- `project`
- `feature`
- `package_key`
- `mode`
- `runner`
- `stage`
- `status`
- `started_at`
- `updated_at`
- `ended_at`

### FR-006 建立 Run Event Timeline

系统必须把关键事件写成时间线，而不是只保留最后状态。

至少包括：

- 进入阶段
- 阻断
- 失败
- 恢复
- 完成
- 降级
- 重建

### FR-007 建立 Artifact Ref Index

系统必须只保存 artifact 的引用与存在性，不复制其正式语义。

至少记录：

- `artifact_type`
- `path`
- `sha256`
- `exists`
- `artifact_scope`

### FR-008 建立 Health Snapshot 与异常观测

系统必须聚合至少以下健康面：

- 上次成功/失败时间
- 卡住或 stale 的 run
- 项目上下文漂移
- 证据缺口
- 同步失败
- PocketBase / SQLite 可用性

### FR-009 PocketBase 必须只消费 Projection Data

PocketBase collection 必须来自 SQLite 或 projector 的派生数据。

PocketBase 不得直接成为 Beacon truth 的写入入口。

### FR-010 提供 Backup / Export 能力

系统必须能对 global runtime data 做备份与导出，至少包括：

- SQLite 数据文件
- PocketBase `pb_data`
- 关键配置与同步元数据

### FR-011 支持断库降级

当 SQLite 或 PocketBase 不可用时：

- 项目本地 `prd/user-story/test-case/implement/qa/release` 不得被阻断
- `status` / `doctor` 只能降级显示“全局投影不可用”
- 不得把“缺少全局状态”误判成“项目状态缺失”

### FR-012 支持从本地 Truth 重建

系统必须提供正式的重建路径，从以下来源恢复最小可用全局状态：

- `docs/beacon/<version>/`
- `.beacon/`
- git worktree / branch / dirty state

### FR-013 看板必须以生命周期为主轴

`Beacon 管理看板` 的总览层必须首先展示：

- 当前处于需求阶段还是实现阶段
- 当前生命周期阶段
- 当前总进度
- 当前 blocker
- 当前建议下一步

而不是先展示 runtime 内部细节。

### FR-014 看板必须支持 CEO 总览视图

CEO 视图必须能够按多项目汇总展示：

- 项目名
- 当前版本
- 当前主 feature
- 当前生命周期阶段
- 当前总进度
- 当前交付状态
- 当前 blocker
- 当前立项工作状态

### FR-015 看板必须支持项目负责人详情视图

项目负责人详情视图必须能够展示：

- 当前版本线
- 主 PRD / 并行 PRD
- requirement materials 是否补齐
- 当前是否在 implement / qa / release
- 当前 runtime 模式
- 当前 git 分支 / worktree 规范状态
- 当前推荐 skill / 下一步

### FR-016 必须显式建模需求物料补齐情况

系统必须对每个 feature 至少判断以下物料状态：

- `prd`
- `user-story`
- `test-case`

并能表达：

- `missing`
- `draft`
- `ready`
- `frozen`

### FR-016A 生命周期主轴必须绑定 requirement traceability

系统不得只把 `prd / user-story / test-case` 当作“是否存在”的材料目录。

它还必须能够正式表达：

- 当前 PRD 是否已冻结承诺面
- 当前 User Story 是否已冻结 acceptance criteria
- 当前 Test Case 是否已建立验收场景
- 后续 implement / qa / release 是否仍然绑定这同一份 requirement truth

### FR-017 必须显式建模实现阶段 runtime 模式

系统必须把以下 runtime 模式作为正式投影对象：

- `single`
- `team`
- `ralph`

并且：

- `single` 必须显示当前 run 与 host runtime
- `team` 必须显示当前 agent 数与角色状态
- `ralph` 必须显示当前 round、failure streak、next action、blocker

### FR-018 必须记录 team 代理运行详情

当 runtime 为 `team` 时，系统必须记录并展示至少以下信息：

- 当前 agent 数
- worker id
- role
- status
- pane / tmux session 引用
- role artifact 引用

### FR-018A `implement single / team / ralph` 必须遵循同一套 PRD 对齐闭环

`single / team / ralph` 在本版本中虽然属于实现阶段 runtime 模式，但不得演化成三套不同的 requirement closure 语义。

系统必须保证三种 implement lane 都满足：

- 共享同一份当前 PRD / user-story / test-case truth
- 共享同一套 `delivery surface manifest`
- 共享同一套 `implementation-summary` / `review-spec` / `gate` 对齐规则
- 不允许因为 runtime mode 不同而绕过 promised-vs-shipped 比对

### FR-019 必须记录 git 分支与 worktree 绑定

系统必须对每个版本迭代 / feature 记录：

- repo root
- branch
- commit
- dirty
- worktree path
- expected branch rule
- spec status

并且看板必须能明确显示该绑定是否符合 Beacon 开发规范。

### FR-020 必须记录 Beacon-observed host session 引用

系统必须允许记录 Beacon 已经捕获到本地证据面的 host session 元数据，包括：

- `Codex`
- `Claude`

但仅限：

- session metadata
- transcript / artifact refs
- linked run / linked feature

不得把宿主内部 session 系统整体纳入 Beacon 真相层。

### FR-021 必须通过生命周期推荐 skill

总览或详情视图必须能够基于当前生命周期状态，给出当前推荐 skill，例如：

- 需求阶段缺口 → `beacon-prd / beacon-user-story / beacon-test-case`
- 实现阶段运行中 → `beacon-implement`
- 验收阶段运行中 → `beacon-qa`
- 阻断修复 / 诊断 → `beacon-doctor`

### FR-022 必须显式排除 Beacon 外运行时

系统必须明确把以下对象排除在正式投影与展示范围外：

- `omc`
- `omx`
- 其他 Beacon 外兼容运行时

允许：

- 在项目本地与 Beacon 共存
- 通过本地 truth 留下间接证据

不允许：

- 作为 `Beacon Runtime Ledger` 的正式 runtime type
- 作为 `Beacon 管理看板` 的默认展示对象

### FR-023 必须 intake 真实环境 debug friction feed

系统必须能够从项目本地以下来源 intake friction/debug 信息：

- `.beacon/debug/index.json`
- `.beacon/debug/issues/*.json`
- `.beacon/debug/runs/*/summary.json`
- `.beacon/debug/runs/*/events.jsonl`

并区分至少 3 种状态：

- `materialized_issue`
- `runtime_feed_only`
- `no_debug_feed`

这样才能正确表达：

- `rolo`：有最新 runtime friction，但 issue 尚未物化
- `slow_uni_bmtop`：有已物化 issue
- `shopxo_canada`：当前没有 debug feed，不等于没有项目运行态

### FR-024 必须建立 Deterministic Projection Envelope

任意一次从本地 truth 到 SQLite / PocketBase 的投影，必须先生成统一的 `projection envelope`，至少包含：

- `project_key`
- `truth_refs`
- `source_hash`
- `projection_version`
- `projection_seq`
- `preflight_status`
- `confidence`
- `uncertainty_reason`

SQLite 与 PocketBase 只能消费同一份 envelope，不允许各自独立解释。

### FR-025 必须在多写前执行 Drift Preflight

在写 SQLite / PocketBase 前，系统必须对以下冲突进行 preflight：

- branch / worktree 与 expected rule 不一致
- docs line / runtime line / context version 不一致
- project_kind 与发现到的 git scope 不一致
- host session 与 active run 关联不清
- 现有投影记录的 `source_hash` 与本次 truth snapshot 不一致

preflight 结果必须显式表达：

- `pass`
- `partial`
- `conflicted`
- `blocked`

### FR-026 必须冻结 Branch / Worktree Source Priority

对于 branch / worktree 这类高漂移字段，系统必须遵守固定优先级：

1. 用户显式 branch / worktree
2. git worktree 实证
3. project-local config / registry
4. 已落盘 truth 绑定
5. heuristic 推断

如果低优先级来源与高优先级来源冲突，系统必须保留冲突并报警，而不是直接覆盖。

### FR-027 多服务 Discovery 必须吸收现有项目配置

对 `multi_repo_workspace`，discovery 不得只按仓根单语言或单服务判断。

至少必须吸收：

- `beacon.config.yaml`
- 已有 `project_skills/profile/registry`
- child repo 列表
- 多语言 / 多服务证据
- 服务角色采样

从而避免把 `rolo` 这类 workspace 错判成单一 `dotnet api-service`。

### FR-028 必须建立 debug repair lane 正式入口

`v1.3.4` 必须把 Beacon 自身摩擦从“debug observation”升级成正式 repair lane，至少允许以下阶段：

- `analyze`
- `research`
- `fix`
- `verify`

这条线至少要能把真实环境中发现的 friction 绑定到：

- project
- feature / version
- issue_id
- source evidence refs
- 建议下一步

### FR-029 Beacon 源码项目必须作为一等受管项目

`v1.3.4` 必须把 Beacon 源码项目本身纳入 `Beacon 管理看板`，至少支持：

- 作为独立 project 注册
- 展示当前版本线与主 feature
- 展示并行 PRD
- 展示 `doctor / qa / release` 相关运行态与自演进状态
- 不因其“系统自身”身份而绕过同一套 projection / preflight / acceptance 规则

### FR-030 必须提供真实项目并板验收矩阵

系统必须把以下 4 个项目纳入正式验收矩阵：

- `rolo`
- `slow_uni_bmtop`
- `shopxo_canada`
- `beacon`

并对每个项目至少验证：

- project registry 成功
- 生命周期阶段显示正确
- runtime / debug feed 显示正确
- project detail 下钻可用
- 推荐下一步与推荐 skill 合理

## 5A. Prototype Contract

`v1.3.4` 的看板可视化需要正式进入 Beacon prototype 轨道，原型目标不是“好看的后台”，而是把主 PRD 中已经确认的生命周期、角色分层和运行态边界编译成可审查的参考原型包。

设计约束：

- 首页优先服务 CEO 汇总视角，不暴露机器洪流。
- 项目详情页优先服务项目负责人，不把 runtime 当主导航。
- `single / team / ralph` 只在运行态下钻层展开。
- `omc` / `omx` 不进入原型主导航与默认内容。
- SQLite / PocketBase 只表达 projection，不改写 truth。

用于 `beacon prototype` 的结构化合同如下：

ui_visualization_required: true
prototype_mode: wireframe
prototype_freeze_required: true
coverage_mode: requirement-page-freeze
prototype_archetype: admin-workbench
theme_mood: disciplined
theme_primary: #1F6FEB
theme_secondary: #0F172A
surface_style: calm-ops board with lifecycle-first information hierarchy
target_user: one-person-company CEO and project owner
brand_keywords: lifecycle-first, delivery-truth, calm-ops, sober-control
sections: home, management-overview, project-detail, runtime-center, recovery-diagnostics, material-viewer
navigation: home, management-overview, project-detail, runtime-center, material-viewer
primary_entry: home
primary_exit: project-detail
primary_cta: 查看项目详情
secondary_cta: 打开运行态
jump_map: home->management-overview: drill into project portfolio summary; management-overview->project-detail: inspect selected project version, parallel PRDs, and lifecycle progress; project-detail->runtime-center: inspect single/team/ralph active runs and agent/session refs; project-detail->material-viewer: open requirement materials by version and type; runtime-center->recovery-diagnostics: inspect stale runs, sqlite unavailable state, and rebuild readiness; recovery-diagnostics->management-overview: return to cross-project summary after diagnosis
states: ready, blocked, intervention-needed, requirement-missing, draft, frozen, runtime-active, single-active, team-active, ralph-active, degraded, rebuild-suggested, doctor-suggested, document-open, source-missing, loading, empty, error
required_pages:
  - home
  - management-overview
  - project-detail
  - runtime-center
  - recovery-diagnostics
  - material-viewer
  - material-document-detail
required_states:
  - ready
  - requirement-missing
  - draft
  - frozen
  - runtime-active
  - single-active
  - team-active
  - ralph-active
  - blocked
  - degraded
  - rebuild-suggested
  - doctor-suggested
  - document-open
  - source-missing
  - loading
  - empty
  - error
page_inventory:
  - home
  - management-overview
  - project-detail
  - runtime-center
  - recovery-diagnostics
  - material-viewer
  - material-document-detail
page_inventory_source:
  CEO overview requires project/version/stage/progress/blocker summary.
  Project owner detail requires version line, main/parallel PRDs, material completeness, git/worktree governance, session refs.
  Runtime center requires single/team/ralph focused drilldown.
  Recovery diagnostics requires degraded mode, rebuild contract, and sync-health explanation.
baseline_protection:
  - page: home
    preserve:
      - lifecycle-first summary cards
      - current version, progress, blocker in one scan line
      - runtime only as compressed badge
      - no raw worker transcript exposure
  - page: management-overview
    preserve:
      - cross-project dense scan view
      - project/version/stage/progress/next-step in one management table
      - runtime only as compressed status, not primary content
  - page: project-detail
    preserve:
      - main PRD and parallel PRD distinction
      - requirement materials completeness panel
      - git and worktree governance card
      - recommended next skill and next action
  - page: runtime-center
    preserve:
      - single team ralph mode separation
      - active agent count and role status for team
      - round count and next action for ralph
      - host session refs without full transcript disclosure
  - page: recovery-diagnostics
    preserve:
      - projection not truth wording
      - sqlite and pocketbase degraded mode explanation
      - rebuild from docs/beacon and .beacon path
      - omc omx explicitly excluded from managed runtime scope
route_closure_required: true
drift_guardrails: runtime-noise-exposed-on-home, agent-count-misused-as-progress, projection-layer-presented-as-truth, omc-omx-leak-into-board, git-worktree-governance-hidden
design_reference_sources: Beacon v1.3.4 main PRD lifecycle-first board model, Beacon v1.3.4 one-person-company ops board model, PocketBase as control plane, not formal delivery truth, Beacon admin-workbench prototype discipline, human minimal surface with runtime drilldown only

## 6. 数据模型

`v1.3.4` 建议至少建立以下核心表或集合：

### 6.1 `projects`

- `project_key`
- `display_name`
- `workspace_root`
- `project_root`
- `docs_root`
- `state_root`
- `project_kind`
- `default_version_or_line`
- `runtime_version`
- `last_seen_at`

### 6.2 `git_scopes`

- `project`
- `repo_root`
- `repo_name`
- `branch`
- `commit`
- `dirty`
- `role`

### 6.3 `feature_packages`

- `project`
- `package_key`
- `package_type`
- `summary_path`
- `release_path`
- `status`

### 6.4 `feature_lifecycle`

- `project`
- `feature`
- `package_key`
- `current_stage`
- `stage_status`
- `progress_percent`
- `blocker_reason`
- `recommended_skill`
- `recommended_next_action`
- `updated_at`

### 6.5 `stage_material_status`

- `project`
- `feature`
- `material_type`
- `status`
- `truth_ref`
- `updated_at`

### 6.6 `runs`

- `run_id`
- `project`
- `feature`
- `package_key`
- `mode`
- `runner`
- `stage`
- `status`
- `started_at`
- `updated_at`
- `ended_at`

### 6.7 `run_workers`

- `run`
- `worker_id`
- `role`
- `status`
- `pane_id`
- `tmux_session`
- `artifact_json_ref`
- `artifact_md_ref`

### 6.8 `run_targets`

- `run`
- `git_scope`
- `target_branch`
- `current_branch`
- `service_name`
- `scope_role`

### 6.9 `run_events`

- `run`
- `stage`
- `event`
- `status`
- `reason_code`
- `ts`
- `details_json`

### 6.10 `artifact_refs`

- `run`
- `artifact_type`
- `path`
- `sha256`
- `exists`
- `artifact_scope`

### 6.11 `git_workspace_bindings`

- `project`
- `feature`
- `package_key`
- `repo_root`
- `branch`
- `commit`
- `dirty`
- `worktree_path`
- `expected_branch_rule`
- `spec_status`
- `updated_at`

### 6.12 `host_sessions`

- `project`
- `feature`
- `run_id`
- `host_runtime`
- `session_id`
- `thread_id`
- `turn_id`
- `transcript_path`
- `status`
- `started_at`
- `ended_at`

### 6.13 `health_snapshots`

- `project`
- `snapshot_at`
- `overall_status`
- `stale_runs`
- `blocked_runs`
- `failing_scopes`
- `sync_status`
- `notes`

### 6.14 `debug_issues`

- `project`
- `issue_id`
- `reason_code`
- `issue_status`
- `materialization_state`
- `latest_event_at`
- `sample`
- `suggested_capability`
- `source_run_id`
- `truth_refs`

### 6.15 `projection_writes`

- `project`
- `write_id`
- `projection_seq`
- `source_hash`
- `preflight_status`
- `confidence`
- `uncertainty_reason`
- `sqlite_status`
- `pocketbase_status`
- `occurred_at`

## 7. 交互与流程

### 7.1 Project Registration

新项目接入后，系统应完成：

1. 识别 `docs/beacon` 与 `.beacon`
2. 判断 `project_kind`
3. 发现 git scopes
4. 写入 project registry
5. 建立初始 health snapshot

### 7.2 Lifecycle Projection

系统必须先物化 feature 的生命周期状态，再决定是否展开 runtime：

1. 判断 requirement materials 是否补齐
2. 计算当前生命周期阶段
3. 计算总进度
4. 生成推荐 skill 与下一步

### 7.2A Projection Preflight

在任意投影写入发生前，系统必须先做一次统一 preflight：

1. 固定 truth snapshot
2. 解析 branch/worktree/version/session source priority
3. 输出 `projection envelope`
4. 标记 `pass / partial / conflicted / blocked`
5. 只有在结果允许时才继续写 SQLite / PocketBase

### 7.2B Debug Intake 与 Repair Routing

系统必须先 intake 项目本地的 debug feed，再决定是否把它提升为正式 repair item：

1. 扫描 `debug/index.json`
2. 扫描 `debug/issues/*.json`
3. 扫描 `debug/runs/*`
4. 区分 `materialized_issue / runtime_feed_only / no_debug_feed`
5. 把可操作摩擦转成 repair backlog / recommended next action

### 7.3 Runtime Projection

当 `implement` / `qa` / `team` / `ralph` 产生关键运行态时，系统应：

1. 提取最小必要运行态
2. 记录 run / run events
3. 记录 artifact refs
4. 更新 health snapshot
5. 同步给 PocketBase 视图

### 7.4 Role-Based Views

`Beacon 管理看板` 至少需要两类视图：

#### CEO 总览视图

- 多项目总览
- 当前版本
- 生命周期阶段
- 总进度
- 当前交付状态
- 立项工作状态
- blocker

#### 项目负责人详情视图

- 当前版本线
- 主 PRD / 并行 PRD
- requirement materials completeness
- runtime mode
- team agents / Ralph 状态
- git / worktree 规范
- session / artifact refs
- 推荐下一步

### 7.5 Recovery / Rebuild

当全局态丢失时，系统应：

1. 扫描本地 truth
2. 回填 project / git scope / package
3. 尽可能恢复 run 历史摘要
4. 对无法确定的字段打 `unknown` / `partial` 标记
5. 恢复可用控制面，而不是伪造完整历史

## 8. 非功能要求

### 8.1 边界安全

- 默认本机使用
- 默认不把 PocketBase 暴露为公网核心服务
- 凭证、token、私有路径不得被无约束回灌到可视化层

### 8.2 一致性

- 全局层允许短时间延迟，但不得长期静默漂移
- 所有投影数据都必须能追溯回本地来源
- SQLite 与 PocketBase 必须消费同一份 projection envelope
- branch / worktree / session 绑定冲突必须显式暴露，不得静默修正

### 8.3 性能

- 日常项目扫描应足够轻量，不拖慢正常 `implement` / `qa`
- 写入 run event 不得成为阶段执行的关键阻塞点

### 8.4 可审计

- 所有同步、重建、降级、失败都必须有机器可读记录

## 9. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 全局库被误当成真相层 | 高 | 在 PRD、schema、命令面、UI 文案中明确 projection/not truth；禁止 PocketBase 直接改写正式材料 |
| `rolo` 类 workspace 建模不足 | 高 | 先把 project 与 git scope 两层分开，再做 run_target 映射；不再默认一项目一仓 |
| SQLite 不可用导致主流程阻断 | 高 | 把 global projection 设计成可选增强层，主流程只依赖本地 truth |
| PocketBase 能力越界 | 中 | 限制为查询、订阅、备份、运维；不承担正式交付判断 |
| 重建时误报完整状态 | 中 | 允许 `partial` / `unknown`；保留重建来源与时间戳 |
| 首页先展示 runtime 细节导致人类认知过载 | 高 | 生命周期作为总览主轴，runtime 只在详情层展开 |
| CEO 视图与项目负责人视图混成一套 | 中 | 明确双层视图与字段边界 |
| git/worktree 只记录不治理 | 中 | 把规范状态做成正式对象与告警 |
| 多写链静默漂移 | 高 | 先产出 deterministic projection envelope，再写 SQLite/PocketBase；冲突只能标记 `conflicted` |
| 分支推断覆盖显式用户意图 | 高 | 冻结 source priority：用户显式 > git worktree > project config > truth binding > heuristic |
| debug feed 有 run 无 issue，导致摩擦被遗漏 | 中 | 对 `runtime_feed_only` 建立正式 intake 与 repair backlog，不再只依赖 issue 文件 |

## 10. 验收标准

### AC-001 Projection / Truth 边界明确

任何正式说明、状态结构或 UI 文案都必须明确：

- `docs/beacon` / `.beacon` 是 truth
- SQLite / PocketBase 是 projection

### AC-002 支持单仓项目

系统必须能正确注册并观测 `slow_uni_bmtop` 这类单仓项目。

### AC-003 支持多仓 workspace

系统必须能正确注册并观测 `rolo` 这类 root 非 git、child repo 多服务项目。

### AC-004 可追踪关键运行态

系统必须能至少对 `implement` / `qa` / `team` / `ralph` 的关键 run 建立时间线与状态聚合。

### AC-005 PocketBase 不管理正式交付真相

PocketBase 中不得成为 requirement、acceptance、release decision 的唯一来源。

### AC-006 断库后项目仍可继续

在 SQLite / PocketBase 缺失时，项目仍可依赖本地 Beacon materials 继续推进。

### AC-007 支持从本地材料重建

系统必须能从本地 truth 恢复最小项目注册、scope 注册、package 注册和 health 摘要。

### AC-008 总览层以生命周期为主轴

首页或总览页必须优先展示：

- 生命周期阶段
- 总进度
- blocker
- 下一步

而不是默认展开 runtime 内部细节。

### AC-008A 生命周期主轴不只是导航，还是 requirement truth 主轴

对于任一 feature，看板和投影层都必须能解释：

- 当前 requirement truth 来自哪份 PRD
- 当前 acceptance criteria 来自哪份 User Story
- 当前验收场景来自哪份 Test Case

不得把生命周期展示退化成“只有阶段 badge，没有 requirement traceability”。

### AC-009 支持 CEO 总览视图

CEO 视图必须能对多项目展示：

- 当前工作进展
- 多项目推进程度
- 当前交付内容
- 当前立项工作

### AC-010 支持项目负责人详情视图

项目负责人详情页必须能展示：

- 当前版本
- 主 PRD / 并行 PRD
- requirement materials completeness
- 当前 implement / qa 状态
- 当前 runtime 详情
- git / worktree 规范状态

### AC-011 `team` 模式必须显示 agent 数

当某个 feature 处于 `team` 模式时，看板必须明确显示：

- 当前运行代理数
- 每个代理的 role
- 当前状态

### AC-012 `ralph` 模式必须显示闭环控制信息

当某个 feature 处于 `ralph` 模式时，看板必须明确显示：

- `round_count`
- `failure_streak`
- `next_action`
- `current_blocker`

### AC-012A `single / team / ralph` 不得绕过同一套 requirement closure

当同一 feature 分别通过 `single / team / ralph` 三种 implement lane 推进时，三者都必须仍然绑定同一份 PRD / user-story / test-case，并接受同一套 delivery summary、review-spec 与 gate 判断。

### AC-013 子 skill 必须通过生命周期推荐

看板必须能基于当前阶段给出推荐 skill，而不是只暴露一组无上下文 skill 列表。

### AC-014 明确排除 Beacon 外运行时

正式文档、数据模型与看板文案必须明确：

- `omc` / `omx` 不属于 Beacon 管理看板范围
- `Beacon Runtime Ledger` 只建模 Beacon-owned 或 Beacon-observed 运行态

### AC-015 支持 debug feed 三态

系统必须能正确区分以下 3 种真实环境状态：

- `rolo`：`runtime_feed_only`
- `slow_uni_bmtop`：`materialized_issue`
- `shopxo_canada`：`no_debug_feed`

### AC-016 多写链具备确定性

对同一份 truth snapshot，重复执行 projection 时：

- 生成的 envelope 结构必须一致
- SQLite 与 PocketBase 看到的 `source_hash / projection_seq` 必须一致
- 不得出现一边更新、一边静默漂移

### AC-017 Branch / Worktree 冲突不会被静默覆盖

如果用户显式 branch / worktree 与 heuristic 推断冲突，系统必须：

- 保留高优先级来源
- 标记冲突
- 给出 preflight / doctor 提示

不能直接覆盖。

### AC-018 多服务 discovery 不再退化成单服务误判

对 `rolo` 这类 workspace，system discovery 必须结合：

- `beacon.config.yaml`
- 已有 profile / registry
- child repo 证据
- 多语言 / 多服务采样

不能再次退化成单一 `dotnet api-service` 判定。

### AC-019 debug repair lane 可把摩擦转成正式修复项

对来自真实项目的 Beacon friction，系统必须能够把 observation 稳定转成：

- issue / repair item
- source refs
- recommended next action
- analyze / research / fix / verify 路径

### AC-020 四个真实项目必须都能进入 Beacon 管理看板

以下 4 个项目必须都能被成功注册并出现在 `Beacon 管理看板`：

- `rolo`
- `slow_uni_bmtop`
- `shopxo_canada`
- `beacon`

### AC-021 四个真实项目的显示语义必须正确

最少必须满足：

- `rolo`
  - 展示为 `multi_repo_workspace`
  - debug feed 状态为 `runtime_feed_only`
  - 不得被误判成单一单服务项目
- `slow_uni_bmtop`
  - 展示为 `single_repo`
  - debug feed 状态为 `materialized_issue`
- `shopxo_canada`
  - 允许无 debug feed
  - 但仍必须展示其运行态、team/handoff 与项目推进信息
- `beacon`
  - 作为源码项目本身被纳入并板
  - 正确显示当前 `v1.3.4` 自迭代主线

### AC-022 Beacon 源码项目必须完成自并板自验收

`beacon` 项目必须通过同一套看板建模规则被展示，而不是以特殊硬编码方式旁路：

- project registry
- lifecycle projection
- runtime projection
- debug / repair signal
- recommended next action

### AC-023 CEO 总览页必须能同时看见四项目差异

CEO 视图必须能够在同一屏内对 4 个项目展示：

- 当前版本
- 生命周期阶段
- 总进度
- blocker
- 当前交付状态

并且能一眼区分：

- `rolo` 的 workspace 复杂度
- `slow_uni_bmtop` 的单仓物料态
- `shopxo_canada` 的运行态但无 debug feed
- `beacon` 的自演进状态

### AC-024 项目详情页必须能正确下钻四项目

对这 4 个项目，项目详情页都必须能下钻并展示：

- 当前版本线
- 主 PRD / 并行 PRD
- requirement materials completeness
- runtime mode
- git / worktree 规范
- 推荐 skill / 下一步

### AC-025 真实项目并板验收必须通过

`v1.3.4` 不能只通过 synthetic fixture 验收。

至少需要对以下 4 个真实项目做一次并板验收通过：

- `/Users/apple/Developer/Company/rolo`
- `/Users/apple/Developer/Personal/products/slow_uni_bmtop`
- `/Users/apple/Developer/Personal/products/shopxo_canada`
- `/Users/apple/Developer/Personal/products/beacon`

并保留机器可读或文档化的验收记录。

### 10.1 真实项目验收场景包

为避免实现阶段把“字段存在”误判成“看板可用”，`v1.3.4` 的正式验收至少还必须覆盖以下场景包：

1. 并板导入场景
   - 4 个真实项目首次进入 `Beacon 管理看板` 时，必须都能被注册、分类并生成稳定卡片。
2. 首页降噪场景
   - 首页默认只显示生命周期、总进度、blocker、下一步，不得把 session、tmux、runtime event 洪流当成首页主内容。
3. 详情下钻场景
   - 进入任一项目详情页后，必须能解释“为什么当前显示为这个阶段、这个 project_kind、这个 debug 状态、这个推荐动作”。
4. debug 三态场景
   - `rolo`、`slow_uni_bmtop`、`shopxo_canada` 必须分别稳定落到 `runtime_feed_only`、`materialized_issue`、`no_debug_feed`，且 `no_debug_feed` 不得被误判成“无项目态”。
5. Beacon 自并板场景
   - `beacon` 源码项目必须按同一规则进入看板，展示 `v1.3.4` 主线、自身 PRD / QA / release 信号与下一步动作，不得走特殊旁路。
6. 断库重建场景
   - 即使 SQLite / PocketBase 缺失，也必须能从 `docs/beacon`、`.beacon` 与 git/worktree 重新恢复四项目最小并板能力。

## 11. 成功指标

- 一台机器上可统一查看多个 Beacon 项目的运行态摘要
- 能区分哪些项目卡在 `implement`、`qa`、`release` 或同步异常
- `rolo` 这类 workspace 项目可以从 project 视角和 service scope 视角同时观察
- `shopxo_canada` 这类无 debug feed 项目不会被误判成“无项目态”
- `beacon` 源码项目可以作为自迭代对象被同一套看板消费
- 全局层缺失时，项目推进不受阻断

## 12. 里程碑建议

| 阶段 | 目标 | 交付 |
|------|------|------|
| Phase 1 | Global SQLite MVP | project / git scope / run / event / health 最小模型 |
| Phase 2 | PocketBase Control Plane | collections、列表页、详情页、基础备份 |
| Phase 3 | Recovery & Drift | rebuild、sync audit、stale detection、降级合同 |

## 13. 待澄清问题

1. PocketBase 是否直接复用同一份 SQLite 数据文件，还是只作为上层集合/同步视图容器。
2. `rolo` 的 service role 命名是否需要标准化字典，例如 `edge` / `bff` / `service` / `job` / `frontend`。
3. 全局层是否需要保留少量 operator-only 注释字段，且明确与正式 truth 隔离。
4. `status` / `doctor` 未来如何暴露全局态摘要，才能既不扩张命令面，又不让信息过载。
5. `projection envelope` 是否需要单独持久化为 JSON artifact，作为 SQLite / PocketBase 双写的一致性锚点。
6. `runtime_feed_only` 类型的 friction，何时自动升级为正式 `debug issue`，何时只保留 observation。
7. `beacon` 源码项目是否需要额外标记 `self_hosted_project=true`，还是与普通受管项目完全同构。

## 14. 关联摩擦与版本依赖

`v1.3.4` 在启动过程中已经暴露出两条与当前版本线直接相关的 Beacon 自身摩擦：

1. `prd create` 仍是通用模板生成器，无法直接生成版本感知、场景感知、边界感知的 PRD 骨架。
2. `v1.3.3` 文档中已经正式承诺 memory/friction toolkit，但 skill 面缺少对应 host-visible subskill。

这两条问题不属于本 PRD 的主交付主题，但它们会直接影响 `v1.3.4` requirement 建设与 optional toolkit 的可达性。

因此它们被转入并行 PRD：

- `beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing`

同时，来自真实环境的新输入已经被正式吸收到本主 PRD 的修复项中：

1. `rolo` 多服务 workspace discovery 纠偏
2. `rolo` 分支 / worktree source priority 冻结
3. debug issue intake 与 repair lane 正式化
4. projection 多写确定性与 preflight 防漂移

---

**Created**: 2026-04-18  
**Version**: v1.3.4  
**Status**: planning line  
**Memory Context**: N/A
