# PRD：Beacon v1.3.0 简化版 Codex 原生子代理

**Feature**: `beacon-v1.3.0-simplified-codex-native-subagents`  
**Version**: `v1.3.0`  
**Date**: `2026-04-10`  
**Status**: `planning line`

## 1. 问题

Beacon 已经把需求、测试、实现与放行收口得比较清楚，但若干阶段仍然把天然适合拆分的工作压成单次生成：

- `think` 里的调研与批判
- `user-story` 里的结构整理与 AC 审核
- `prd` 里的需求解析与风险审阅
- `test-case` 里的场景展开与覆盖检查
- `qa` 里的验证与 repair handoff
- `implement run` 里的执行、复核与测试

当前 Beacon 仍缺一套跨阶段共用、显式、可审计的 Codex 原生子代理契约。

## 2. 目标

引入一套简化版 Codex 原生子代理模型，满足以下目标：

1. 始终从属于 Beacon 阶段命令
2. 默认关闭、显式启用、边界明确
3. 所有委托都写入 run-scoped evidence
4. 最终仍回写为 Beacon 正式工件
5. 不把 Beacon 演进成通用多代理调度器

## 3. 功能需求

### FR-001 阶段级 `subagent_mode`

`think`、`user-story`、`prd`、`test-case`、`qa`、`implement run` 必须支持受约束的阶段级 `subagent_mode`。

### FR-002 角色注册表

Beacon 必须内置一个小型角色注册表，按阶段声明允许角色，而不是允许任意 agent 自由进入正式流程。

### FR-003 委托计划工件

在进入子代理执行前，Beacon 必须先写出子代理计划工件，至少包含：

- stage
- role
- feature / version / run_id
- allowed_scope
- expected_output_schema

### FR-004 子代理证据工件

子代理完成后，Beacon 必须先把 worker evidence 写入运行时目录，再决定是否进入正式 writeback。

### FR-005 正式回写所有权

`think`、`user-story`、`prd`、`test-case`、`qa`、`implement run` 仍然必须对最终 Beacon 工件负责，不能把正式 writeback 让给 worker。

### FR-006 适配器边界

`implement run` 对接 Codex 原生子代理时，必须把它视为 adapter，而不是新的 Beacon runtime core。

### FR-007 规划类 prompt 路由

`beacon ask` 必须把“下一版本 / 子代理演进 / 调研新方向”这类输入路由到 `version` 规划面，而不是 QA 执行面。

### FR-008 并发边界契约

子代理运行时必须保持浅层、可审计、可解释：

- 显式阶段角色注册
- 有界并发 fan-out
- 不允许递归 worker 再开 worker
- 每个 worker 必须带 allowed_scope 元数据

### FR-009 implement-first 落地顺序

`implement run` 必须是第一条真正落地 Codex 原生多代理集成的执行面。

### FR-010 阶段扩面前置条件

`think`、`user-story`、`prd`、`test-case`、`qa` 只有在 `implement run` 已证明 plan/evidence/writeback 闭环稳定之后，才允许复用共享运行时。

### FR-011 版本语义规范注册表

Beacon 必须把现有版本字段的语义冻结并集中管理，以下字段必须保持 canonical 且互不重叠：

- `package_version`
- `runtime_version`
- `docs_default_line`
- `current_runtime_release_line`
- `planning_lines`
- `partial_runtime_supplement_lines`

### FR-012 字段逐项语义定义

Beacon 必须对现有字段逐项给出唯一语义：

- `package_version`：已安装 Beacon 包版本
- `runtime_version`：CLI 与受管上下文当前使用的 Beacon runtime/toolkit 版本线
- `docs_default_line`：docs-oriented 命令在 `auto/latest` 时默认命中的文档线
- `current_runtime_release_line`：当前被视为正式 runtime release truth 的版本线
- `planning_lines`：已开启规划、但尚未提升为 current runtime release 的未来文档线
- `partial_runtime_supplement_lines`：已有局部 runtime 增强、但仍未替代 current runtime release 的规划版本线

### FR-013 统一解析归口

