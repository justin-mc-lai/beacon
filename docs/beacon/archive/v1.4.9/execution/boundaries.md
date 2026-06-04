# Execution Boundaries (v1.4.9)

## 核心规则

`v1.4.9` 是 UI/UX execution 外部化、Prototype adapter 化、版本级需求可视化契约的需求冻结线，不是 runtime release 线。

Beacon 主链仍保持：

`prd -> user-story -> test-case -> implement -> qa -> release`

`change/refreeze` 只负责重新闭合 requirement truth；不得自动执行 implement、QA 或 release。

## UI/UX Execution Boundary

本版本冻结以下边界：

- UI/UX exploration、system recommendation、review、polish、extract、library lookup 由 `ui-ux-dev` 承担。
- Beacon 不再把内部 `prototype` 作为 v1.4.9+ 设计生成面扩张。
- `prototype` 在 v1.4.9+ 只承担 accepted design result 的 requirement-facing adapter。
- `beacon-design-review` 只承担 route / governance support，不替代 `ui-ux-dev review`。
- `ui-ux-dev` 不拥有 Beacon lifecycle、gate verdict、PRD、user-story 或 test-case truth。

## Adapter Boundary

Accepted design result 进入 Beacon 后，必须显性绑定：

- screen intent
- page / flow outline
- state visibility contract
- interaction handoff
- PRD promise mapping
- user-story acceptance mapping
- test-case coverage mapping
- truth binding diagnostics

缺失 binding 时，implement 必须 fail closed。

## Version Visualization Boundary

版本级可视化只允许作为人类可读 projection：

- business flow projection 只讲业务闭环，不讲实现细节。
- state-machine projection 只讲 stable closure states，不讲页面 widget 交互细节。
- PRD / user-story / test-case map 只讲 truth ownership 和 traceability，不新增需求。

每张 freeze-facing projection 必须声明 truth bindings；没有 bindings 的图只能是说明图，不能作为冻结材料。

## Delivery Boundary

Implementation may plan only after the frozen requirement package is readable and gates pass.

QA and release remain blocked until:

- runtime implementation exists
- executable tests for AC-001 through AC-012 exist
- accepted design result adapter bindings are verified where applicable
- visualization truth bindings are verified where declared required
- QA evidence is recorded
- release checklist is updated with actual verification results

