# Beacon v1.4.0 OPSX Borrowing Map and Missing Boundaries

## 1. 目标

本稿基于以下输入，分析 OpenSpec 的 OPSX 工作流当前对 Beacon `v1.4.0` 最有借鉴意义的点，以及 Beacon 目前尚未显式收敛的边界面。

输入依据：

- `oss-sync/automation/autoresearch/openspec/docs/opsx.md`
- `oss-sync/automation/autoresearch/openspec/docs/workflows.md`
- `oss-sync/automation/autoresearch/openspec/docs/concepts.md`
- `oss-sync/automation/autoresearch/openspec/src/commands/change.ts`
- `oss-sync/automation/autoresearch/openspec/src/commands/workflow/instructions.ts`
- `docs/beacon/global-boundaries.md`
- `skills/beacon/using-beacon/SKILL.md`
- `beacon/commands/archive.py`
- `beacon/commands/help.py`
- `beacon/commands/workflow.py`
- `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`

重点问题：

1. OPSX 哪些机制值得 Beacon 借鉴
2. 哪些点必须改写后才能适配 Beacon
3. 哪些边界是 Beacon 目前还未充分显式化的
4. `implement` 缺少 `tasks.md checkbox progress` 这类执行面，说明了什么结构性缺口

## 2. 高置信度结论

高置信度结论如下：

- OPSX 对 Beacon 最有价值的，不是“公开命令集合”，而是“artifact-guided workflow contract”
- Beacon 已经有比 OPSX 更强的：
  - global boundary
  - requirement freeze
  - gate
  - host-runtime / Ralph
  - archive governance
- 但 Beacon 比 OPSX 弱的地方主要在：
  - 人机共读的执行账本
  - 变更单元的聚合可见性
  - 轻量 artifact progress 面
  - 面向人类的“下一步动作可理解性”

换句话说：

> Beacon 不需要变成 OPSX，但应该吸收 OPSX 那种“以 artifact 为执行驱动、以可见 progress 为协作面、以 change unit 为组织单元”的轻量优点。

## 3. 第一性原理对比

### 3.1 Beacon 的强项

Beacon 当前强项是：

- 跨版本 global-boundaries
- `docs/beacon/<version>/**/*.md` 唯一冻结真相
- `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`
- gate 对 completion/blocking 的强定义
- host-runtime 与 Ralph 的执行闭环
- archive 是正式治理动作，而不是简单目录搬迁

OPSX 当前并不具备 Beacon 这类“冻结真相 + gate + release acceptance”强治理深度。

### 3.2 OPSX 的强项

OPSX 当前强项是：

- artifacts 是显式工作单元
- change 是显式容器
- workflow 是 action-oriented，不是埋在代码里的黑箱
- per-artifact instruction / schema / template 可调
- `tasks.md` 作为人机共读进度账本非常轻
- 并行 change、archive、progress、validate 的人类面非常直观

Beacon 当前并不缺 contract 深度，但缺这类“低摩擦协作可见性”。

### 3.3 因此真正应借鉴的不是“谁更强”，而是结构互补

Beacon 应借鉴 OPSX 的点，是为了补足：

- 人类可理解执行面
- 轻量进度面
- change container 可见性
- artifact dependency 明示

而不是削弱 Beacon 自己已经很强的：

- freeze truth
- gate
- archive governance
- global boundaries

## 4. OPSX 最值得借鉴的点

## 4.1 借鉴点一：artifact-guided workflow

OPSX 的核心不是 phase，而是 artifacts + dependencies。

对 Beacon 的借鉴意义：

- Beacon 的 requirement chain 已经是 artifact chain
- 但 implement/change/archive/support 层还没有完全做到 artifact-guided
- `workflow/help/status` 虽能给出下一步，但对人类来说仍偏 machine/read-model 视角

建议 Beacon 借鉴为：

- 每个关键动作都绑定明确 artifact
- 每个 artifact 都绑定依赖、状态、下一步 unlock 关系
- `help/status` 优先回答：
  - 现在卡在哪个 artifact
  - 下一个可推进 artifact 是什么
  - 为什么不是别的