后续所有版本解析都必须经过统一 versioning 层，而不是命令内部再写一套版本判断。

至少适用于：

- `ask` / `prompt`
- `help`
- `status`
- `doctor`
- `init`
- `version`
- `gate` / `release`

### FR-014 防漂移约束

后续源码演进不得：

- 为现有版本语义引入重叠别名
- 静默把 docs-target resolution 与 runtime-target resolution 混用
- 在命令内部私自重解释 version truth 字段
- 新增版本状态字段却不更新 canonical contract 与对应消费者

### FR-015 planning line 解析规则

当用户输入明确表达“下一版本规划”时，Beacon 必须按 canonical planning-line 语义解析目标，而不是默认回退到 current runtime release line。

### FR-016 人类默认中文、机器默认英文

`v1.3.0` 之后，Beacon 在版本规划材料中必须显式区分：

- 人类可读主输出：默认中文
- 机器可读 artifact：默认英文或机器友好键名

### FR-017 双面镜像同步

对于同时存在机器面与人类面的 contract：

- 机器面是 source of truth
- 人类面是中文镜像
- 两侧必须通过统一渲染/测试机制保持同步

版本语义 contract 至少必须满足这一规则。

### FR-018 新 contract artifact 四件套

未来若新增任意 contract 类 artifact，必须同时具备：

- source JSON artifact
- 中文镜像 Markdown
- 统一 render 函数
- drift test

不允许只补其中一部分。

### FR-019 implement plan 与 implement run 的 team-mode 优先策略

`v1.3.0` 必须把 `implement plan` 与 `implement run` 明确收敛到 team-mode 优先策略：

- `implement plan` 默认应输出面向 team-mode 的拆解
- `implement run` 应优先使用 `codex-subagents` 路径
- 必须存在显性、稳定、可重复的 team-mode 触发方式，而不是只靠模糊启发式

### FR-020 QA 的 team-mode 要求

`qa` 在 `v1.3.0` 也必须优先提供显性 team-mode 执行路径，用于：

- verifier
- repair-handoff-writer
- coverage / blocker 汇总

### FR-021 implement 与 QA 的上下文隔离

实现与 QA 必须视为两条相互隔离的角色执行面：

- QA 不应继承实现阶段的私有上下文
- 两者只允许通过正式工件、evidence refs、handoff 摘要进行协作
- 不允许把“实现对话上下文”直接当作 QA 真相源

### FR-022 显性稳定的 team-mode 触发契约

Beacon 必须为 team-mode 提供统一且稳定的显性触发契约，至少覆盖：

- `implement plan`
- `implement run`
- `qa`

其目标是让用户和后续源码都能明确知道何时进入 team-mode，而不是依赖隐式路由猜测。

## 4. 源码落点

当前最小落地路径建议从以下文件入手：

- `beacon/utils/intent_router.py`
- `beacon/commands/ask.py`
- `beacon/commands/think.py`
- `beacon/commands/user_story.py`
- `beacon/commands/prd.py`
- `beacon/commands/test_case.py`
- `beacon/commands/qa.py`
- `beacon/commands/implement.py`
- `beacon/utils/implement_native.py`
- `beacon/utils/project_skills.py`
- `beacon/commands/team.py`
- `beacon/utils/versioning.py`
- `beacon/version-semantics.json`
- `beacon/artifact-language-policy.json`

## 5. 非目标

- 通用任意 shell DAG 编排器
- 替换现有 project-skill orchestration
- 强制所有项目开启 native subagents
- 在 Beacon 正式工件之外再造第二套 release truth
- 让机器 artifact 也强制转成中文

## 6. 推进顺序

1. 规划线与工件 contract 收口
2. 版本语义冻结与统一解析归口
3. 共享 subagent plan/evidence 运行时
4. `implement plan` / `implement run` 的 team-mode 与 Codex-native adapter
5. `qa` 的 team-mode 与 implement/qa 上下文隔离
6. `think / user-story / prd / test-case / qa` 的只读/批判类扩面
7. gate / release 硬化
8. 中文人类面与英文机器面双轨同步治理
