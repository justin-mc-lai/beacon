# PRD: Beacon 闭环控制层、恢复层与学习层增强（v1.1.9）

## 1. 背景

Beacon v1.1.8 已经完成一条较完整的交付主干：

- `workflow`：承接 `think → user-story → prd → [prototype] → test-case → implementation → verify → gate`
- `implement`：产出 `implementation-summary-*` 与 `technical-implementation-*`
- `qa`：已经成为主入口，并支持 session 保存与状态查询
- `debug`：已经支持 prompt sync、project-feed、harvest、issue/idea 聚合
- `review / gate / release`：已经形成 evidence / traceability / coverage / delivery 的治理面

从代码与文档现状看，Beacon 已有以下关键基础：

1. **生命周期记忆与阶段上下文**
   - `beacon/commands/workflow.py`
   - `beacon/utils/workflow_memory.py`
2. **QA session 与状态化验收入口**
   - `beacon/commands/qa.py`
   - `beacon/utils/qa_runtime.py`
3. **实现结果技术归档与评审回写**
   - `beacon/commands/implement.py`
   - `beacon/commands/review.py`
4. **实践反馈采集与 issue/idea 收敛**
   - `beacon/commands/debug.py`
   - `beacon/utils/debug_feedback.py`
5. **Gate 证据检查与 traceability 审核**
   - `beacon/commands/gate.py`

所以 v1.1.9 的问题已经不再是“缺不缺一个新命令”，而是：

> 如何基于现有 Beacon 功能面，把需求、实现、验证、反馈、恢复与下一轮版本输入真正串成 **抗失败、抗假完成、能持续学习** 的闭环？

### 1.1 当前关键断点

虽然 v1.1.8 已经具备很多能力，但还存在 4 个关键缝隙：

1. **Debug 健壮性不足**
   - 现在能采集反馈，但还不能正式表达 failure streak / escalation / strategy switch
   - resume 后仍可能重复试同一路径

2. **QA 验证健壮性不足**
   - 现在有 `qa`、`review quality`、`gate`，但“实现完成”与“证据完成”还未严格拆层
   - 缺少 requirement delta 驱动的 targeted rerun 语义

3. **需求到实现的 trace contract 不够显式**
   - 现在有 story / AC / test-case / technical archive / coverage
   - 但 requirement → implementation → evidence 三层约束还没有冻结成正式 contract

4. **技术实现反哺不够清晰**
   - 现在能生成 technical archive，也能 harvest debug
   - 但还没有正式桥接到下一轮 requirement rewrite / baseline uplift / version planning

### 1.2 来自 v1.1.9 研究输入的直接启发

当前 v1.1.9 已有两份直接研究输入：

- `docs/beacon/v1.1.9/research/beacon-pua-exhaustiveness-layer-analysis.md`
- `docs/beacon/v1.1.9/research/beacon-karpathy-autoresearch-evo-analysis.md`

它们给出的核心启发分别是：

#### A. Exhaustiveness / Recovery 启发
不是引入人格化高压，而是引入：

```text
failure signal
→ escalation state
→ methodology switch
→ evidence hard-stop
→ recoverable loop
→ structured checkpoint/resume
```

#### B. Evo / Keep-Discard 启发
不是直接让 Beacon 自改整仓，而是先建立：

```text
small editable surface
→ fixed budget experiment
→ single main KPI
→ keep / discard discipline
→ real benchmark corpus
```

因此，v1.1.9 的正确方向是：

> 在 v1.1.8 交付主干之上，正式引入 **控制层（control plane）+ 恢复层（recovery plane）+ 学习层（learning plane）**。

### 1.3 当前代码级现实判断：主链强闭环，外围与 QA 仍有断点

本轮分析不只参考设计文档，也直接对照了当前代码实现：

