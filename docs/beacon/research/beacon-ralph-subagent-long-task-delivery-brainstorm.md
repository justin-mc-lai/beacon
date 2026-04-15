# Brainstorm: Beacon Ralph / Subagent 基本规范与长任务交付闭环

**日期**：2026-04-14  
**方法**：基于 `$brainstorm` 七维发散框架收敛  
**目标**：把 Ralph、subagent、长任务闭环三件事从概念堆叠压成 Beacon 可持续采用的统一协议，回答三个问题：

1. Ralph 的正确边界到底是什么  
2. subagent 在 Beacon 中应遵守哪些基本规范  
3. 长任务如何从探索、实现、验证一路凿穿到完整可交付

**主要输入**：

- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.3.1/SUMMARY.md`
- `docs/beacon/v1.3.1/execution/architecture-blueprint.md`
- `docs/beacon/v1.3.0/prd/beacon-v1.3.0-simplified-codex-native-subagents.md`
- `docs/beacon/v1.3.0/execution/architecture-blueprint.md`
- `docs/beacon/v1.3.2/SUMMARY.md`
- `docs/beacon/v1.3.2/execution/implement-execution-modes-blueprint.md`
- `docs/beacon/v1.3.2/execution/ralph-closure-state-machine.md`
- `docs/beacon/v1.3.2/research/beacon-v1.3.2-responsibility-optimization-analysis.md`
- `docs/beacon/research/beacon-codex-native-subagent-direction-gstack-superpowers.md`
- `docs/beacon/research/beacon-open-source-reference-source-map.md`
- `beacon/utils/subagent_readiness.py`
- `beacon/utils/subagent_runtime.py`
- `beacon/utils/ralph_runtime.py`
- `beacon/commands/ralph_bridge.py`
- OpenAI Codex subagent docs:
  - <https://developers.openai.com/codex/concepts/subagents>
  - <https://developers.openai.com/codex/subagents>
- Claude Code subagent docs:
  - <https://code.claude.com/docs/en/sub-agents>
- Beacon 已冻结的外部参考项目：
  - `gstack`
  - `superpowers`
  - `codex-turbo`
  - `awesome-codex-subagents`

---

## 1. 先给结论

### 1.1 Ralph 的一句话定义

> Ralph 不是执行器，不是真相层，也不是通用多代理平台；Ralph 是围绕 `implement + review + qa + gate + repair` 的闭环控制器。

它只回答四个问题：

1. 当前是否还能继续推进  
2. 下一步应该调用哪个正式阶段  
3. 为什么要继续或停止  
4. 当前停在什么终态

### 1.2 Subagent 的一句话定义

> Subagent 是受限、可审计、浅层、有所有权边界的执行单元，用来隔离噪声、并行独立子任务、压缩主线程上下文，而不是替代 stage owner。

### 1.3 长任务的正确形态

Beacon 的长任务不应该理解成“开更多 agent 一直跑”，而应该理解成：

```text
brainstorm 收口问题
→ requirement freeze
→ deterministic implementation contract
→ choose execution family(single|team|ralph)
→ implement / review / qa 多轮闭环
→ stop state
→ release-ready deliverable
```

也就是说：

- `brainstorm` 负责把问号收口到可冻住
- `team/subagent` 负责把实现与验证拆成 bounded work
- `ralph` 负责把多轮执行推进到明确终态

---

## 2. Beacon 视角下的基本规范

## 2.1 Ralph 基本规范

### Ralph 应该做什么

1. 只围绕 `implement + qa` 主链持续推进
2. 读取正式工件，而不是读取私有对话上下文
3. 持有 durable state：
   - `phase`
   - `rounds`
   - `stop_state`
   - `current_blocker`
   - `next_action`
   - `recommended_command`
4. 复用已有 control-plane 信号：
   - `failure_streak`
   - `required_next_action`
   - `checkpoint`
   - `repair_handoff`
5. 给出明确终态，而不是“还在跑”

### Ralph 不应该做什么

1. 不直接改写 `prd / user-story / test-case`
2. 不直接充当代码执行器
3. 不绕过 `review / qa / gate`
4. 不新造第二套 truth 或 memory plane
5. 不把人类主命令扩张成新的公开一级命令面

### Ralph 的 canonical stop states

1. `release_ready`
2. `human_blocked`
3. `budget_exhausted`

这三个终态已经足够覆盖 Beacon 的交付判断：

- 可以放行
- 必须人类裁决
- 当前预算下不值得再追

## 2.2 Subagent 基本规范

### 统一原则

1. `stage owner` 继续持有正式 writeback
2. subagent 只产出 run-scoped evidence
3. worker 必须有明确 ownership
4. 并发必须 bounded
5. 默认禁止递归 spawn
6. 先并行读，再谨慎并行写
7. 子代理上下文必须最小化打包，不继承主线程全部历史

### 在 Beacon 中的最小合同

从 `beacon/utils/subagent_readiness.py` 和 `beacon/utils/subagent_runtime.py` 可以收敛出当前最小合同：

1. `runtime-readiness`
   - 宿主可判定
   - 上下文文件存在
   - 全局边界文档已继承
2. `delegation-readiness`
   - `prd`
   - `user-story`
   - `test-case`
   - `implementation-plan`
   - `git-workflow`
   - `qa baseline bundle`
   必须齐全
3. `worker spec`
   - role
   - scope
   - expected output
   - result path
4. `worker result`
   - 独立结果文件
   - 可回收、可等待、可 HUD 展示
5. `team HUD`
   - JSON
   - HTML
   - role status
   - pane/session mapping

### Host-native 规范差异

#### Codex 官方口径

Codex 官方文档给出的关键规范是：

1. subagent workflow 主要用来隔离噪声和并行独立任务
2. Codex 不会自动启用 subagents，必须显式要求
3. 适合先从 read-heavy 并行任务开始
4. write-heavy 并行需要更谨慎，因为会带来写冲突和协调成本
5. 自定义 agent 通过 `~/.codex/agents/` 或 `.codex/agents/` 的 TOML 文件配置
6. 默认 `agents.max_threads = 6`
7. 默认 `agents.max_depth = 1`

这些规则和 Beacon 当前边界高度一致：

- 显式触发
- 浅层深度
- bounded fan-out
- 先读后写

#### Claude Code 官方口径

Claude 的官方口径更强调整个 subagent 产品面：

1. subagent 可以自动或显式委托
2. 每个 subagent 都有自己的系统提示、工具、权限和上下文
3. 可以前台阻塞，也可以后台并发
4. 可以启用 `isolation: worktree`
5. 可以启用 `memory`
6. subagent 不能再 spawn subagent
7. 对于 sustained parallelism 或超出单窗口上下文的任务，应升级到 `agent teams`

对 Beacon 的翻译是：

1. `team` 应吸收 worktree 隔离与后台并行能力
2. 但正式 truth 仍不应下放给 team worker
3. 长任务应由 Ralph 持有 closure，而不是让单个 subagent 无限续跑

---

## 3. 结合 Beacon 已调研开源项目的深度分析

## 3.1 `gstack`：产品化 specialist surface 很强，但不是 Beacon 的主轴

`gstack` 最强的不是“多 agent”，而是：

1. 把高价值流程产品化成 specialist surfaces
2. 有持久运行时
3. 有分层验证与运维自改进意识

Beacon 应吸收的部分：

1. specialist surface 的清晰度
2. 持久 runtime + status/HUD
3. 先便宜验证，再昂贵验证

Beacon 不应吸收的部分：

1. browser-first worldview
2. 以 skill catalog 数量取代主链治理
3. 让 specialist surface 反向接管 requirement truth

结论：

> `gstack` 给 Beacon 的价值是“产品化执行面和可观测性”，不是“让 Beacon 变成技能工厂”。

## 3.2 `superpowers`：对子代理纪律的启发最大

`superpowers` 对 Beacon 最有价值的不是目录结构，而是四个纪律：

1. 先 brainstorm / plan，再进入执行
2. fresh subagent per task
3. 两段评审梯度：
   - spec compliance
   - code quality
4. controller 负责拆解、问答、重派、整合

这几条直接决定 Beacon 的长任务协议：

1. 需求没收口，不能进长任务执行
2. 每个 worker 只拿必要上下文
3. 评审不是末尾附加项，而是每轮闭环结构
4. 主线程/协调器永远比 worker 更接近真相

结论：

> `superpowers` 提供的是“长任务纪律”，这是 Beacon 真正应该深吸收的部分。

## 3.3 `codex-turbo`：证明 native multi-agent 有实操价值，但更像操作模板

`codex-turbo` 的价值主要在：

1. 把 Codex 原生多智能体能力落成一套可复用配置
2. 强调并发控制、角色区分、developer instruction 注入
3. 证明 multi-agent 的收益来自上下文隔离和职责聚焦

但它更偏“本地配置模板”和“操作方法论”：

1. 重心在如何配置 Codex CLI
2. 边界治理与 formal truth 没有 Beacon 这么重
3. 更适合当实现参考，不适合直接当产品主架构

结论：

> `codex-turbo` 证明了 native subagent 值得用，但没替 Beacon 回答“正式交付链如何持真相”这个更难的问题。

## 3.4 `awesome-codex-subagents`：说明生态很丰富，但 catalog 不是 protocol

这个仓库的价值是：

1. 说明角色 catalog 非常丰富
2. 说明 Codex subagent 的可分工边界很多
3. 给出模型和 sandbox 的典型搭配

但它的局限也很明确：

1. catalog 不等于 workflow
2. 角色数量不等于闭环质量
3. 它更偏“可安装角色市场”，不负责 requirement-to-release 的闭环

对 Beacon 的提醒是：

1. 角色越多，越要收紧 role registry
2. 不应为了角色丰富度而扩张主流程
3. Beacon 需要 protocol first，而不是 catalog first

结论：

> `awesome-codex-subagents` 最适合用来启发角色命名和职责切片，不适合作为 Beacon 闭环协议的主源。

## 3.5 OpenAI Codex 与 Claude Code 官方规范的综合判断

把两边官方文档合起来，Beacon 可以冻结下面这组跨宿主规范：

1. subagent 的核心价值是上下文隔离，不是炫技并行
2. 并行首先服务 read-heavy、自包含子任务
3. write-heavy 必须有 ownership、隔离、顺序和回写 owner
4. 深度默认应浅层，嵌套 spawn 默认禁止
5. 主协调器负责：
   - task split
   - wait
   - synthesis
   - acceptance
6. 对于持续并行、长周期、多轮推进任务，必须升级到 team/closure 模式，而不是无限堆单轮 subagent

---

## 4. 七维 `$brainstorm`：长任务如何做到“凿穿到可交付”

## 4.1 用户维度

### 核心用户

1. release owner
   - 关心当前 feature 能否闭环到放行
2. AI coding agent
   - 关心如何在不丢上下文的前提下稳定执行长任务
3. tech lead / QA owner
   - 关心每轮发现是否真的提升交付确定性

### 潜在用户

- takeover 项目维护者
- 多服务 monorepo owner
- 需要跨多轮浏览器验收的交付团队

### 一定不适合的用户

- 只想做一次性微调的人
- 没有冻结 requirement baseline 的项目
- 对 evidence/gate 没有要求的纯实验环境

## 4.2 场景维度

### 典型场景

#### 场景 A：需求复杂、单轮上下文放不下

- 需要多份参考文档
- 需要多轮研究与比对
- 需要把噪声隔离出主线程

#### 场景 B：多服务或多模块联动

- 需要 planner / architect / implementer / reviewer / tester 分工
- 不能让所有人同时写同一块

#### 场景 C：浏览器 QA 必须多轮推进

- 第 1 轮找到阻断
- 第 2 轮修复后需要重测
- 第 3 轮才真正到 release-ready

### 触发条件

一个任务满足下面任意两条，就应视为长任务候选：

1. 需要多轮 implement + qa
2. 需要并行研究或并行执行
3. 涉及多个服务目录或工作区
4. 有明确 gate / release 压力
5. 单轮对话上下文易污染

## 4.3 业务维度

长任务闭环对 Beacon 的核心业务价值不只是“更自动”，而是：

1. 降低假完成率
2. 降低需求未冻住就开工的返工率
3. 降低 QA 只跑一遍就误判放行的风险
4. 让复杂任务可以稳定落成正式交付包，而不是长聊天记录

### 差异化机会

相对普通多 agent 工具，Beacon 的差异化点是：

1. 真相链有文档锚点
2. 长任务不是自由漫游，而是 formal workflow
3. 终态是“可交付”，不是“agent 说做完了”

## 4.4 技术维度

### 技术挑战

| 挑战 | 难度 | 必要应对 |
|---|---|---|
| 子任务拆解质量 | 高 | 先有 implementation plan，再开 team |
| 写冲突 | 高 | ownership + worktree + bounded concurrency |
| 上下文污染 | 高 | fresh context packaging + summary return |
| 长周期状态丢失 | 高 | Ralph durable state + checkpoints |
| QA 漏验 | 高 | round-based QA + repair handoff + coverage delta |
| 假完成 | 高 | formal review / qa / gate 必经 |

### 最关键的技术结论

1. 长任务要有 state machine，不要只有 prompt
2. 长任务要有 stop state，不要只有 continue
3. 长任务要有 artifact chain，不要只靠 transcript
4. 长任务要把 `implement` 与 `qa` 当作一体两面，不要一前一后松散连接

## 4.5 体验维度

长任务的理想体验不是“我看见很多 agent 在跑”，而是：

1. 我知道当前在哪一轮
2. 我知道为什么继续
3. 我知道为什么停止
4. 我知道现在离可交付还差什么

### 人类默认输出应该收敛为

1. 当前状态
2. 当前阻断
3. 推荐下一步
4. 对应命令或 handoff

复杂度保留在机器面：

- HUD
- worker artifacts
- checkpoints
- round summaries
- scorecards

## 4.6 价值维度

### 最核心价值

1. 功能价值
   - 复杂任务可以稳定闭环
2. 认知价值
   - 人类不再需要手工维持长链条状态
3. 交付价值
   - 最终沉淀的是正式文档和正式工件

### 更深一层的价值

> Beacon 把“会做很久”转成“会稳定推进到停在对的地方”。

这是长任务产品化的关键。

## 4.7 风险维度

| 风险 | 概率 | 影响 | 应对 |
|---|---|---|---|
| 任务拆解错误 | 中 | 大 | freeze 前必须有 implementation plan |
| 并行写冲突 | 高 | 大 | ownership/worktree/顺序合并 |
| QA 变成装饰 | 中 | 大 | Ralph 只能读取正式 QA 输出推进 |
| Ralph 无限循环 | 中 | 大 | round cap + budget cap + stop states |
| 用户看不懂模式 | 高 | 中 | 统一成 `single / team / ralph` 三模式 |
| 机器层过重 | 中 | 中 | 人类面保持 6+3，machine 面隐藏 |

---

## 5. Beacon 长任务的推荐实现协议

## 5.1 五层模型

### Layer 1: Requirement truth

- `brainstorm`
- `prd`
- `user-story`
- `test-case`
- `freeze`

职责：

- 收口问题
- 冻住真相
- 给执行面提供确定输入

### Layer 2: Deterministic execution contract

必须物化：

1. implementation plan
2. git workflow contract
3. service/worktree boundary
4. QA baseline bundle

没有这层，不进入长任务。

### Layer 3: Execution family

三模式语义应继续收敛为：

1. `single`
   - 小范围、低耦合、单 owner
2. `team`
   - bounded worker lanes
   - role registry
   - HUD / tmux / worker artifacts
3. `ralph`
   - 把 `single` 或 `team` 包进 closure loop

### Layer 4: Formal acceptance ladder

每轮最少经过：

1. implement
2. review
3. qa
4. gate decision

有 repair handoff 就继续，没有就停止。

### Layer 5: Release deliverable

最终必须能落成：

1. implementation summary
2. technical implementation archive
3. QA evidence / scorecard
4. Ralph state
5. change doc
6. release decision

## 5.2 推荐状态机

```text
brainstorm
→ requirement clarity review
→ freeze
→ implementation contract ready
→ choose mode(single|team|ralph)
→ implement round
→ formal review
→ qa round
→ closure evaluate
→ continue repair loop | stop
→ release-ready deliverable
```

## 5.3 每轮最小产物

每一轮都至少应写出：

1. `round_id`
2. `executor`
3. `worker refs`
4. `changed_files`
5. `review verdict`
6. `qa findings`
7. `coverage_delta`
8. `repair_handoff`
9. `recommended_next_action`

## 5.4 什么时候不用 Ralph

以下情况不应直接启用 Ralph：

1. requirement 仍有关键未决项
2. implementation plan 还没写出来
3. 只是一个快速单点改动
4. 还处于高频来回讨论期

这时应留在：

- `brainstorm`
- `prd`
- `user-story`
- 或 `implement --mode single`

## 5.5 什么时候必须上 Ralph

以下情况满足两条以上，就应优先考虑 Ralph：

1. 目标是“直到完整可交付”
2. 预期至少两轮 implement + qa
3. 需要 repair handoff 驱动下一轮
4. 有 release 或 gate 压力
5. 有明确预算上限，需要 stop-state 治理

---

## 6. 对 Beacon 的落地建议

## 6.1 规范冻结建议

建议把下面几条冻结成跨版本规范：

1. `Ralph = closure controller`
2. `subagent = bounded execution unit`
3. `team/subagent` 默认留在机器内部
4. `brainstorm` 嵌入 `prd -> user-story`
5. 长任务必须先过 requirement clarity + implementation contract 两道门
6. `single / team / ralph` 是同一 execution family

## 6.2 近期实现建议

### P0

1. 继续统一 `implement` 对外语义，只保留 `single / team / ralph`
2. 把 `ralph-bridge` 完整降级为兼容 alias
3. 在 `status/help` 里稳定显示：
   - 当前 mode
   - Ralph phase
   - Ralph stop state
   - next action

### P1

1. 给 `team` 增加更明确的 ownership / worktree 约束
2. 给每轮 Ralph 增加 round summary artifact
3. 把 QA delta、repair handoff、gate result 都并入 Ralph closure evaluate

### P2

1. 让 `qa` 也有和 `implement` 对齐的 mode 语义
2. 把 browse/replay/autoresearch 统一到 QA execution family 下
3. 给 long-task stop reason 建立更强的可视化和统计

## 6.3 最终判断

这轮研究最终收敛成一个很明确的方向：

> Beacon 不该把“长任务能力”理解成“再多加几个 subagent 和 runner”，  
> 而应把它理解成：  
> **用 `brainstorm` 把需求收口，用 `team/subagent` 把执行拆稳，用 `ralph` 把多轮 implement + qa 凿穿到完整可交付。**

因此真正需要冻结的不是更多命令，而是三条总规则：

1. **真相层不下放**
2. **执行层有边界**
3. **闭环层有终态**

只要这三条守住，Beacon 的长任务能力就会越来越强，但不会演化成失控的通用 agent runtime。
