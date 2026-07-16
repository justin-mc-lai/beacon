---
slug: code2truth-project-intake
version: v1.5.2
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/archive/v1.5.2/features/code2truth-project-intake/truth.md
  user_story: docs/beacon/archive/v1.5.2/features/code2truth-project-intake/truth.md
  test_case: docs/beacon/archive/v1.5.2/features/code2truth-project-intake/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Feature Truth: Code2Truth Project Intake

## Overview

`code2truth-project-intake` 让 Beacon 面对已有实现项目时，可以从代码、文档、skill、测试、CLI 行为和代码地图 provider 中重建 candidate truth，再由用户确认并冻结为 v1.5.2 package-authoritative truth。

核心规则是：

```text
code can propose candidate truth;
user-confirmed and frozen Beacon package Markdown is formal truth.
```

这不是把代码直接当 truth，而是把已有实现变成可审计、可确认、可冻结、可 QA 的 Beacon 真相交付闭环。

## Problem

很多接入 Beacon 的项目已经有实现和使用习惯，但没有绑定 v1.5.2 的 `features/<slug>/{truth,tests,tasks,evidence}.md` package truth。操作者需要 Beacon 快速理解项目需求真相，而不是从空白 PRD 重写；同时 Beacon 不能把“当前代码行为”误判成“用户确认的产品意图”。

## Goal

提供一个 source-driven intake 契约，使 Beacon 能：

- 读取已有实现和辅助代码地图，形成带证据的 candidate truth。
- 将第三方/本地 provider 作为 evidence provider，而不是 truth authority。
- 在用户确认后，把 accepted candidate truth 冻结进 Beacon package。
- 当已有代码已经满足 frozen truth 时，允许 `beacon implement` 以 no-op/evidence-only 方式闭环。
- 由 `beacon QA` 验收 package truth、evidence、tasks、governance 和现有行为，而不是强制制造代码改动。

## Non-Goals

| Item | Rationale |
|---|---|
| 代码直接成为正式 truth | 代码只能证明实现行为，不能证明用户意图、弃用状态或 bug 是否应被保留 |
| 第三方代码地图成为 authority | `understand-anything` 等 provider 只提供 source graph evidence |
| 绕过用户确认 | candidate truth 必须被用户接受后才能进入 package truth |
| 绕过 requirement clarity / freeze | refreeze 仍负责 requirement closure |
| 强制 implement 改代码 | 已有代码满足 frozen truth 时，应允许 no-op/evidence-only execution |

## Intake Loop

```text
existing implementation
  -> source/code-map evidence
  -> candidate truth reconstruction
  -> user confirmation
  -> frozen Beacon package truth
  -> implement no-op or evidence-only execution
  -> beacon QA verifies truth/evidence/governance
```

## Provider Boundary

Beacon-native providers include `beacon-source-driven`, `beacon lighthouse`, source architecture projection, truth-map resolver, tests, CLI behavior, docs, and skill files.

Local or third-party providers such as `qi-dev-understand-anything` / Understand-Anything may enrich the source inventory with deterministic file, module, function, class, export, `contains`, and `imports` relationships. Their generated artifacts are evidence refs only:

- `.understand-anything/intermediate/scan-result.json`
- `.understand-anything/intermediate/import-map.json`
- `.understand-anything/intermediate/batches.json`
- `.understand-anything/intermediate/structure-result.json`
- `.understand-anything/knowledge-graph.json`
- `.understand-anything/graph-build-report.json`
- `.understand-anything/meta.json`

Provider artifacts cannot override package truth, acceptance criteria, QA verdict, or release readiness.

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | source-inventory | Code2truth intake must build a source inventory from existing code, docs, skills, tests, CLI behavior, Beacon lighthouse/source-architecture outputs, and available provider artifacts. |
| AC-002 | provider-evidence-boundary | Third-party or local code-map providers such as `qi-dev-understand-anything` must be treated as evidence providers only, never as requirement authority. |
| AC-003 | candidate-truth-reconstruction | Intake must reconstruct candidate truth with source refs, confidence, and ambiguity markers for each material claim. |
| AC-004 | user-confirmation-gate | Candidate truth can become formal truth only after user confirmation and governed promotion into the Beacon feature package. |
| AC-005 | package-authority | The frozen truth source must be resolver-selected `features/<slug>/{truth,tests,tasks,evidence}.md`; generated JSON, legacy triptych, provider graphs, and support research cannot win authority. |
| AC-006 | implement-no-op-admission | `beacon implement` may complete as no-op/evidence-only execution when frozen ACs are already satisfied by existing code and every task has evidence-backed closure. |
| AC-007 | tasks-evidence-closure | `tasks.md` must express implementation intent and may mark existing-code satisfaction through evidence refs; it must not fake source churn or replace execution/gate evidence. |
| AC-008 | qa-truth-governance-verification | `beacon QA` must validate truth-map resolution, package coverage, evidence refs, provider boundary, governance/doctor verification, and current behavior satisfaction. |
| AC-009 | fail-closed-ambiguity | Ambiguous, stale, conflicting, low-confidence, or unproven behavior must fail closed into questions, exclusions, or change routing instead of freezing as authoritative truth. |
| AC-010 | existing-project-pilot | The intake model must support a bounded pilot on an existing skill project such as `/Users/apple/Developer/Personal/products/justin-mc-lai-skills`, preferably by one skill pack before whole-repo adoption. |

## Implement No-Op Contract

`beacon implement` can be a no-code-change pass only when all of these are true:

- package truth and coverage exist and pass resolver/package validation;
- each AC is already satisfied by existing code, docs, tests, CLI behavior, or accepted provider evidence;
- user confirmation distinguishes intended behavior from accidental implementation;
- no frozen AC requires new or changed code;
- low-confidence or conflicting evidence has been excluded or routed back to change;
- task closure records evidence, not artificial source edits.

If any AC cannot be proven from current behavior or evidence, `implement` must either change code or route back to truth/change.

## Authority

The authoritative requirement source for this feature is this package:

- `docs/beacon/archive/v1.5.2/features/code2truth-project-intake/truth.md`
- `docs/beacon/archive/v1.5.2/features/code2truth-project-intake/tests.md`
- `docs/beacon/archive/v1.5.2/features/code2truth-project-intake/tasks.md`
- `docs/beacon/archive/v1.5.2/features/code2truth-project-intake/evidence.md`

Support research is upstream evidence only: `docs/beacon/archive/v1.5.2/research/code2truth-project-intake.md`.
