---
slug: beacon-truth-map-center-and-package-cutover
version: v1.5.1
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/archive/v1.5.1/prd/beacon-truth-map-center-and-package-cutover.md
  user_story: docs/beacon/archive/v1.5.1/user-story/beacon-truth-map-center-and-package-cutover.md
  test_case: docs/beacon/archive/v1.5.1/qa/test-cases/beacon-truth-map-center-and-package-cutover.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative_ready
truth_map_contract: beacon-truth-map-v1
---

# Feature Truth: Beacon Truth Map Center and Package Cutover

## Summary

v1.5.1 建立 truth-map resolver center。真相地图是 CLI resolver/static contract，不是 JSON truth。JSON/MD truth-map 输出只是 generated machine state、diagnostic、runtime record 或 evidence，不能成为 truth authority。

v1.5.1 可以执行 truth_center integration sweep：正常真相读取、写入目标解析、gate input 解析、legacy rebuild target、legacy absorb target 等入口统一接到 truth_center。该 sweep 只统一入口，不切换 truth authority；`feature_package_authoritative_ready` 保持准备态，v1.5.2 才能在验证通过后做 policy flip。

v1.5.1 还必须维护高风险真相入口 inventory。inventory 用于防止 `prd/user-story/test-case`、workflow、truth、gate、bootstrap、manifest、acceptance kit 和 skill 指南继续通过旧路径漂移。每个入口必须接入 truth_center/resolver，或被明确标记为 v1.5.1 legacy/generated/runtime 例外并绑定 fail-closed 或 v1.5.2 cutover 路径。

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | resolver-center | 提供 `beacon.utils.truth_map` 作为唯一 truth resolver 中心。 |
| AC-002 | no-json-authority | `truth-map.json` 只能由 resolver 生成，不能作为 truth authority 输入。 |
| AC-003 | md-authority-ready | `features/<slug>/truth.md`、`tests.md`、`tasks.md`、`evidence.md` 被定义为 v1.5.2 canonical-ready source。 |
| AC-004 | static-contract | resolver 暴露固定 contract constants，例如 truth source model、package contract、resolver contract。 |
| AC-005 | source-read-unification | 新增或改造的 CLI 真相读取必须通过 truth-map resolver，不允许新增硬编码旧路径。 |
| AC-006 | skill-read-unification | LLM skill 指南必须要求先读取 truth map，再读取 feature package。 |
| AC-007 | no-md-json-multiwrite | v1.5.1 不再把 Markdown 到 JSON 的多写投影作为验收目标。 |
| AC-008 | doctor-rebuild-path | doctor 提供或预留从 feature package 重建旧 triptych 的路径。 |
| AC-009 | change-absorb-path | change 提供或预留把旧 triptych 吸收到 feature package 的路径。 |
| AC-010 | drift-prevention | truth-map verify 能发现 resolver、feature package、旧 rebuild artifact 之间的漂移。 |
| AC-011 | machine-json-rebuild | truth-map 提供 requirement-derived `.machine` JSON 全量再生成计划和命令入口。 |
| AC-012 | machine-json-role-labels | 生成的机器面 JSON 必须标记 `machine_json_role = generated_state_not_truth` 或等价角色。 |
| AC-013 | source-hash-freshness | 再生成的机器面 JSON 必须记录 resolver contract、source paths 和 source hashes，并能验证 stale 状态。 |
| AC-014 | runtime-json-exemption | runtime/process JSON 保留为运行记录，不需要 Markdown twin，也不能作为 requirement authority。 |
| AC-015 | stale-machine-fail-closed | stale、非 resolver 生成或 source hash 不匹配的 `.machine` JSON 必须在 verify 中 fail closed。 |
| AC-016 | version-governance-resolver | truth-map resolver 必须解析版本级治理真相，不只解析 `features/<slug>` feature truth。 |
| AC-017 | governance-authority-classification | resolver 必须区分 feature truth、version governance truth、generated governance state、runtime/process record。 |
| AC-018 | manifest-index-not-truth | manifest、index、cache JSON 只能是 resolver 生成或校验的索引/缓存，不能作为 truth authority 输入。 |
| AC-019 | material-audit-resolver-first | material-audit 必须先询问 resolver，再读取 manifest 或旧路径；manifest 只能作为辅助索引。 |
| AC-020 | qa-release-resolver-first | QA、release、status 等版本治理消费面必须 resolver-first，不能直接拼接旧版本级路径。 |
| AC-021 | governance-fail-closed | resolver 找不到必须的版本治理真相或发现 manifest/source hash 漂移时，治理消费面必须 fail closed。 |
| AC-022 | no-feature-package-overload | 不允许把 global boundaries、summary、release、source architecture、metadata 等版本治理材料塞进 feature package。 |
| AC-023 | generated-governance-state-labels | QA/release/material-audit/manifest 等生成治理状态必须带有非 authority 角色标签或等价声明。 |
| AC-024 | implement-governance-preflight | `implement plan`、`compile-plan`、`team-plan`、`dev-run` 必须 resolver-first 校验 version governance metadata branch contract；metadata、当前 git branch、git workflow expected branch 不一致时必须在 implement 前 fail closed。 |
| AC-025 | truth-center-integration-sweep | v1.5.1 可把正常真相读取、写入目标解析、gate input 解析、legacy rebuild target、legacy absorb target 等入口统一接到 truth_center；但不得在 v1.5.1 切换真相权威，`feature_package_authoritative_ready` 必须保持为准备态，v1.5.2 仅在 sweep 验证后做 policy flip。 |
| AC-026 | truth-center-entrypoint-inventory | v1.5.1 必须维护高风险真相读写入口 inventory，至少覆盖 `beacon/commands/prd.py`、`beacon/commands/user_story.py`、`beacon/commands/test_case.py`、`beacon/commands/workflow.py`、`beacon/commands/truth.py`、`beacon/commands/gate.py`、`beacon/utils/prd_bootstrap.py`、`beacon/utils/requirement_clarity.py`、`beacon/utils/requirement_deepening.py`、`beacon/utils/manifest.py`、`beacon/utils/acceptance_kit.py`、packaged skills、`.agents/skills`；每项必须接入 truth_center/resolver，或明确声明为 v1.5.1 legacy/generated/runtime 例外并给出 fail-closed 或 v1.5.2 cutover 处理路径。 |

