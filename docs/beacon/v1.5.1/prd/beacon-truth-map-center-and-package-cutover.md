# PRD: Beacon Truth Map Center and Package Cutover

- version: `v1.5.1`
- feature: `beacon-truth-map-center-and-package-cutover`
- status: `frozen`
- language: `zh`

## Problem

Beacon v1.5.0 已经上线 `features/<slug>/{truth,tests,tasks,evidence}.md`，但它仍是并行 read model。当前源码中大量命令、工具和 skill 仍直接拼接旧路径，例如 `prd/`、`user-story/`、`qa/test-cases/`、`.machine/`。

如果直接把 feature package 改成唯一真相，会出现局部读新源、局部读旧源的漂移。

## Goals

v1.5.1 建立 truth-map resolver center，让 Beacon 所有真相读取入口逐步收敛到一个确定性 resolver。该 resolver 是 CLI 函数和静态 schema contract，不是 JSON 文件。

同时，v1.5.1 必须补齐机器面 JSON 的全量收敛/再生成路径：所有 requirement-derived `.machine` JSON 必须由 resolver 选定的 Markdown truth 重建、带 source hash，并被明确标记为 generated machine state，而不是 truth source。

另外，v1.5.1 必须补齐 version governance resolver：truth-map resolver 不只解析 feature package，也要解析版本级治理真相。QA、release、material-audit、status、manifest 等版本治理消费面必须 resolver-first，否则 v1.5.2 切 feature package 唯一真相时仍会从旧版本级路径或 manifest 漂移。

## Scope

v1.5.1 的交付范围是建立 truth-map resolver center、接入本轮新增或改造的真相消费面、补齐 resolver 驱动的 requirement-derived machine JSON 重建与校验路径，并让版本治理消费面具备 resolver-first 的读取和 fail-closed 能力。

v1.5.1 允许追加 `truth_center integration sweep`：把正常真相读取、写入目标解析、gate input 解析、legacy rebuild target、legacy absorb target 等入口统一接到 truth-map resolver / truth_center API。该 sweep 只统一入口和策略中心，不在 v1.5.1 切换真相权威；v1.5.2 只应在 sweep 验证后做 policy flip。

范围内包括 feature package resolver、version governance resolver、truth-map CLI、material-audit、QA runtime、release scorecard、status surface、implement 前置治理校验、truth_center read/write/gate/rebuild/absorb 入口统一、高风险真相入口 inventory、相关 skill 指南、机器面 JSON 角色标签、source hash freshness 校验、测试契约索引和发布前 read-model 材料。

范围外包括 v1.5.2 的唯一真相源一刀切、在 v1.5.1 把 feature package 标记为唯一 authority、旧体系退役、长期兼容主链、把 JSON 定义为 truth authority、以及删除 runtime/process JSON。

## Non-Goals

- 不把 `truth-map.json` 定义为真相。
- 不继续扩大 MD-to-JSON 多写投影。
- 不要求每个 Markdown 真相都同步生成等价 JSON。
- 不在 v1.5.1 完成全量一刀切。
- 不在 v1.5.1 把 `feature_package_authoritative_ready` 提升为 `feature_package_authoritative`。
- 不保留长期旧体系兼容主链。
- 不删除运行/多进程记录 JSON，例如 `.beacon/auto-test-status.json`、`.beacon/qa/status.json` 或 `.jsonl` trace。

## Core Principles