### 4.2 借鉴点二：change container 作为可见工作单元

OPSX 的 `change` 很清楚：

- 一个 change 一个目录
- proposal / specs / design / tasks 围绕它组织
- list/show/validate/archive 都围绕它

对 Beacon 的借鉴意义非常高：

- Beacon 当前 change 语义散落
- 需要更强的一等 change identity
- 需要更强的 per-change visibility

Beacon 应吸收：

- 单一 change unit
- 单一 change summary
- 单一 change progress view
- 单一 change archive chain

### 4.3 借鉴点三：`tasks.md` 作为人机共读的实现账本

这是当前 Beacon 最值得立即吸收的点之一。

OPSX 明确把：

- `tasks.md`
- checkbox
- N/M progress
- blocked / all complete

作为 apply 阶段的人类主观察面。

Beacon 当前虽然已经有：

- implementation plan markdown
- implementation plan json
- implementation progress json
- next_task_id
- blocked_task_ids
- mapped AC/test/scenario/QA ids

但它缺少 OPSX 这种简单、强可读、低认知成本的：

> “人类和 agent 同时看的任务账本”

这意味着 Beacon 当前 `implement` 有 machine plan，但缺：

- 人类面持续可读 progress ledger
- 逐任务完成的简单操作协议
- “完成一项就 visibly close 一项”的轻反馈面

这不是小问题，而是当前 Beacon `implement` 人类面仍偏：

- machine-centric
- contract-rich
- execution-heavy

而缺：

- task-visible
- progress-readable
- interruption-friendly

### 4.4 借鉴点四：instruction 外显与可局部测试

OPSX 强调：

- prompt/template/schema 可改
- 单 artifact 可独立测试
- 不是全埋在代码里

对 Beacon 的借鉴意义：

- Beacon 现在很多 compile / implement / help / brainstorm 行为仍偏“代码逻辑内生”
- 后续 `v1.4.0` 若要减负，应该尽量把：
  - contract schema
  - route rule
  - artifact dependency
  - implement task rendering
  外显化

不是为了开放无限自定义，而是为了：

- 降低黑箱度
- 提高可验证性
- 提高演进速度

### 4.5 借鉴点五：progress / archive / validate 的轻量人类反馈面

OPSX 很擅长告诉用户：

- 当前 change 是 complete / in-progress / no-tasks
- tasks 完成了多少
- archive 前缺什么
- validate 发现了什么

Beacon 现在也能回答这些问题，但路径更深：

- `help`
- `status`
- `gate`
- `report`
- `.machine/...`

对熟悉系统的人够强，但对人类主面来说偏重。

Beacon 可以借鉴 OPSX 的轻反馈逻辑：

- 用更少概念展示更多状态
- 默认展示最关键 blockers
- 把复杂 read-model 留在下层

## 5. Beacon 已有但可以借 OPSX 再强化的点

## 5.1 `global-boundaries` 对应 OPSX 的 project context，但 Beacon 更强

OPSX 有 `config.yaml context/rules` 注入。  
Beacon 有 `docs/beacon/global-boundaries.md`。

两者相似点：

- 都提供贯穿 artifact 的上位上下文

Beacon 更强的地方：

- 它是跨版本 canonical boundary，不是可随意漂移的局部配置

Beacon 可借鉴的不是“变成 project config”，而是：

- 增加 boundary projection 到各 artifact 的显式 trace
- 让每个 artifact 更清楚显示“受哪些全局边界约束”

也就是说，应借 OPSX 的“context injection 可见性”，不是借它的“自由配置强度”。

### 5.1A Beacon 还缺一个显性的人类面全局上下文/边界子 skill

这是当前非常值得补齐、但还没有被显式命名的一条边界缺口。

现状是：

- Beacon 已有 `docs/beacon/global-boundaries.md`
- AGENTS.md 已要求它作为 canonical Beacon-wide global constraint source
- 各子流程理论上都应受其约束

但人类面仍缺少一个直接可用的、显式围绕“项目全局上下文 / 边界 / 版本线级约束”工作的子 skill 或命令面。

