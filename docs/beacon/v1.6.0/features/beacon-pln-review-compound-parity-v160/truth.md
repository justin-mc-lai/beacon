---
slug: beacon-pln-review-compound-parity-v160
version: v1.6.0
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/v1.6.0/features/beacon-pln-review-compound-parity-v160/truth.md
  user_story: docs/beacon/v1.6.0/features/beacon-pln-review-compound-parity-v160/truth.md
  test_case: docs/beacon/v1.6.0/features/beacon-pln-review-compound-parity-v160/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：Beacon Planner Review Compound Parity v1.6.0

## 概述

`beacon-pln-review-compound-parity-v160` 把 Compound Engineering 式多代理 code review 能力、source parity 防缩水能力和 finding 合成分级能力正式纳入 Beacon planner 面。

本 feature 不是“再增加一批 planner skills”，也不是把 QA 类型继续堆厚。它的目标是在 Beacon 已有 truth/evidence/release 闭环之上，补齐 plan 到 truth 之前的工程审查能力：

- 多 reviewer 审查必须系统化，而不是靠单段总结；
- 用户说“复刻、同等能力、做全、不要 MVP”时，必须默认进入 `full_parity`；
- 任何能力裁剪、延期、MVP 降级都必须进入 deferral ledger，并要求用户显式接受；
- review findings 必须可合成、可去重、可分级、可路由；
- 小问题只能被标记为 generator 可执行的 `safe_auto` 候选，planner 自身不能改 truth 或代码；
- 大问题必须路由到 truth/change/implement/qa/release/governance，而不能被 review 阶段静默吞掉。

## 背景

Beacon v1.6.0 已经具备：

- compact harness skill surface；
- `beacon-pln-review` 作为 planner 多视角审查入口；
- intent parity、source parity、state-machine 和 runtime multi-agent review 的基础 contract；
- QA9、多层验收、benchmark、release gate 和 post-release skill surface 管理。

但对比 Compound、gstack、OpenSpec、Spec Kit 和 compound-engineering-plugin，Beacon 仍缺少一层可交付的 planner review 工程能力：

- Compound 强在 diff/PR scope、persona reviewer、finding 合成、autofix 分类和人工路由；
- gstack 强在开发操作闭环、浏览器会话、deploy/canary/ship；
- OpenSpec / Spec Kit 强在轻量 spec/change ergonomics；
- Beacon 强在真相唯一、证据闭环和 release gate，但 planner review 还需要把“用户真实意图和 source 能力”完整带进 truth，而不是只形成可读建议。

本 feature 聚焦 planner review 能力，不替代后续 `beacon-gen-change`、`beacon-gen-implement`、`beacon-eval-qa` 或 `beacon-eval-release`。

## Scope Mode

本 feature 的 scope mode 是 `full_parity`。不得降级为 MVP。

用户已明确要求保留 Beacon 真相交付能力，同时补齐其他 OSS 工程边界。因此本轮冻结必须覆盖：

- Compound 式多代理 review 结构；
- source parity delivery；
- finding schema 和 synthesis；
- autofix routing boundary；
- PR/diff/worktree scope review；
- release ops closure review；
- QA evidence hygiene review；
- harness 边界和状态机落点。

## In Scope

- 扩展 `beacon-pln-review` 的 planner review artifact contract，使其覆盖 Compound 式 reviewer catalog、scope detection、finding 合成和 route synthesis。
- 定义 source parity delivery mode：当用户引用 source 项目、成熟 OSS、完整复刻、同等能力、做全或不要 MVP 时，必须产生 source capability inventory、parity matrix、coverage mapping 和 deferral ledger。
- 定义 PR/diff/worktree scope review contract：review 必须能描述 base scope、changed files、untracked/generated files、skill projection surface 和 risk classification。
- 定义 finding synthesis contract：finding 必须有 severity、confidence、authority、dedup key、merged_from、conflict_group、owner、autofix_class、recommended_route 和 verification requirement。
- 定义 autofix routing contract：planner 只能分类，不执行修复；`safe_auto` 候选必须路由到 generator；`gated_auto`、`manual`、`human`、`release` 必须要求用户或对应 harness 处理。
- 定义 release ops closure review contract：planner review 能识别 post-release install、agent skill projection、多副本漂移、canary、rollback 和 hook evidence 缺口，并路由到 release/governor。
- 定义 QA evidence hygiene review contract：review 能识别 JUnit、assertion_count、fake runner、placeholder evidence、browser admission 和 compatibility evidence 缺口，并路由到 QA 或 implement。
- 更新 `beacon-pln-review` references，使 Compound parity 能力作为内部 reviewer/runtime contract 出现，不新增 host-visible reviewer 子 skill。
- 扩展 skill eval benchmark，覆盖 Compound parity、source parity、防 MVP 缩水、finding synthesis、autofix boundary、PR/diff scope、release ops 和 QA evidence hygiene。
- 增加可执行测试，验证 truth package、review artifact schema、synthesis rules、benchmark case 和 skill projection。

