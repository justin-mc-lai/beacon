# PRD：Beacon v1.3.2 implement 三模式与迭代浏览器 QA 闭环

**Feature**: `beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa`  
**Version**: `v1.3.2`  
**Date**: `2026-04-14`  
**Status**: `planning line`

## 1. 问题

`v1.3.0` 与 `v1.3.1` 已经把 Beacon 的 team runtime、人类主线和 machine lanes 讲得更清楚，但 `v1.3.2` 当前仍有三个关键不清晰点：

1. `implement` 侧已经同时存在 `native-single`、`codex-subagents`、`team-run`、`ralph-bridge` 等语义，用户无法直观看懂“当前到底是单进程、多代理还是持续闭环”。
2. 三模式讨论容易被误扩到所有阶段，但真正需要这套模式的其实只有：
   - `implement`
   - `qa`
3. QA 的“自动化迭代演进”虽然已有 learning / auto research / browser runner 等基础，但还没有被收成一个明确、稳定、围绕冻结材料的正式闭环合同。

换句话说，当前最缺的不是更多 runner，也不是在 Beacon 里桥接更多外部执行器，而是：

- `implement` 的三模式语义统一
- `qa` 的浏览器驱动、自迭代、自反馈正式定义
- `ralph` 作为实现+QA 持续推进层的边界与终态

## 2. 目标

`v1.3.2` 的目标是把三模式正式收口为：

### 2.1 只作用于 `implement` 与 `qa`

三模式不是 Beacon 全阶段通用执行模型。

它只服务：

- 代码实现阶段 `implement`
- 自动化测试与浏览器验收阶段 `qa`

而以下阶段仍保持单 owner 正式材料面：

- `think`
- `prd`
- `user-story`
- `test-case`

### 2.2 `implement` 提供三种执行模式

- `single`
- `team`
- `ralph`

其中：

- `single` 是最小单进程执行面
- `team` 是 bounded multi-agent 执行面
- `ralph` 是围绕 `implement + qa` 的持续穷尽闭环，而不是新的实现执行器

### 2.3 `qa` 成为冻结材料驱动的浏览器化迭代演进闭环

QA 必须围绕冻结的：

- `prd`
- `user-story`
- `test-case`

按顺序、可迭代地推进自动化浏览器测试，并且每一轮都必须带来新的边界信息、结构推演或覆盖增强，而不是重复跑同一套脚本。

## 3. 设计原则

### 3.1 正式材料不下放

正式 requirement truth 仍由：

- `prd`
- `user-story`
- `test-case`

持有。

`implement` 与 `qa` 都只能围绕冻结材料推进，不得擅自扩 scope 或重写 requirements。

### 3.2 三模式是 execution family，不是三套产品

用户应理解的是模式，而不是底层 runner 名称。

也就是说，对外主语义应是：

- `single`
- `team`
- `ralph`

而不是：

- `native-single`
- `codex-subagents`
- `team-run`
- `ralph-bridge`

### 3.3 QA 必须是浏览器原生的

`qa` 的主价值不是命令执行，而是围绕目标项目启动真实浏览器环境，执行有状态、可回放、可演进的验收过程。

### 3.4 外部参考基线

`v1.3.2` 在 team subagent 稳定调用这条线上，必须参考三类现有事实，而不是完全凭内部假设设计：

1. `omx` 侧：
   - Beacon 仓内已有基于 `omx` 的 adapter-driven 实现示例：
     - [`skills/beacon/examples/implementation-with-omx.md`](../../../../skills/beacon/examples/implementation-with-omx.md)
   - 该示例强调先 `skill list/detect`、再 `implement list-runners`、再 `dry-run`，最后才进入正式执行。
2. Codex 官方侧：
   - OpenAI 官方 Codex cloud 文档明确强调：
     - 任务可以在隔离环境中并行运行
     - 技能和环境配置是稳定委托的重要前提
     - 参考：<https://platform.openai.com/docs/codex>
   - OpenAI 官方 shell 工具文档明确强调：
     - shell 调用必须 sandbox
     - 必须有 allow/deny lists
     - 必须记录工具活动并支持审计
     - 参考：<https://platform.openai.com/docs/guides/tools-shell>