1. 唯一真相源优先是 Markdown feature package。
2. 真相地图是 CLI resolver 和静态 schema，不是可被 LLM 任意编辑的 JSON。
3. JSON 只能是诊断、证据、缓存或重建 metadata，不能成为 authority source。
4. 所有 CLI / skill 消费真相前必须先询问 truth-map resolver。
5. 旧 PRD / user-story / test-case 只允许通过 doctor 重建，或通过 change 吸收，不再作为未来主链目标。
6. requirement-derived machine JSON 必须可从 resolver-selected Markdown 全量再生成，并可用 source hash 校验新鲜度。
7. runtime/process JSON 是运行记录，不要求 Markdown twin，也不能被当成 requirement truth。
8. version governance truth 不塞进 `features/<slug>/`；它保留在版本级材料树，但必须由同一个 resolver 定位、分类和校验。
9. manifest/index/cache 是 generated governance state，不是 resolver 的 authority 输入。
10. `implement plan`、`compile-plan`、`team-plan`、`dev-run` 必须在生成执行计划或进入实现前完成 version governance preflight；project metadata branch contract 与 git workflow projection 冲突时必须 fail closed。
11. v1.5.1 可以把所有正常读写入口统一接到 truth_center，但 truth authority 仍保持 `feature_package_authoritative_ready`；v1.5.2 才能在验证通过后切换 policy。
12. v1.5.1 必须把已知高风险真相读写入口列入 migration inventory；每个入口必须接入 truth_center/resolver，或被明确标记为 legacy/generated/runtime 例外并绑定 fail-closed 或 v1.5.2 cutover 路径。

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
| AC-024 | implement-governance-preflight | `implement plan`、`compile-plan`、`team-plan`、`dev-run` 必须 resolver-first 校验 version governance metadata branch contract；metadata、当前 git branch、git workflow expected branch 不一致时必须在 implement 前 fail closed，并给出 doctor metadata repair route。 |
| AC-025 | truth-center-integration-sweep | v1.5.1 可把正常真相读取、写入目标解析、gate input 解析、legacy rebuild target、legacy absorb target 等入口统一接到 truth_center；但不得在 v1.5.1 切换真相权威，`feature_package_authoritative_ready` 必须保持为准备态，v1.5.2 仅在 sweep 验证后做 policy flip。 |
| AC-026 | truth-center-entrypoint-inventory | v1.5.1 必须维护高风险真相读写入口 inventory，至少覆盖 `beacon/commands/prd.py`、`beacon/commands/user_story.py`、`beacon/commands/test_case.py`、`beacon/commands/workflow.py`、`beacon/commands/truth.py`、`beacon/commands/gate.py`、`beacon/utils/prd_bootstrap.py`、`beacon/utils/requirement_clarity.py`、`beacon/utils/requirement_deepening.py`、`beacon/utils/manifest.py`、`beacon/utils/acceptance_kit.py`、packaged skills、`.agents/skills`；每项必须接入 truth_center/resolver，或明确声明为 v1.5.1 legacy/generated/runtime 例外并给出 fail-closed 或 v1.5.2 cutover 处理路径。 |

## Required Resolver Contract

The resolver center must expose deterministic APIs:

```python
TRUTH_SOURCE_MODEL = "feature_package_authoritative_ready"
TRUTH_PACKAGE_CONTRACT = "beacon-feature-package-v2"
TRUTH_MAP_CONTRACT = "beacon-truth-map-v1"

resolve_truth_map(project_root, version)
resolve_feature_truth(project_root, version, feature)
resolve_truth_surface(project_root, version, feature, surface)
resolve_machine_json_plan(project_root, version, feature)
rebuild_machine_json(project_root, version, feature)
verify_truth_map(project_root, version)
```

The resolver center must also expose or reserve deterministic governance APIs:

```python
resolve_version_governance(project_root, version)
resolve_governance_surface(project_root, version, surface)
verify_governance_truth(project_root, version)
evaluate_implement_version_governance_preflight(project_root, version, feature)
resolve_truth_read_refs(project_root, version, feature, consumer)
resolve_truth_write_target(project_root, version, feature, surface, producer)
resolve_gate_inputs(project_root, version, feature, gate)
resolve_legacy_rebuild_targets(project_root, version, feature)
resolve_legacy_absorb_targets(project_root, version, feature)
resolve_truth_entrypoint_inventory(project_root, version)
verify_truth_entrypoint_inventory(project_root, version)
```

## Truth Center Entrypoint Inventory

v1.5.1 的 truth_center integration sweep 不能只停留在抽象原则。以下高风险入口必须进入 inventory，并由测试逐项验证：

| Entrypoint | Required Classification |
|---|---|
| `beacon/commands/prd.py` | truth read/write command surface |
| `beacon/commands/user_story.py` | truth read/write command surface |
| `beacon/commands/test_case.py` | truth read/write command surface |
| `beacon/commands/workflow.py` | lifecycle/gate routing surface |
| `beacon/commands/truth.py` | direct truth command surface |
| `beacon/commands/gate.py` | gate input consumer |
| `beacon/utils/prd_bootstrap.py` | bootstrap truth writer |
| `beacon/utils/requirement_clarity.py` | requirement truth consumer/gate support |
| `beacon/utils/requirement_deepening.py` | requirement truth support consumer |
| `beacon/utils/manifest.py` | generated index/manifest surface |
| `beacon/utils/acceptance_kit.py` | acceptance/gate input consumer |
| `skills/beacon/**/SKILL.md` | packaged LLM skill read/write guidance |
| `.agents/skills/**/SKILL.md` | installed/project LLM skill read/write guidance |

For each inventory row, one of these outcomes is required:

1. normal truth read/write/gate/rebuild/absorb behavior routes through truth_center or truth-map resolver;
2. the row is explicitly classified as legacy, generated state, or runtime/process record for v1.5.1, and has a fail-closed or v1.5.2 cutover route.

