# PRD: Beacon Version Truth / Profile Boundary / Learning Plane Governance（v1.1.12）

## 1. Problem Statement

Beacon `v1.1.12` 当前已经开始讨论：

- prototype design governance
- bounded autoresearch
- implement branch gate

但真实项目实践又暴露出另一组更底层的问题：

1. **版本真相分裂**
   - skill、package、runtime、release line 不是单一事实源
2. **navigator 仍偏向 generic Beacon path**
   - project profile / stage binding 还不是一等真相
3. **project skill execution boundary 过宽**
   - orchestration 已经接近任意 shell 编排，而不是 adapter-governed execution
4. **learning plane 尚未类型化**
   - 文档定义了 bounded surfaces，但 runtime 没有与之对齐的 typed mutation surface
5. **takeover baseline 还不是 runtime hard gate**
   - current-state baseline 未冻结时，系统仍可能过早进入 implement / delivery

这不是五个独立 bug。
它们本质上都是同一个问题：

> Beacon 还没有把“版本真相 / 执行边界 / learning plane”统一成同一套治理系统。

## 2. Product Principles

1. one version truth, many consumers
2. navigator should be profile-aware before native-default
3. Beacon core is not the project runtime platform
4. learning plane may optimize judgement surfaces, not execution surfaces
5. takeover projects must freeze current-state truth before delivery expansion
6. readonly project contracts are first-class inputs

## 3. Goals

1. 建立单一 machine-readable version truth
2. 让 help / doctor / status 变成 profile-aware first
3. 给 project skill orchestration 增加 capability boundary
4. 把 learning plane subject surface 拆成 typed policy families
5. 给 takeover 模式增加 baseline-required runtime gate
6. 把 service-slice / boundary / evidence docs 变成 readonly contract inputs
7. 把 requirement-anchored QA divergence 变成正式治理对象，而不是任由场景向相邻产品语义漂移

## 4. Non-goals

1. 不把 Beacon core 扩成 rolo-dev / gateway / UAT / pipeline 平台
2. 不让 learning plane 直接修改项目运维命令或业务代码
3. 不让 release/gate 最终裁决逻辑变成 autoresearch surface
4. 不让 takeover 的 current-state architecture truth 被自动学习面改写
5. 不把“开屏页视频上传/展示”这类 requirement 漂移成“视频播放器能力验证”

## 5. Functional Responsibility Model

Beacon `v1.1.12` 必须把功能、职责与边界固定为四层，不再混淆：

### Layer 1: Requirement kernel

负责：

- think
- user-story
- prd
- test-case
- architecture / boundaries / source materials

不负责：

- 项目实现命令
- UAT / gateway / pipeline 操作
- learning plane 的策略调优执行

### Layer 2: Delivery evidence kernel

负责：

- implement summary
- technical archive
- qa scorecard
- review / gate / release evidence

不负责：

- 直接接管项目 delivery runtime
- 直接重写项目执行脚本

### Layer 3: Project execution adapters

负责：

- rolo-dev
- gateway / UAT / pipeline
- SQL / Redis / browser profile
- 项目特有 implementation / verification operation surfaces

约束：

- 这一层可以被 Beacon 调度，但不能被 Beacon core 吸收成默认 native truth
- Beacon 只能通过 capability-bounded adapter 进入这一层

### Layer 4: Learning plane

负责：

- policy surface
- compiler surface
- evaluation surface

不负责：

- project ops
- arbitrary repository code mutation
- secrets / cookies / storage-state learning
- final release verdict override

## 6. Functional Requirements

### FR-001 Single Version Truth Source

Beacon 必须维护单一 machine-readable version truth source，至少包含：

- `runtime_version`
- `package_version`
- `docs_default_line`
- `planning_lines`
- `partial_runtime_supplement_lines`
- `current_runtime_release_line`

以下消费者必须共用这份事实：

- package/runtime metadata
- `SKILL.md`
- help/status/doctor version context
- docs current release selector
- tests/current-doc contracts

### FR-002 Release Truth Status Model

Beacon 必须能区分：

- `planning_only`
- `planning_with_partial_runtime_supplement`
- `current_runtime_release`

也就是说，`v1.1.12` 这种 planning line 可以声明“已有局部 runtime supplement”，但不能因此与“current runtime release line”混淆。

### FR-003 Profile-aware Navigator First

下一步推荐必须遵循：

```text
version truth
→ project mode
→ feature/profile binding
→ stage-local execution binding
→ fallback only if no profile binding exists
```

不能再默认：

- `implement run --runner native-single`
- `review quality`