3. Claude 官方侧：
   - Claude Code 官方 subagents 文档明确区分：
     - subagents：单 session 内的独立上下文 worker
     - agent teams：跨 session 的并行协作
     - 参考：<https://docs.anthropic.com/en/docs/claude-code/sub-agents>
   - Claude 官方 settings 文档明确要求：
     - project-level 与 user-level subagent 位置清晰
     - 权限、环境变量、settings precedence 可被正式配置
     - 参考：<https://docs.anthropic.com/en/docs/claude-code/settings>

这些参考的正确用法是：

- `omx`：只作为借鉴 Beacon 如何做 adapter 检测、dry-run、artifact 检查的研究样本
- Codex 官方：作为 Beacon skill 安装到 Codex 后，调用 Codex 原生 subagent/team 特性的目标依据
- Claude 官方：作为 Beacon skill 安装到 Claude 后，调用 Claude 原生 subagent/team 特性的目标依据

因此 `v1.3.2` 不应把目标理解成“Beacon 自己桥接 OMX/Codex/Claude 多运行时执行器”，而应明确为：

> Beacon 作为 agent skill，被安装到 Codex 或 Claude 后，应稳定使用宿主原生 subagent/team 能力。

### 3.5 Beacon 全局约束：继续沿袭人类极简心智工作流

`v1.3.2` 不得因为原生 subagent/team 能力增强，就破坏 `v1.3.1` 已经建立的人类极简心智工作流。

这条线必须被提升为 Beacon 全局约束，而不是 feature 私有偏好：

- 对外公开命令面必须极度克制
- 复杂度必须默认留在机器内部消化
- 人类不应承担 team/subagent/precheck/runtime 细节
- 人类主流程仍应沿袭：
  - `prd`
  - `user-story`
  - `test-case`
  - `implement`
  - `qa`
  - `release`

也就是说，`v1.3.2` 的增强不应让用户额外学习：

- `team`
- `subagent`
- `runtime-readiness`
- `delegation-readiness`
- 宿主差异化配置细节

这些都应该默认由 Beacon 机器内部处理；只有在阻断时，才通过极简诊断面暴露给人类。

### 3.6 `global-boundaries` 必须成为正式功能特性

`global-boundaries` 在 `v1.3.2` 中不能只被视为一份顶层文档。

它必须被定义为 Beacon 的正式功能特性，至少覆盖两层：

1. **Beacon 源码开发自身**
   - Beacon 的后续源码迭代、命令设计、skill 暴露、文档结构，必须持续遵守并消费 `global-boundaries`
2. **Beacon 的目标项目**
   - 当 Beacon 被安装、接入、同步到真实项目后，目标项目也必须能读取、继承并验证 `global-boundaries`

也就是说，`global-boundaries` 的正确定位不是：

- “仓库里有一份全局文档，供人类参考”

而是：

- “Beacon 源码与 Beacon 目标项目都可被验证地支持这份全局约束”

## 4. 功能需求

### FR-001 三模式只在 `implement` 与 `qa` 生效

`v1.3.2` 中讨论的三模式，只允许正式作用于：

- `implement`
- `qa`

不得把该模式体系默认扩展到 `prd / user-story / test-case / think` 等 requirement 面。

### FR-002 `implement` 必须支持 `single`

`single` 模式必须满足：

- 单进程
- 单 owner
- 最小执行面
- 不启动 team lanes
- 仍然对接 formal review / qa / gate

适合：

- 小范围修改
- 确定性需求
- 不需要并行 reviewer/tester lane 的实现

### FR-003 `implement` 必须支持 `team`

`team` 模式必须满足：