## Out of Scope

- 不新增 Beacon 主生命周期 stage。
- 不新增 `beacon-pln-review-correctness`、`beacon-pln-review-security` 等 host-visible 子 skill。
- 不让 planner 执行代码修复、truth 写入、QA verdict 或 release verdict。
- 不要求本 feature 实现真实 PR 平台集成、GitHub API 自动评论或外部 LLM worker 调度；若未接入，必须作为 deferral 或 runtime fallback 明确记录。
- 不把 review artifact 当作 requirement truth、QA pass 或 release go verdict。
- 不替代 `beacon-eval-qa` 的正式验收，也不替代 `beacon-eval-release` 的发布门禁。

## Planner Review Compound Parity Contract

`beacon-pln-review` 必须支持一个 Compound parity review output contract：

```text
schema_version
review_id
feature
version
intent_snapshot
scope_mode
diff_scope
source_capability_inventory
parity_matrix
coverage_mapping
deferral_ledger
selected_reviewers
reviewer_lanes
findings
synthesis
autofix_routing
release_ops_review
qa_evidence_hygiene
state_model
recommended_route
user_decision_required
runtime_evidence_only
requirement_truth
formal_verdict_authority
release_verdict_authority
```

`runtime_evidence_only=true`、`requirement_truth=false`、`formal_verdict_authority=false`、`release_verdict_authority=false` 是强制字段。

## Reviewer Catalog Contract

Always-on reviewer：

| Reviewer | Purpose |
|---|---|
| `correctness-reviewer` | 检查逻辑、状态、边界条件和错误传播。 |
| `testing-reviewer` | 检查测试覆盖、断言强度、mock-only 风险和证据形态。 |
| `maintainability-reviewer` | 检查复杂度、耦合、命名、重复和长期维护风险。 |
| `project-standards-reviewer` | 检查 AGENTS、skill creator、Beacon harness、package truth 和路径规范。 |
| `intent-fidelity-reviewer` | 检查用户真实意图是否被误译、弱化、MVP 化或静默延期。 |
| `route-boundary-reviewer` | 检查 planner/generator/evaluator/governor 边界是否被越权。 |

Conditional reviewer：

| Reviewer | Trigger |
|---|---|
| `source-parity-reviewer` | 用户引用 OSS/source、完整复刻、同等能力、做全、parity、不要 MVP。 |
| `diff-scope-reviewer` | 存在 PR、branch、base、worktree、untracked files、generated files 或 skill projection。 |
| `security-reviewer` | 涉及 auth、permission、secret、public endpoint、敏感数据或用户输入。 |
| `performance-reviewer` | 涉及长任务、并发、缓存、批量、token、时间预算、IO 或数据处理。 |
| `api-contract-reviewer` | 涉及 CLI/API schema、command contract、JSON payload、version surface。 |
| `reliability-reviewer` | 涉及 retries、resume、rollback、canary、timeouts、failure recovery。 |
| `browser-ops-reviewer` | 涉及浏览器、CDP、attached session、SSO、live protected surface 或 UI evidence。 |
| `release-ops-reviewer` | 涉及 install、global/local skill projection、post-release hooks、canary、rollback。 |
| `adversarial-reviewer` | 大变更、高风险、跨 harness、source parity 或用户质疑时触发。 |
| `state-machine-reviewer` | 涉及 lifecycle、workflow、loop、queue、resume、stop、recovery、multi-agent 或 gate transitions。 |

