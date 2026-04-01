# User Story: Beacon 版本真相、项目执行边界与 learning-plane typed governance（v1.1.12）

**Feature**: `beacon-version-truth-profile-boundary-governance`
**Version**: `v1.1.12`

## Story

**As a** 使用 Beacon 管理多版本文档、project profile、takeover 接管、project skill 执行面与 autoresearch learning plane 的维护者 / release owner / AI coding agent
**I want** Beacon 在 `v1.1.12` 统一版本真相、把 navigator 改成 profile-aware first、收紧 project skill 执行边界、把 learning plane 拆成 typed policy surfaces、把 QA/autoresearch 发散锚定到 requirement boundary 内，并把 takeover baseline 变成 runtime gate
**So that** Beacon 不会在真实项目里因为版本漂移、错误执行面、过宽 shell 编排、需求外发散或未冻结 baseline 而把人和 agent 拉向错误路径

## Story Slices

### US-001: 当前版本真相必须有单一机器源
作为 release owner，我希望 skill / help / status / docs current line / package version 都读取同一份 machine-readable version truth，而不是各自维护“当前版本”。

### US-002: Beacon 的职责边界必须固定为四层
作为 Beacon 维护者，我希望 Requirement kernel、Delivery evidence kernel、Project execution adapters、Learning plane 各自有清晰职责和禁区，不再混层。

### US-003: Navigator 必须 profile-aware first
作为项目使用者，我希望 help / doctor / status 的下一步推荐先看 project mode、feature binding 和 stage-local execution surface，再决定是否降级到 Beacon native 路径。

### US-004: Project skill orchestration 不能退化成任意 shell 编排
作为平台维护者，我希望 orchestration 在执行前先校验 supported stages、capabilities 和 evidence contract，不满足就 blocked。

### US-005: Learning plane 必须是 typed policy surfaces
作为 Beacon 维护者，我希望 autoresearch/evo 只优化显式类型化的小策略面，而不是继续挂在模糊 requirement rewrite 或任意执行动作上。

### US-006: Takeover 项目必须先冻结 current-state baseline
作为 takeover 项目负责人，我希望 Beacon 在 architecture / service map / refactor boundaries / frozen baseline 不完整时阻止进入 implement。

### US-007: 项目 service-slice map 应该作为只读 contract input
作为 profile 项目协作者，我希望像 `rolo` 这样的项目把 service slices / evidence contracts 作为 Beacon 的只读输入，而不是把 Layer 3 项目执行动作并回 Beacon core。

### US-008: QA/autoresearch 发散必须锚定 requirement
作为质量与学习面维护者，我希望 Beacon 的场景扩展始终锚定 PRD、user story、project contract 与 evidence truth，而不是从需求语义漂移到相邻产品语义。

### US-009: 发散场景必须有 Requirement Anchor Score
作为 release owner，我希望每个新增或学习到的发散场景都能被 `Requirement Anchor Score (RAS)` 量化，并用明确阈值控制自动执行、review 或 blocked。

