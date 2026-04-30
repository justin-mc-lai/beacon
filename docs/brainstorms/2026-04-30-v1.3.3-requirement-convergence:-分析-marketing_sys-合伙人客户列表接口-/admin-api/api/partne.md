# Beacon Brainstorm

## prompt_summary
v1.3.3 requirement-convergence: 分析 marketing_sys 合伙人客户列表接口 /admin-api/api/partner/customers 中手机号展示原因。已知 UAT 返回样例中 customer A: relation_type=INDIRECT, sale_type=PASSIVE_SALE, customer_state=PROTECTED, consume_amount_fen=0, phone_visibility=not_revealable；customer B: relation_type=DIRECT, sale_type=ACTIVE_SALE, customer_state=PROTECTED, consume_amount_fen=0, phone_visibility=revealable, can_view_full_phone=true, tags含已阅读报告。请基于 docs/beacon/v1.3.3 冻结真相收敛：1) 当前 revealable 的必要条件；2) 为什么 B 在未消费且90天内仍可展示完整手机号；3) 这是否与 v1.3.3 冻结口径一致；4) 是否存在文档/实现不一致风险。只读分析，不改文档不改代码。

- version: `v1.3.3`
- mode: `requirement-convergence`
- feature: ``

## version_material_refs
- `docs/beacon/global-boundaries.md` (present, required)
- `docs/beacon/v1.3.3/SUMMARY.md` (present, optional)
- `docs/beacon/v1.3.3/execution/index.md` (present, optional)
- `docs/beacon/v1.3.3/execution/architecture-blueprint.md` (present, optional)
- `docs/beacon/v1.3.3/prd/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md` (present, optional)
- `docs/beacon/v1.3.3/prd/beacon-v1.3.3-memory-friction-evolution-toolkit.md` (present, optional)
- `docs/beacon/v1.3.3/prd/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.md` (present, optional)
- `docs/beacon/v1.3.3/user-story/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md` (present, optional)
- `docs/beacon/v1.3.3/user-story/beacon-v1.3.3-memory-friction-evolution-toolkit.md` (present, optional)
- `docs/beacon/v1.3.3/user-story/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.md` (present, optional)
- `docs/beacon/v1.3.3/qa/test-cases/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md` (present, optional)
- `docs/beacon/v1.3.3/qa/test-cases/beacon-v1.3.3-memory-friction-evolution-toolkit.md` (present, optional)
- `docs/beacon/v1.3.3/qa/test-cases/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.md` (present, optional)
- `docs/beacon/v1.3.3/qa/test-cases/index.md` (present, optional)

## confirmed_facts
- Beacon version material root is docs/beacon/v1.3.3.
- This sidecar is read-only against Beacon requirement truth.
- Frozen PRD, user-story, test-case, prototype, and .machine artifacts are not rewritten by brainstorm.
- Resolved project topology: single_repo.
- Resolved execution service: beacon.

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
- selected_branch: ``

## converged_recommendation
Converge missing or ambiguous requirement points into explicit questions and candidate decisions before editing frozen truth.

## next_route
beacon-prd, beacon-user-story, beacon-test-case, or beacon-change