- `beacon/commands/workflow.py`
- `beacon/utils/workflow_memory.py`
- `beacon/commands/freeze.py`
- `beacon/commands/reopen.py`
- `beacon/utils/revision_state.py`
- `beacon/utils/story_state.py`
- `beacon/commands/implement.py`
- `beacon/commands/review.py`
- `beacon/commands/gate.py`
- `beacon/commands/qa.py`
- `beacon/commands/auto_test.py`
- `beacon/commands/test_case.py`
- `beacon/utils/coverage.py`
- `beacon/utils/v110_baseline.py`

得出的现实结论是：

#### A. 正式交付主链已经比较强
当前 Beacon 已经具备：

1. lifecycle 主链与 next-step 导航
2. freeze / reopen revision 生命周期
3. implement → review → gate → release 的正式治理
4. coverage、spec fingerprint、baseline snapshot、delivery manifest 等正式检查

也就是说，**v1.1.8 当前正式 release line 是能闭环交付的**。

#### B. 但“所有生命周期、所有端口”的防漂移还没有完全闭环
当前仍有几类明显断点：

1. **baseline 语义多中心**
   - `revision_state.py`
   - `story_state.py`
   - `v110_baseline.py`
   三处都在表达 baseline / fingerprint / drift，但口径并未完全统一。

2. **入口端口仍有 README / skill / CLI 语义错位**
   - 文档中的 `beacon qa run "<feature>" --profile ...` 心智
   - 与 `qa.py -> auto_test.create(scope, ...)` 的实际实现
   之间仍存在偏差。

3. **debug / resume 仍偏“有采集、有恢复入口”，但缺少强控制语义**
   - 有 `debug`、`project-feed`、`harvest`
   - 有 `resume` / `workflow continue`
   - 但还没有 failure streak / escalation / strategy switch / checkpoint hypothesis restore

4. **skill / installed copy / managed block 虽有 doctor 检查，但还不是全链硬门禁**
   - 有 `installed_skill_copy_drift`
   - 有 `managed_block_version_drift`
   - 有 command catalog / sync script
   - 但 root README / root skill / packaged skill / CLI 语义一致性仍未完全自动化锁死

#### C. QA 子命令当前并不能“实现完毕后根据用户故事依次进行 QA 验证”
这是本轮分析里最关键的现实差距之一。

当前实际情况是：

1. `test-case create` 会从 `user-story` / `prd` 提取 AC，生成：
   - `ac-test-matrix`
   - `qa9-matrix`
2. `qa run` 只是转发到 `auto-test create`
3. `auto-test create` 的主模型是：
   - scope-driven
   - layer/matrix-driven
   而不是 feature-driven / story-sequential

因此当前 Beacon 能做到的是：

```text
story/AC -> matrix
matrix -> auto-test execution
execution -> coverage/review/gate
```

但还做不到：

```text
implement done
→ qa run <feature>
→ 自动定位该 feature 的 user-story/test-case matrix
→ 按用户故事 / AC 顺序逐项验证
→ 逐项 writeback verification state
```

另外，文档中多次提到的 `beacon qa evolve` 当前还只是设计语义，不是已实现命令。

这意味着 v1.1.9 必须把下列差距正式收口为 requirement，而不是继续停留在“设计上想要”。 

## 2. 第一性原理结论

### 2.1 v1.1.9 的职责不是替代 v1.1.8 主链

v1.1.9 不应新造一套平行 lifecycle。

它应该是对现有主链的覆盖增强：

```text
v1.1.8 = delivery kernel
v1.1.9 = control + recovery + learning overlay
```

也就是：

- Delivery plane：继续沿用 `workflow / implement / qa / review / gate / release`
- Control plane：新增证据门禁、失败升级、模式路由
- Learning plane：新增 archive/debug → next requirement/version 的正式回流

### 2.2 真闭环必须至少覆盖 4 层

#### 层 A：执行层
- 任务怎么跑
- 当前阶段是什么
- 产生了哪些输出

#### 层 B：证据层
- 哪些 claim 有验证
- 哪些 evidence 缺失
- 当前是否真的 gate-ready

#### 层 C：恢复层
- 失败后是否切换了策略
- 下次继续时是否保留已排除路径与下一假设
- 是否进入 recoverable loop 而不是草率退出

