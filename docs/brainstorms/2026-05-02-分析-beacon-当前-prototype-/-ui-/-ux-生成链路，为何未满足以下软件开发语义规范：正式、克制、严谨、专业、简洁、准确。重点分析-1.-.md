# Beacon Brainstorm

## prompt_summary
分析 Beacon 当前 prototype / ui / ux 生成链路，为何未满足以下软件开发语义规范：正式、克制、严谨、专业、简洁、准确。重点分析 1. 当前生成链路哪些环节会引入主观词、模糊词、口语化、愿景化描述 2. PRD/UX PRD/preview 文案/看板投影分别缺哪些语义约束层 3. 需要抽象哪些统一语义 contract、术语字典、禁用词、句式模板、字段约束模板、状态枚举模板，才能让 Beacon 生成的软件文档与 UI 文案符合企业级软件开发规范 4. 输出应给出问题分层、根因、缺失模块、最小改造闭环，禁止改写现有 requirement truth

- version: `v1.3.11`
- mode: `requirement-convergence`
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
Converge missing or ambiguous requirement points into explicit questions and candidate decisions before editing frozen truth.

## next_route
beacon-prd, beacon-user-story, beacon-test-case, or beacon-change
