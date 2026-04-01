# 调研：Beacon v1.1.12 的 requirement-anchor divergence closure 与整体调整方向

**日期**：2026-04-01
**调研方式**：`v1.1.12` 需求链 + Beacon runtime 源码 + `v1.2.0` 产品 skill 调研交叉复核
**目标**：将“需求锚定发散”从口头原则收敛为 Beacon `v1.1.12` 可落地的统一判断合同，并明确后续整体调整方向。

---

## 1. 结论摘要

这轮复核后的核心判断是：

> `v1.1.12` 不应只被定义成“prototype design governance”线，也不应只被定义成“QA 发散更严格”线。
> 它真正要补的是一个 **Requirement Anchor Kernel**：
> 用同一套需求锚定合同，统一约束 prototype、QA、rewrite、project contract drift、takeover baseline 与 learning plane。

当前 Beacon 已经具备两个很重要的基础：

1. 原型链已经接近一个真正的 bounded iteration loop
2. QA 链已经具备 scenario map、precision、confidence calibration 和 continue decision

但两条链还没有被统一到同一个“需求锚定判断系统”里。

结果是：

- 原型可以持续补页面/状态/设计系统，但还缺“这次发散是否仍在需求内”的统一分数
- QA 可以持续补场景，但主要仍按 `scenario_family` 和 `confidence` 驱动，而不是按 requirement anchor 驱动
- learning plane 已经开始从 prototype review / QA audit 里学习，但顶层 subject surface 仍然过粗
- help / status / project profile / takeover gate / version truth 仍未被收口成同一条解释链

一句话：

> Beacon 已经长出了多条局部闭环，但还没有把它们合成一个稳定、准确、不漂移的 judgement kernel。

---

## 2. 当前源码里已经存在的闭环雏形

## 2.1 Prototype 闭环已经比 QA 更成熟

`prototype` 主链当前已经不是简单的 HTML 生成器。

源码中已经存在以下结构：

- `beacon prototype plan`
  - 从 requirement contracts 编译 `prototype-plan.json`
- `compile_design_brief()`
  - 生成 `design-brief.json`
- `compile_design_system_contract()`
  - 生成 `design-system-contract.json`
- `review_prototype_bundle()`
  - 生成 `web-guideline-review.json`
  - 生成 `design_review_outcome`
- `write_prototype_design_rewrite_input()`
  - 将 design review findings 回写为下一轮 rewrite / benchmark 输入

这说明 Beacon 在原型链上已经具备以下能力：

```text
requirements
→ design brief
→ design-system contract
→ prototype rendering
→ web-guideline audit
→ design review outcome
→ iteration writeback
```

这是一条真正的 bounded iteration 雏形。

## 2.2 QA 闭环已有结构，但“锚定判断”仍弱

QA 主链当前已经有：

- `story_scenarios.expand_story_scenarios()`
  - 从 story / AC 派生 scenario map
- `build_feature_qa_precision_artifacts()`
  - 产出 `scenario_results_v2`
  - 产出 `ac_closure`
  - 产出 `feature_scorecard`
- `qa_precision`
  - 维护 calibration model
  - 支撑 `auto_accept / review_required` band

这条链的优点是：

- 已经能表达 evidence sufficiency
- 已经能表达 replay requirement
- 已经能表达 continue / stop_for_repair / ready_for_release

但它当前更像：

```text
scenario family expansion
→ execution evidence
→ confidence calibration
→ closure decision
```

而不是：

```text
requirement anchor resolution
→ bounded scenario divergence
→ anchor fitness judgement
→ evidence judgement
→ closure decision
```

也就是说，QA 现在更擅长判断“这个场景证据够不够”，
还不擅长判断“这个场景本来该不该存在”。

## 2.3 Learning Plane 已经有候选生成，但 contract 还没跟上

`learning_loop` 现在已经能从：

- technical archive rewrite input
- prototype design review rewrite input
- debug issues
- QA audit labels

中生成 learning candidates。

实际候选里已经出现：

- `qa_confidence_policy`
- `qa_evidence_sufficiency_policy`
- `debug_recovery_policy`
- `requirement_rewrite`
- `execution_baseline`

但顶层 contract 仍然把 `subject_surface` 写成：

- `execution_baseline`
- `requirement_rewrite`
- `debug_recovery_policy`

这会导致三层不一致：

1. 文档层说应该有 typed policy families
2. 候选生成层已经长出了更细分类别
3. 顶层 decision engine 却仍然对外暴露粗粒度 contract

结果就是 learning plane 虽然已经“长出形状”，但还不能稳定宣称自己是 typed governance。