#### 层 D：学习层
- 哪些高频摩擦进入了 debug issue/idea
- 哪些技术事实要反哺 PRD/test-case
- 哪些动作应升级为 execution baseline

Beacon 如果只做到 A/B，就还是“可用工作流”；
要做到 A/B/C/D，才会变成“真正闭环内核”。

## 3. 目标

1. **把 v1.1.8 已有交付面串成一个更强的闭环控制层**
2. **让 debug 具备 failure escalation / checkpoint / resume 的正式语义**
3. **让 qa / review / gate 能区分 implementation_done 与 evidence_done**
4. **让 requirement → implementation → evidence 的三层 trace contract 冻结下来**
5. **让 technical archive 与 debug harvest 能正式反哺下一轮 requirement rewrite 与 version planning**
6. **为后续 evo harness 提供真实 benchmark corpus，但不在本版直接开放整仓自治**

## 4. 非目标

1. 不引入人格化高压提示系统或 PUA 风格外壳；
2. 不在 v1.1.9 直接把 Beacon 变成“自改整仓”的自治系统；
3. 不替换 v1.1.8 已稳定的 `workflow / implement / qa / review / gate / release` 命令主面；
4. 不要求 v1.1.9 一次性实现完整 persistent browser daemon；
5. 不要求所有项目都开启 evo harness；
6. 不让 debug/qa 退化成业务日志平台或全量观测平台。

## 5. 核心设计

## 5.1 三层增强架构

### A. Delivery Plane（沿用现有能力）
- `workflow`
- `implement`
- `qa`
- `review`
- `gate`
- `release`
- `debug`

### B. Control / Recovery Plane（v1.1.9 新增重点）
- evidence hard-stop
- exhaustiveness escalation
- execution mode router
- checkpoint / resume contract
- recoverable loop contract

### C. Learning Plane（v1.1.9 新增重点）
- debug harvest → issue / idea
- technical archive → requirement rewrite input
- version research → keep/discard decision
- execution baseline uplift
- evo harness input corpus

## 5.1.1 Skill 文档清晰化：root / packaged 一主一辅

v1.1.9 不只要强化 runtime 闭环，也要强化 **operator surface**。

当前 Beacon 的 skill 入口有两层：

- root `SKILL.md`
- `skills/beacon/SKILL.md`

如果两者结构和定位不稳定，会直接导致：

1. 用户不知道哪份文档是“完整产品说明”
2. 安装态 / 打包态 / 仓库态 reader 看到的说明不一致
3. 下一轮新增内容时继续漂移

因此 v1.1.9 必须把 skill 文档也纳入闭环治理：

### A. 角色分工
- root `SKILL.md` = **主文档 / main product document**
- `skills/beacon/SKILL.md` = **辅文档 / supplementary package document**

### B. 固定结构模板
两份 skill 文档必须稳定覆盖：

1. 当前版本 / 发布线
2. 产品定位
3. 适合谁 / 不适合谁
4. Quick Start / 快速上手
5. Workflow Model / 主工作流模型
6. Current Product Surfaces / 当前产品面
7. Why This Skill Matters / 为什么重要
8. Recommended Reading Order / 推荐阅读顺序
9. Common Usage Modes / 常见使用场景
10. Command / Wrapper Surface / 命令入口
11. Lifecycle Navigation Rules / 阶段导航规则
12. Docs / Troubleshooting / Examples / References

### C. 同步规则
- 产品说明内容冲突时，以 root `SKILL.md` 为准
- 标准 skill 包装与目录约定，以 `skills/beacon/SKILL.md` 为准
- 任一版本线更新 release line / workflow model / operator guidance 时，必须同步更新两份 skill 文档

这件事看起来像“文档整理”，但本质上属于 v1.1.9 的闭环增强：

> **如果 skill 入口本身不清晰，用户就无法稳定进入 Beacon 的 requirement → implementation → evidence → gate 主链。**

## 5.1.2 防漂移闭环增强：从“主链强”升级到“全端口强”

