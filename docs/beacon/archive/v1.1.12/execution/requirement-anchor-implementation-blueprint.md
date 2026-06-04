# Requirement Anchor Implementation Blueprint

## 1. Objective

将 `v1.1.12` 中“需求锚定发散”从文档原则收敛为可执行运行时蓝图。

目标不是新增一个孤立的 QA 功能，而是建立统一的 `Requirement Anchor Kernel`，由它驱动：

- prototype 发散
- QA scenario 发散
- rewrite writeback
- project contract drift
- takeover baseline summary
- learning plane keep/discard

---

## 2. First-principles Order

实现顺序必须遵循：

```text
version truth
→ project mode
→ execution surface
→ requirement anchor kernel
→ prototype / QA / rewrite / profile consumers
→ typed learning plane
→ help / status / review / gate decision trace
```

不是：

```text
先扩场景 / 先扩 prototype
→ 再补锚定和边界
```

---

## 3. Target Runtime Architecture

```text
version truth state machine
→ project mode + profile gate
→ requirement anchor kernel
   ├─ prototype anchor consumer
   ├─ QA anchor consumer
   ├─ rewrite anchor consumer
   ├─ contract drift consumer
   └─ takeover manifest consumer
→ typed learning plane
→ help/status/review/gate decision trace
```

核心原则：

1. 先判断任务属于什么需求边界
2. 再判断允许在哪个执行面运行
3. 再判断允许发散到什么程度
4. 最后才进入执行和学习

---

## 4. Artifact Model

建议新增以下 machine-readable artifacts：

```text
.beacon/state/
  version-truth.json
  project-mode-gate.json
  learning-plane-contract.json
  requirement-anchor-policy.json
  requirement-anchor-thresholds.json

docs/beacon/<version>/.machine/anchors/
  requirement-anchor-<feature>.json
  prototype-anchor-scorecards-<feature>.json
  rewrite-anchor-input-<feature>.json

.beacon/qa/features/<feature>/
  scenario-anchor-map.json
  anchor-scorecard.json

.beacon/state/drift-decisions/
  <run-id>.json
```

### 4.1 requirement-anchor-<feature>.json

至少表达：

- `anchor_ids`
- `anchor_kinds`
- `source_refs`
- `semantic_scope`
- `allowed_divergence_families`
- `forbidden_adjacent_capabilities`
- `project_contract_refs`
- `divergence_budget`

### 4.2 prototype-anchor-scorecards-<feature>.json

至少表达：

- page/state id
- source anchor ids
- semantic scope
- adjacent capability flags
- `prototype_anchor_score`
- blocked / review / allow

### 4.3 scenario-anchor-map.json

至少表达：

- `scenario_id`
- `source_tc_id`
- `anchor_ids`
- `anchor_kinds`
- `semantic_scope`
- `adjacent_capability_flags`
- `divergence_budget`
- `qa_anchor_score`

---

## 5. Module Change Plan

## 5.1 `beacon/utils/versioning.py`

目标：

- 版本真相不再只是聚合上下文
- 变成明确的 state model

最小改造：

- 新增 version truth schema：
  - `runtime_version`
  - `package_version`
  - `docs_default_line`
  - `planning_lines`
  - `partial_runtime_supplement_lines`
  - `current_runtime_release_line`
- `describe_project_version_context()` 输出 status model，而不是只输出 version values

产出：

- `version_truth_source`
- `release_truth_status`

## 5.2 `beacon/utils/help_support.py`

目标：

- 下一步推荐真正变成 profile-aware first
- 输出统一 decision trace

最小改造：

- `_next_step()` 在任何 native fallback 前先解析：
  - version truth
  - project mode
  - profile/stage binding
  - requirement anchor readiness
- `build_help_payload()` 增加：
  - `execution_surface`
  - `learning_surface`
  - `decision_trace`
  - `requirement_anchor_ready`
  - `requirement_anchor_score_summary`

blocked reason 应新增：

- `requirement_anchor_missing`
- `requirement_drift`
- `adjacent_semantics_blocked`

## 5.3 `beacon/utils/project_skills.py`

目标：

- project execution adapter 不能继续退化成 shell orchestrator

最小改造：

- 在渲染 `command_template` 前校验：
  - `supported_stages`
  - `capabilities`
  - `entry`
  - `evidence_contract`
  - `produces_evidence`
  - `produces_cases`
- 不满足时直接返回结构化 blocked payload
- `shell=True` 路径只在 boundary 校验通过后执行

## 5.4 `beacon/utils/story_scenarios.py`

目标：

- scenario expansion 从 family-driven 升级为 anchor-driven

最小改造：

- `expand_story_scenarios()` 为每个 scenario 增加：
  - `anchor_ids`
  - `anchor_kinds`
  - `semantic_scope`
  - `divergence_budget`
  - `adjacent_capability_flags`
  - `qa_anchor_score`

新增判断器：

- adjacent capability classifier
- semantic scope matcher
- divergence budget matcher

## 5.5 `beacon/utils/qa_feature.py`

目标：

- QA precision 不只看 confidence，也看 anchor fitness

最小改造：

- 在 `build_feature_qa_precision_artifacts()` 中追加：
  - `requirement_anchor_score`
  - `anchor_band`
  - `anchor_blocked`
  - `anchor_reason`
- closure decision 变成：

```text
anchor fitness
→ evidence fitness
→ closure outcome
```

默认 band：

- `85-100` auto
- `70-84` review_required
- `50-69` manual approval
- `<50` blocked

## 5.6 `beacon/utils/qa_precision.py`

目标：

- 保留 confidence calibration
- 不让 confidence 冒充 anchor fitness

最小改造：