---

## 3. 当前最关键的结构缺口

## 3.1 Requirement Anchor 还不是运行时一等对象

`v1.1.12` PRD 已经要求：

- `anchor_ids`
- `anchor_kinds`
- `semantic_scope`
- `divergence_budget`
- `adjacent_capability_flags`
- `Requirement Anchor Score (RAS)`

但这些字段当前还没有正式进入：

- scenario map
- prototype page/state expansion
- rewrite input
- project profile gate
- help/status decision trace

这意味着“需求锚定发散”目前还是文档约束，不是 runtime truth。

## 3.2 原型链和 QA 链还没有共享一套锚定合同

原型当前能编译：

- design brief
- design-system contract
- design prompt

QA 当前能编译：

- story scenario map
- precision artifacts
- scorecard

但二者还没有共享以下合同：

- 需求语义边界
- 相邻能力边界
- divergence budget
- allowed expansion domains
- blocked semantic families

所以才会出现典型风险：

- prototype 在表达“开屏视频上传/展示”
- QA 却可能按“视频播放器”思路继续发散

## 3.3 confidence 不等于 anchor fitness

当前 QA 的 calibrated confidence 有价值，但它衡量的是：

- 执行结果可靠度
- evidence 完整度
- replay 是否存在

它并不直接衡量：

- 是否仍在需求语义内
- 是否越过项目 contract
- 是否跳到了相邻产品能力

所以 `confidence` 不能替代 `RAS`。

最合理的模型应该是：

```text
Anchor fitness
×
Evidence fitness
→
Can execute / review / block
```

而不是只靠单一 confidence。

## 3.4 Profile / Takeover / Version Truth 仍未并入同一 decision trace

`help_support` 当前虽然会看：

- feature scorecard
- project profile gate
- workflow blocking reasons

但仍存在：

- QA stop reason 直接推回 `native-single`
- doc frozen 后直接推 native implementation
- profile-aware first 仍未彻底变成默认顺序

`project_skills.run_profile_orchestration()` 当前也仍会：

- 读取 `command_template`
- 渲染命令
- 直接 `shell=True` 执行

这说明执行边界、需求锚定、项目 contract、版本真相，尚未收成同一条解释链。

---

## 4. Requirement-anchor divergence 真正该落在哪些面

## 4.1 原型面

应该允许的 requirement-anchored 发散：

- page additions
- state additions
- route/state completeness
- design-system normalization
- guideline-fix writeback

应新增的运行时对象：

- `prototype_anchor_contract.json`
- `page_anchor_scorecards.json`
- `state_anchor_scorecards.json`

每个新增页面/状态都应携带：

- 来源 AC / PRD section
- semantic scope
- divergence budget
- adjacent capability flags
- `prototype_anchor_score`

这样 Beacon 才能判断：

- 这个页面/状态是否应该补
- 是真实需求内补齐，还是已经漂成相邻产品

## 4.2 QA 面

应该允许的 requirement-anchored 发散：

- happy
- negative
- boundary
- recovery
- compatibility

但前提是仍然回挂到：

- PRD requirement
- AC
- project contract
- replay/evidence truth

应新增的运行时对象：

- `scenario_anchor_map.json`
- `qa_anchor_scorecard.json`
- `drift_decisions/<run-id>.json`

这里的核心不是让 QA 更保守，而是让 QA 发散时始终知道：

> 我是沿着需求在扩，还是跳到了另一个产品语义。

## 4.3 Rewrite 面

当前 Beacon 已经在做：

- technical archive -> requirement rewrite input
- prototype review -> rewrite input

下一步应把 rewrite 也 anchor 化：

- `rewrite_anchor_score`
- `rewrite_target_kind`
- `anchor_support_refs`

避免 rewrite 把一轮局部观察误升格成整个需求方向。

## 4.4 Profile / Contract Drift 面

`rolo` 这类项目的：

- service-slice map
- evidence contract
- consumer/reference service declarations

不应只在 blocked 时被“读一眼”，而应进入 requirement anchor contract 作为只读输入。

这样 system 才能判断：

- 当前发散是否越过项目边界
- 当前测试是否落到了错误 execution surface

## 4.5 Takeover 面

takeover 项目最该引入的不是更多 workflow，而是：

- current-state manifest
- service backlog
- subsystem summary
- frozen baseline truth

这块应借鉴 `v1.2.0` 调研里从 `claude-code` 提炼出的做法：

- manifest-first
- backlog-first
- thin CLI reporting
- minimal verification surface

这样 takeover 的 current-state truth 才不会被 feature 发散覆盖。