- 进入 bounded multi-agent runtime
- 保留显式角色分工
- 支持 `file` / `tmux` 等 runtime
- 生成 HUD、role reports、worker evidence、session / pane 映射
- 后续允许接入 worktree isolation

### FR-004 `implement` 必须支持 `ralph`

`ralph` 模式必须满足：

- 它不是新的实现执行器
- 它是包在 `implement + qa` 外层的持续推进闭环
- 它必须根据每轮正式结果决定下一轮动作：
  - 继续实现
  - 继续 QA
  - 进入 repair handoff
  - 停止并升级到人类处理

### FR-005 `qa` 必须成为三模式体系中的第二执行面

`qa` 在 `v1.3.2` 中不再只是 `implement` 之后的一次收尾动作。

它必须成为与 `implement` 对应的正式执行面：

- `implement` 负责产出代码与实现证据
- `qa` 负责产出浏览器验收、边界发现、结构推演与 repair handoff

### FR-006 `qa` 必须围绕冻结材料顺序推进

QA 的正式输入必须固定为冻结的：

- `prd`
- `user-story`
- `test-case`

QA 不得脱离这些材料自行定义新的正式目标。

QA 的推进顺序至少应满足：

```text
frozen prd
→ frozen user-story
→ frozen test-case
→ scenario ordering
→ browser execution
→ evidence / boundary feedback
→ next iteration
```

### FR-007 `qa` 必须启动目标项目浏览器环境

QA 不应停留在静态断言或离线文本判断。

它必须能够围绕目标项目启动真实浏览器环境，并支持项目选择的 browser-capable runners，例如：

- `browser-cli`
- `agent-browser`
- `pageagent`
- `browser-use`

如有需要，也可以继续兼容：

- `playwright`
- `cypress`

但 `v1.3.2` 的核心口径是：

> QA 是浏览器原生的目标项目验收，不是附属 runner 列表。

### FR-008 `qa` 必须支持顺序可迭代演进

QA 不得只做“一次性跑完全部 case”。

它必须支持：

- 顺序推进
- 分轮迭代
- 每轮根据上一轮发现补充下一轮验证重点
- 保留每轮的 evidence / summary / newly learned boundaries

### FR-009 每一轮 QA 都必须带来新的 auto research 增量

QA 中的 auto research 不得只是重复探索。

每一轮至少必须新增以下之一：

- 新边界条件
- 新异常路径
- 新页面状态
- 新结构推演
- 新 coverage gap closure
- 新 repair handoff

如果本轮没有新增价值，不应被视为有效迭代进展。

### FR-010 QA 必须反馈边界信息

每一轮 QA 至少应能反馈：

- 当前覆盖到的边界
- 尚未覆盖的边界
- 新发现的条件分支
- 推断出的页面/流程结构
- 对冻结材料的解释性补充说明

这些反馈不直接改写 PRD / story / test-case，但必须能进入：

- QA evidence
- repair handoff
- Ralph closure decision

### FR-011 QA 必须支持结构推演

QA 不只是做 pass/fail 判断。

它还必须具备结构推演能力，例如：

- 页面状态机
- 关键流程转移条件
- 登录态 / 会话依赖
- 表单校验层次
- 页面组件依赖或业务路径依赖

这些结构推演结果应帮助后续迭代更快定位边界和空白，而不是停留在零散 bug 列表。

### FR-012 QA 必须逐轮打磨产品功能与体验

多轮 QA 的目标不是“证明失败”，而是：

- 逐轮打磨功能正确性
- 逐轮打磨验收路径完整性
- 逐轮打磨产品边界清晰度
- 逐轮让功能产品更接近可交付状态

### FR-013 Ralph 必须使用 `implement + qa` 闭环

Ralph 在 `v1.3.2` 中必须明确只围绕：

- `implement`
- `qa`

进行闭环推进。

它不直接迭代 requirement 阶段，不直接控制 `prd`、`user-story`、`test-case` 的正式写回。

### FR-014 Ralph 必须有明确终态

Ralph 不得无限循环。

至少必须存在以下终态：