v1.1.9 不能只满足于“正式 release line 能交付”，还必须把防漂移检查从主链扩展到所有关键端口：

### A. Lifecycle 主链
- workflow stages
- freeze / reopen / revision lifecycle
- implement / review / gate / release

### B. Operator 入口端口
- README
- root `SKILL.md`
- `skills/beacon/SKILL.md`
- command catalog / sync script
- help / doctor / status

### C. Runtime / Evidence 端口
- `.beacon/qa/`
- `.beacon/debug/`
- `.beacon/implement/`
- `.beacon/memory/`
- `.beacon/state/baselines/`

### D. Installed Copy / Managed Block 端口
- `~/.agents/skills/beacon`
- `~/.codex/skills/beacon`
- `~/.claude/skills/beacon`
- managed block version / context file integrity

当前这些面并不是都没有治理；而是：

> **已有检查点，但还没有被统一编进一个“全端口 anti-drift closure contract”。**

v1.1.9 要补的不是某一个点，而是把这些检查点统一成一个版本级 requirement：

- 入口不能讲一套、实现跑一套
- baseline 不能三套定义并存而没有 canonical contract
- skill/README/CLI 不能在 feature-oriented 与 scope-oriented 之间来回漂移
- doctor 检查不能只提示，还要成为 requirement-level consistency surface

## 5.2 Debug 健壮性闭环

现有基础：
- `beacon debug enable / sync-prompts / project-feed / harvest`
- `workflow_memory` 已支持 stage / attempt / checkpoint 相关事件
- `beacon resume` / `beacon workflow continue`

v1.1.9 新增要求：

### A. Exhaustion State
建议引入：

```text
.beacon/state/exhaustion.json
```

最小字段：
- `failure_streak`
- `escalation_level`
- `last_failed_stage`
- `attempted_strategies[]`
- `excluded_causes[]`
- `next_hypothesis`
- `evidence_gap[]`

### B. Escalation Contract
- `E1`：必须切换本质不同策略
- `E2`：必须补一手文档 / 源码 / 假设验证
- `E3`：必须补 exhaustiveness checklist
- `E4`：只能进入 recoverable loop 或结构化失败边界

### C. Checkpoint / Resume Contract
resume 时至少要恢复：
- tried approaches
- excluded causes
- next hypothesis
- current blocker
- evidence gap

这样 debug 不再只是“记日志”，而是：

```text
失败
→ 升级
→ 改策略
→ 保存检查点
→ 恢复后不重复踩坑
```

## 5.3 QA 验证健壮性闭环

现有基础：
- `beacon qa run/status`
- QA session manifest
- `review quality`
- `gate check release`
- coverage / evidence / qa9 / compatibility / delivery checks

v1.1.9 新增要求：

### A. Completion Contract 拆层
至少拆出：
- `implementation_done`
- `evidence_done`

只有同时满足，才能进入：
- review-quality pass
- gate-ready
- release-ready

### B. Delta-aware QA
基于：
- `workflow_memory` stage context
- `technical-implementation-*` 的 changed_files / api_changes / db_changes
- `coverage` 的 story / AC / TC 缺口

判断：
- 哪些 test cases 必须重跑
- 哪些 evidence 已失效
- 哪些 session 仍可复用

### C. QA Failure Routing
QA 失败后至少区分：
- requirement ambiguity → 回 `think / user-story / prd`
- implementation drift → 回 `implement / review spec`
- env/data issue → 回 `debug`
- evidence missing → 卡在 `gate`

### D. Feature-aware / Story-sequential QA
这是 v1.1.9 必须显式增强的一点。

当前 `qa run` 实际上是 `auto-test create` 的 alias，主要消费的是：

- scope
- layer
- matrix entries

而不是：

- feature
- user-story ordering
- AC-by-AC verification progression

因此 v1.1.9 需要把 QA 能力升级为两层：

#### Layer 1：保留当前 matrix-driven execution
继续支持：
- `qa run qa9`
- `--qa-matrix-path`
- layer/scope execution

