# Research: Beacon Planner Review Compound Parity v1.6.0

- outcome: 将 Compound 式多代理 review、source parity、防 MVP 缩水、finding 合成分级和工程闭环发现能力纳入 Beacon planner review。
- authority: support_advisory
- lake_or_ocean: lake
- truth_refs: docs/beacon/v1.6.0/features/beacon-pln-review-compound-parity-v160/truth.md
- source_refs: /Users/apple/.codex/skills/compound-engineering/ce-code-review/SKILL.md, docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md, docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md, skills/beacon/beacon-pln-review/SKILL.md
- evidence_refs: docs/beacon/v1.6.0/features/beacon-pln-review-compound-parity-v160/evidence.md
- truth_gap: 现有 planner review 已有 intent/source parity 和 multi-agent runtime 基础，但缺少 Compound 式 diff scope、persona finding 合成、autofix 分类、release ops 和 QA evidence hygiene 统一 contract。
- test_gap: 现有 benchmark 未系统覆盖 Compound parity、diff/worktree scope、autofix boundary、release ops closure 和 QA evidence hygiene。
- prd_refs: docs/beacon/v1.6.0/features/beacon-pln-review-compound-parity-v160/truth.md
- user_story_refs: docs/beacon/v1.6.0/features/beacon-pln-review-compound-parity-v160/truth.md
- test_case_refs: docs/beacon/v1.6.0/features/beacon-pln-review-compound-parity-v160/tests.md
- coverage_notes: AC-001..AC-016 map to TC-001..TC-016 with contract, unit, negative, behavior, regression and integration coverage.
- out_of_scope_notes: No new public lifecycle stage, no host-visible reviewer child skills, no planner repair execution, no QA/release verdict authority.
- implementation_risk: medium
- verification_risk: medium
- recommended_route: beacon-gen-change -> beacon-gen-implement -> beacon-eval-qa -> beacon-eval-release
- user_decision: accepted
- promotion_ref: docs/beacon/v1.6.0/features/beacon-pln-review-compound-parity-v160/truth.md

## 分析结论

Beacon 当前不是缺 QA 类型。真正缺口是 QA 之前和 release 之后的工程审查闭环：

- plan 阶段需要识别用户真实意图是否被缩小；
- source 项目能力需要转成 parity matrix；
- review findings 需要合成、去重、分级和路由；
- 小修复需要标记为 generator 可处理的 safe_auto，但 planner 不能自行修；
- 大问题需要 route 到 truth/change/implement/qa/release/governor；
- release/install/projection/canary/rollback 缺口需要被 review 发现；
- JUnit、assertion_count、fake runner、placeholder evidence 这类 QA evidence hygiene 问题需要提前暴露。

## State Machine

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

非法转移：

- 未解析 scope/source context 就选择 reviewer；
- full parity 未形成 parity matrix 就推荐 implement；
- lane 未输出 finding 或 no_findings 就合成；
- finding 未 dedup/arbitrate 就给 route；
- P0/P1 finding 没有 owner/route 就终止；
- planner 写 truth、代码、`.machine`、QA verdict 或 release verdict。

## User Decision

用户已明确要求使用 `beacon-gen-change v1.6.0` 落 `beacon-pln-review-compound-parity-v160`。本 research 已接受进入 package-authoritative truth。