Reviewer catalog 是内部能力，不新增同名 public skills。

## Source Parity Delivery Contract

当 prompt 或 source refs 触发 `source-parity-reviewer` 时，review artifact 必须包含：

- source project / artifact refs；
- source capability inventory；
- source behavior/state/API/CLI/evidence boundary；
- target Beacon capability mapping；
- missing parity items；
- accepted deferrals；
- rejected or unapproved deferrals；
- coverage mapping；
- recommended route。

默认规则：

- “完整复刻”“同等能力”“做全”“不要 MVP”“parity”“same capability” 默认 `scope_mode=full_parity`。
- 缺少 source capability inventory 时，不得进入 implement。
- 缺少 parity matrix 时，不得 freeze full parity truth。
- 缺少 deferral ledger 时，不得把 full parity 缩小为 MVP。
- 任何 deferral 必须有 user decision；没有用户接受就保持 blocker。

## Finding Synthesis Contract

每个 finding 必须包含：

```text
finding_id
reviewer
lane_id
severity: P0 | P1 | P2 | P3
confidence: 0 | 25 | 50 | 75 | 100
authority_level: user_quote | package_truth | source_evidence | implementation_evidence | runtime_evidence | assumption
issue
evidence_refs
affected_surface
dedup_key
merged_from
conflict_group
owner: planner | generator | evaluator | governor | human | release
autofix_class: safe_auto | gated_auto | manual | advisory | human | release
requires_verification
recommended_route
user_decision_required
```

合成器必须：

- 按 `dedup_key` 合并重复 finding；
- 保留 `merged_from` reviewer/lane；
- 按 P0 > P1 > P2 > P3 选择最高 severity；
- 对 route 冲突生成 `conflict_group`；
- authority 优先级为 `user_quote > package_truth > source_evidence > implementation_evidence > runtime_evidence > assumption`；
- 选择最保守 route；
- 输出单一 `recommended_route`。

## Autofix Routing Contract

Planner review 不得执行修复。它只能分类和路由。

| autofix_class | Meaning | Allowed next route |
|---|---|---|
| `safe_auto` | 局部、确定、低风险，可由 generator 执行的候选修复。 | `beacon-gen-implement` |
| `gated_auto` | 有明确修复方式，但涉及行为、contract、权限、版本或用户承诺。 | `beacon-gen-change` 或用户确认后 `beacon-gen-implement` |
| `manual` | 需要人类或后续工作拆分。 | `human`、`beacon-pln-friction`、`defer/queue` |
| `advisory` | 提示性 finding，不阻断但必须留证据。 | `defer/queue` 或后续 review |
| `release` | 影响 ship/canary/install/rollback。 | `beacon-eval-release` 或 `beacon-gov-doctor` |

P0/P1 finding 不得被 planner 自动修复；必须路由。

## Diff / PR / Worktree Scope Contract

当 review 涉及代码变更时，artifact 必须能表达：

- base ref 或无法确定 base 的 reason；
- changed tracked files；
- untracked files；
- generated/projection files；
- deleted files；
- touched harness surfaces；
- affected truth/test/evidence surfaces；
- high-risk file categories；
- review scope confidence。

无法确定 diff scope 时，不得给“完整 review 已完成”的结论，只能输出 degraded review 和 route。

## Release Ops Closure Review Contract

当 feature 触发 release/install/skill projection/post-release 语义时，review 必须检查：

- repo source skill；
- project `.agents/skills` projection；
- global agent skill projection；
- stale duplicate skill copies；
- post-release hook evidence；
- canary or smoke install evidence；
- rollback or cleanup route；
- version surface alignment。

缺少这些 evidence 时，planner 只能 route 到 `beacon-eval-release`、`beacon-gov-doctor` 或 `beacon-gov-hooks`，不能声明 release ready。

## QA Evidence Hygiene Review Contract

当 review 涉及 QA、benchmark、browser、compatibility 或 release proof 时，review 必须检查：

- passed layer 是否有真实命令；
- pytest/JUnit 是否写入 `junit.xml`；
- assertion_count 是否大于 0；
- fake runner / placeholder evidence 是否存在；
- browser admission 是否可解释；
- compatibility matrix 是否有 pair evidence；
- benchmark artifact 是否包含 metadata、grading、analysis；
- residual stop reasons 是否被路由。

