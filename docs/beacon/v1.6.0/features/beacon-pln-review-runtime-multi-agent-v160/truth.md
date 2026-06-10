---
slug: beacon-pln-review-runtime-multi-agent-v160
version: v1.6.0
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md
  user_story: docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md
  test_case: docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：Beacon Planner Review Runtime Multi-Agent v1.6.0

## 概述

`beacon-pln-review-runtime-multi-agent-v160` 补齐 `beacon-pln-review` 的真实多代理审查能力。上一轮 `beacon-pln-review-intent-parity-state-machine-v160` 已经建立了多视角 reviewer catalog、intent parity、source parity、deferral ledger 和 state-machine 审查标准，但 runtime 层仍主要是单 skill 内部规则合成。

本 feature 的目标是把“多视角”升级为可验证的 planner review multi-agent execution model：每个 reviewer 作为独立 reviewer lane 产出结构化 finding，合成器独立执行 merge/dedup/arbitration，runtime evidence 明确记录 lane spec、lane result、合成结果、冲突、fallback 和证据路径。它不是最小 MVP，也不能用“catalog 里有多个 reviewer”冒充真实多代理能力。

## 背景

当前 Beacon 已经具备以下能力：

- `beacon-pln-review` 作为收敛后的 planner public skill；
- internal reviewer catalog 覆盖 intent、scope、coverage、route、state-machine、source parity、security、performance、design、brownfield、evidence 和 simplification；
- benchmark 能证明 full parity 不被静默 MVP 化、source parity matrix 缺失会阻断、state-machine 落点缺失会路由回 truth/change；
- skill package 和 agent surface 已通过 v1.6.0 compact taxonomy 验证。

缺口是：这些 reviewer 目前不是 runtime 上可追踪的多代理 execution。用户要求“多代理、多角度审查”时，Beacon 必须能证明：

- 哪些 reviewer lane 被选中；
- 每个 lane 的输入边界、独立结论、finding 和 evidence refs；
- 哪些 finding 被合并、去重、提升 severity 或降级为 advisory；
- reviewer 冲突如何仲裁；
- host 没有 subagent 时如何明确 fallback，而不是伪装成并行多代理；
- planner HARD GATE 仍然阻止任何 truth/code/QA/release 写入。

## Scope Mode

本 feature 的 scope mode 是 `full_parity`，不得降级为 `mvp`。最小交付必须覆盖真实 multi-agent review execution contract、runtime artifact、skill surface 指引、benchmark case 和单元测试。任何延期都必须写入 deferral ledger 并由用户显式接受；本轮没有用户接受的延期。

## In Scope

- 定义 `beacon-pln-review` 的 runtime multi-agent review model。
- 新增 planner review runtime artifact builder，用于产生 deterministic reviewer lane specs、lane results、合成结果和 runtime evidence。
- reviewer lane 必须覆盖 always-on reviewer，且按 trigger 激活 conditional reviewer：
  - always-on：`intent-fidelity`、`scope-mode`、`coverage-shape`、`route-boundary`、`state-machine`；
  - conditional：`source-parity`、`deferral-sovereignty`、`security-boundary`、`performance-boundary`、`design-flow`、`brownfield-contract`、`evidence-proof-shape`、`simplification-risk`、`founder-business`、`adversarial-doubt`、`adr-documentation`、`context-engineering`。
- 每个 reviewer lane 必须产生独立结构化 finding 或明确 `no_findings`，不能只把所有 finding 写成单个综合段落。
- 合成器必须执行 merge/dedup/arbitration，并输出单一 `recommended_route`、冲突列表、最高 severity、user decision requirement 和 route rationale。
- runtime evidence 必须标记为 `runtime_evidence_only=true`、`requirement_truth=false`、`formal_verdict_authority=false`、`release_verdict_authority=false`。
- 当 host 不具备真实 subagent dispatch 时，必须输出 `execution_mode=single_process_multi_reviewer` 或 `fallback_reason`；不能声称 parallel subagent execution。
- 更新 `beacon-pln-review` skill references，说明 multi-agent review 是 planner-only runtime evidence，不写 truth、不实现、不验收。
- 扩展 `beacon skill eval-kit benchmark --version v1.6.0`，覆盖 multi-agent lane selection、independent findings、synthesis arbitration、fallback transparency、boundary negative。
- 增加可执行单元测试，验证 runtime artifact、benchmark grading 和 skill package projection。

## Out of Scope

- 不新增 public lifecycle stage。
- 不新增 `beacon-pln-review-agent-*` host-visible skills。
- 不让 planner 写 `features/<slug>/truth.md`、implementation、`.machine/`、QA verdict 或 release verdict。
- 不要求本 feature 接入真实外部 LLM worker；如果没有 host subagent runtime，必须 deterministic fallback，并把 fallback 作为证据字段。
- 不把 benchmark runtime evidence 当 formal QA 或 release verdict。

## Runtime Multi-Agent Review Contract

`beacon-pln-review` 的 multi-agent runtime artifact 必须包含：

```text
schema_version
feature
version
review_id
execution_mode
host_runtime
subagent_runtime_available
fallback_reason
input_context
selected_reviewers
reviewer_lanes[]
findings[]
synthesis
state_model
parity_matrix
deferral_ledger
evidence_paths
runtime_evidence_only
requirement_truth
formal_verdict_authority
release_verdict_authority
```

每个 `reviewer_lanes[]` 必须包含：

