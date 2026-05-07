# Beacon Brainstorm

## prompt_summary
合并 Beacon core-kernel-spec 与 capability-gap-map，形成 Beacon v2 lightweight kernel architecture，包含 minimal machine contract schema、核心命令与插件命令边界、重构迁移阶段图。目标是在不丢 truth freeze、gate、implement/qa、host-LLM、learning、meta、memory、archive/support 的前提下做减重。

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