这带来三个问题：

1. **discoverability 不足**
   - 知道 Beacon 深层结构的人会主动读 `global-boundaries.md`
   - 但普通用户或新线程不会自然想到“先校准全局边界”
2. **human-loop 校准入口不足**
   - 当用户想问“这个需求是否违反 Beacon 全局边界”
   - 或“当前版本线是否应该吸收某条上位原则”
   - 目前没有一个显式的人类面入口来处理
3. **project-level context operations 缺统一承载面**
   - 比如全局原则解释
   - 上下文边界 diff
   - 新版本线承接哪些 global constraints
   - 哪些外部借鉴已经正式吸收、哪些仍只是研究样本

OPSX 在这方面给 Beacon 的启发不是“照搬 config.yaml”，而是：

> 上位上下文不仅要存在，还要有显式的人类面操作入口。

也就是说，Beacon 需要的不一定是一个新的一级命令，但至少需要一个正式子 skill，例如语义上接近：

- `beacon-boundaries`
- `beacon-context`
- 或 `beacon-global-boundaries`

它的职责应是：

- 解释 Beacon 全局边界
- 校准当前问题是否越界
- 判断某条新原则应进入 `global-boundaries`、版本 PRD，还是只保留在 brainstorm
- 让人类可以显式做“全局上下文对齐”，而不是只能隐式依赖底层文档

这条能力很重要，因为 Beacon 的强项之一恰恰是：

- 有跨版本 boundary truth

但如果没有显式 human surface，它就会出现：

- 内核上存在
- 对人类主面不明显
- 实际使用依然靠熟悉者记忆

这是典型的“能力存在，但 surface 不可见”问题。

## 5.2 `archive` 对应 OPSX archive，但 Beacon 需要更轻的 operator surface

Beacon 的 `archive` 已经比 OPSX 更成熟：

- 是正式治理动作
- 有 archive status model
- 有 support projection

但 Beacon 仍可借鉴 OPSX 的地方：

- archive 前的人类可读 readiness 提示
- archive 后的简洁 change closure summary
- archive 对当前 work queue 的影响可见性

Beacon 不缺 archive 语义，缺的是 archive 的低摩擦可理解面。

## 5.3 `using-beacon` 对应 OPSX generated skills，但 Beacon 缺更清楚的 public workflow card

OPSX 很强调：

- 用户可以看到可用动作
- action 的用途直观可读

Beacon 也有：

- `using-beacon`
- `beacon-help`
- `beacon-status`

但仍偏“已知 Beacon 的人使用起来顺手”，对新进入者来说缺一层更轻的：

- public workflow card
- route matrix card
- common path vs advanced path 的明确差异

这是一层 human-surface packaging gap。

## 6. Beacon 目前还未充分显式化的边界面

## 6.1 边界一：人类可读任务账本 vs 机器执行计划

当前 Beacon 有 machine 计划，却缺一份足够清晰的：

- human-readable tasks ledger
- checked / unchecked progress contract
- blocked reason directly attached to task view

这正是你指出的 `Tasks track progress via checkboxes in tasks.md` 缺口。

应明确新增边界：

- machine plan 负责结构、traceability、gate
- task ledger 负责人类面 progress 协作

两者不能互相替代，但应来自同一 canonical implementation plan。

## 6.2 边界二：change truth vs change execution surface

Beacon 正在补 change kernel，但还需更明确区分：

- change truth document
- compiled change contract
- change execution progress
- change archive summary

否则 change 会继续散落在：

- reopen/freeze
- change-impact
- release aggregation

而看不出“当前 change 到底推进到哪”。

## 6.3 边界三：workflow action surface vs lifecycle truth surface

OPSX 的优势之一是 action 很直观。  
Beacon 的约束之一是 lifecycle 不能膨胀。

Beacon 还需更明确这条边界：

- lifecycle truth surface:
  - `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`
- action surface:
  - continue
  - refresh
  - refreeze
  - apply
  - verify
  - archive

也就是说，Beacon 可以借鉴 OPSX 的 action thinking，但不能把 action 变成新的一级主流程。

