---
slug: beacon-truth-skill-lifecycle-rename
version: v1.5.2
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/truth.md
  user_story: docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/truth.md
  test_case: docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Feature Truth: Truth Skill Lifecycle Rename

## Summary

v1.5.2 已完成 feature package authoritative cutover。后续 Beacon 人类生命周期表达必须跟随新真相源，把旧文档时代的 `prd -> user-story -> test-case` 公共说法收敛为 truth package 下的模式化 truth 链路。

本 feature 冻结一个新的 preferred truth umbrella：`beacon-truth`。它不是新的 truth authority，也不是新的 gate；它是人类入口和 skill 路由面，用于把 `truth.md` / `tests.md` 的新权威模型表达清楚。

## Problem

当前运行时已经把正常生产/消费入口切到 resolver-selected feature package，但公开 skill 名称仍主要暴露 `beacon-prd`、`beacon-user-story`、`beacon-test-case`。这些名称在 v1.5.2 中已经是新真相源入口，却容易让操作者误解为旧 `prd/`、`user-story/`、`qa/test-cases/` 目录仍是 canonical。

## Goal

新增并冻结 `beacon-truth` preferred umbrella skill 的需求，使它以子模式方式替代旧生命周期说法，同时保留旧 skill 作为 compatibility aliases。后续实现应更新 Beacon root skill、brainstorm route-back 文案和相关 packaged/project agent skill guidance。

## Non-Goals

- 不在本 feature 中把 `brainstorm` 提升为 lifecycle stage。
- 不在本 feature 中改变 feature package 的 authority；authority 仍由 truth-map resolver 和 package frontmatter 决定。
- 不删除 `beacon-prd`、`beacon-user-story`、`beacon-test-case`，避免破坏既有用户和测试。
- 不把 `truth.md`、`tests.md`、`tasks.md`、`evidence.md` 合并成单文件。
- 不让 `beacon-truth` 直接发布 QA 或 release verdict。

## Lifecycle Contract

Preferred v1.5.2+ human lifecycle:

```text
brainstorm/support
  -> truth.define
  -> truth.acceptance
  -> truth.coverage
  -> implement
  -> qa
  -> release
```

Compatibility mapping:

```text
truth.define      = beacon-prd semantics
truth.acceptance  = beacon-user-story semantics
truth.coverage    = beacon-test-case semantics
truth.change      = beacon-change / beacon-change-refreeze semantics
```

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | truth-umbrella | Beacon exposes `beacon-truth` as the preferred v1.5.2+ human-facing truth umbrella for feature package requirement work. |
| AC-002 | mode-separation | `beacon-truth` must preserve distinct modes for definition, acceptance, coverage, and change instead of flattening all requirement work into one freeform truth surface. |
| AC-003 | package-authority | Every `beacon-truth` mode must resolve feature truth through `beacon truth-map resolve <feature> --project . --version v1.5.2 --json` before reading or writing requirement material. |
| AC-004 | compatibility-aliases | Existing `beacon-prd`, `beacon-user-story`, and `beacon-test-case` skills remain available as compatibility aliases for `truth.define`, `truth.acceptance`, and `truth.coverage`. |
| AC-005 | lifecycle-language | Root Beacon and brainstorm guidance must describe the preferred truth chain as `truth.define -> truth.acceptance -> truth.coverage`, while documenting the old skill names as aliases. |
| AC-006 | no-stage-inflation | `beacon-truth` must not turn brainstorm, change-refreeze, QA, or release into truth authoring stages. |
| AC-007 | coverage-boundary | Coverage truth remains in `features/<slug>/tests.md`; `truth.md` owns requirement and acceptance framing, not executable coverage matrices. |
| AC-008 | closure-trace | The new lifecycle language must preserve the closure route from support research to truth package, requirement clarity, implementation, QA, and release. |

## Authority

The authoritative requirement source for this feature is this package:

- `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/truth.md`
- `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/tests.md`
- `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/tasks.md`
- `docs/beacon/archive/v1.5.2/features/beacon-truth-skill-lifecycle-rename/evidence.md`

Legacy `prd/`, `user-story/`, and `qa/test-cases/` files, if later rebuilt, are generated compatibility artifacts only.
