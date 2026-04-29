# Beacon Brainstorm

## prompt_summary
基于 beacon friction-intake 最新 scan 结果，对以下摩擦集合做 project-evolution 分析：1) prd-create-generic-template-only；2) prd-implement-delivery-drift-gate-missing；3) prototype-reference-pack-visual-quality-drift；4) missing-memory-friction-subskill；5) pocketbase-control-plane-admin-surface-missing；6) runtime_feedback。约束：只读分析，不改写 docs。目标：a) 判断这些摩擦是否属于同一根因簇；b) 判断哪些应继续留在 friction queue，哪些应升级为 beacon-change requirement delta；c) 如果重新 scan 没有出现用户口中的“新增摩擦”，分析可能原因，是 scan source 不足、分类规则不足、还是该摩擦需要 capture 模式手工录入；d) 给出最小收敛路径，优先保证 v1.3.9 当前发布线不被历史拖尾问题污染。输出要求：first principles、evidence、closure constraints、recommended routing。

- version: `v1.3.9`
- mode: `project-evolution`
- feature: ``

## version_material_refs
- `docs/beacon/global-boundaries.md` (present, required)
- `docs/beacon/v1.3.9/SUMMARY.md` (present, optional)
- `docs/beacon/v1.3.9/execution/index.md` (present, optional)
- `docs/beacon/v1.3.9/execution/architecture-blueprint.md` (present, optional)
- `docs/beacon/v1.3.9/prd/beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md` (present, optional)
- `docs/beacon/v1.3.9/prd/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md` (present, optional)
- `docs/beacon/v1.3.9/prd/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md` (present, optional)
- `docs/beacon/v1.3.9/prd/beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility.md` (present, optional)
- `docs/beacon/v1.3.9/user-story/beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md` (present, optional)
- `docs/beacon/v1.3.9/user-story/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md` (present, optional)
- `docs/beacon/v1.3.9/user-story/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md` (present, optional)
- `docs/beacon/v1.3.9/user-story/beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility.md` (present, optional)
- `docs/beacon/v1.3.9/qa/test-cases/beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md` (present, optional)
- `docs/beacon/v1.3.9/qa/test-cases/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md` (present, optional)
- `docs/beacon/v1.3.9/qa/test-cases/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md` (present, optional)
- `docs/beacon/v1.3.9/qa/test-cases/beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility.md` (present, optional)
- `docs/beacon/v1.3.9/qa/test-cases/index.md` (present, optional)

## confirmed_facts
- Beacon version material root is docs/beacon/v1.3.9.
- This sidecar is read-only against Beacon requirement truth.
- Frozen PRD, user-story, test-case, prototype, and .machine artifacts are not rewritten by brainstorm.

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

## converged_recommendation
Treat this as an evolution candidate. Capture options in brainstorm output first, then route accepted scope through beacon-prd or beacon-change.

## next_route
beacon-prd or beacon-change
