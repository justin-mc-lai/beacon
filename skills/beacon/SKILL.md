---
name: beacon
description: Beacon v1.6.7 host-level router for harness-first planner/generator/evaluator/governor skills.
metadata:
  author: Beacon CLI
  version: "v1.6.7"
  organization: Beacon
  date: June 2026
  abstract: Harness-first Beacon meta-protocol. Route coarse user intent into planner, generator, evaluator, or governor skills without preserving old host-visible aliases.
---

# Beacon Skill

This package is the canonical `skills/beacon/` host-visible Beacon skill package for Codex and Claude.

v1.6.0 introduced a breaking skill-surface migration (still the taxonomy baseline through v1.6.7). Host-visible child skills use only:

- `beacon-pln-*`
- `beacon-gen-*`
- `beacon-eval-*`
- `beacon-gov-*`

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

## GIT_ADMISSION (mandatory — Tier A/B when version+feature known)

Before ANY repo write or implement/qa/release route:
1. `beacon workspace admit --project-root . --version <v> --feature <slug> --json`
2. If status != pass → STOP; show reason_codes; do NOT edit files
3. Set cwd to worktree_path from payload
4. Do NOT git checkout elsewhere to "fix" branch

## Harness Routing

- `planner`: 拆分粗提示词，判断湖/海规模，读取 truth/source/evidence，并产出 research/planning artifact 或 route recommendation。
- `generator`: 在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth、implementation、prototype、design 或 delivery artifact。
- `evaluator`: 验证 evidence，识别 truth drift、fake delivery、missing coverage、placeholder evidence，并产出 verdict/finding/route/block。
- `governor`: 维护 context、archive、memory、hooks、automation、metadata、status 和 diagnostic support。

## Host-Visible Skills

Planner:

- `beacon-pln-brainstorm`
- `beacon-pln-source`
- `beacon-pln-review`
- `beacon-pln-friction`

Planner tools may still route to stable CLI commands. For example, `beacon-pln-friction` can recommend `beacon friction-intake run ...` while remaining a planner support surface.
Former fine-grained planner surfaces such as founder, doubt, security, performance, context, simplify, ADR, design, and deep review are internal reviewers inside `beacon-pln-review`, not default host-visible routes.

Generator:

- `beacon-gen-truth`
- `beacon-gen-truth-init`
- `beacon-gen-change`
- `beacon-gen-refreeze`
- `beacon-gen-prototype`
- `beacon-gen-implement`
- `beacon-gen-design`
- `beacon-gen-design-init`
- `beacon-gen-design-explore`
- `beacon-gen-design-system`
- `beacon-gen-design-polish`

Evaluator:

- `beacon-eval-qa`
- `beacon-eval-qa-deep`
- `beacon-eval-release`
- `beacon-eval-real-project`

Governor:

- `beacon-gov-library`
- `beacon-gov-extract`
- `beacon-gov-doctor`
- `beacon-gov-debug`
- `beacon-gov-status`
- `beacon-gov-help`
- `beacon-gov-archive`
- `beacon-gov-learn`
- `beacon-gov-hooks`
- `beacon-gov-automation`
- `beacon-gov-branch`
- `beacon-gov-lighthouse`
- `beacon-gov-metadata`
- `beacon-gov-router`

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
route = beacon-gen-change or beacon-gen-refreeze
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