#### Layer 2：新增 feature-aware orchestration
支持：

```text
qa run <feature>
→ resolve version + feature slug
→ locate user-story / test-case matrix
→ execute verification in story / AC order
→ write verification results back per item
```

### E. `qa evolve` 从设计语义变为正式 requirement
当前 `qa evolve` 只在文档中出现，尚未形成实现面。

v1.1.9 需要把它升级成正式 requirement，至少定义：

- 何时检测 requirement delta
- 如何识别受影响 AC / TC
- 如何决定 targeted rerun
- 如何让失效 evidence 进入 blocked / rerun-required 状态

## 5.4 Requirement → Implementation → Evidence Trace Contract

现有基础：
- workflow 已记录 stage context
- implement 已输出 `technical-implementation-*`
- review / gate 已检查 traceability 与 coverage

v1.1.9 要把它冻结成正式三层契约：

### Requirement Layer
- user story
- AC
- test-case
- optional prototype baseline

### Implementation Layer
- changed_files
- modules_touched
- api_changes
- db_changes
- config/env/feature flag changes

### Evidence Layer
- verification[]
- QA evidence refs
- gate evidence refs
- delivery manifest / report consistency

### 关键新增要求
1. `artifact_updates` 不能只作为提示，必须成为 writeback obligation
2. `known_risks` / `rollback_notes` 在 relevant 变更下必须显式存在
3. review recommendations 必须能回流为 requirement/test-case/version 的修订输入
4. verification writeback 不能只停留在“整体通过后汇总”，还必须逐步支持 AC / TEST item 粒度对齐

## 5.5 Technical Archive → Requirement Rewrite Bridge

现有基础：
- `.beacon/implement/<run_id>/request|result|stdout|stderr`
- `technical-implementation-<feature>.md/json`
- `debug harvest` / `debug export-ideas`

v1.1.9 新增要求：

### A. Archive Learning Extraction
从技术归档中提取：
- 高频改动模块
- 高频风险类型
- 高频 artifact_updates
- 高频 rollback pattern
- 高频验证缺口

### B. Writeback Targets
反哺到：
- PRD 模板补充项
- user-story/AC 模糊点
- test-case 缺口
- debug baseline 提升项
- execution baseline 强制项

### C. Learning Output
建议形成：
- `version` research 输入
- future issue / idea 候选
- evo harness benchmark corpus

## 5.6 Execution Baseline 与 Evo Harness 边界

v1.1.9 可以定义：
- 哪些高质量动作升级为默认义务
- 哪些真实问题进入 keep/discard 决策面

但不应在本版承诺：
- 整仓自治修改
- 无限预算自进化
- 没有 scorecard 的自动 patch 留存

正确边界是：

```text
先定义 baseline / ledger / benchmark / keep-discard discipline
再决定是否进入更深实现
```

## 6. 功能需求

### FR-001 v1.1.9 必须以 overlay 方式增强现有 Beacon 主链
不得新造一套与 `workflow / implement / qa / review / gate / release` 平行的生命周期。

### FR-002 Debug 必须支持 exhaustion / escalation / checkpoint / resume 语义
debug 不得只停留在事件采集层，必须支持 failure streak、升级状态和恢复语义。

### FR-003 QA 必须区分 implementation_done 与 evidence_done
不得继续把“实现看起来做完了”与“验证证据已完成”混为一谈。

### FR-004 QA 必须支持 delta-aware rerun 语义
需求、实现或证据变化后，必须能识别应重跑的测试范围与失效 evidence。

### FR-005 Beacon 必须冻结 requirement → implementation → evidence 三层 trace contract
至少覆盖：story/AC/test-case、technical-implementation、verification/QA/gate evidence。

### FR-006 `artifact_updates` 必须升级为 writeback obligation
不得只停留在 summary 提示；必须成为 gate/review/resume 可消费的正式待办。

### FR-007 Technical archive 必须能正式反哺 requirement rewrite
技术归档不应只是归档文档，还必须成为 PRD/test-case/version research 的输入源。

