---
feature_slug: beacon-agent-eval-v161
version: v1.6.1
authority: support_advisory
promotion_ref: docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md
---

# Research: Beacon Agent Eval v1.6.1

## outcome

v1.6.1 full parity Agent Eval：统一 `beacon eval` 分数面、capability catalog 全 harness 覆盖、replay/simulated/live 分层 runner、with_skill vs baseline 行为证据、composite 0–100 scorecard（runtime_evidence_only，不替代 formal QA/release）。

## lake_or_ocean

**海**（catalog 面向全 harness 能力覆盖定义）；本 feature package 为 **湖**（冻结 eval 契约与 scorecard schema）。

## truth_refs

- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md`（Skill Eval Benchmark 契约，条目 018–022）
- `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md`（program CLI 纳入 catalog）
- `docs/beacon/v1.6.0/features/beacon-truth-integrity-gates-v160/truth.md`

## source_refs

- 对话：scope A full parity、完善完整覆盖 Beacon 能力、eval 评估分数
- Planner review：`.beacon/state/planner-review/beacon-agent-eval-v161/pln-review-20260615t090341z.json`

## evidence_refs

- v1.6.0 `beacon skill eval-kit benchmark` 四类 artifact 契约
- v1.6.1 program harness QA 28/28（`beacon-harness-program-plan-v161`）

## truth_gap

v1.6.1 此前无统一 Agent Eval 公共面；skill eval 为 replay/模拟，无 composite scorecard 与 v1.6.1 catalog。

## test_gap

tests.md 映射 AC-AE-001..033。truth **frozen R2**（全 skill live P0，2026-06-15）。

## implementation_risk

- **全 skill live（37 条）** 成本/flaky/admission 护栏为 P0 主风险
- simulated 分数被误读为 release gate

## verification_risk

- TIG 对 anti-gaming 措辞敏感；evidence 索引须避免 deferral 占位词
- 分数 authority 必须与 formal QA 分离
- live matrix 条目数须与 doctor strict 对齐，禁止 silent 缩减

## recommended_route

change R2 refreeze → Phase A–F implement（live matrix 优先）→ beacon-eval-qa 33/33

## user_decision

promoted

## change_decision_r2

accepted_full_skill_live

用户确认：坚持全 skill live；37 条 host-visible skill live matrix 为 P0 closure 核心。

## promotion_ref

`docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md`

## Version Projection Truth Binding

- prd_refs: docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md
- user_story_refs: docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md
- test_case_refs: docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/tests.md
- coverage_notes: AC-AE-001..033 与 TC-AE-001..033；§I full skill live matrix（37 条）；AgentEvalState FSM；live admission；scorecard authority；R2 change 全 skill live。
- out_of_scope_notes: Agent Eval 分数不替代 `beacon qa run` / release；PB-AE-002（LLM judge）仍 defer v2。

## Decision Summary

```text
scope A (full_parity)
  → capability catalog materialize (pln/gen/eval/gov + CLI + program)
  → full skill live matrix（37 host-visible skills，doctor strict 对齐）
  → beacon eval run live regression-core 逐条 trace
  → scorecard (六维 + composite, runtime_evidence_only)
  → benchmark v1.6.1 case set (inherit taxonomy-v160 行为轴)
  → formal QA 仍由 beacon-eval-qa 裁决
```

## Deep Summary

- source_skill: `beacon-deep`
- updated_at: `2026-06-15T11:33:26.441696+00:00`
- deep_artifact_root: `docs/beacon/archive/v1.6.1/deep/beacon-agent-eval-v161`
- machine_artifact_root: `docs/beacon/archive/v1.6.1/.machine/deep/beacon-agent-eval-v161`
- deep_requirement_state: `required`
- status: `closed`
- route_decision: `closed`
- release_supplement_ref: `docs/beacon/archive/v1.6.1/.machine/deep/beacon-agent-eval-v161/release-supplement.json`
- adoption_status: `route_only`