### US-010: 系统必须透明解释推荐与阻断
作为项目协作者，我希望 help / status / review / gate / QA scenario generation 都输出 decision trace，说明版本真相、执行面、学习面、评分和 blocked reason。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Single Version Truth | Beacon 必须存在单一 machine-readable version truth source，至少表达 runtime/package/docs default line/planning line/partial runtime supplement |
| AC-002 | Responsibility Layering | Beacon 必须把 Requirement kernel、Delivery evidence kernel、Project execution adapters、Learning plane 的职责和禁区固定为四层模型 |
| AC-003 | Separate Status Semantics | `planning line`、`partial runtime supplement`、`current runtime line` 必须可同时表达，避免 release truth 自相矛盾 |
| AC-004 | Profile-aware First | help / doctor advise / status 的下一步推荐必须先看 project mode、feature/profile binding、stage-local binding，再决定是否 native fallback |
| AC-005 | No Premature Native Default | 存在 profile binding 时，Beacon 不得默认先推荐 `native-single` 或 generic review path |
| AC-006 | Stage Validation | project skill orchestration 运行前必须校验 `skill.supported_stages` 覆盖当前 node stage |
| AC-007 | Capability Validation | orchestration 运行前必须校验 `skill.capabilities` 与请求动作一致，不一致则 blocked |
| AC-008 | Evidence Contract Validation | node 声明的 `produces_evidence` / `produces_cases` 必须与 skill/profile contract 一致，不一致则 blocked |
| AC-009 | Adapter Boundary | project skill execution 不得退化成无边界任意 shell 编排；若保留 command template，必须经过 adapter-boundary 校验 |
| AC-010 | Typed Learning Plane | learning plane 必须显式区分 `qa_policy`、`design_policy`、`contract_policy`、`rewrite_policy`、`debug_policy`、`benchmark_policy` |
| AC-011 | Design Surface Alignment | `v1.1.12` 文档里声明的 design brief extraction / guideline mapping / review thresholds 等 surfaces 必须在 learning plane contract 中可见 |
| AC-012 | Takeover Baseline Gate | project mode=`takeover` 时，缺少 architecture blueprint / current-state service map / refactor boundaries / frozen baseline 任一项都不得进入 implement |
| AC-013 | Readonly Project Inputs | `rolo` 这类项目的 service-slice map / boundary docs / required evidence contracts 必须作为只读 contract inputs，而不是 Beacon core 的通用实现动作 |
| AC-014 | Requirement-anchored Expansion | QA/autoresearch 发散场景必须携带 `anchor_ids`、`anchor_kinds`、`semantic_scope`、`divergence_budget`、`adjacent_capability_flags` 等锚定信息 |
| AC-015 | Requirement Anchor Score | 每个发散场景必须计算 `RAS`，并按 auto / review / manual / blocked 四个分段治理 |
| AC-016 | Adjacent-semantics Drift Block | 若 requirement 仅是开屏页视频上传/展示，Beacon 不得自动把场景扩张成视频播放器语义，如 `500MB` 压测、seek、fullscreen、subtitle、buffering |
| AC-017 | Transparent Decision Trace | help / status / review / gate / QA scenario generation 输出必须包含 `version_truth_source`、`project_mode`、`execution_surface`、`learning_surface`、`requirement_anchor_score`、`blocked_reason` |
| AC-018 | Stable Workflow Order | Beacon 必须先解析 version truth、project mode、execution surface、learning surface、requirement anchors，再进入 help / implement / review / gate |

## First-principles Loop

正确链路应是：

```text
resolve version truth
→ resolve project mode
→ resolve feature/profile/stage binding
→ resolve allowed execution surface
→ resolve allowed learning surface
→ resolve requirement anchors + divergence budget
→ run workflow / verify / implement / gate
```

不是：

```text
先推 generic Beacon path
→ 运行中再发现 profile / takeover / version truth 不一致
```

## Anti-drift Example

以 `rolo` 开屏页视频上传/展示需求为例：

- 需求内发散：
  - 上传失败重试
  - 格式不合法提示
  - 展示成功证据回放
  - 在已声明大小边界附近做验证
- 需求外漂移：
  - 上传 `500MB` 视频并验证长时间流畅播放
  - seek / pause / fullscreen / subtitle / buffering
  - 背景播放恢复

这类“把开屏素材展示扩张成视频播放器验证”的场景，默认应得到很低的 `RAS`，并被 blocked。

## Notes

- 这条线不是为了把 Beacon 扩成“更强大的项目执行器”。
- 它的目标恰恰相反：把 Beacon 收回到 requirement/evidence kernel，并把 project adapter 和 learning plane 的边界说清楚。
- `autoresearch` 应优化 Beacon 的判断系统，不应优化项目的执行系统。
