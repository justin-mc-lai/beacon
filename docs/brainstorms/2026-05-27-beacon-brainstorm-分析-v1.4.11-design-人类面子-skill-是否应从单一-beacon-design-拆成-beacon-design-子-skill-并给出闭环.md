# Beacon Brainstorm

## prompt_summary
分析 v1.4.11 design 人类面子 skill 是否应从单一 beacon-design 拆成 beacon-design-* 子 skill，并给出闭环子 skill 结构

- version: `v1.4.11`
- mode: `requirement-convergence`
- canonical_mode: `requirement-convergence`
- feature: ``

## version_material_refs
- `docs/beacon/global-boundaries.md` (present, required)
- `docs/beacon/v1.4.11/SUMMARY.md` (present, optional)
- `docs/beacon/v1.4.11/execution/index.md` (present, optional)
- `docs/beacon/v1.4.11/execution/architecture-blueprint.md` (present, optional)
- `docs/beacon/v1.4.11/prd/authority-vocabulary-and-baseline-inventory-contract.md` (present, optional)
- `docs/beacon/v1.4.11/prd/beacon-design-product-prototype-rebuild-contract.md` (present, optional)
- `docs/beacon/v1.4.11/prd/browser-fallback-deterministic-command-contract.md` (present, optional)
- `docs/beacon/v1.4.11/prd/compatibility-registry-and-command-catalog-contract.md` (present, optional)
- `docs/beacon/v1.4.11/prd/implement-package-legacy-loader-retirement-contract.md` (present, optional)
- `docs/beacon/v1.4.11/prd/memory-intent-historical-migration-boundary-contract.md` (present, optional)
- `docs/beacon/v1.4.11/prd/qa-prd-legacy-mirror-retirement-contract.md` (present, optional)
- `docs/beacon/v1.4.11/prd/test-directory-marker-relayering-contract.md` (present, optional)
- `docs/beacon/v1.4.11/user-story/authority-vocabulary-and-baseline-inventory-contract.md` (present, optional)
- `docs/beacon/v1.4.11/user-story/beacon-design-product-prototype-rebuild-contract.md` (present, optional)
- `docs/beacon/v1.4.11/user-story/browser-fallback-deterministic-command-contract.md` (present, optional)
- `docs/beacon/v1.4.11/user-story/compatibility-registry-and-command-catalog-contract.md` (present, optional)
- `docs/beacon/v1.4.11/user-story/implement-package-legacy-loader-retirement-contract.md` (present, optional)
- `docs/beacon/v1.4.11/user-story/memory-intent-historical-migration-boundary-contract.md` (present, optional)
- `docs/beacon/v1.4.11/user-story/qa-prd-legacy-mirror-retirement-contract.md` (present, optional)
- `docs/beacon/v1.4.11/user-story/test-directory-marker-relayering-contract.md` (present, optional)
- `docs/beacon/v1.4.11/qa/test-cases/authority-vocabulary-and-baseline-inventory-contract.md` (present, optional)
- `docs/beacon/v1.4.11/qa/test-cases/beacon-design-product-prototype-rebuild-contract.md` (present, optional)
- `docs/beacon/v1.4.11/qa/test-cases/browser-fallback-deterministic-command-contract.md` (present, optional)
- `docs/beacon/v1.4.11/qa/test-cases/compatibility-registry-and-command-catalog-contract.md` (present, optional)
- `docs/beacon/v1.4.11/qa/test-cases/implement-package-legacy-loader-retirement-contract.md` (present, optional)
- `docs/beacon/v1.4.11/qa/test-cases/index.md` (present, optional)
- `docs/beacon/v1.4.11/qa/test-cases/memory-intent-historical-migration-boundary-contract.md` (present, optional)
- `docs/beacon/v1.4.11/qa/test-cases/qa-prd-legacy-mirror-retirement-contract.md` (present, optional)
- `docs/beacon/v1.4.11/qa/test-cases/test-directory-marker-relayering-contract.md` (present, optional)

## confirmed_facts
- Beacon version material root is docs/beacon/v1.4.11.
- This sidecar is read-only against Beacon requirement truth.
- Frozen PRD, user-story, test-case, prototype, and .machine artifacts are not rewritten by brainstorm.
- Resolved project topology: single_repo.
- Resolved execution service: beacon.
- Resolved canonical branch: beacon/v1.4.10.

## assumptions_under_test
- The prompt may represent a requirement gap, an evolution idea, or implementation-risk question until mapped to frozen evidence.
- Any accepted requirement change must be routed through the Beacon requirement/change loop before implementation.

## first_principles_breakdown
- 用户价值: identify the irreducible user outcome before proposing mechanism.
- 证据约束: every implementation idea must trace back to frozen PRD/user-story/test-case evidence.
- 闭环约束: if evidence is missing or changing, return to requirement/change routing instead of implementing.

## socratic_questions
- What exact user outcome would fail if this idea is not implemented?
- Which frozen acceptance criterion proves this idea is required?
- What evidence would falsify this proposed direction?
- If this is an evolution, what is the smallest safe requirement delta?

## redundancy_cuts
- Remove implementation mechanisms that cannot be tied to frozen acceptance evidence.
- Remove duplicate document-to-document reconciliation; use canonical Beacon truth or route a change.
- Remove broad roadmap speculation unless it produces a concrete next Beacon route.

## material_signals
- → implement
- - `prototype` 只可作为条件触发层插入 `test-case` 与 `implement` 之间，不得被默认抬升为所有 feature 的常驻主段。
- - `ceo-review`、`brainstorm`、`design-review`、`deep`、`help`、`status`、`doctor`、`archive` 等都属于 support surface，不是新的 lifecycle stage。
- - `implement / qa / release` 只能沿这条链闭环，不得反向改写 requirement truth。
- - `implement` 仍是唯一默认执行入口。
- - `ceo-review`、`brainstorm`、`design-review`、`deep` 这类 guidance/support surface 必须优先贯彻这套哲学。
- - 当前版本聚合范围：8 个 frozen requirement package 均已完成 implementation / QA acceptance，版本 change 聚合材料已对齐到 8 个 feature，release check 已通过；当前尚未执行 release 发布或 post-release install。
- - `docs/beacon/v1.4.11/research/authority-vocabulary-and-baseline-inventory-contract.md`

## human_closure_scaffold
- enabled: `False`
- research_path: ``
- source_architecture_path: ``

## human_closure_created
- none

## human_closure_existing
- none

## project_metadata
- metadata_ref: `.beacon/metadata/project-version-metadata.json`
- topology_kind: `single_repo`
- selected_service: `beacon`
- selected_branch: `beacon/v1.4.10`

## converged_recommendation
Converge missing or ambiguous requirement points into explicit questions and candidate decisions before editing frozen truth.

## next_route
brainstorm closed