- 增加独立 `anchor_thresholds` loader
- calibration model 继续只负责 evidence / judgement calibration
- `RAS` 阈值由独立 contract 管理

## 5.7 `beacon/utils/prototype_utils.py`

目标：

- prototype 成为 requirement-anchor divergence 的第一实验场

最小改造：

- design brief / prototype plan 编译阶段引入 requirement anchor refs
- page/state spec 生成时计算：
  - `prototype_anchor_score`
  - `adjacent_capability_flags`
- review 时写出：
  - `prototype_anchor_scorecards`
  - `drift_decisions`

设计 review findings 除了回写 rewrite input，还应回写：

- page additions
- state additions
- semantic drift blockers

## 5.8 `beacon/utils/learning_loop.py`

目标：

- learning plane 顶层 contract 与候选分类一致

最小改造：

- 顶层 `subject_surface` 改为正式 typed families：
  - `qa_policy`
  - `design_policy`
  - `contract_policy`
  - `rewrite_policy`
  - `debug_policy`
  - `benchmark_policy`
- `_build_learning_candidates()` 把现有候选映射到上述 families
- learning candidate 中加入：
  - `anchor_support_refs`
  - `negative_exemplar_refs`
  - `allowed_mutation_surface`

明确禁止：

- command template learning
- arbitrary code mutation
- release final verdict mutation

## 5.9 `beacon/commands/gate.py`

目标：

- gate 正式消费 anchor truth

最小改造：

- prototype gate 增加：
  - `prototype_requirement_drift`
  - `prototype_adjacent_semantics_blocked`
- QA gate 增加：
  - `qa_requirement_anchor_missing`
  - `qa_requirement_drift`
- profile / takeover gate 输出统一 blocked reason taxonomy

## 5.10 `persona / jtbd / roadmap / analyze`

这组不属于 `v1.1.12` 的 runtime P0。

但 blueprint 必须保留前向方向：

- 停止写 `docs/product/...`
- 改为 skill-wrapper
- 回收到 `docs/beacon/<version>/`

这部分建议留到 `v1.2.0` 路线。

---

## 6. Example Policy

以 `rolo` 开屏页视频上传/展示为例：

`requirement-anchor-<feature>.json` 应能表达：

- 需求语义：开屏素材上传与展示
- 允许发散：
  - 格式约束
  - 上传失败重试
  - 展示成功回放
  - 已声明大小边界
- 禁止相邻能力：
  - video player controls
  - fullscreen
  - subtitle
  - buffering
  - background playback
  - `500MB` stress upload

若某个 QA scenario 命中：

- `500MB upload`
- `seek/fullscreen/buffering`

则默认：

- `adjacent_capability_flags != []`
- `qa_anchor_score < 50`
- status=`blocked`
- reason=`requirement_drift`

---

## 7. Phase Plan

## Phase 0: Boundary Truth Repair

目标：

- 统一 version truth
- 修正 navigator 默认路径
- 给 project_skills 加 boundary gate

交付：

- `version-truth.json`
- help/status decision trace v1
- orchestration preflight validation

## Phase 1: Requirement Anchor Kernel

目标：

- 定义统一 anchor schema
- 从 PRD / user-story / project contract 编译 anchor artifact

交付：

- `requirement-anchor-<feature>.json`
- `requirement-anchor-policy.json`
- `requirement-anchor-thresholds.json`

## Phase 2: Prototype + QA Consumer Uplift

目标：

- prototype 计算 page/state anchor score
- QA 计算 scenario `RAS`

交付：

- `prototype-anchor-scorecards`
- `scenario-anchor-map`
- `qa anchor scorecard`

## Phase 3: Typed Learning Plane Closure

目标：

- 顶层 contract 与候选分类对齐
- learning 只优化 judgement surfaces

交付：

- typed `learning-plane-contract.json`
- exemplar / negative exemplar support
- keep/discard scorecard update

## Phase 4: `v1.2.0` Forward Path

目标：

- PM skill-wrapper
- discovery surface
- takeover manifest / backlog / summary

交付：

- `beacon skill recommend`
- `beacon skill search`
- current-state manifest / backlog CLI

---

## 8. Verification Plan

至少新增以下验证面：

- version truth state model unit tests
- help/status decision trace regression tests
- project skill boundary validation tests
- scenario anchor metadata unit tests
- `RAS` threshold tests
- adjacent-semantics blocker tests
- prototype anchor score tests
- learning plane subject-surface alignment tests
- takeover manifest / baseline gate tests

重点回归样例：

1. `rolo` 开屏视频不漂成视频播放器
2. design review finding 能回写到下一轮 prototype/QA 输入
3. profile-bound project 不再默认落回 `native-single`
4. planning line / partial runtime supplement / current runtime line 可以同时表达

---

## 9. Non-goals

本蓝图明确不做：

- 让 Beacon 学项目运维命令
- 让 learning plane 直接改业务仓代码
- 把 Beacon 改成 PM skill library
- 在 `v1.1.12` 里完成所有 `v1.2.0` 前链路重构

---

## 10. Final Implementation Principle

`v1.1.12` 的真正实现原则是：

> 先让 Beacon 知道“什么属于这个需求”，
> 再决定“该往哪里扩、该在哪里测、该学什么、该阻断什么”。

如果没有 Requirement Anchor Kernel，
prototype 会漂、QA 会漂、rewrite 会漂、navigator 会漂、learning plane 也会漂。

因此这条线的最小可行实现，不是“再加一个评分器”，而是：

```text
一个统一的 requirement-anchor contract
+ prototype/qa/rewrite/profile/takeover consumers
+ typed learning plane
+ transparent decision trace
```
