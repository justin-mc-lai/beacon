# Beacon Revision Delta

- feature: `beacon-v2-rust-kernel-redesign`
- version: `v2.0.0`
- revision_id: `R7`
- source_revision_id: `R6`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `1`
- added_requirement_count: `7`

## Removed Requirement Surfaces
- `AC-020` 六能力 surface + legacy removal

## Added Requirement Surfaces
- `AC-020` 六能力 surface + legacy removal + progressive disclosure + BranchContext
- `AC-122` **：`BranchContext.v1` 是所有写入/agent/evidence/release harness 的共同输入，字段至少覆盖 caller cwd、target project root、admitted worktree、base/feature/canonical branch、dirty policy、protected paths 与 admission artifact。
- `AC-123` **：branch/workspace governance 是 hard gate；任何 generator/implement/qa-evidence/release 写路径缺失 admission 或 BranchContext mismatch 时必须 fail-closed，不能降级为 warning。
- `AC-124` **：Harness boundary 以 reason_code enforce：planner/truth 不实现，implement 不改 frozen truth/不自评 QA，qa-evidence 不改 truth/implementation，release 不绕过 human gate，loop 不替代任一裁决面。
- `AC-120` **：skill loader 必须采用 progressive disclosure；默认只加载 public `SKILL.md`，按 intent/topic 选择性加载 `references/` 与 `examples/`，并产出 `skill_load_plan.v1`。
- `AC-121` **：六个 public skill 都必须提供 route examples；示例覆盖 `truth review -> decision_packet -> loop`、`design_primitives -> implement`、`qa-evidence -> release`、`branch blocked -> repair_route`，且示例不是 requirement authority。
- `AC-029` R6 refreeze：六 public skill 渐进式披露 contract；内部保留 branch governance / doctor / router / hooks / metadata / status / archive / debug；新增 BranchContext.v1 与 Harness Boundary hard gate（AC-125–130）