## 6.4 边界四：artifact dependency visibility

OPSX 很擅长表达：

- 什么 ready
- 什么 blocked
- 缺什么 dependency
- 做完这个会 unlock 什么

Beacon 现在也有相当多依赖关系，但对人类主面表达不够显式。

当前 Beacon 还缺一个正式边界：

> artifact dependency graph 是需要被人类面投影出来的，不应只存在于机器推理里。

## 6.5 边界五：并行 change / 并行 implement 的可见性

OPSX 显式支持 parallel changes。  
Beacon 当前虽有强 metadata / runtime / Ralph，但对“并行变更工作单元”的人类面表达还不够。

Beacon 未来至少要明确：

- active changes
- active implement runs
- 哪些 share 同一 version line
- 哪些冲突或互斥

这是多 change 治理面，当前还未充分显式化。

## 6.6 边界六：中断恢复的人类面

OPSX 的任务勾选天生适合：

- 中断
- 恢复
- 切换 change

Beacon 当前虽然有：

- run state
- Ralph state
- workflow memory
- next_task_id

但它对人类恢复语义还不够直观。

Beacon 还应显式收敛：

- 当前任务做到哪
- 哪个 task 被阻断
- 恢复时先做什么
- 哪些 task 不应重复做

## 6.7 边界七：全局上下文边界的人类面操作入口

当前 Beacon 已有：

- 全局边界 truth
- AGENTS/skill/runtime 中的隐式引用

但仍缺：

- 显式的人类面入口来“操作全局边界上下文”

这导致一个常见问题：

- 用户知道有 feature 级 PRD / story / test-case
- 但不知道什么时候该先回到全局边界面校准问题

因此 Beacon 应显式增加一个边界：

> global boundary truth 与 feature truth 之间，需要一个 human-usable context operation surface。

这个 surface 至少应支持：

- 解释当前全局边界
- 判断当前需求是否越界
- 判断外部规范应吸收到全局边界还是只停留在研究层
- 判断某条原则应进 global-boundaries 还是进单个版本线

这不是新增主流程，而是补齐 Beacon 上位上下文能力的人类面可操作性。

## 7. Beacon 不应照搬 OPSX 的点

## 7.1 不应照搬“fluid not rigid”到 requirement truth

OPSX 强调 fluid actions。  
Beacon 不能把这条原则直接套到 truth closure 上。

因为 Beacon 的核心是：

- freeze truth
- gate completion
- anti-drift

所以 Beacon 只能借：

- action fluidity

不能借：

- truth fluidity

## 7.2 不应照搬公开命令扩张

OPSX 命令很多，但 Beacon 已有 global-boundaries：

- 不新增新的公开一级主命令
- 人类面极简

所以 Beacon 不能直接照搬 `/opsx:new /continue /ff /verify /bulk-archive` 这种风格。

可以借鉴的是它们背后的内部能力，而不是公开命令数量。

## 7.3 不应照搬弱 gate 模式

OPSX 适合 lightweight spec workflow。  
Beacon 则承担更强的：

- requirement closure
- QA acceptance
- release blocking

所以 Beacon 不能为了变轻而削弱 gate。

## 8. 对 `implement` 缺失 `tasks.md checkbox` 的专项判断

这是当前非常值得补齐的一块，而且补齐后不会违背 Beacon 核心边界。

### 8.1 为什么它值得补

因为它同时解决四个问题：

1. 让人类看到执行进度
2. 让 agent 执行时有更低摩擦的 task ledger
3. 让中断恢复更直观
4. 让 archive / QA / help 的“完成度”更容易投影

### 8.2 为什么它不会破坏 Beacon

只要坚持以下规则，它不会破坏 Beacon：

- `tasks.md` 不是 truth
- `tasks.md` 不是 gate 真相
- `tasks.md` 不是 release 准入真相
- `tasks.md` 是 implementation-plan 的 human projection

也就是说：

> Beacon 应该拥有 `tasks.md`，但它应当是 implementation contract 的人类投影，而不是平行执行真相。

### 8.3 正确落法

建议落法：

- canonical source:
  - `implementation-plan-<feature>.json`