Skill guidance must not present `prd/user-story/test-case` as the future authoritative truth path. If those names remain, they must be framed as current lifecycle surfaces, legacy rebuild/absorb routes, or support material pending v1.5.2 cutover.

## Version Governance Resolver Contract

Version governance truth is not a feature package. It remains version-level material, but every reader must discover it through the truth-map resolver.

| Governance Surface | Canonical Role | Required Resolver Behavior |
|---|---|---|
| `docs/beacon/global-boundaries.md` | global governance truth | resolve as global invariant source. |
| `docs/beacon/<version>/SUMMARY.md` | version governance truth | resolve as version summary source. |
| `docs/beacon/<version>/execution/*.md` | execution governance truth/read model | classify exact surface before use. |
| `docs/beacon/<version>/source-architecture/index.md` | source map governance truth/read model | resolve as source architecture index. |
| `docs/beacon/<version>/release/<version>.md` | release governance truth/read model | resolve as release material. |
| `.beacon/metadata/*.json`, `.beacon/*manifest*.json` | generated governance state/index | validate as generated/index only, never authority. |
| `.beacon/qa/*.json`, `.beacon/release-gate-report.json` | generated governance state | validate labels/source freshness where applicable. |

## Implement Version Governance Preflight

`implement` 是默认执行入口，因此它不能晚于 QA/release 才发现版本治理漂移。v1.5.1 必须在 `implement plan`、`compile-plan`、`team-plan`、`dev-run` 入口前置一个统一 preflight。

Required behavior:

1. 通过 truth-map resolver 解析 version governance surface，而不是直接拼接 metadata 或 git-workflow 路径。
2. 运行等价于 `doctor metadata verify` 的 branch contract 校验。
3. 对比 project metadata selected branch、当前 git branch、git workflow expected branch。
4. 如果 metadata branch contract 与 git workflow projection 冲突，以 version governance resolver 输出为准，并 fail closed。
5. 输出明确 reason code 和修复命令，例如 `beacon doctor metadata verify` / `beacon doctor metadata update`。

Required reason codes:

- `implement_metadata_contract_blocked`
- `implement_metadata_branch_mismatch`
- `implement_git_workflow_metadata_drift`
- `implement_version_governance_missing`
- `implement_version_governance_generated_state_stale`

## Authority Model

| Artifact | v1.5.1 Role | Truth Authority |
|---|---|---|
| CLI resolver constants/functions | resolver authority | yes |
| `features/<slug>/*.md` | canonical-ready source | future yes |
| `truth-map.md` | human read model | no |
| `truth-map.json` | diagnostic/cache projection | no |
| `.machine/*.json` | generated state / evidence / rebuild metadata | no |
| version governance Markdown | version governance truth/read model | yes for its governance surface |
| manifest/material-audit/QA/release JSON | generated governance state/index | no |
| `.beacon/*.json`, `.jsonl` | runtime/process record | no |
| `prd/`, `user-story/`, `qa/test-cases/` | legacy rebuild/absorb targets | no future authority |

## Machine JSON Convergence Plan

v1.5.1 的机器面 JSON 收敛必须覆盖以下类别：

| Class | Examples | Required v1.5.1 Behavior |
|---|---|---|
| requirement state | `.machine/requirement/<slug>.freeze-state.json`, `feature-package-validation.json` | 从 resolver-selected Markdown 重建，记录 source hash。 |
| user-story state | `.machine/user-story/<slug>.json` | 从 resolver-selected truth 重建，不直接硬编码旧 `user-story/` 路径。 |
| QA matrices | `.machine/qa/<slug>.ac-test-matrix.json`, `.qa9-matrix.json`, `.story-scenario-map.json` | 从 resolver-selected `tests.md` 或映射后的 legacy test source 重建。 |
| test contract index | `.machine/testing/test-contract-index.json` | QA matrices 重建后刷新，验证 source hash 新鲜度。 |
| requirement clarity | `.machine/execution/requirement-clarity-<slug>.json` | 从 resolver-selected truth 生成诊断/gate input。 |
| change/refreeze transactions | `.machine/change/*.json` | 保留为 transaction evidence，写入前通过 resolver 确认 truth source。 |
| runtime/process records | `.beacon/*.json`, `.jsonl` | 保留为运行记录，不要求 Markdown twin。 |

Required CLI shape:

```bash
beacon truth-map rebuild-machine "<feature>" --project . --version v1.5.1 --json
beacon truth-map verify "<feature>" --project . --version v1.5.1 --strict --json
```

## Cutover Promise

v1.5.1 must prepare v1.5.2 to remove the old production/consumption chain as the normal path. Compatibility is not the goal. Rebuild and absorption are the only allowed old-surface uses.