### FR-008 Debug harvest 与 technical archive 必须共同组成 learning input
这两类信息必须可共同服务：
- issue/idea 聚合
- execution baseline uplift
- future version research
- evo benchmark corpus

### FR-009 v1.1.9 必须保留当前主链命令面的稳定性
不得为了闭环增强而破坏 v1.1.8 已有主面与已发布线语义。

### FR-010 当前 v1.1.9 先冻结设计物料
当前版本先输出 PRD / user-story / test-case 与执行蓝图，不宣称上述能力已经全部编码实现。

### FR-011 Beacon 必须明确 skill 文档的一主一辅结构
必须正式定义：
- root `SKILL.md` 为主文档
- `skills/beacon/SKILL.md` 为辅文档

两者不得继续自由漂移。

### FR-012 Beacon skill 文档必须采用固定结构模板
两份 skill 文档必须稳定覆盖统一 section 顺序，并在产品说明、workflow 模型、推荐阅读、命令入口、导航规则、故障排查上保持镜像语义。

### FR-013 Skill 文档必须成为 v1.1.9 operator clarity 的一部分
v1.1.9 的 requirement material 中必须明确：skill 文档清晰度本身也是闭环的一部分，因为它决定使用者能否稳定进入正确 stage、读对文档、调用对命令。

### FR-014 v1.1.9 必须定义“全端口 anti-drift closure contract”
防漂移 requirement 不得只覆盖 workflow 主链，还必须覆盖：
- CLI
- README
- root skill
- packaged skill
- runtime state
- docs version package
- installed skill copies
- managed block / context files

### FR-015 v1.1.9 必须收敛 baseline / fingerprint / drift 的 canonical contract
当前 revision_state / story_state / v110_baseline 都在表达 baseline 相关语义；v1.1.9 必须明确：
- 哪个是 canonical baseline source
- 哪个是 story/revision projection
- 哪个是 report/gate drift snapshot

避免 baseline 语义继续多中心漂移。

### FR-016 `qa run` 必须支持 feature-aware 入口
除了现有 scope-driven 入口外，v1.1.9 必须支持：
- `qa run <feature>`
- 自动解析该 feature 的 user-story / test-case / matrix
- 自动进入该 feature 的正式 QA 闭环

### FR-017 QA 必须支持按用户故事 / AC 顺序验证
QA 不得只停留在 matrix-driven layer execution；还必须支持：
- user-story ordered verification
- AC-by-AC progression
- per-item verification writeback

这样“实现完毕后根据用户故事依次进行 QA 验证”才真正成立。

### FR-018 `qa evolve` 必须从设计语义升级为正式 requirement
v1.1.9 必须明确 `qa evolve` 的 contract，使 requirement delta → targeted rerun 成为正式能力，而不是文档里的未来想法。

### FR-019 QA 必须支持 user-story → scenario families 编译
v1.1.9 必须把 browser-relevant user-story / AC 编译成正式 scenario families，而不是仅保留 AC → 单个 executable TC 映射。

### FR-020 v1.1.9 必须生成 `story-scenario-map` machine artifact
至少新增：

```text
docs/beacon/<version>/.machine/qa/<feature>.story-scenario-map.json
```

用于承载：
- AC → scenarios
- scenario family
- browser requirement
- dependency / stop_on_fail
- coverage axes
- replay requirement

### FR-021 `qa run` 必须支持 `story-exhaustive` 模式
除了现有 feature-aware 入口外，v1.1.9 必须支持：

```text
qa run <feature> --mode story-exhaustive
```

其语义是：
- 按 user-story / AC 顺序推进
- 按 scenario families 展开验证
- 支持 dependency-aware gating
- 支持 scenario-level evidence capture

### FR-022 浏览器验证必须采用双层执行器
v1.1.9 不得把 agent-browser/browser-use 视为唯一真相源。
浏览器验证至少应拆为：

- exploratory runner
- deterministic evidence runner

对于 P0/P1 browser claims，必须有 deterministic replay evidence。

