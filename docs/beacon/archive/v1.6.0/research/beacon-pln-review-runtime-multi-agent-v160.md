# Research: Beacon Planner Review Runtime Multi-Agent v1.6.0

- outcome: 将 `beacon-pln-review` 从多视角 catalog 升级为可验证的 planner-only multi-agent runtime evidence。
- authority: support_advisory
- lake_or_ocean: lake
- truth_refs: docs/beacon/archive/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md
- source_refs: skills/beacon/beacon-pln-review/references/reviewer-catalog.md, beacon/utils/skill_eval_kit.py, beacon/utils/implement_native.py, beacon/commands/qa.py
- evidence_refs: docs/beacon/archive/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/evidence.md
- truth_gap: 现有 truth 已要求多角度 reviewer，但没有要求真实 runtime reviewer lane、独立 finding、合成仲裁和 fallback evidence。
- test_gap: 现有 benchmark 证明 reviewer synthesis，但未证明独立 lane execution、fallback transparency 和 fake parallel claim 阻断。
- prd_refs: docs/beacon/archive/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md
- user_story_refs: docs/beacon/archive/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md
- test_case_refs: docs/beacon/archive/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/tests.md
- coverage_notes: AC-001..AC-015 map to TC-001..TC-015 with contract, unit, behavior, regression, integration and evidence coverage.
- out_of_scope_notes: No new public lifecycle stage, no host-visible reviewer child skills, no planner truth/code writes, no QA/release verdict authority.
- implementation_risk: medium
- verification_risk: medium
- recommended_route: beacon-gen-change -> beacon-gen-implement -> beacon-eval-qa
- user_decision: accepted
- promotion_ref: docs/beacon/archive/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md

## 分析结论

当前 `beacon-pln-review` 已具备多视角规则，但不是 runtime multi-agent。补齐方向必须避免两个假闭环：

- 不用 reviewer catalog 冒充真实多代理；
- 不用 deterministic fallback 冒充 parallel subagent execution。

因此冻结范围必须要求 runtime artifact 同时记录 selected reviewers、reviewer lanes、lane findings、synthesis、fallback 和 authority flags。

## State Machine

```text
ReviewRequested -> ContextResolved -> ReviewerSelection -> LaneExecution -> FindingSynthesis -> RouteRecommendation -> Terminal
```

非法转移：

- 未解析 context 就执行 lanes；
- 未产生 lane outputs 就合成；
- 未仲裁冲突就推荐 route；
- planner 写 truth/code/.machine/QA/release；
- fallback 模式声称 parallel subagent。

## User Decision

用户已明确要求“不是最小 MVP，而是完善的 review 真实多代理能力”，本 research 已接受进入 truth/change。
