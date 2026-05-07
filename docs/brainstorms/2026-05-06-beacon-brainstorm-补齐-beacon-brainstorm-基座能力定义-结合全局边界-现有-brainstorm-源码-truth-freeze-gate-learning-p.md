# Beacon Brainstorm

## prompt_summary
补齐 Beacon Brainstorm 基座能力定义：结合全局边界、现有 brainstorm 源码、truth freeze、gate、learning plane、host-LLM 语义能力，给出第一性原理驱动的高置信度收敛方案。重点回答：1. Brainstorm 是否应成为 core kernel 的正式一部分；2. 它与 PRD/change/freeze 的关系；3. 它如何避免发散成新真相源；4. 它如何成为跨 code/media/copy/novel 场景的统一收敛前置层。

- version: `v1.3.12`
- mode: `project-evolution`
- canonical_mode: `project-evolution`
- feature: ``

## version_material_refs
- `docs/beacon/global-boundaries.md` (present, required)
- `docs/beacon/v1.3.12/SUMMARY.md` (present, optional)
- `docs/beacon/v1.3.12/execution/index.md` (present, optional)
- `docs/beacon/v1.3.12/execution/architecture-blueprint.md` (present, optional)
- `docs/beacon/v1.3.12/prd/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md` (present, optional)
- `docs/beacon/v1.3.12/user-story/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md` (present, optional)
- `docs/beacon/v1.3.12/qa/test-cases/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md` (present, optional)
- `docs/beacon/v1.3.12/qa/test-cases/index.md` (present, optional)

## confirmed_facts
- Beacon version material root is docs/beacon/v1.3.12.
- This sidecar is read-only against Beacon requirement truth.
- Frozen PRD, user-story, test-case, prototype, and .machine artifacts are not rewritten by brainstorm.
- Resolved project topology: single_repo.
- Resolved execution service: beacon.
- Resolved canonical branch: beacon/v1.3.11.

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
- selected_branch: `beacon/v1.3.11`

## converged_recommendation
Treat this as an evolution candidate. Capture options in brainstorm output first, then route accepted scope through beacon-prd or beacon-change.

## next_route
brainstorm closed