- `release_ready`
- `human_blocked`
- `budget_exhausted`

### FR-015 Ralph 必须复用现有 control plane

Ralph 不应新造一套重复状态机。

它应优先复用现有控制面能力：

- `failure_streak`
- `escalation_level`
- `required_next_action`
- `checkpoint`

并在此基础上增加针对 `implement + qa` 闭环的 round summary 与 final verdict。

### FR-016 QA 浏览器验证必须有正式证据输出

每轮浏览器 QA 至少应产出以下证据中的合理子集：

- screenshot
- current URL
- action transcript
- DOM / snapshot
- console excerpt
- network summary
- browser session / profile reference
- round summary

### FR-017 QA 的结果必须服务下一轮迭代

QA 输出不应只是归档。

它必须能够驱动下一轮的：

- scenario 优先级调整
- 边界补测
- repair handoff
- Ralph next-action 决策

### FR-018 `status/help` 必须显式表达当前模式与迭代轮次

对于 `implement` / `qa` / `ralph` 执行面，`status/help` 至少必须能明确输出：

- 当前 mode
- 当前 executor
- 当前轮次
- 当前 blocker
- 推荐下一步

### FR-019 Beacon 作为 skill 必须稳定调用 Codex / Claude 原生 team subagent 能力

当 Beacon 被安装为：

- Codex skill
- Claude skill

并进入 `team` 模式或 `ralph + team executor` 时，Beacon 的目标不是桥接外部执行器，而是稳定使用宿主提供的原生 subagent/team 能力。

这里的“稳定调用”不等于一律放行，而是：

- 先判断当前宿主环境是否满足稳定调用条件
- 满足才允许进入原生 team subagent
- 不满足则显式阻断，并给出 fallback 或修复建议

### FR-020 原生 team subagent 调起前必须拆成两个稳定预检查

`v1.3.2` 必须把 team subagent 调起前的检查固定为两段，而不是零散散落在 runner 内部：

1. `runtime-readiness precheck`
2. `delegation-readiness precheck`

规则：

- 两段都通过，才允许进入宿主原生 team subagent
- 第一段失败，说明运行时本身不可用
- 第二段失败，说明项目或任务上下文不满足安全委托条件

### FR-021 `runtime-readiness precheck` 必须检查宿主原生能力可用性

第一段预检查至少必须覆盖：

- 当前宿主是否为 Codex 或 Claude
- Beacon skill 是否已被宿主正确安装
- 宿主原生 subagent / team 能力是否可用
- 必需 settings / environment / skill path 是否存在
- 是否支持非交互、可审计、可恢复的执行

### FR-022 `delegation-readiness precheck` 必须检查项目委托条件

第二段预检查至少必须覆盖：

- frozen `prd / user-story / test-case` 是否齐备
- implementation plan / git workflow contract 是否齐备
- role contract 与 output artifact contract 是否齐备
- QA baseline bundle / browser session contract 是否齐备
- 当前任务是否适合进入 team 模式，而不是应回退到 `single`
- 当前任务是否已具备可审计的 handoff / stop-state contract

### FR-023 `omx` 仅作为调研参考，不作为 `v1.3.2` 目标运行时

`v1.3.2` 可以参考 `omx` 的以下经验：

- launcher / adapter 检测
- dry-run 优先
- artifact / stdout / stderr / command 可写

但 `v1.3.2` 不应把 `omx` 作为 Beacon 需要桥接支持的正式 team subagent 运行时。

### FR-024 Codex 路径必须使用 Codex 宿主原生 subagent/team 能力

对 Codex 路径，Beacon 必须吸收 OpenAI 官方 Codex / shell 文档中明确的稳定性要求：

- 执行环境必须是隔离的
- shell / command execution 必须可 sandbox
- 必须具备 allow/deny 控制能力
- 必须记录可审计的执行日志
- 不得依赖交互式命令才能成功

因此，Beacon 在 Codex 中作为 skill 运行时，至少必须验证：