---

## 5. 其他仍可继续闭环的场景

## 5.1 Prototype review -> QA recommendation

当前原型 review 已经能发现：

- URL state 问题
- generic 风格问题
- accessibility / guideline 问题

下一步可以把这些 finding 映射成：

- 推荐新增哪些 QA scenarios
- 推荐新增哪些 replay obligations
- 推荐哪些 requirement clarifications

这样 design governance 和 QA 不再是平行流程，而会彼此增强。

## 5.2 QA finding -> prototype/state gap writeback

反方向也可以成立：

- 如果 QA 一直在某个 state family 上失败
- 而 prototype 中又没有对应 state artifact

那么系统应能判断：

- 这是 prototype completeness gap
- 不是单纯执行失败

这能让 prototype 和 QA 在同一语义面上继续收敛。

## 5.3 Contract drift -> requirement writeback

项目 profile 的 drift 现在更多表现为 blocked reason。

下一步更稳的做法是：

- 不只 blocked
- 还把 drift 显式回写为 requirement/contract mismatch candidate

这样 contract drift 不只是一种“阻断”，还是一种“输入修正”。

## 5.4 Current-state manifest -> help/status/report

takeover / rewrite 项目最需要的不是更多命令，而是更真实的 summary surface。

这块建议增加：

- `current-state manifest`
- `port backlog`
- `subsystem summary`

并让 help/status/report 都直接消费它们。

---

## 6. 结合 `v1.2.0` 调研后的整体调整方向

`v1.2.0` 调研给出的关键启发，不是“要多做几个 PM 命令”，而是：

- skill body
- facilitation protocol
- command orchestration
- discovery metadata

对 `v1.1.12` 来说，这个启发应该这样落：

## 6.1 v1.1.12 先做 Judgement Kernel

先不要急着扩更多生成命令。

应优先完成：

- version truth state model
- profile-aware routing
- capability-bounded project adapters
- requirement anchor kernel
- typed learning plane

也就是先把“判断系统”收稳。

## 6.2 v1.2.0 再做 PM Skill Wrapper

当前 `persona / jtbd / roadmap / analyze` 仍在：

- 输出 `docs/product/...`
- 更像模板生成器

这与 `v1.2.0` 调研建议一致：

- 不要继续堆模板命令
- 应改为 skill-wrapper
- 正式输出回收到 `docs/beacon/<version>/`

因此合理顺序是：

1. `v1.1.12` 稳住 judgement kernel
2. `v1.2.0` 再重构前链路 skill-wrapper 与 discovery surface

## 6.3 Product 心智应保持不变

Beacon 不应变成：

- 纯 PM skill library
- 纯 prototype generator
- 任意 shell orchestrator

Beacon 应保持为：

> 一个 evidence-first workflow kernel。
> 在新功能交付上接 PM skill system；
> 在 takeover / rewrite 项目上接 migration governance surface；
> 在 prototype / QA / review / rewrite 上统一 requirement-anchor judgement。

---

## 7. 推荐优先级

## P0：先稳边界真相

- 单一 version truth 状态机
- profile-aware navigator
- capability-bounded project orchestration
- takeover baseline gate

## P1：建立 Requirement Anchor Kernel

- 定义统一 anchor schema
- prototype / QA / rewrite 共用
- 引入 `RAS`
- 引入 adjacent-semantics drift blocker

## P2：完成 Typed Learning Plane

- 顶层 contract 与候选分类对齐
- prototype / QA / contract / rewrite / debug / benchmark 变成正式 subject surfaces
- keep/discard 学习只允许修改 judgement surfaces

## P3：进入 `v1.2.0` 风格的 skill-wrapper / discovery

- `think / user-story / prd` skill-wrapper uplift
- `persona / jtbd / roadmap / analyze` 输出路径与方法论重构
- `beacon skill recommend`
- `beacon skill search`

---

## 8. 最终结论

`v1.1.12` 的正确定位，不应只是：

```text
design governance
```

也不应只是：

```text
QA divergence tightening
```

而应是：

```text
version truth
+ execution-boundary stabilization
+ requirement-anchor divergence governance
+ typed learning-plane closure
```

其中最关键的一步是：

> 把 Requirement Anchor 变成 Beacon 的统一判断合同，让 prototype、QA、rewrite、profile gate、takeover summary 与 learning plane 都围绕它工作。

这一步完成后，Beacon 才可能真正做到：

- 稳定
- 准确
- 不漂移

并为 `v1.2.0` 的 PM skill-wrapper / discovery surface 奠定正确基础。