除非当前 feature 没有 profile/stage binding。

### FR-004 Project Skill Capability Boundary

project skill orchestration 在执行前必须校验：

- `skill.supported_stages`
- `skill.capabilities`
- `skill.entry`
- `skill.evidence_contract`
- node `produces_evidence`
- node `produces_cases`

任一条件不满足时，必须返回结构化 blocked 结果，而不是继续执行命令。

### FR-005 Adapter-governed Execution Surface

Beacon core 不应把 project skill orchestration 设计成“任意 shell 编排器”。

允许的最宽语义应是：

- node 通过 skill adapter 进入执行面
- adapter 可以有受约束模板
- 但模板必须被 capability/stage/evidence contract 包住

不应允许：

- 无边界 raw command template
- 仅凭字符串拼接就进入 shell 执行

### FR-006 Typed Learning Plane

learning plane 的 `subject_surface` 必须显式类型化，至少包含：

- `qa_policy`
- `design_policy`
- `contract_policy`
- `rewrite_policy`
- `debug_policy`
- `benchmark_policy`

其中：

- `design_policy` 应覆盖 `v1.1.12` 已定义的：
  - design brief extraction
  - design-system normalization
  - guideline severity mapping
  - review thresholds
- `qa_policy` 应覆盖：
  - scenario expansion
  - evidence sufficiency
  - false-complete reduction
  - continue decision calibration

### FR-007 Forbidden Learning Surfaces

learning plane 明确禁止直接优化：

- project skill command templates
- rolo-dev / UAT / pipeline 具体命令
- arbitrary repository implementation code
- release / gate final verdict logic
- cookies / secrets / storage state
- takeover architecture truth

### FR-008 Takeover Baseline Runtime Gate

当 `project_mode=takeover` 时，Beacon 必须在进入 implement 前验证以下 baseline truth：

- `architecture-blueprint`
- `current-state-service-map`
- `refactor-boundaries`
- frozen baseline

缺任一项时返回：

- `takeover_baseline_required`

并阻断：

- implement
- implementation delegate
- profile-native fallback

### FR-009 Readonly Project Contract Inputs

对于 `rolo` 这类项目，Beacon core 必须能把以下材料作为 readonly contract inputs 消费：

- service-slice map
- project boundaries
- required evidence contracts
- consumer/reference service declarations

它们应用于：

- navigator routing
- contract drift diagnosis
- evidence gate

不应用于：

- 把 Layer 3 项目动作拉回 Beacon core 默认执行路径

### FR-010 Requirement-anchored Scenario Expansion

当 Beacon 生成、扩展或学习 QA 场景时，必须先锚定以下 requirement anchors：

- PRD requirement
- user story acceptance criteria
- project contract / profile contract
- evidence / replay truth
- divergence budget

每个场景至少应携带：

- `anchor_ids`
- `anchor_kinds`
- `semantic_scope`
- `divergence_budget`
- `adjacent_capability_flags`

只有能回挂到上述 anchors 的发散场景，才允许进入执行或学习面。

### FR-011 Requirement Anchor Score Governance

Beacon 必须为每个新增或学习到的发散场景计算 `Requirement Anchor Score (RAS)`，范围 `0-100`。

建议评分维度如下：

- `requirement_traceability`：`0-25`
- `semantic_intent_match`：`0-25`
- `project_contract_match`：`0-20`
- `divergence_budget_fit`：`0-15`
- `business_risk_realism`：`0-15`

默认阈值：

- `85-100`：允许自动发散并执行
- `70-84`：允许进入 `review_required`
- `50-69`：必须人工审批
- `0-49`：判定为 requirement drift，直接 blocked

`autoresearch` 允许优化：

- 评分权重
- band thresholds
- exemplars / negative exemplars
- drift classifier calibration

但不允许通过学习面绕过最低 blocked band。

### FR-012 Adjacent-semantics Drift Blocker

Beacon 必须显式阻断“相邻产品语义漂移”。

例如：

- 当 requirement 是 `rolo` 开屏页视频上传/展示
- 系统可以在需求内发散上传成功、格式约束、展示成功、证据回放、已声明大小边界等场景
- 系统不得自动把该需求扩张成 seek / fullscreen / subtitle / buffering / background playback / 500MB stress upload 等“视频播放器语义”

除非以下任一条件成立：

- PRD 明确声明该能力
- user story / AC 明确声明该能力
- project contract 明确声明该能力
- 风险模型要求并有人工放行

### FR-013 Transparent Decision Trace

