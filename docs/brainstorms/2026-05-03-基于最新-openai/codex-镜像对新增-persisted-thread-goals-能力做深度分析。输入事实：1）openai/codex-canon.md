# Beacon Brainstorm

## prompt_summary
基于最新 openai/codex 镜像对新增 persisted thread goals 能力做深度分析。输入事实：1）openai/codex canonical mirror 已同步到最新 main；2）goal 相关能力在最近提交中分 1/5 persistence foundation、2/5 app-server API、3/5 model tools、4/5 core runtime、5/5 TUI UX 连续落地；3）当前对外模型工具为 get_goal/create_goal/update_goal，其中 create_goal 只能在用户或系统明确要求时创建，update_goal 只能标记 complete，pause/resume/budget_limited 由用户或系统控制；4）runtime 模板包含自动 continuation prompt 与 budget_limit prompt；5）目标状态、token/time usage、thread notifications、app-server thread/goal/set 与 thread/goal/updated 已存在。请结合 Beacon v1.3.11 冻结材料，重点回答：A. goal 能力的真实产品语义是什么，不要只复述接口；B. 它解决了 Codex 之前哪类长任务断裂；C. 它与 Beacon 当前 runtime kernel / board / status / release 思路有哪些重合与差异；D. 如果 Beacon 要吸收这类能力，最小 requirement delta 是什么，哪些应进入 requirement truth，哪些属于 truth 之外的执行层；E. 从 first principles / socratic / occam 三个角度给出收敛结论。要求：只读分析，不改写 frozen truth，用中文，偏严格、专业、少空话。

- version: `v1.3.11`
- mode: `project-evolution`
- feature: ``

## version_material_refs
- `docs/beacon/global-boundaries.md` (present, required)
- `docs/beacon/v1.3.11/SUMMARY.md` (present, optional)
- `docs/beacon/v1.3.11/execution/index.md` (present, optional)
- `docs/beacon/v1.3.11/execution/architecture-blueprint.md` (present, optional)
- `docs/beacon/v1.3.11/prd/beacon-execution-runtime-kernel.md` (present, optional)
- `docs/beacon/v1.3.11/prd/beacon-operator-workbench-and-board-launcher.md` (present, optional)
- `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md` (present, optional)
- `docs/beacon/v1.3.11/prd/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md` (present, optional)
- `docs/beacon/v1.3.11/prd/prototype-design-intelligence-and-governed-rendering-separation.md` (present, optional)
- `docs/beacon/v1.3.11/user-story/beacon-execution-runtime-kernel.md` (present, optional)
- `docs/beacon/v1.3.11/user-story/beacon-operator-workbench-and-board-launcher.md` (present, optional)
- `docs/beacon/v1.3.11/user-story/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md` (present, optional)
- `docs/beacon/v1.3.11/user-story/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md` (present, optional)
- `docs/beacon/v1.3.11/user-story/prototype-design-intelligence-and-governed-rendering-separation.md` (present, optional)
- `docs/beacon/v1.3.11/qa/test-cases/beacon-execution-runtime-kernel.md` (present, optional)
- `docs/beacon/v1.3.11/qa/test-cases/beacon-operator-workbench-and-board-launcher.md` (present, optional)
- `docs/beacon/v1.3.11/qa/test-cases/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md` (present, optional)
- `docs/beacon/v1.3.11/qa/test-cases/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md` (present, optional)
- `docs/beacon/v1.3.11/qa/test-cases/index.md` (present, optional)
- `docs/beacon/v1.3.11/qa/test-cases/prototype-design-intelligence-and-governed-rendering-separation.md` (present, optional)

## confirmed_facts
- Beacon version material root is docs/beacon/v1.3.11.
- This sidecar is read-only against Beacon requirement truth.
- Frozen PRD, user-story, test-case, prototype, and .machine artifacts are not rewritten by brainstorm.
- Resolved project topology: single_repo.
- Resolved execution service: beacon.
- Resolved canonical branch: beacon/v1.3.11.

## assumptions_under_test
- The prompt may represent a requirement gap, an evolution idea, or implementation-risk question until mapped to frozen evidence.
- Any accepted requirement change must be routed through the Beacon requirement/change loop before implementation.

## first_principles_breakdown
- 用户价值: identify the irreducible user outcome before proposing mechanism.
- 证据约束: every implementation idea must trace back to frozen PRD/user-story/test-case evidence.
- 闭环约束: if evidence is missing or changing, return to requirement/change routing instead of implementing.

## socratic_questions
- What exact user outcome would fail if this idea is not implemented?
- Which frozen acceptance criterion proves this idea is required?
- What evidence would falsify this proposed direction?
- If this is an evolution, what is the smallest safe requirement delta?

## redundancy_cuts
- Remove implementation mechanisms that cannot be tied to frozen acceptance evidence.
- Remove duplicate document-to-document reconciliation; use canonical Beacon truth or route a change.
- Remove broad roadmap speculation unless it produces a concrete next Beacon route.