- 当前宿主是否暴露原生 subagent/team 能力
- shell / tool execution 是否具备明确 sandbox 策略
- 关键工具行为是否可记录到 artifact / logs
- 当前任务是否支持稳定的并行或后台执行语义

并且不得把目标实现成：

- 由 Beacon 自己桥接另一个 Codex 执行器
- 由 Beacon 自己复制一套平行 subagent runtime

### FR-025 Claude 路径必须区分单 session subagent 与多 session team

参考 Claude 官方文档，Beacon 在 `v1.3.2` 中不得把 Claude 的 subagent 与跨 session team 混为一谈。

至少必须区分：

- Claude subagent：单 session 内独立上下文 worker
- Claude team / 多 worker 并行：跨 session 或显式 team orchestration

因此，Beacon 在 Claude 中作为 skill 运行并调起 team subagent 时：

- 不得默认假设 subagent 可无限嵌套
- 不得把单 session subagent 直接当作通用 team runtime
- 必须显式判断当前目标是“单 session subagent”还是“多 session team”

### FR-026 Claude 多环境 subagent 必须拆成两个稳定预检查

对于 Claude 运行时，必须把预检查稳定拆成两段：

#### A. Claude runtime/config precheck

至少检查：

- `.claude/agents/` 与 `~/.claude/agents/` 的可用性
- project-level 与 user-level agent 的优先级是否明确
- Claude settings / env / login 或 API 配置是否可用
- 所需 tools / permissions / MCP 可用性是否满足要求

#### B. Claude delegation/project precheck

至少检查：

- 当前任务是否应走单 session subagent，还是应走跨 session team
- 当前项目的 `CLAUDE.md` / settings / managed block 是否与 Beacon 约束一致
- 当前 feature 的 frozen materials、branch/worktree、output contract 是否齐备
- 当前任务是否允许在 Claude 路径下安全地进入 team delegation

### FR-027 预检查失败必须阻断 team subagent 并给出 fallback

任一预检查失败时：

- 不得继续调起宿主原生 team subagent
- 必须显式输出失败原因
- 必须给出推荐 fallback：
  - 回退到 `single`
  - 继续 `doctor`
  - 修复 skill install / settings / session / contract

### FR-028 `doctor` 必须成为多环境 subagent 预检查的统一入口

`v1.3.2` 不应把这些预检查散落到实现器里各自判断。

Beacon 必须为 team subagent 稳定调用提供统一的 doctor / preflight surface，用于：

- 运行 `runtime-readiness precheck`
- 运行 `delegation-readiness precheck`
- 输出 machine-readable 结果
- 输出人类可执行的修复建议

### FR-029 Beacon 必须继续沿袭极简人类主流程

`v1.3.2` 必须把以下命令继续视为 Beacon 的人类主流程：

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

这条 6 段主链必须继续稳定，不得因 `team/subagent` 能力增强而让人类主心智扩张。

### FR-030 对外公开命令面必须极度克制

即使内部支持 Codex / Claude 原生 team subagent，Beacon 也不得为此新增面向人类的宽公开命令面。

至少在 `v1.3.2` 中：

- 不得新增新的一级主命令来暴露 team/subagent 能力
- 不得要求人类在主流程中显式操作 team/subagent/precheck 命令
- `implement` 与 `qa` 仍必须是唯一主执行入口

### FR-031 复杂度必须默认留在机器内部

所有以下复杂度，都应默认由 Beacon 机器内部消化：

- team subagent 调起
- Codex / Claude 宿主能力判断
- runtime-readiness precheck
- delegation-readiness precheck
- team lane 选择
- repair handoff / next-action routing

人类默认不应直接承担这些复杂度。

### FR-032 预检查必须默认内嵌到 `implement` / `qa`

`runtime-readiness precheck` 与 `delegation-readiness precheck` 必须默认作为：

- `implement`
- `qa`

内部的前置动作执行，而不是新增给人类的独立日常操作步骤。

`doctor` 只应承担：