### FR-023 浏览器场景必须生成标准 evidence pack
每个 browser scenario 至少应支持落盘以下证据中的合理子集：

- screenshot
- current URL
- DOM / snapshot
- action transcript
- console excerpt
- network summary
- result manifest
- replay reference

### FR-024 QA 必须支持 scenario-level writeback 与 delta rerun
除了现有 AC / TEST item writeback 外，v1.1.9 还必须支持：
- scenario-level verification state
- scenario-level targeted rerun
- stale browser evidence detection

### FR-025 Gate 必须校验 scenario families / replay / exhaustiveness
release / acceptance gate 不得仅依据“跑过 QA”通过；
还必须检查：
- required scenario families 是否覆盖
- required browser replay 是否存在
- required evidence pack 是否完整
- exhaustiveness score 是否达阈值

### FR-026 v1.1.9 不得退化为纯 agent 浏览器测试器
本版允许使用 agent-browser / browser-use 作为浏览器执行入口；
但不得允许“只有 agent 探索、没有 deterministic replay / evidence contract”的 browser QA 被视为 gate-ready。

### FR-019 QA 必须支持 user-story → scenario families 编译
v1.1.9 必须把 browser-relevant user-story / AC 编译成正式 scenario families，而不是仅保留 AC → 单个 executable TC 映射。

### FR-020 v1.1.9 必须生成 `story-scenario-map` machine artifact
至少新增：

```text
docs/beacon/<version>/.machine/qa/<feature>.story-scenario-map.json
```

用于承载：
- AC → scenarios
- scenario family
- browser requirement
- dependency / stop_on_fail
- coverage axes
- replay requirement

### FR-021 `qa run` 必须支持 `story-exhaustive` 模式
除了现有 feature-aware 入口外，v1.1.9 必须支持：

```text
qa run <feature> --mode story-exhaustive
```

其语义是：
- 按 user-story / AC 顺序推进
- 按 scenario families 展开验证
- 支持 dependency-aware gating
- 支持 scenario-level evidence capture

### FR-022 浏览器验证必须采用双层执行器
浏览器验证至少应拆为：

- exploratory runner
- deterministic evidence runner

对于 P0/P1 browser claims，必须有 deterministic replay evidence。

### FR-023 浏览器场景必须生成标准 evidence pack
每个 browser scenario 至少应支持落盘以下证据中的合理子集：

- screenshot
- current URL
- DOM / snapshot
- action transcript
- console excerpt
- network summary
- result manifest
- replay reference

### FR-024 QA 必须支持 scenario-level writeback 与 delta rerun
除了现有 AC / TEST item writeback 外，v1.1.9 还必须支持：
- scenario-level verification state
- scenario-level targeted rerun
- stale browser evidence detection

### FR-025 Gate 必须校验 scenario families / replay / exhaustiveness
release / acceptance gate 不得仅依据“跑过 QA”通过；还必须检查：
- required scenario families 是否覆盖
- required browser replay 是否存在
- required evidence pack 是否完整
- exhaustiveness score 是否达阈值

### FR-026 v1.1.9 不得退化为纯 agent 浏览器测试器
本版允许使用 agent-browser / browser-use 作为浏览器执行入口；
但不得允许“只有 agent 探索、没有 deterministic replay / evidence contract”的 browser QA 被视为 gate-ready。

## 7. 验收语义

### Pass
- v1.1.9 明确被定义为 control + recovery + learning overlay；
- debug / qa / requirement→implementation / archive feedback 四个闭环都定义清晰；
- 与现有 Beacon 功能面的结合方式明确，不是抽象空谈。

### Fail
- 仍停留在“再加几个命令/功能点”的层面；
- 没有把现有 workflow / implement / qa / debug / review / gate 串成正式闭环；
- 没有明确 recovery / writeback / learning 的 contract。

### Blocked
- v1.1.9 与现有主链是否 overlay 仍存在关键分歧；
- 或 debug/qa/writeback/evo 边界仍有重大冲突。