## Authority

The authority source is Markdown feature package plus CLI resolver contract. JSON twins are not required for truth validity.

## Version Governance Boundary

Version governance truth is not part of `features/<slug>`. It remains in version-level materials such as `global-boundaries.md`, `SUMMARY.md`, `execution/`, `source-architecture/`, `release/`, metadata, QA, release, manifest, and material-audit state. These surfaces must be resolved and classified through truth-map resolver before consumption.

Implement entry points are version governance consumers. They must resolve metadata branch contract and git workflow projection through the resolver before planning or execution, and must fail closed on branch drift instead of deferring the problem to QA or release.

## Entrypoint Inventory Boundary

The inventory must include high-risk command, utility, and skill surfaces:

- `beacon/commands/prd.py`
- `beacon/commands/user_story.py`
- `beacon/commands/test_case.py`
- `beacon/commands/workflow.py`
- `beacon/commands/truth.py`
- `beacon/commands/gate.py`
- `beacon/utils/prd_bootstrap.py`
- `beacon/utils/requirement_clarity.py`
- `beacon/utils/requirement_deepening.py`
- `beacon/utils/manifest.py`
- `beacon/utils/acceptance_kit.py`
- `skills/beacon/**/SKILL.md`
- `.agents/skills/**/SKILL.md`

Each row must be classified as resolver/truth_center-routed, v1.5.1 legacy exception, generated state, or runtime/process record. Legacy/generated/runtime exceptions must carry fail-closed or v1.5.2 cutover handling. Skill references to `prd/user-story/test-case` must not present those paths as the future authoritative truth source.

## Machine JSON Boundary

Requirement-derived `.machine` JSON must be regenerated from resolver-selected Markdown and labeled as generated state/evidence. Runtime/process JSON remains allowed as execution record. Neither class is truth authority.
