---
name: beacon
description: Beacon v1.6.0 host-level router for harness-first planner/generator/evaluator/governor skills.
metadata:
  author: Beacon CLI
  version: "v1.6.0"
  organization: Beacon
  date: June 2026
  abstract: Harness-first Beacon meta-protocol. Route coarse user intent into planner, generator, evaluator, or governor skills without preserving old host-visible aliases.
---

# Beacon Skill

This package is the canonical `skills/beacon/` host-visible Beacon skill package for Codex and Claude.

v1.6.0 is a breaking skill-surface migration. Host-visible child skills use only:

- `beacon-planner-*`
- `beacon-generator-*`
- `beacon-evaluator-*`
- `beacon-governor-*`

Old host-visible aliases such as `using-beacon`, `beacon-prd`, `beacon-user-story`, `beacon-test-case`, `beacon-implement`, `beacon-qa`, `beacon-release`, and `beacon-brainstorm` are intentionally not present in this package. If CLI compatibility is needed, it belongs in CLI routing or migration tooling, not duplicate host-visible skill directories.

## Meta-Protocol

Always start with one routing question:

> 当前请求应该由哪个 harness 负责：planner、generator、evaluator，还是 governor？

Route by authority boundary, not by old stage names or tool familiarity.

## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

## Harness Routing

- `planner`: 拆分粗提示词，判断湖/海规模，读取 truth/source/evidence，并产出 research/planning artifact 或 route recommendation。
- `generator`: 在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth、implementation、prototype、design 或 delivery artifact。
- `evaluator`: 验证 evidence，识别 truth drift、fake delivery、missing coverage、placeholder evidence，并产出 verdict/finding/route/block。
- `governor`: 维护 context、archive、memory、hooks、automation、metadata、status 和 diagnostic support。

## Host-Visible Skills

Planner:

- `beacon-planner-brainstorm`
- `beacon-planner-deep-analysis`
- `beacon-planner-friction-intake`
- `beacon-planner-founder-review`
- `beacon-planner-design-review`
- `beacon-planner-security-review`
- `beacon-planner-performance-review`
- `beacon-planner-doubt-review`
- `beacon-planner-source-driven`
- `beacon-planner-context-engineering`
- `beacon-planner-design-simplify`
- `beacon-planner-documentation-adr`

Planner tools may still route to stable CLI commands. For example, `beacon-planner-friction-intake` can recommend `beacon friction-intake run ...` while remaining a planner support surface.

Generator:

- `beacon-generator-truth-package`
- `beacon-generator-truth-bootstrap`
- `beacon-generator-truth-change`
- `beacon-generator-truth-refreeze`
- `beacon-generator-prototype-binding`
- `beacon-generator-implementation`
- `beacon-generator-design-support`
- `beacon-generator-design-bootstrap`
- `beacon-generator-design-explore`
- `beacon-generator-design-system`
- `beacon-generator-design-polish`

Evaluator:

- `beacon-evaluator-qa`
- `beacon-evaluator-qa-deep`
- `beacon-evaluator-release`
- `beacon-evaluator-real-project`

Governor:

- `beacon-governor-design-library`
- `beacon-governor-design-extract`
- `beacon-governor-doctor`
- `beacon-governor-debug-recovery`
- `beacon-governor-status`
- `beacon-governor-help`
- `beacon-governor-archive`
- `beacon-governor-learn`
- `beacon-governor-hooks`
- `beacon-governor-automation`
- `beacon-governor-branch`
- `beacon-governor-lighthouse`
- `beacon-governor-metadata`
- `beacon-governor-router`

## Lifecycle

The user-visible v1.6.0 lifecycle is:

```text
plan -> truth -> generate -> evaluate -> release
```

Requirement authority still resolves through:

```text
beacon truth-map resolve <feature> --project . --version <version> --json
docs/beacon/<version>/features/<slug>/{truth,tests,tasks,evidence}.md
```

`prd`, `user-story`, and `test-case` are legacy concepts. They may appear in migration docs or archives, but they are not v1.6.0 host-visible skill categories.

## Research Contract

Planner research lives at:

```text
docs/beacon/<version>/research/<feature-slug>.md
```

Its authority is `support_advisory`. It can support routing, risk analysis, lake/ocean classification, source anchoring, and gap discovery. It cannot become requirement truth, implementation closure, QA pass, or release readiness by itself.

Research can enter the main chain only when:

```text
user_decision = accepted/promoted
promotion_ref is present
route = beacon-generator-truth-change or beacon-generator-truth-refreeze
```

## Hard Gates

Every v1.6.0 child `SKILL.md` must include the shared preamble followed immediately by a harness-specific `HARD GATE`.

The gate must prevent:

- planner writing truth, code, `.machine/`, QA verdict, or release verdict
- generator self-certifying completion or using fake delivery as closure
- evaluator rewriting truth or repairing implementation inside the verdict action
- governor becoming a truth, implementation, QA, or release stage

Verify with:

```bash
beacon skill package verify --project-root . --version v1.6.0 --package-root skills/beacon --json
beacon doctor setup-agent-surface --project-root . --version v1.6.0 --agent codex --json
beacon doctor verify-agent-surface --project-root . --version v1.6.0 --agent codex --strict --json
```

## No-Fake-Delivery

These signals cannot close implementation, QA, or release:

- placeholder implementation
- docs-only completion
- fake runner evidence
- zero assertions
- placeholder evidence

Use:

```bash
beacon skill package verify-closure --payload-json '{"implementation":"real code path exercised","assertions":"12 assertions"}' --json
```

## References

- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md`
- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/tests.md`
- `docs/beacon/v1.6.0/execution/implementation-summary-beacon-skill-harness-taxonomy-v160.md`
