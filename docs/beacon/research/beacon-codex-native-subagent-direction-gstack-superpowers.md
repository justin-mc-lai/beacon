# Research: Beacon codex-native subagent direction from `gstack`, `superpowers`, and the v1.3.0 seed note

**Date**: 2026-04-13  
**Intent**: 将原本放在 `docs/beacon/v1.3.0/research/` 下的子代理方向稿，提升为跨版本全局研究，并补入 `gstack` 与 `superpowers` 两个外部参考项目的可复用结论。  
**Seed note**: [`../v1.3.0/research/beacon-v1.3.0-codex-native-subagent-direction.md`](../v1.3.0/research/beacon-v1.3.0-codex-native-subagent-direction.md)  
**External references**:

- [`gstack` repository](https://github.com/garrytan/gstack)
- [`gstack` architecture note](https://raw.githubusercontent.com/garrytan/gstack/main/ARCHITECTURE.md)
- [`superpowers` repository](https://github.com/obra/superpowers)
- [`Superpowers for Codex`](https://raw.githubusercontent.com/obra/superpowers/main/docs/README.codex.md)
- [`superpowers/skills/brainstorming/SKILL.md`](https://raw.githubusercontent.com/obra/superpowers/main/skills/brainstorming/SKILL.md)
- [`superpowers/skills/writing-plans/SKILL.md`](https://raw.githubusercontent.com/obra/superpowers/main/skills/writing-plans/SKILL.md)
- [`superpowers/skills/subagent-driven-development/SKILL.md`](https://raw.githubusercontent.com/obra/superpowers/main/skills/subagent-driven-development/SKILL.md)
- [`superpowers/skills/using-git-worktrees/SKILL.md`](https://raw.githubusercontent.com/obra/superpowers/main/skills/using-git-worktrees/SKILL.md)

**Verified local source directories**:

- canonical source map:
  [`./beacon-open-source-reference-source-map.md`](./beacon-open-source-reference-source-map.md)
- `gstack`:
  `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack`
- `superpowers`:
  `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/superpowers`
- historical refs from the original seed note:
  - `codex-turbo`:
    `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/codex-turbo`
  - `awesome-codex-subagents`:
    `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/awesome-codex-subagents`

---

## 1. Why this note is global, not version-bound

原 `v1.3.0` 子代理方向稿虽然是沿着 `v1.3.0` 需求线写出来的，但它讨论的其实不是单次 release 问题，而是更稳定的跨版本问题：

1. Beacon 到底应不应该引入 Codex-native 子代理
2. 如果引入，边界该如何治理
3. 阶段 owner、worker、evidence、writeback 应如何分层
4. 外部 agent workflow 项目里，哪些模式值得复用，哪些必须拒绝

这些问题会反复影响后续 release line，不应该继续埋在单版本 `research/` 目录里。

因此，这篇文档的角色不是“某次版本内调研附件”，而是：

> Beacon 关于 Codex-native 子代理治理、采用边界与外部参考映射的全局研究入口。

版本线以后只消费这里的结论，再把属于该版本的 adoption slice 落到 `docs/beacon/<version>/execution/`。

---

## 2. Executive summary

三个输入放在一起后，可以把 Beacon 的正确方向压缩成一句话：

> Beacon 应吸收 `gstack` 的“产品化 specialist workflow + 持久运行时/验证分层”能力，吸收 `superpowers` 的“强制阶段纪律 + fresh subagent per task + review ladder”能力，但仍坚持 Beacon 自己的主轴: `PRD -> user-story -> QA` 证据链，以及 stage owner 持有 canonical truth。

这意味着 Beacon 不该变成：

- 通用多代理操作系统
- 任何事情都能 delegate 的开放 runtime
- 第二套独立 truth / memory plane

而应变成：

- 有边界的阶段 orchestrator
- 只在特定 surface 上启用 bounded subagents
- 由 stage owner 做正式 writeback
- 由 workers 生产 run-scoped evidence
- 由 versioned execution materials 决定当前 release line 采用哪一部分能力

最重要的新增判断有六条：

1. Codex-native 子代理研究应归入 `docs/beacon/research/` 全局目录，而不是锁在单一版本下。
2. `implement` 与 `qa` 仍是最适合稳定采用多代理的两个 surface。
3. 子代理的核心 contract 不只是 “能 spawn”，而是：
   - fresh context packaging
   - explicit ownership
   - bounded depth
   - review-before-acceptance
4. Beacon 应借鉴 `superpowers` 的阶段硬门，但不能把所有简单改动都强制升级为完整长链 ceremony。
5. Beacon 应借鉴 `gstack` 的 specialist/productized surface，但不能把自己重构成 browser-first skill factory。
6. 全局研究负责“为什么与怎么治理”，版本线负责“这一版实际采用哪些切片”。

---

## 3. Beacon first-principles reminder

在吸收任何外部项目之前，Beacon 的第一原则必须先固定：

1. Beacon 的根不是通用 agent runtime。
2. Beacon 的根是 evidence-first product workflow kernel。
3. Beacon 的主链仍然是：
   `PRD -> user-story -> QA`
4. `implement` 和 `qa` 可以拥有强执行面，但 requirement truth 不应该下放给 worker。
5. release truth、gate、version semantics、docs/beacon 正式材料，必须继续由 Beacon 自己持有。

因此，任何外部借鉴都必须回答一个问题：

> 它是在强化 Beacon 的主链，还是在诱导 Beacon 偏离主链？

只有前者值得引入。

---

## 4. Input A: what the v1.3.0 seed note already got right

原始 `v1.3.0` 方向稿已经做对了几件关键事：

1. 明确拒绝“把 Beacon 扩成通用多代理 runtime”。
2. 把第一个真正多代理 adopter 锁定在 `implement run`。
3. 把 worker 输出定义为 evidence，而不是第二事实源。
4. 强调 role registry 和 bounded team contract，比“自由 prompt delegation”更重要。
5. 指出 `implement-team` 与 `qa-team` 应该分层治理、上下文隔离。
6. 把版本语义治理与子代理治理绑定在一起，避免命令面各自解释。

但这篇旧稿还有两个局限：

1. 它仍然带着明显的 `v1.3.0` 语境，容易被误读成“一次性 release note”。
2. 它只纳入了较早的外部参考，没有把 `gstack` 和 `superpowers` 这种更成熟的 workflow/skill/subagent 实践一起吸收进来。

这就是本次上提成全局研究的理由。

---

## 5. Reference B: what Beacon should learn from `gstack`

从当前 `gstack` 仓库公开材料可以看到三层特别强的东西。

### 5.1 Productized specialist workflow surface

`gstack` 不是只提供几个脚本，而是把能力打包成大量明确分工的 specialist surfaces：

- `/office-hours`
- `/plan-ceo-review`
- `/plan-eng-review`
- `/review`
- `/qa`
- `/ship`
- `/browse`
- `/learn`

这给 Beacon 的启发不是“技能越多越好”，而是：

1. 当一个高价值流程稳定后，应该有清晰的 operator surface。
2. “规划/审查/QA/发布”这些不同角色，最好是显式产品面，而不是隐含在一个总命令里。
3. 用户心智是 role + workflow，不是内部实现器名字。

对 Beacon 的翻译是：

- `implement-team`
- `qa-team`
- `version`
- `gate`
- `release`

这些 surface 都应该是用户可理解的稳定入口，而不是只有内部 runtime 语义。

### 5.2 Persistent runtime + tiered verification mindset

`gstack` 在架构说明里强调两件事：

1. 复杂 agent workflows 需要持久状态，而不是每次冷启动
2. 验证要分层，先跑便宜检查，再跑昂贵验证

虽然 `gstack` 的具体 runtime 是 browser daemon，这不是 Beacon 当前最需要照搬的部分；但它背后的方法论很值得吸收：

1. 让高成本能力有稳定运行时，而不是命令临时拼接
2. 让验证形成梯度，而不是所有检查都同价
3. 让文档、命令、校验之间尽量同源，减少 drift

对 Beacon 的翻译是：

- team runtime / tmux HUD / run-scoped evidence 应继续被视为一等运行时，而不是一次性脚手架
- `doctor / verify / gate / release` 应继续走分层校验路线
- team mode 的 operator 文档、machine contract、execution blueprint 应保持同源

### 5.3 Specialist catalog and distribution discipline

`gstack` 还展示了一个重要判断：

1. 角色集合可以很大，但必须是产品化 catalog，而不是任意散落 prompt
2. 同一套 workflow 能被多个 host agent 消费
3. 技能/命令的 discoverability 本身是一种产品能力

对 Beacon 的启发是：

1. 如果未来 Beacon 要继续扩 team roles，应该优先建设清晰 catalog，而不是追加隐式角色。
2. host-specific adapter 可以存在，但治理 contract 应由 Beacon 自己定义。
3. “当前 release line 支持哪些 roles / runtime / gate” 应该由 versioned materials 宣布，而不是靠用户猜。

### 5.4 What not to copy from `gstack`

Beacon 不应直接复制这些部分：

1. browser-first worldview  
   `gstack` 的核心难点是持久浏览器；Beacon 的核心难点不是浏览器，而是 requirement truth 与 evidence chain。
2. 巨大的 slash-skill catalog 作为产品主轴  
   Beacon 仍应以 product workflow kernel 为中心，而不是以 skill 数量为中心。
3. 让外部 specialist surface 反过来接管 canonical requirement writeback  
   这会破坏 Beacon 的主链。

---

## 6. Reference C: what Beacon should learn from `superpowers`

`superpowers` 的价值更直接落在“Codex-native skills + subagent workflow discipline”上。

### 6.1 Hard-gated phase progression

`superpowers` 的核心工作流很清晰：

1. `brainstorming`
2. `using-git-worktrees`
3. `writing-plans`
4. `subagent-driven-development` 或 `executing-plans`
5. `test-driven-development`
6. `requesting-code-review`
7. `finishing-a-development-branch`

这不是“建议顺序”，而是被 skill 文档明确成 hard gate 的强制工作流。

对 Beacon 的启发非常强：

1. 子代理不是先出现的，设计和计划先出现。
2. 进入执行面前，隔离工作区、计划粒度、测试纪律、评审梯度都应该被明确定义。
3. 多代理最有效的地方，不是“更自由”，而是“更守纪律”。

### 6.2 Fresh subagent per task

`superpowers` 的 `subagent-driven-development` 反复强调一个原则：

> 每个任务一个 fresh subagent；controller 不把整段 session history 直接塞给 worker，而是自己打包最小必要上下文。

这和 Beacon 现有设计高度一致，也进一步强化了全局 contract：

1. worker 不应继承控制器的全部上下文。
2. worker 只应该拿到：
   - 当前任务
   - 所需文件
   - 上一轮必要结论
   - 明确的 done condition
3. controller 负责拆分、提问、重派、整合、验收。

这应成为 Beacon 子代理治理的全局规则，而不是单版本实现细节。

### 6.3 Review ladder after implementation

`superpowers` 不是“子代理写完就算结束”，而是明确要求：

1. implementer 完成
2. spec compliance review
3. code quality review
4. final review / branch finish

这给 Beacon 的关键启发是：

1. 子代理治理的核心，不只是 spawn policy，还包括 acceptance ladder。
2. `implement-team` 最终稳定形态不应只是 planner/implementer/reviewer/tester 并列，而应把 review 顺序显式化。
3. `qa-team` 也应该有类似的 verify / repair-handoff / final acceptance 阶梯。

### 6.4 Worktree isolation as a first-class rule

`superpowers` 把 `using-git-worktrees` 做成强制技能，而不是“工程师自己想起来再用”。

这与 Beacon 当前在 `v1.3.0` 对 git workflow contract 的推进是高度兼容的：

1. 分支
2. worktree
3. service roots
4. clean baseline verification

这些都不该藏在全局配置里，而应作为 execution-scoped contract 被声明。

### 6.5 What not to copy from `superpowers`

Beacon 不应一比一照抄这些部分：

1. 对每个简单任务都强制完整 brainstorming/spec/plan ceremony  
   Beacon 已有阶段系统，应该区分“正式 feature workflow”与“小范围维护动作”。
2. 把 plan 细化到极小任务文本模板，作为 Beacon 唯一交付方式  
   这对某些工程任务有效，但 Beacon 还需要兼容 requirement-side materials。
3. 把 TDD 教条本身抬升成 Beacon 的顶层产品定义  
   TDD 可以是 implement runtime discipline，不应覆盖 Beacon 的产品主链定义。

---

## 7. Synthesis: the global Beacon direction

把原始 `v1.3.0` 方向稿、`gstack`、`superpowers` 放在一起后，Beacon 的跨版本方向可以固定为下面七条。

### 7.1 Beacon should adopt bounded subagents, not open delegation

全局默认应是：

- 子代理默认关闭
- 只有特定 surface 显式开启
- 最大深度浅层可控
- ownership 必须声明
- writeback 只能由 stage owner 执行

### 7.2 Beacon needs a stage-role catalog, not a flat worker pile

角色至少应按下面几层分开治理：

1. implementation execution
2. qa verification and repair handoff
3. planning critique / research
4. meta orchestration / coordinator

这同时吸收了：

- 原始 seed note 对 stage role registry 的判断
- `gstack` 的 specialist catalog productization
- `superpowers` 的 task-specific worker discipline

### 7.3 Beacon needs a review ladder, not just worker completion

建议把全局 acceptance ladder 固定成类似结构：

1. worker self-check
2. spec / contract compliance review
3. code or artifact quality review
4. stage-owner acceptance
5. gate / release integration

这样“worker finished”不再等于“stage accepted”。

### 7.4 Beacon should keep requirement truth single-owner

当前跨版本稳定判断仍然是：

- `think`
- `user-story`
- `prd`
- `test-case`

这些阶段的正式材料面依旧应该是单 owner writeback。

它们可以引入：

- research assistance
- critique roles
- evidence lanes

但不应直接变成多 writer parallel truth surface。

### 7.5 Beacon should treat `implement` and `qa` as the main stable multi-agent adopters

这不是偶然，而是因为两个阶段都具备：

1. 比较成熟的 execution contract
2. 可以与 truth 面分层
3. 更自然的 review / verify / repair 闭环

后续 release lines 即使扩面，也应先围绕这两条线继续硬化。

### 7.6 Beacon should separate global governance research from release adoption

未来相关文档的正确分层应是：

- `docs/beacon/research/`
  - 为什么需要这类能力
  - 外部项目带来什么启发
  - 全局治理原则是什么
- `docs/beacon/<version>/execution/`
  - 这一版实际启用了什么
  - 哪些 surface 可用
  - 哪些 contract 被 runtime 消费
- `docs/beacon/<version>/research/`
  - 单一 release 的临时调研、问题排查、版本内特化分析

### 7.7 Beacon should define host-agnostic contracts, then adapt per host

`superpowers` 展示了 Codex skill discovery / multi-agent flag 的 host-specific 配置方式；`gstack` 展示了多 host distribution 的产品化方向。

Beacon 更合理的做法是：

1. 先定义 host-agnostic governance contract
2. 再让 Codex / Claude / 其他 host adapter 去消费这个 contract

而不是让 host 的安装方式反向定义 Beacon 的产品边界。

---

## 8. What this means for Beacon's global research project layout

这次上提后，Codex-native 子代理相关研究建议固定成如下结构。

### 8.1 Canonical global note

本文件就是 canonical note，负责保存：

1. 外部参考项目借鉴
2. Beacon 全局治理判断
3. 适用边界与反例

### 8.2 Version consumption rule

每个 release line 如果要消费这条研究，应只做两件事：

1. 在 `SUMMARY.md` / `execution/index.md` 中把它列为上游研究入口
2. 在本版本 execution materials 中明确：
   - adopted surfaces
   - adopted roles
   - adopted runtime mode
   - non-goals

### 8.3 Future related research placement

以后这类内容原则如下：

- 研究外部 agent workflow / skill / subagent 项目，并抽象为长期可复用治理结论:
  放 `docs/beacon/research/`
- 针对某个版本落地过程中的具体偏差、bug、验证问题:
  放 `docs/beacon/<version>/research/`

---

## 9. Immediate Beacon decisions that now look stable

基于当前材料，下面这些判断已经足够稳定，可以视作后续 release line 的默认前提：

1. Beacon 不做通用 agent OS。
2. Beacon 允许 bounded Codex-native subagents。
3. `implement` 与 `qa` 是稳定 adopter surfaces。
4. stage owner 继续持有 canonical truth。
5. workers 只生产 run-scoped evidence。
6. fresh context packaging 是硬规则。
7. review ladder 是子代理能力的一部分，不是附加项。
8. worktree / branch / service-root contract 应进入 execution materials，而不是只躲在用户全局配置。
9. 外部参考项目研究默认应先归入全局研究，再由版本线消费。

---

## 10. One-sentence conclusion

`gstack` 让 Beacon 更清楚怎样把 specialist workflow 和稳定运行时产品化，`superpowers` 让 Beacon 更清楚怎样把子代理执行纪律化，而原 `v1.3.0` seed note 说明 Beacon 已经知道自己不该变成通用 runtime；三者合并后的正确结论是：

> Beacon 的 Codex-native 子代理方向应当成为跨版本全局治理研究，由版本线按需采纳切片，而不是继续作为单一 release 的内嵌调研稿存在。
