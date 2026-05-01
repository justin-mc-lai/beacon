# Beacon Brainstorm

## prompt_summary
深度分析 Beacon prototype 子skill 当前能力边界与重构需求。要求：1）识别当前 prototype 命令、rule compile、canonical envelope、review/gate、asset projection、default preset、LLM fallback、design governance 的真实能力；2）指出哪些是结构性能力，哪些仍是占位或 generic；3）分析为什么这意味着需要完整重构 prototype，而不是局部修补；4）补充一个二开项目视角：prototype 应如何支持 takeover/current-state 项目的原型梳理、UI/UX 盘点、页面意图抽取、状态与路由梳理、design-md 资产冻结。不要改写任何 frozen docs。

- version: `v1.3.10`
- mode: `implementation-readiness`
- feature: ``

## version_material_refs
- `docs/beacon/global-boundaries.md` (present, required)
- `docs/beacon/v1.3.10/SUMMARY.md` (present, optional)
- `docs/beacon/v1.3.10/execution/index.md` (present, optional)
- `docs/beacon/v1.3.10/execution/architecture-blueprint.md` (present, optional)
- `docs/beacon/v1.3.10/prd/beacon-v1-3-10-prototype-ux-prd-closure-and-design-asset-projection.md` (present, optional)
- `docs/beacon/v1.3.10/prd/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md` (present, optional)
- `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md` (present, optional)
- `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md` (present, optional)
- `docs/beacon/v1.3.10/qa/test-cases/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md` (present, optional)
- `docs/beacon/v1.3.10/qa/test-cases/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md` (present, optional)
- `docs/beacon/v1.3.10/qa/test-cases/index.md` (present, optional)

## confirmed_facts
- Beacon version material root is docs/beacon/v1.3.10.
- This sidecar is read-only against Beacon requirement truth.
- Frozen PRD, user-story, test-case, prototype, and .machine artifacts are not rewritten by brainstorm.
- Resolved project topology: single_repo.
- Resolved execution service: beacon.
- Resolved canonical branch: main.

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
- - 它位于 `test-case` 与 `implement` 之间
- ### 4. `implement` 与 `qa` 仍是唯一执行入口
- - `implement` 仍是唯一实现入口
- - verifier / repair-handoff-writer / implementation-architect 等内部角色协作
- ### 6. 预检查必须内嵌到 `implement` / `qa`
- - `implement`
- - `implement / qa / release` 只能沿这条链闭环，不得反向改写 requirement truth

## project_metadata
- metadata_ref: `.beacon/metadata/project-version-metadata.json`
- topology_kind: `single_repo`
- selected_service: `beacon`
- selected_branch: `main`

## converged_recommendation
Use this only as a pre-implementation reasoning check. If frozen PRD/user-story/test-case drift is found, stop and route through beacon-change before implement.

## next_route
beacon-implement after drift is resolved
