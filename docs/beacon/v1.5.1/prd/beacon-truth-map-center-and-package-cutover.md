# PRD: Beacon Truth Map Center and Package Cutover

- version: `v1.5.1`
- feature: `beacon-truth-map-center-and-package-cutover`
- status: `frozen`
- language: `zh`

## Problem

Beacon v1.5.0 已经上线 `features/<slug>/{truth,tests,tasks,evidence}.md`，但它仍是并行 read model。当前源码中大量命令、工具和 skill 仍直接拼接旧路径，例如 `prd/`、`user-story/`、`qa/test-cases/`、`.machine/`。

如果直接把 feature package 改成唯一真相，会出现局部读新源、局部读旧源的漂移。

## Goal

v1.5.1 建立 truth-map resolver center，让 Beacon 所有真相读取入口逐步收敛到一个确定性 resolver。该 resolver 是 CLI 函数和静态 schema contract，不是 JSON 文件。

## Non-Goals

- 不把 `truth-map.json` 定义为真相。
- 不继续扩大 MD-to-JSON 多写投影。
- 不要求每个 Markdown 真相都同步生成等价 JSON。
- 不在 v1.5.1 完成全量一刀切。
- 不保留长期旧体系兼容主链。

## Core Principles

1. 唯一真相源优先是 Markdown feature package。
2. 真相地图是 CLI resolver 和静态 schema，不是可被 LLM 任意编辑的 JSON。
3. JSON 只能是诊断、证据、缓存或重建 metadata，不能成为 authority source。
4. 所有 CLI / skill 消费真相前必须先询问 truth-map resolver。
5. 旧 PRD / user-story / test-case 只允许通过 doctor 重建，或通过 change 吸收，不再作为未来主链目标。

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

## Required Resolver Contract

The resolver center must expose deterministic APIs:

```python
TRUTH_SOURCE_MODEL = "feature_package_authoritative_ready"
TRUTH_PACKAGE_CONTRACT = "beacon-feature-package-v2"
TRUTH_MAP_CONTRACT = "beacon-truth-map-v1"

resolve_truth_map(project_root, version)
resolve_feature_truth(project_root, version, feature)
resolve_truth_surface(project_root, version, feature, surface)
verify_truth_map(project_root, version)
```

## Authority Model

| Artifact | v1.5.1 Role | Truth Authority |
|---|---|---|
| CLI resolver constants/functions | resolver authority | yes |
| `features/<slug>/*.md` | canonical-ready source | future yes |
| `truth-map.md` | human read model | no |
| `truth-map.json` | diagnostic/cache projection | no |
| `.machine/*.json` | projection/evidence/rebuild metadata | no |
| `prd/`, `user-story/`, `qa/test-cases/` | legacy rebuild/absorb targets | no future authority |

## Cutover Promise

v1.5.1 must prepare v1.5.2 to remove the old production/consumption chain as the normal path. Compatibility is not the goal. Rebuild and absorption are the only allowed old-surface uses.