```text
reviewer
lane_id
role
trigger_reason
input_refs
output_status
finding_ids
confidence
authority_level
runtime_evidence_ref
```

每个 finding 必须沿用 `beacon-pln-review` finding schema，并额外包含：

```text
lane_id
merged_from
dedup_key
conflict_group
```

## Reviewer Selection

Always-on reviewer 每次都必须进入 `selected_reviewers`。Conditional reviewer 根据 prompt、source refs、truth refs、evidence refs 和关键词触发：

- source/full parity 触发 `source-parity`；
- MVP/cut/defer/partial 触发 `deferral-sovereignty`；
- auth/permission/secret/public route 触发 `security-boundary`；
- long-running/concurrency/cache/bulk/token/time 触发 `performance-boundary`；
- UI/UX/cross-screen/design 触发 `design-flow`；
- brownfield/legacy/migration/cutover 触发 `brownfield-contract`；
- QA/evidence/release/benchmark 触发 `evidence-proof-shape`；
- simplification 触发 `simplification-risk`；
- business/founder/CEO 触发 `founder-business`；
- challenge/doubt/adversarial 触发 `adversarial-doubt`；
- ADR/architecture decision 触发 `adr-documentation`；
- context/prompt drift/source order 触发 `context-engineering`。

## Synthesis And Arbitration

合成器必须：

- 按 `dedup_key` 合并重复 finding；
- 保留 `merged_from` lane 列表；
- 按 P0 > P1 > P2 > P3 提升 severity；
- authority 优先级为 `user_quote > package_truth > source_evidence > implementation_evidence > runtime_evidence > assumption`；
- 当 reviewer route 冲突时生成 `conflict_group`，并选择最保守的 route；
- P0/P1 `intent-fidelity`、`source-parity`、`state-machine`、`route-boundary` finding 必须阻断 implement/release route；
- 输出单一 `recommended_route`，只能是 `beacon-gen-truth`、`beacon-gen-change`、`beacon-gen-refreeze`、`beacon-gen-implement`、`beacon-eval-qa`、`beacon-eval-release`、`beacon-pln-friction` 或 `defer/queue`。

## State Model

本 feature 自身要求 state-machine review，状态机如下：

```text
ReviewRequested
  -> ContextResolved
  -> ReviewerSelection
  -> LaneExecution
  -> FindingSynthesis
  -> RouteRecommendation
  -> Terminal
```

Blocked transitions：

- `ReviewRequested -> LaneExecution` without context resolution；
- `ReviewerSelection -> FindingSynthesis` without lane outputs；
- `FindingSynthesis -> RouteRecommendation` without arbitration；
- any state -> truth/code/QA/release write from planner；
- fallback mode -> claimed parallel subagent execution。

Recovery paths：

- missing input refs -> route `beacon-pln-source` or `beacon-gen-change`；
- missing lane output -> mark lane blocked and synthesize conservative route；
- subagent unavailable -> `single_process_multi_reviewer` fallback with explicit reason；
- schema invalid -> route `beacon-gen-implement` repair after truth freeze。

Terminal states：

- `review_ready_for_truth_change`
- `review_ready_for_implementation`
- `review_blocked_needs_user_decision`
- `review_queued_or_deferred`

## 验收标准

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | feature-truth | 新 feature package 使用 package-authoritative truth，并声明 scope mode 为 `full_parity`。 |
| AC-002 | runtime-artifact | planner review runtime artifact 包含 review id、execution mode、host runtime、fallback reason、selected reviewers、reviewer lanes、findings、synthesis 和 evidence paths。 |
| AC-003 | always-on-lanes | always-on reviewers 每次都生成独立 reviewer lane。 |
| AC-004 | conditional-lanes | source parity、deferral、security、performance、design、brownfield、evidence、simplification、founder、doubt、ADR、context 等 conditional reviewer 按触发信号选择。 |
| AC-005 | independent-findings | 每个 lane 必须产生独立 finding 或明确 `no_findings`，不得只输出单一综合段落。 |
| AC-006 | synthesis | 合成器执行 merge/dedup/arbitration，保留 `merged_from`、冲突、最高 severity 和单一 recommended route。 |
| AC-007 | fallback-transparency | 没有真实 subagent runtime 时，必须显式 `single_process_multi_reviewer` 或 fallback reason，不得声称 parallel subagent execution。 |
| AC-008 | planner-boundary | planner runtime evidence 不写 truth、代码、`.machine`、QA verdict 或 release verdict。 |
| AC-009 | runtime-evidence-authority | runtime evidence 标记为非 truth、非 formal QA verdict、非 release verdict。 |
| AC-010 | state-machine | runtime multi-agent review 自身状态机覆盖 request、context、selection、lane execution、synthesis、route、terminal 和 blocked transitions。 |
| AC-011 | skill-surface | `beacon-pln-review` references 说明真实 multi-agent review model、fallback 语义和 planner-only 边界。 |
| AC-012 | benchmark | `beacon skill eval-kit benchmark --version v1.6.0` 覆盖 multi-agent lane selection、independent findings、synthesis、fallback transparency 和 planner boundary。 |
| AC-013 | tests | 单元测试覆盖 runtime artifact builder、benchmark grading 和 skill package projection。 |
| AC-014 | no-public-sprawl | 不新增 host-visible reviewer 子 skill；reviewer lanes 是 internal runtime evidence。 |
| AC-015 | implementation-evidence | 实现证据必须列出 changed files、测试命令、benchmark artifact 和 formal QA 后续路由。 |
