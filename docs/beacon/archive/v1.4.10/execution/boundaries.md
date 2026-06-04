# Execution Boundaries (v1.4.10)

## 核心规则

`v1.4.10` 是 QA evo-deep 与 Skill Eval Kit P0 契约冻结线，不是 runtime release 线。

Beacon 主链仍保持：

```text
prd -> user-story -> test-case -> implement -> qa -> release
```

`change/refreeze` 只负责重新闭合 requirement truth；不得自动执行 implement、QA 或 release。

## P0 Boundary

本版本 P0 只冻结：

- `qa-evo-deep-state-scenario-round-memory-contract`
- `better-harness-skill-eval-kit-regression-core`

P0 不包括：

- Ralph Task Loop controller。
- project lifecycle hooks runtime。
- automatic `beacon learn` context-to-project-skill injection。
- splitting `beacon-implement` into multiple public skills。

## QA Evo Deep Boundary

`qa-evo-deep` 只能产出 routeable findings：

- truth drift -> `beacon change/refreeze`
- implementation gap -> `beacon implement repair`
- QA evidence gap -> `beacon qa supplement`
- release supplement -> release readiness input

它不得替代 `beacon qa run`，不得给 release pass verdict，不能改 PRD、user-story、test-case 或 freeze state。

## Skill Eval Kit Boundary

Skill Eval Kit 只治理 skill/harness quality：

- route stability
- boundary preservation
- source anchor sufficiency
- actionability
- material effect closure
- clarification quality
- token efficiency

Eval runs、traces、metrics、scorecards 是 runtime evidence，不是 requirement truth。Regression core failure 可以阻断 skill/harness release readiness，但不能自动改需求。

## Delivery Boundary

Implementation may plan only after the frozen requirement package is readable and material gates pass.

QA and release remain blocked until:

- runtime implementation exists
- executable tests for AC-001 through AC-009 exist
- QA evo-deep topology and authority boundaries are verified
- Skill Eval Kit schema, splits, regression core, and evidence boundaries are verified
- QA evidence is recorded
- release checklist is updated with actual verification results