- human projection:
  - `execution/tasks-<feature>.md`
- machine progress:
  - `implementation-plan-<feature>.progress.json`

同步规则：

- JSON plan 决定 task identity / dependency / traceability
- `tasks.md` 只负责可勾选进度与人类面阻断提示
- progress json 负责 machine status 聚合

### 8.4 gate 如何消费

gate 不应直接以 checkbox 为唯一依据。  
正确方式是：

- checkbox progress 是辅助信号
- 真正 closure 仍以 implementation evidence、QA evidence、traceability 为准

这样能兼得：

- 人类好用
- 机器可审计

## 9. 建议的借鉴地图

## 9.1 直接可借鉴

- change container visibility
- artifact dependency visibility
- task progress ledger
- archive 前后的人类可读 closure summary
- action-oriented help/status phrasing

## 9.2 需要本地化改写后借鉴

- context/rules injection
- global context human surface
- apply/verify/archive 流程
- parallel changes
- customization/schema 外显
- workflow profile

## 9.3 不应照搬

- 公开命令扩张
- fluid truth model
- 弱 gate
- 用 task completion 替代 acceptance closure

## 10. 结论

OPSX 对 Beacon `v1.4.0` 的最大启发不是“再多做一套 workflow”，而是：

> 在不破坏 Beacon 冻结真相、gate、archive、host-runtime 闭环的前提下，把变更单元、任务进度、artifact 依赖、人类下一步动作这些执行协作面做得更轻、更直观。

Beacon 当前最值得优先吸收的点有三：

1. `change` 的 container 化与可见化
2. `implement` 的 `tasks.md checkbox progress ledger`
3. `help/status/archive` 的 action-oriented human projection

再往前一层，还应补齐一个上位支点：

4. `global-boundaries` 的显性人类面操作子 skill

## 11. 输出 contract

```json
{
  "schema_version": "2.0",
  "artifact": "beacon_brainstorm_convergence",
  "version": "v1.4.0",
  "mode": "project-evolution",
  "domain": "code",
  "prompt_summary": "Assess which OPSX ideas from OpenSpec are genuinely valuable for Beacon v1.4.0, especially around context, archive, human-facing skills, workflow, change containerization, and task progress ledgers.",
  "source_truth_refs": [
    "docs/beacon/global-boundaries.md",
    "docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md"
  ],
  "confirmed_facts": [
    "Beacon already has stronger global truth and gate governance than OPSX.",
    "Beacon currently lacks a lightweight human-readable implementation task ledger equivalent to OPSX tasks.md checkboxes.",
    "Beacon change visibility is still weaker than OPSX's explicit change container model.",
    "Beacon has global-boundaries truth but still lacks a direct human-facing subskill for global context/boundary operations."
  ],
  "assumptions_under_test": [
    "A tasks.md projection can be added without creating a second execution truth source.",
    "Beacon can improve action-oriented human surfaces without violating its global boundary against public command sprawl."
  ],
  "contradictions": [
    "Borrowing OPSX action fluidity is useful, but borrowing truth fluidity would conflict with Beacon freeze/gate semantics.",
    "Borrowing task ledgers is useful, but allowing checkbox completion to define acceptance truth would be incorrect."
  ],
  "open_questions": [
    "What is the exact projection contract between implementation-plan.json, tasks.md, and progress.json?",
    "How should Beacon expose parallel changes and interrupted task recovery on the human surface?",
    "What is the correct human-facing subskill surface for global boundary/context operations?"
  ],
  "route_candidates": [
    "beacon-user-story",
    "beacon-change"
  ],
  "recommended_route": "beacon-user-story",
  "recommended_target_artifact": "user-story",
  "confidence": {
    "overall": "high",
    "evidence_sufficiency": "high",
    "route_confidence": "high"
  },
  "closure_state": "supplement_required",
  "closure_reason": "The borrowing opportunities are clear, but Beacon still needs explicit stories for task-ledger projection, change visibility, action-oriented support surfaces, and parallel/interrupted execution boundaries.",
  "next_step_command": "beacon-user-story"
}
```
