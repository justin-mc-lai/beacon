# Beacon Brainstorm

## prompt_summary
结合 ui-ux-pro-max-skill、impeccable、awesome-design-md 三个设计 skill 的思路，分析 Beacon prototype 与 implement 如何拥有根据 requirement truth（PRD/user-story/test-case/prototype freeze）进行设计渲染的能力，而不是把设计指导规范本身直接渲染到 UI。请从 requirement-convergence + project-evolution 角度输出：1) 设计 skill 在 Beacon 中应处于什么层；2) prototype 子 skill 应生成哪些中间设计工件；3) implement 应消费哪些设计工件；4) 哪些属于 internal design governance，哪些属于 production-visible UI；5) 最小演进蓝图。

- version: `v1.3.11`
- mode: `project-evolution`
- feature: ``

## version_material_refs
- `docs/beacon/global-boundaries.md` (present, required)
- `docs/beacon/v1.3.11/SUMMARY.md` (present, optional)
- `docs/beacon/v1.3.11/execution/index.md` (present, optional)
- `docs/beacon/v1.3.11/execution/architecture-blueprint.md` (present, optional)
- `docs/beacon/v1.3.11/prd/beacon-execution-runtime-kernel.md` (present, optional)
- `docs/beacon/v1.3.11/prd/beacon-operator-workbench-and-board-launcher.md` (present, optional)
- `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md` (present, optional)
- `docs/beacon/v1.3.11/prd/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md` (present, optional)
- `docs/beacon/v1.3.11/user-story/beacon-execution-runtime-kernel.md` (present, optional)
- `docs/beacon/v1.3.11/user-story/beacon-operator-workbench-and-board-launcher.md` (present, optional)
- `docs/beacon/v1.3.11/user-story/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md` (present, optional)
- `docs/beacon/v1.3.11/user-story/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md` (present, optional)
- `docs/beacon/v1.3.11/qa/test-cases/beacon-execution-runtime-kernel.md` (present, optional)
- `docs/beacon/v1.3.11/qa/test-cases/beacon-operator-workbench-and-board-launcher.md` (present, optional)
- `docs/beacon/v1.3.11/qa/test-cases/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md` (present, optional)
- `docs/beacon/v1.3.11/qa/test-cases/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md` (present, optional)
- `docs/beacon/v1.3.11/qa/test-cases/index.md` (present, optional)

## confirmed_facts
- Beacon version material root is docs/beacon/v1.3.11.
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
Treat this as an evolution candidate. Capture options in brainstorm output first, then route accepted scope through beacon-prd or beacon-change.

## next_route
beacon-prd or beacon-change