- 显式诊断
- 阻断修复
- 深入排查

而不是成为人类主链的新增常驻步骤。

### FR-033 宿主上下文必须唯一，不讨论运行时选择

`v1.3.2` 讨论的是：

- Beacon 作为 skill 运行在 Codex 中
- Beacon 作为 skill 运行在 Claude 中

而不是：

- 同一轮执行中在 Codex / Claude / OMX 之间做选择
- Beacon 自己决定桥接哪一个外部执行器

因此，`v1.3.2` 的宿主上下文必须被视为唯一：

- 当前宿主是谁
- 当前宿主是否支持原生 subagent/team
- 当前宿主是否满足稳定调用条件

只回答这些问题，不引入多运行时选择叙事。

### FR-034 人类输出必须极简，机器输出必须完整

对同一次 precheck / delegation / blocker 判断，Beacon 必须支持双层输出：

#### 人类层

- 一句阻断原因
- 一个推荐下一步
- 一个 fallback 或修复命令

#### 机器层

- 完整 machine-readable payload
- 详细 reason codes
- runtime / delegation 细节
- evidence refs / diagnostics

规则：

> 复杂细节必须保留给机器与审计面，而不是默认倾倒给人类。

### FR-035 `global-boundaries` 必须成为 Beacon 的正式全局特性

`v1.3.2` 必须把 `global-boundaries` 定义为 Beacon 的正式全局特性，而不是仅作为顶层文档存在。

至少必须满足：

- 存在唯一 canonical global boundaries source
- 各版本线只能继承、引用、落实它，不得各自发明新的“全局真相”
- 后续 Beacon 功能迭代必须把 `global-boundaries` 作为正式输入，而不是只当注释性材料

### FR-036 Beacon 源码开发自身必须支持 `global-boundaries`

Beacon 源码开发自身必须能够被 `global-boundaries` 约束和验证。

至少必须覆盖：

- 顶层 docs 组织
- host-visible skill 暴露
- `help / status / doctor / implement / qa` 的对外命令面
- team/subagent/precheck 的机器内化策略
- 版本包对全局约束的引用方式

规则：

- Beacon 后续源码迭代若违反 `global-boundaries`，应可被识别为 package drift 或 boundary drift

### FR-037 Beacon 目标项目必须支持 `global-boundaries`

当 Beacon 被安装到真实目标项目后，目标项目也必须支持 `global-boundaries` 特性。

这里的“支持”至少包括：

- 目标项目上下文能感知 Beacon 全局约束
- 目标项目中生成的 `AGENTS.md` / `CLAUDE.md` / managed context 能引用或继承该约束
- 目标项目的 `implement / qa / doctor / status / help` 语义不应与 `global-boundaries` 冲突

### FR-038 `init/setup-context/sync-materials/verify-context` 必须支持 `global-boundaries`

Beacon 的以下能力必须显式支持 `global-boundaries`：

- `init`
- `doctor setup-context`
- `doctor verify-context`
- `doctor sync-materials`

至少要求：

- 新项目初始化时能建立 `global-boundaries` 的可见继承关系
- 已接入项目能验证自己是否仍符合 `global-boundaries`
- 旧项目升级后能把 `global-boundaries` 正确同步进目标上下文，而不是靠人工补文档

### FR-039 版本包必须显式声明如何继承 `global-boundaries`

每个版本包都不得重新定义 Beacon 全局约束本体。

每个版本包必须显式回答：

- 当前版本如何引用 `global-boundaries`
- 当前版本在什么地方落实该约束
- 当前版本是否新增任何对全局约束的补充说明

但不得把版本级约束文档冒充成新的全局真相。

### FR-040 目标项目的交付闭环必须可验证地遵守 `global-boundaries`

Beacon 目标项目中的以下闭环必须可验证地遵守 `global-boundaries`：

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

至少要求：

- 人类主流程仍保持极简
- team/subagent/precheck 默认留在机器内部
- 目标项目不因 Beacon 接入而暴露额外主命令负担

