# User Story: Beacon QA 置信度、closure outcome 与 autoresearch 精准度闭环（v1.1.10）

**Feature**: beacon-qa-confidence-autoresearch-closure  
**Version**: v1.1.10

**As a** 使用 Beacon 管理需求、实现、QA、gate 与 release 的维护者 / QA owner / release owner / AI Agent 协作者  
**I want** Beacon 在 v1.1.9 的 feature-aware QA、story-exhaustive、browser evidence、release scorecard 与 keep/discard skeleton 之上，增加 closure outcome、calibrated confidence、audit truth 与 QA precision feedback loop  
**So that** Beacon 不再只会说“测过了”，而是能说清“为什么能放行、为什么不能放行、什么时候必须 abstain、哪些真实误判应进入下一轮策略优化”。

## Story Slices

### US-001: Beacon 将 scenario result 从 status-only 升级为 closure-aware result
作为 QA owner，我希望每个 scenario 不只输出 `passed / failed / blocked`，还输出 closure action 与 review requirement。

### US-002: Beacon 区分 raw evidence strength 与 calibrated confidence
作为 release owner，我希望系统能区分原始证据强度、规则打分与校准后的 release confidence，而不是把 exhaustiveness 误当成 confidence。

### US-003: Beacon 把 AC closure 变成可推导结论
作为评审人，我希望 AC closure 来源于 scenario families、replay、evidence sufficiency 与 unresolved outcomes，而不是主观猜测。

### US-004: Beacon 为 feature 生成 confidence-aware QA scorecard
作为 release owner，我希望 feature 级别能看到 closure summary、confidence floor、review count 与 false-complete risk。

### US-005: Beacon 把 abstain 作为正式成功路径
作为 QA owner，我希望低置信度时系统能明确产出 `review_required`、`needs_more_evidence` 或 `needs_replay`，而不是硬判通过。

### US-006: Beacon 在 closure 结果中保留 root cause 归因
作为维护者，我希望 closure 结果能区分 spec gap、implementation gap、runner gap、environment gap、flake 与 evidence gap。

### US-007: Beacon 用 sampled QA audit label 建立 benchmark truth
作为质量负责人，我希望 sampled audit 能把 `true_pass / false_pass / true_block / false_block / spec_gap / runner_gap / flake` 固化为机器工件。

### US-008: Beacon 将 false-complete 与 false-block 作为正式学习样本
作为学习面维护者，我希望 benchmark corpus 直接收录真实错判案例，而不是只收录“跑过”的样本。

### US-009: Beacon 把 QA precision 训练面限制在小策略面
作为系统设计者，我希望 autoresearch/keep-discard 只优化 scenario expansion、delta selection、evidence sufficiency、confidence threshold 与 release threshold 等小面。

### US-010: Beacon 保持 v1.1.9 契约兼容
作为既有 Beacon 用户，我希望 v1.1.10 扩展 `story-scenario-map / exhaustiveness-report / browser-evidence-pack / release_scorecard / keep_discard_engine`，而不是破坏它们。

### US-011: Beacon 在 operator surfaces 暴露 confidence 与 review signals
作为 release owner，我希望 `status / report / release scorecard` 能回答“通过了什么”“多大把握”“哪些还要人审”“哪些应该进入下一轮 experiment”。

### US-012: Beacon 将 QA 精准度反馈写回下一轮策略迭代
作为 Beacon 维护者，我希望 audit drift、false-complete、false-block、delta rerun precision 与 calibration error 能回流到下一轮 keep/discard 决策。

### US-013: Beacon 能绑定目标项目的专属 skill/profile/workflow
作为目标项目维护者，我希望 Beacon 能识别并绑定该项目的 profile、skill registry 与 verify orchestration，而不是只走通用 QA 路径。

### US-014: Beacon 在浏览器 QA 中保存可复用的鉴权会话记录
作为 QA owner，我希望 browser QA 能保存 session manifest、profile ref、cookies ref、storage-state ref，并在后续 story-exhaustive 或 delta rerun 中复用。

### US-015: Beacon 让 QA 缺陷能回流 implement 并生成技术归档
作为 release owner，我希望 QA 暴露的实现缺口能直接路由到 `beacon implement`，并形成 `technical-implementation-*` 归档，而不是停留在散乱评论里。