## material_signals
- → implement
- - 它位于 `test-case` 与 `implement` 之间
- ### 4. `implement` 与 `qa` 仍是唯一执行入口
- - `implement` 仍是唯一实现入口
- - verifier / repair-handoff-writer / implementation-architect 等内部角色协作
- ### 6. 预检查必须内嵌到 `implement` / `qa`
- - `implement`
- - `implement / qa / release` 只能沿这条链闭环，不得反向改写 requirement truth

## project_metadata
- metadata_ref: `.beacon/metadata/project-version-metadata.json`
- topology_kind: `single_repo`
- selected_service: `beacon`
- selected_branch: `beacon/v1.3.11`

## converged_recommendation
Treat this as an evolution candidate. Capture options in brainstorm output first, then route accepted scope through beacon-prd or beacon-change.

## next_route
beacon-prd or beacon-change

---

## 深度分析结论

### A. `goal` 能力的真实产品语义

`openai/codex` 新增的 `persisted thread goals`，本质上不是“多了一个 slash 命令”或“多一组模型工具”。

它的真实产品语义是：

> 把长期目标从“当前 prompt 里的临时意图”提升为“线程级、可持久、可恢复、可计量、受 runtime 托管的 objective state”。

这意味着它正式引入了一个新的运行态对象：

- 目标不是一段提示词
- 目标不是一次 turn 的局部上下文
- 目标不是由模型自行决定何时开始、何时暂停、何时预算耗尽

而是一个由 runtime 持有、模型只在有限边界内读写的长期 objective contract。

从当前代码与模板看，这个 contract 至少明确了：

- objective 文本
- status
- token budget
- tokens used
- time used
- complete 的唯一模型可写状态
- pause / resume / budget_limited 的系统或用户控制边界
- goal continuation prompt
- budget-limit steering prompt

因此，`goal` 不是 prompt engineering 技巧，而是一种 thread-scoped runtime primitive。

### B. 它解决了 Codex 之前哪类长任务断裂

它主要解决四类断裂：

#### 1. Objective persistence 断裂

此前长任务在多轮推进时，objective 主要依赖：

- 当前 prompt
- 历史消息
- 模型自身短期记忆

这导致：

- 中断后不知道当前长期目标是否仍然有效
- 同一线程无法稳定承载一个持续 objective
- 后续恢复时难以区分“新的任务”与“继续同一个目标”

`goal` 把这一点显式化了。

#### 2. Completion boundary 断裂

以前“任务是否完成”更多依赖模型临时判断。

现在 Codex 明确把边界改成：

- objective 未完成，不得调用 `update_goal`
- `update_goal` 只能标记 `complete`
- completion 必须做 evidence audit，而不是靠主观感觉

这等于把“完成条件”从软语义提升成 runtime contract。

#### 3. Budget accounting 断裂

此前 token/time 的消耗虽然存在，但不绑定到长期 objective。

现在 objective 自身就带：

- token budget
- tokens used
- time used
- budget limited state

这使长期任务第一次有了 objective 级 accounting。

#### 4. Resume / continuation 断裂

之前恢复更多是“恢复线程”，不是“恢复目标”。

现在 continuation prompt 明确要求：

- 继续朝 active goal 推进
- 避免重复工作
- 做 completion audit
- 若 budget reached，则转入收束而不是继续扩张工作

这本质上修复了 long-running turn 的连续性问题。

### C. 它与 Beacon 当前 runtime kernel / board / status / release 思路的重合与差异

#### 重合点

1. 都在解决“单轮 prompt 心智不足以承载长任务”的问题
2. 都开始把运行态对象正式建模
3. 都强调恢复、继续、阻断、预算之类的状态不应靠人工心智维持
4. 都在往 operator-visible runtime surface 演进

#### 差异点

Codex `goal` 的中心对象是：

- thread-scoped objective

Beacon 当前 `v1.3.11` 的中心对象是：

- requirement truth
- feature / revision / release closure
- run / workspace / evidence / ordering 的执行治理

所以两者的侧重点不同：

- Codex goal 更偏“持续执行中的 objective runtime”
- Beacon 更偏“需求真相与交付闭环治理”

再具体一点：

| 维度 | Codex `goal` | Beacon `v1.3.11` |
| --- | --- | --- |
| 主对象 | thread goal | feature / revision / run / release |
| 主要问题 | 长任务 objective persistence | requirement truth + delivery governance |
| 状态边界 | active / paused / budget_limited / complete | frozen / reopened / accepted / blocked / retry 等多层状态 |
| 完成判断 | goal completion audit | requirement + QA + release closure |
| 主要宿主 | runtime / app-server / TUI | docs + machine mirrors + support surfaces + emerging runtime layer |
| 当前强项 | runtime continuity | truth governance |

因此它们不是同类替代品，而是两套不同重心的系统能力。

### D. 如果 Beacon 要吸收这类能力，最小 requirement delta 是什么

Beacon 不应直接复制 `goal` 命令外形，而应抽取它的最小运行语义。

最小 requirement delta 应该是：

#### 1. 新增正式运行实体

建议增加一个正式运行实体，例如：

- `ExecutionObjective`
或
- `RunObjective`

该实体至少需要：