### FR-041 `doctor` 必须能检查 `global-boundaries` 的源码侧与项目侧一致性

`doctor` 不应只检查包版本、物料版本和上下文缺失。

在 `v1.3.2` 中，`doctor` 应至少具备：

- 检查 Beacon 源码包是否仍符合 `global-boundaries`
- 检查目标项目上下文是否正确继承 `global-boundaries`
- 指出“源码侧已升级但项目侧仍未同步”的 global-boundaries drift

### FR-042 `global-boundaries` 必须进入成功判定

`v1.3.2` 的成功不只在于：

- 三模式清晰
- QA 迭代闭环清晰
- Codex / Claude 宿主原生 subagent 语义清晰

还必须包括：

- Beacon 源码开发自身可验证地支持 `global-boundaries`
- Beacon 目标项目可验证地支持 `global-boundaries`
- 两者之间不存在“顶层约束存在，但项目侧无法消费”的断层

## 5. 非功能约束

1. 不得把三模式扩成 Beacon 全阶段通用 runtime。
2. 不得让 QA 脱离冻结材料自由扩 scope。
3. 不得把 agent 浏览器探索误当成唯一真相。
4. 不得让 Ralph 绕过 review / qa / gate 的正式阶段结果。
5. 不得让 worker 直接持有正式 requirement writeback ownership。

## 6. 成功标准

1. 用户能够明确理解 `single / team / ralph` 的区别，不再依赖 runner 名称猜语义。
2. 三模式的正式作用范围被明确收口为 `implement + qa`。
3. QA 被正式定义为浏览器原生、冻结材料驱动、顺序可迭代演进的闭环。
4. 每轮 QA 都能沉淀新的边界信息、结构推演或 coverage 增量。
5. Ralph 能基于 `implement + qa` 的正式结果持续推进，直到达到清晰终态。
6. Beacon 能在 Codex / Claude 宿主环境下稳定判断是否可以调起原生 team subagent，而不是盲目尝试。
7. Claude 路径下的 team subagent 调起，必须经过两段稳定预检查并可明确阻断。
8. 人类主心智仍保持在 `prd -> user-story -> test-case -> implement -> qa -> release`，而不被 team/subagent/precheck 复杂度扩张。
9. Beacon 源码开发自身与 Beacon 目标项目都可验证地支持 `global-boundaries` 特性。

## 7. 验收语义

### Pass

- `implement` 三模式语义清晰且范围受控
- `qa` 的浏览器驱动、自迭代、auto research 增量被正式定义
- Ralph 的闭环对象、终态和边界被清晰定义
- Codex / Claude 宿主原生 team subagent 的调起前置检查被正式定义
- Claude 多环境 subagent 的两段稳定预检查被正式定义
- 对外公开命令面仍然极度克制，复杂度被明确要求保留在机器内部
- `global-boundaries` 被正式定义为 Beacon 全局特性，而不是单纯文档
- Beacon 源码侧与目标项目侧都能验证性支持 `global-boundaries`

### Fail

- 仍然把三模式讲成底层 runner 名称集合
- 仍然让 QA 只停留在一次性测试或泛化 runner 列表
- Ralph 仍然只是 bridge 状态记录，没有明确闭环合同
- team subagent 仍然是“选 runner 就直接跑”，没有统一 precheck
- 仍然把 Beacon 的目标写成桥接 OMX/Codex/Claude 执行器，而不是作为 skill 使用 Codex/Claude 原生能力
- Claude 路径仍然把 subagent 与 team runtime 混成一个概念
- 新能力让人类必须理解更多内部命令、team lane 或 precheck 细节，破坏极简心智面
- `global-boundaries` 只存在于 Beacon 仓库文档中，但 Beacon 源码与目标项目都无法验证性支持它

### Blocked

- `qa` 是否只围绕冻结材料推进仍存在重大分歧
- 或 `ralph` 是否只服务 `implement + qa` 仍存在架构分歧