### US-016: Beacon 让实现归档反哺技术架构文档与下一轮 requirement rewrite
作为架构负责人，我希望 implement 技术归档与 QA 缺陷能反哺 architecture blueprint、requirement rewrite input 与下一轮 project-skill evolution。

### US-017: Beacon 把 project-specific verify workflow 接入 `qa run <feature>` 主链
作为目标项目维护者，我希望 feature-aware QA 主入口直接消费 profile binding、verify orchestration 与 required evidence gate，而不是把项目 workflow 放在旁路命令里。

### US-018: Beacon 把 source-architecture 文档线纳入正式门禁
作为架构负责人，我希望源码架构并行线不只存在于 docs，而要进入正式 materials audit / gate contract，避免后续再次漂移。

### US-019: Beacon 保护人工编写的 QA 文档不被 machine refresh 覆盖
作为 requirement maintainer，我希望 `test-case create` 刷新 machine materials 时默认不覆盖人工编写的 QA 设计文档。

## Fact Anchors

这些锚点限定了 v1.1.10 的可用边界，也是 QA 覆盖的核心事实源：

1. **Anchor-A / Existing Reality**
   v1.1.9 已经有 `qa run <feature>`、`qa evolve`、`story-scenario-map`、`exhaustiveness-report`、`release_scorecard`、`keep_discard_engine`。

2. **Anchor-B / Truth Hierarchy**
   `status` 是执行状态，不是 closure truth；`confidence` 是判断层，不是 evidence 本体。

3. **Anchor-C / High-risk Rule**
   高风险 browser scenario 不能只靠 agent exploratory pass，需要 deterministic replay 与 browser evidence pack。

4. **Anchor-D / Honest Abstain**
   低置信度不是系统失败；低置信度下还能 bluff 才是系统失败。

5. **Anchor-E / Audited Learning**
   QA precision 只能由 sampled audit truth 驱动，不能由模型自评直接定义 keep/discard。

6. **Anchor-F / Additive Evolution**
   v1.1.10 必须 additive extend v1.1.9 contracts，不允许默认 destructive break。

7. **Anchor-G / Project-specific Truth Path**
   目标项目的真实交付路径可能通过 project profile / external skill / verify orchestration 表达，Beacon 不能假设所有项目只走同一套 verify 路径。

8. **Anchor-H / Session Reuse Boundary**
   浏览器鉴权记录应保存 artifact refs 与 session metadata，而不是把不受控 secrets 散落到 release 文档和 requirement 材料。

9. **Anchor-I / Architecture Feedback**
   QA 缺陷不是终点；它们必须能进入 implement、technical archive、requirement rewrite 与 architecture doc feedback loop。

10. **Anchor-J / Mainline Truth Path**
   如果 project-specific verify workflow 不进入 `qa run <feature>` 主链，那么 QA precision 仍然优化的是“旁路流程”，不是实际交付流程。

11. **Anchor-K / Human Doc Integrity**
   人工编写的 QA 文档本身是 requirement material，machine refresh 不能默认覆盖它们。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Status vs Closure | scenario result 明确区分 `status` 与 `closure_outcome`，不再把 status 当成 closure truth |
