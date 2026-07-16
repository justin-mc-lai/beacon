---
slug: beacon-skill-harness-taxonomy-v160
version: v1.6.0
authority: support_advisory
status: queued
created: 2026-06-09
updated: 2026-06-09
user_decision: queued
promotion_ref: ""
---

# Beacon Skill Harness Taxonomy v1.6.0 Research Index

## Support Advisory Contract

- authority: support_advisory
- status: queued
- outcome: 收敛 Beacon v1.6.0 compact skill harness taxonomy、formal QA evidence binding 和 skill eval benchmark 闭环。
- lake_or_ocean: lake，范围集中在单个 v1.6.0 feature package、skill package projection、QA matrix 和 eval-kit behavior evidence。
- truth_refs: docs/beacon/archive/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md, docs/beacon/archive/v1.6.0/features/beacon-skill-harness-taxonomy-v160/tests.md
- source_refs: beacon/utils/agent_surface.py, beacon/utils/qa_feature.py, beacon/commands/auto_test.py, beacon/utils/skill_eval_kit.py
- evidence_refs: docs/beacon/archive/v1.6.0/research/skill-creator-eval-harness-research.md, .beacon/state/skill-eval/benchmarks/
- truth_gap: 无；本文件不是 requirement truth，只索引 planner support_advisory 研究结论。
- test_gap: formal QA 需继续验证 TC-003 到 TC-017 的 generated projection、research contract、negative promotion gate 和 behavior benchmark。
- implementation_risk: medium，主要风险是 generated skill projection、host-visible package 和 QA runtime matrix target 不一致。
- verification_risk: medium，主要风险是 CLI structured evidence 未被 QA 识别为 assertion/JUnit evidence。
- recommended_route: beacon-gen-implement
- user_decision: queued
- promotion_ref:

## Notes

本文件只补齐 `research/<feature-slug>.md` planner support_advisory surface，不能替代
`features/beacon-skill-harness-taxonomy-v160/{truth,tests,tasks,evidence}.md`，也不能作为
implementation、QA 或 release closure。若后续要把研究结论升级为需求真相，必须先由用户接受并通过
`beacon-gen-change` / `beacon-gen-refreeze` 进入 frozen feature package。