`assertion_count_zero_pass`、`junit_missing_or_invalid`、`placeholder_evidence`、`fake_runner` 必须产生 finding。

## State Model

本 feature 需要状态机审查。

```text
ReviewRequested
  -> ScopeResolved
  -> SourceParityResolved
  -> ReviewerSelection
  -> LaneExecution
  -> FindingSynthesis
  -> RouteRecommendation
  -> Terminal
```

Blocked transitions：

- `ReviewRequested -> ReviewerSelection` without scope or source context；
- `SourceParityResolved -> RouteRecommendation` without parity matrix when full parity is required；
- `LaneExecution -> FindingSynthesis` without lane output or no_findings marker；
- `FindingSynthesis -> RouteRecommendation` without dedup/arbitration；
- `RouteRecommendation -> Terminal` while P0/P1 finding has no owner or route；
- any planner state -> truth/code/QA/release write。

Terminal states：

- `review_ready_for_truth_change`
- `review_ready_for_implementation`
- `review_blocked_needs_user_decision`
- `review_degraded_scope_unknown`
- `review_queued_or_deferred`

## 验收标准

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | feature-package | 新 feature package 使用 package-authoritative truth，状态为 frozen，scope mode 为 `full_parity`。 |
| AC-002 | compound-review-contract | `beacon-pln-review` references 定义 Compound parity review output contract。 |
| AC-003 | reviewer-catalog | always-on 和 conditional reviewer catalog 覆盖 correctness、testing、maintainability、standards、intent、route、source parity、diff scope、security、performance、API、reliability、browser ops、release ops、adversarial 和 state machine。 |
| AC-004 | source-parity | 用户表达完整复刻、同等能力、做全、不要 MVP 或引用 OSS/source 时，默认 `scope_mode=full_parity`，并要求 source capability inventory、parity matrix、coverage mapping 和 deferral ledger。 |
| AC-005 | no-silent-mvp | full parity 到 MVP、patch 或 defer 的任何降级必须进入 deferral ledger，并要求用户显式接受。 |
| AC-006 | finding-schema | findings 包含 severity、confidence、authority、dedup、merged_from、conflict_group、owner、autofix_class、requires_verification 和 recommended_route。 |
| AC-007 | synthesis | synthesis 必须执行 merge/dedup/arbitration，保留冲突，提升最高 severity，并输出单一 recommended route。 |
| AC-008 | autofix-boundary | planner 只能分类 `safe_auto/gated_auto/manual/advisory/release`，不能执行修复；safe_auto 只能路由到 generator。 |
| AC-009 | diff-scope | PR/diff/worktree review 必须记录 base、changed、untracked、generated/projection、deleted、high-risk files 和 scope confidence；scope 不明时输出 degraded review。 |
| AC-010 | release-ops | release/install/skill projection 场景必须检查 global/local skill、stale copies、post-release hooks、canary/smoke install、rollback 和 version alignment。 |
| AC-011 | qa-evidence-hygiene | QA/benchmark/browser/compatibility 场景必须检查 JUnit、assertion_count、fake runner、placeholder evidence、browser admission、compatibility pair evidence 和 benchmark metadata/grading/analysis。 |
| AC-012 | state-machine | review 状态机覆盖 scope、source parity、reviewer selection、lane execution、finding synthesis、route recommendation、blocked transitions 和 terminal states。 |
| AC-013 | planner-boundary | review artifact 明确非 truth、非 QA verdict、非 release verdict，并禁止 planner 写 truth、代码、`.machine` 或执行修复。 |
| AC-014 | benchmark | `beacon skill eval-kit benchmark --version v1.6.0 --json` 覆盖 Compound parity、source parity、防 MVP 缩水、finding synthesis、autofix boundary、diff scope、release ops 和 QA evidence hygiene。 |
| AC-015 | tests | 单元/契约测试覆盖 review contract references、artifact schema、synthesis rules、benchmark grading 和 skill projection。 |
| AC-016 | no-public-sprawl | 不新增 host-visible reviewer 子 skill；新增能力必须作为 `beacon-pln-review` internal reviewer/reference/runtime contract。 |

