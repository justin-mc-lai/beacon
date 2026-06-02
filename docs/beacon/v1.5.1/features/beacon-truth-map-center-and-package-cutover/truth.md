---
slug: beacon-truth-map-center-and-package-cutover
version: v1.5.1
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/v1.5.1/prd/beacon-truth-map-center-and-package-cutover.md
  user_story: docs/beacon/v1.5.1/user-story/beacon-truth-map-center-and-package-cutover.md
  test_case: docs/beacon/v1.5.1/qa/test-cases/beacon-truth-map-center-and-package-cutover.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative_ready
truth_map_contract: beacon-truth-map-v1
---

# Feature Truth: Beacon Truth Map Center and Package Cutover

## Summary

v1.5.1 建立 truth-map resolver center。真相地图是 CLI resolver/static contract，不是 JSON truth。JSON/MD truth-map 输出只是 projection、diagnostic 或 evidence。

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

## Authority

The authority source is Markdown feature package plus CLI resolver contract. JSON twins are not required for truth validity.