- objective
- scope binding
- owner surface
- status
- budget contract
- completion contract
- evidence linkage

#### 2. 明确状态机

至少要有：

- `active`
- `paused`
- `budget_limited`
- `complete`

并明确：

- 哪些状态由 operator 改
- 哪些状态由 system 改
- 哪些状态可被 model 显式声明

#### 3. 明确与 run / workspace / release 的绑定方式

Beacon 不能把它做成孤立对象，必须说明：

- objective 绑定哪个 run
- objective 是否跨 run 持续
- objective 与 workspace drift / recovery 的关系
- objective 完成是否影响 release readiness

#### 4. 明确 board / status 的读取 contract

如果 Beacon 吸收这类能力，`status` 与 `board` 都必须正式读取：

- current objective
- objective status
- budget usage
- recommended next action

否则 objective 只存在于底层 runtime 而不可见，价值会打折。

#### 进入 requirement truth 的部分

应进入 requirement truth 的，是正式 contract：

- objective entity 的存在
- objective 状态机
- objective 与 run/workspace/evidence 的绑定
- objective completion contract
- objective 在 board/status/recovery 中的可见性

#### 不应进入 requirement truth 的部分

不应写死到 truth 的，是具体执行实现：

- continuation prompt 的 wording
- TUI 菜单细节
- app-server transport 细节
- state-db 表设计
- semaphore / resume trigger 的内部实现

这些属于 truth 之外的执行层。

### E. 从 first principles / socratic / occam 三个角度的收敛结论

#### First principles

用户真正需要的，不是“告诉模型再继续一下”，而是：

- 让长期目标在中断后仍然存在
- 让系统知道现在究竟在追什么
- 让继续、暂停、收束、完成变成正式 runtime 行为

`goal` 命中的是这个根因。

#### Socratic

需要追问的不是“Beacon 要不要也做 /goal”，而是：

- Beacon 当前缺的是命令，还是缺 objective runtime primitive？
- Beacon 的长期目标是 feature 级、run 级，还是 thread 级？
- 哪些 objective 状态必须被 release / board / recovery 消费？
- 如果 objective 不进入 truth，执行层是否还能自洽？

这些问题都指向同一个结论：

- Beacon 缺的不是 UI 命令，而是 objective-level runtime modeling。

#### Occam

最小正确吸收方式不是：

- 复制 Codex 的 `/goal`
- 复制同名工具
- 复制 TUI 行为

最小正确方式是：

- 给 Beacon runtime kernel 增加 objective entity
- 只定义必要状态与边界
- 让 board / status / recovery 正式消费它

也就是说，应吸收其“runtime primitive”，而不是其“交互皮肤”。

---

## 对照表：Codex goal capability -> Beacon current gap -> Beacon minimal delta

| Codex goal capability | Beacon current gap | Beacon minimal delta | 建议进入后续版本 |
| --- | --- | --- | --- |
| 线程级持久 objective | 缺少 objective-level runtime object | 新增 `ExecutionObjective`/`RunObjective` | 是 |
| objective 状态机 | 缺少 active/paused/budget_limited/complete 明确边界 | 定义 objective status contract | 是 |
| objective 级 token/time accounting | Beacon 当前更偏 run/release evidence，缺 objective accounting | 为 objective 增加 budget / usage 字段 | 是 |
| 自动 continuation prompt | Beacon 缺 objective-aware continuation runtime | 在执行层增加 continuation steering，不写入 truth wording | 否，属于执行层 |
| budget-limit steering | 缺 objective 级“到预算就收束”语义 | 增加 `budget_limited` 状态与 operator-visible handling | 是 |
| app-server goal notifications | Beacon board/status 还缺 objective 更新事件面 | 为 board/status 增加 objective read/update event surface | 是 |
| TUI `/goal` UX | Beacon 没有 objective-first operator interaction | 后续可做 CLI/board interaction，但不应先行 | 否，先不进 truth |
| 模型只能 complete，不能 pause/resume | Beacon 尚未明确 objective state ownership | 明确 model/operator/system 的状态权限边界 | 是 |
| goal completion audit | Beacon 有 release closure，但缺 objective completion audit contract | 增加 objective completion verification contract | 是 |
| persisted thread requirement | Beacon runtime kernel 仍未完全实体化持久执行宿主 | 把 objective 绑定到 persisted run/runtime host | 是 |

---

## 最终收敛

`openai/codex` 新增的 `goal` 能力，最值得 Beacon 学习的不是命令形式，而是以下三个 runtime 原则：

1. 长期目标必须成为正式运行态对象，而不是 prompt 里的约定
2. completion boundary 必须由 contract 限制，而不是靠模型自由发挥
3. objective 的状态权必须拆开：模型、系统、用户各自可改的范围不同

对 Beacon 来说，这一能力最自然的吸收位置不是 support surface，而是：

- `execution runtime kernel`
- `status / board` 的运行态可见层
- `recovery / continue / retry` 的执行治理层

如果后续要进入正式版本演进，建议 route 到：

- `beacon-prd`
或
- `beacon-change`

但应以“runtime objective modeling”命名，而不是直接以“goal command”命名。