| AC-002 | Confidence Axes | scenario result 明确包含 `confidence_raw`、`confidence_calibrated`、`confidence_band` 与 review flag |
| AC-003 | Derived AC Closure | AC closure 由 required scenario families、replay、evidence sufficiency、confidence threshold 与 unresolved outcomes 推导 |
| AC-004 | High-risk Browser Truth | 高风险 browser scenario 自动放行前必须同时具备 deterministic replay、browser evidence pack 与 calibrated confidence threshold |
| AC-005 | Abstain Path | Beacon 正式支持 `review_required`、`needs_more_evidence`、`needs_replay`、`needs_requirement_clarification` |
| AC-006 | Root Cause Taxonomy | scenario result 正式支持 `spec_gap / implementation_gap / runner_gap / environment_gap / flake / evidence_gap` |
| AC-007 | AC Closure Artifact | `.beacon/qa/features/<feature>/ac-closure.json` 作为正式 machine artifact 被定义 |
| AC-008 | Feature QA Scorecard | `.beacon/qa/features/<feature>/scorecard.json` 正式表达 closure、confidence、review count 与 false-complete risk |
| AC-009 | Release Decision Policy | release scorecard 使用 calibrated confidence、review count、needs_replay、open outcomes 决定 `release_ready` |
| AC-010 | Human Audit Labels | `.beacon/state/qa-audits/<run_id>/<scenario_id>.json` 作为 sampled audit truth artifact 被定义 |
| AC-011 | Benchmark Corpus | benchmark corpus 至少覆盖 false pass、false block、stale evidence、missing replay、wrong delta rerun、story/AC trace mismatch |
| AC-012 | Small Editable Surface | QA precision 优化面只允许 scenario expansion、delta selection、evidence sufficiency、confidence calibration 与 release thresholds |
| AC-013 | Fixed-budget Governance | keep/discard experiment 必须固定预算、可比较、可回滚，不能演变为整仓自治 |
| AC-014 | Deterministic Truth Boundary | v1.1.10 不替换 deterministic replay，不允许把 LLM judgement 变成唯一 truth source |
| AC-015 | Cross-version Compatibility | v1.1.10 扩展而不破坏 v1.1.9 QA contracts、v1.1.7 project skill/profile/orchestration、v1.1.8 `technical-implementation-*` 归档面 |
| AC-016 | Project Skill Workflow | 目标项目可通过 profile/skill binding、verify orchestration、required evidence gate 声明项目专属 QA workflow，并在 operator surfaces 中被解释清楚 |
| AC-017 | Mainline Project Workflow | `qa run <feature>` 主链直接消费 profile binding、verify orchestration 与 required evidence gate，而不是要求操作者手工走平行 `verify run` |
| AC-018 | Browser Auth Persistence | browser QA session manifest 支持保存 `profile_ref / cookies_ref / storage_state_ref / scopes / expiry`，并可供后续 QA/replay/workflow 复用 |
| AC-019 | Implement And Architecture Feedback | QA 缺陷、review-required outcome 或 release block 可路由到 `beacon implement`，并产出 `technical-implementation-*`、requirement rewrite input 与 architecture feedback |
| AC-020 | Formal Closure And Doc Integrity | QA test feedback 必须能回写 benchmark truth、audit drift、candidate surface、project skill evolution input 与 next experiment set；同时 machine refresh 默认不得覆盖人工编写的 QA requirement docs |

## Risks And Reminders

- 若只增加 confidence 字段、不定义 closure outcome，release 仍会停留在“看起来通过”
- 若把 exhaustiveness 直接当 calibrated confidence，会把 coverage completeness 和 judgement reliability 混为一谈
- 若 review-required 不是正式 outcome，系统会继续偏向乐观误判
- 若 sampled audit label 不形成 machine artifact，keep/discard 将缺少真实 benchmark truth
- 若训练面不受限，autoresearch 会从 precision optimization 演化成不受控自治
- 若破坏 v1.1.9 artifacts，现有 `qa / gate / release / status / report` 主链会失去兼容性
- 若不接入目标项目的 profile/skill/orchestration，Beacon 仍会在真实项目里回退到“通用 QA 看似通过”
- 若浏览器鉴权会话不能保存与复用，story-exhaustive / delta rerun 会不断重做登录，既增加波动也降低证据可追溯性
- 若 QA 缺陷不能进入 implement 与技术架构文档回流，闭环会停在 defect list 而不是系统性演进
- 若 `verify` 能感知项目 workflow 而 `qa run` 不能，主 QA 路径与真实交付路径仍会分叉
- 若 source-architecture 线不进入正式 audit/gate，它仍然只是“有测试兜底的附属文档”
- 若 `test-case create` 默认覆盖人工 QA 文档，requirements 本身会被工具回写破坏

## Execution Semantics

- `Pass`: requirement materials 明确表达 closure、confidence、abstain、audit、learning 五层关系
- `Pass`: QA 覆盖既能围绕事实锚点做全方位扩展，又不越出 deterministic truth boundary
- `Fail`: 仍把 status 当 closure，把 exhaustiveness 当 confidence，把 exploratory pass 当 release truth
- `Blocked`: sampled audit、benchmark truth、release threshold、compatibility strategy 之间仍有关键冲突