help / status / review / gate / QA scenario generation 结果必须输出结构化 decision trace，至少包含：

- `version_truth_source`
- `project_mode`
- `execution_surface`
- `learning_surface`
- `requirement_anchor_score`
- `blocked_reason`

这样系统才能解释“为什么推荐这个执行面”、“为什么允许/阻断这次发散”。

### FR-014 Context-managed Requirement Version Guard

当用户显式输入 `--version vX.Y.Z` 时，Beacon 必须把它与以下上下文版本信号比对：

- `AGENTS.md` / `CLAUDE.md` managed marker
- onboarding docs version
- current git branch embedded semver

如果显式版本与上下文推荐版本冲突，则：

- 返回 `context_version_mismatch`
- 阻断 requirement-material 写入类命令
- 在 help/status 中给出推荐版本与恢复命令

## 7. Requirement-anchor Governance Model

Beacon 的稳定性不只取决于 typed learning surface，还取决于“发散是否始终锚在需求里”。

### 7.1 锚定原则

目标项目上的所有发散补充，都必须先锚定：

1. PRD 的能力语义
2. user story / AC 的用户任务语义
3. project profile / boundary contract
4. 已有 evidence / replay / technical archive truth

允许在需求范围内向 happy / negative / boundary / recovery / compatibility 发散。
不允许跳到相邻产品语义。

### 7.2 RAS 示例

场景：`rolo` 开屏页视频上传需求。

若 PRD 只要求：

- 上传开屏素材
- 成功展示开屏视频
- 满足已声明的格式/大小/时长约束

则以下场景属于需求内发散：

- 上传失败重试
- 格式不合法提示
- 展示成功回放证据
- 在已声明大小上限附近的边界验证

以下场景默认属于需求外漂移：

- 上传 `500MB` 视频并检验是否流畅播放
- seek / pause / fullscreen / subtitle / buffering
- 后台播放恢复
- 长视频播放器控制条验证

上述“500MB 上传并验证播放器行为”的场景，默认 `RAS` 应落在低分段，例如 `18/100` 左右，因为：

- requirement traceability 很弱
- semantic intent 已从开屏素材展示漂移到视频播放器
- project contract 未声明该能力
- divergence budget 明显超支

### 7.3 Learning Plane 落点

`autoresearch` 应优化的是 Beacon 的判断系统：

- 哪些场景该扩
- 扩到什么程度
- 什么分数该自动放行
- 什么分数必须 review 或 blocked

而不是去优化项目执行系统：

- 不直接改 command templates
- 不直接改业务仓实现代码
- 不直接替代 release / gate 最终裁决

## 8. Stable Workflow Order

最稳的 Beacon skill workflow 必须遵循以下顺序：

```text
single version truth
→ project mode
→ execution surface
→ bounded learning surface
→ requirement anchors + divergence budget
→ help / status / implement / review / gate
```

如果顺序反过来，系统就会出现：

- docs current-line 漂移
- navigator 误推 native path
- project adapter 边界被打穿
- autoresearch 学到执行面而不是判断面

## 9. Suggested Artifact Model

```text
docs/beacon/<version>/
  research/
    beacon-practice-boundary-learning-analysis.md
  execution/
    boundaries.md
    architecture-blueprint.md
  user-story/
    beacon-version-truth-profile-boundary-governance.md
  prd/
    beacon-version-truth-profile-boundary-governance.md
  qa/test-cases/
    beacon-version-truth-profile-boundary-governance.md

.beacon/state/
  version-truth.json
  project-mode-gate.json
  learning-plane-contract.json
  profile-adapter-gate.json
  requirement-anchor-policy.json
  requirement-anchor-thresholds.json

.beacon/qa/
  anchor-scorecards/<feature>.json
  drift-decisions/<run-id>.json
```

注：路径可调整，但语义必须保留。

## 10. Success Standard

这条线完成时，Beacon 应能稳定做到：

1. help / status / skill reader 不再各自维护“当前版本”
2. 有 project profile 的 feature 不会被默认推回 `native-single`
3. project skill orchestration 会先过 capability/stage/evidence boundary 再执行
4. learning plane 只优化 typed judgement/policy surfaces
5. takeover 项目在 baseline 未冻结前不会进入 implement
6. `rolo` 一类项目会把 service-slice docs 当 contract input，而不是把项目运行命令内嵌进 Beacon core
7. QA/autoresearch 的发散会锚定 PRD / user story / project contract，不会把需求扩成相邻产品
8. 系统能解释每一次推荐、阻断和发散评分，做到稳定、准确、不漂移
