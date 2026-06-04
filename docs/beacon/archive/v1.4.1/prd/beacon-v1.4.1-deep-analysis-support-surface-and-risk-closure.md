# PRD: Beacon v1.4.1 Deep Analysis Support Surface and Risk Closure

**Feature**: `beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure`  
**Version**: `v1.4.1`  
**Date**: `2026-05-09`  
**Status**: `freeze-ready`  
**Track**: `requirement-depth + qa-risk + release-governance`  
**Scenario**: `complex-business-risk-discovery + deep-test-delta + release-supplement`  
**Template**: `main PRD / next-version planning`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Previous release planning line: `docs/beacon/v1.4.0/SUMMARY.md`
- Previous architecture blueprint: `docs/beacon/v1.4.0/execution/architecture-blueprint.md`
- Research supplement:
  - `docs/beacon/archive/v1.4.1/research/beacon-deep-capability-upgrade-research-supplement.md`
- Source project research:
  - `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/execution/2026-05-09-beacon-deep-capability-upgrade-research.md`

## Overview

Beacon already supports the standard requirement and delivery closure path:

```text
prd
-> user-story
-> test-case
-> implement
-> qa
-> release
```

This path is effective for validating known requirements. A real `slow_uni_bmtop / friend-match` QA loop showed that this is not always enough for complex business features. The feature passed after fixing a P2 issue, but the defect category revealed a deeper gap: the score fact source, derived ranking fields, detail response, personal statistics, and guest post-match attribution were not modeled as one explicit consistency chain.

`v1.4.1` therefore introduces a next-version requirement for a deep analysis support surface.

The goal is not to add another mandatory stage. The goal is:

> Let Beacon discover hidden state, transition, invariant, fact-source, and cross-module consistency risks for high-risk features, then converge those findings into test deltas and release-facing risk closure without expanding the human main lifecycle or weakening frozen-truth governance.

## 4. 范围

In scope:

- Define `deep` as a support/analysis/gate-supplement surface.
- Define high-risk trigger rules for when deep analysis is required or recommended.
- Define skip reason semantics for low-risk features.
- Define human-readable artifacts for deep analysis, state machine, test delta, risk register, and closure brief.
- Define how deep findings become requirement supplements through change/refreeze instead of direct truth mutation.
- Define how QA consumes deep test deltas through supplemental QA.
- Define how release consumes deep closure or skip reason as supporting evidence.
- Define minimum CLI and artifact contract for a first implementation.

Out of scope:

- Making `deep` a new required human lifecycle stage.
- Replacing `prd`, `user-story`, `test-case`, `qa`, or `release`.
- Letting deep directly edit frozen PRD/user-story/test-case truth.
- Letting deep findings become release gate truth without human acceptance.
- Requiring deep for every low-risk feature.
- Executing browser/API tests directly in the first deep iteration.
- Creating a second canonical truth source under `.machine`, `.beacon`, or runtime projections.

## Diagram Truth

- `branch-flow`
  - `known requirement -> MVP QA -> hidden structural risk -> deep analysis -> test delta -> supplemental QA -> release closure`
  - `deep finding -> supplement proposal -> change/refreeze -> canonical truth update`
  - `low-risk feature -> deep skip reason -> release evidence`
- `state-machine`
  - `deep_requirement_state: not_required | recommended | required | completed | waived`
  - `deep_finding_state: candidate | accepted | deferred | rejected | closed`
  - `deep_delta_state: proposed | adopted | executed | waived`
  - `release_risk_state: none | accepted | blocked | waived`
- `decision-priority`
  - `global boundaries > frozen truth > accepted change/refreeze > deep finding > learning note`
  - `test delta > test rewrite`
  - `support surface > new lifecycle stage`
  - `high-risk trigger > default deep everywhere`

## 1. 问题

### 1.1 MVP QA can pass while structural business risk remains under-modeled

MVP QA answers whether defined acceptance criteria pass. It does not always answer whether a complex feature has complete state and data closure.

Examples of structural risks:

- scoring succeeds, but leaderboard derives from a stale or different field
- detail page and list page read different fact sources
- personal statistics do not reconcile with match results
- post-match identity binding changes attribution unexpectedly
- illegal state transitions are not explicitly rejected
- repeated actions are not idempotent

### 1.2 User-story-based test matrices can miss cross-story invariants

Beacon's test-case generation is intentionally grounded in user stories and acceptance criteria. That is correct for traceability, but complex features often need an additional matrix:

- entity state
- transition
- actor
- event
- fact source
- derived field
- page/API surface
- invariant

Without this matrix, a feature can satisfy each individual story while still violating an end-to-end business invariant.

### 1.3 Current support surfaces do not yet produce a release-facing deep risk closure

Beacon has `qa`, `release`, `gate`, `learning`, and decision surface capability, but there is no standard artifact family for:

- deep analysis
- state-machine report
- test delta
- risk register
- deep closure brief

As a result, deep insights are easy to keep as ad-hoc human notes instead of becoming auditable delivery evidence.

## 2. 目标

### 2.1 Primary goals

1. Establish a formal deep analysis support surface for complex business features.
2. Preserve the existing Beacon main lifecycle and global human-surface constraints.
3. Force state-machine, invariant, and consistency-chain analysis for high-risk feature categories.
4. Generate incremental test deltas rather than rewriting existing test cases.
5. Route accepted requirement gaps through change/refreeze.
6. Let QA execute adopted deep deltas as supplemental QA.
7. Let release consume deep closure, waiver, or skip reason as evidence.
8. Prevent scope creep by classifying findings as MVP / Deep / Release / Backlog.

### 2.2 Non-goals

- Deep does not replace QA.
- Deep does not become a second PRD generator.
- Deep does not write canonical truth directly.
- Deep does not require every feature to perform heavyweight modeling.
- Deep does not make backlog risks block release by default.
- Deep does not bypass existing gate reason codes or release scorecards.

## Scope

The v1.4.1 scope is limited to `beacon-deep` as a loop-capable support skill/toolkit surface, its artifact contracts, trigger and skip semantics, cross-stage routing rules, QA preflight delta handoff, release supplement semantics, and implementation-ready requirement package closure.

The scope explicitly excludes lifecycle expansion, direct frozen-truth mutation by deep artifacts, runtime release promotion, and implementation execution during requirement freeze.

## 3. 设计原则

### 3.1 Boundary first

- `deep` 必须服从 `docs/beacon/global-boundaries.md` 的主流程边界。
- `deep` 是支持面和分析面，不是新的主阶段。
- `deep` 不能直接改写 frozen truth，不能替代 gate verdict。

### 3.2 Layering first

- 分层规则保持为：canonical markdown truth -> compiled contract -> support/runtime projection。
- deep artifacts 只能作为分析证据、delta 建议和 release supplement，不能成为第二 truth root。
- 任何被接受的需求缺口都必须回到 `change/refreeze`，再进入 implementation / QA / release。

### 3.3 Recovery first

- 当 deep 发现 requirement gap、test gap 或 release-blocking risk 时，恢复路径必须可审计。
- 恢复路径优先级为：document finding -> classify risk -> propose delta -> human accept -> change/refreeze or supplemental QA。
- 不能通过静默忽略 deep finding 来维持 release pass。

### 3.4 Risk mitigation first

- 风险必须被分类为 `MVP / Deep / Release / Backlog`。
- 缓解方式必须显式记录为 `fix / test-delta / waiver / backlog / reject`。
- Backlog 风险不得默认阻塞当前 release，除非被显式提升为 release-blocking。

## 3A. Users and Operators

### 3.1 Human operator

Needs to know whether a complex feature has hidden structural risk before release.

The operator should be able to see:

- whether the feature requires deep analysis
- which state machines and invariants were analyzed
- which new test deltas were proposed
- which deltas are release-blocking
- which findings are accepted backlog

### 3.2 Host LLM / agent

Needs a structured protocol for doing more than shallow template fill:

- extract roles, states, events, and invariants
- identify fact-source and derived-field relationships
- map cross-surface consistency chains
- produce delta cases with severity and gate classification

### 3.3 Gate / release checker

Needs machine-checkable evidence that either:

- deep was not required and a skip reason exists
- deep was required and closure artifacts exist
- release-blocking deep findings are closed or waived

## 4A. Deep Trigger Rules

### 4.1 Required deep triggers

Deep should be required when a feature includes one or more high-risk domains:

- payment, order, wallet, settlement
- tournament, ranking, scoring, leaderboard
- identity binding, account attribution, permission ownership
- invitation, joining, relationship-chain mutation
- reporting, statistics, historical record
- migration, old-system takeover, cross-database reconciliation
- multi-role, multi-state, multi-surface workflows
- post-fact attribution or retroactive binding

### 4.2 Recommended deep triggers

Deep should be recommended when:

- QA found a P0/P1/P2 defect caused by missing business modeling
- acceptance passed but evidence shows cross-module uncertainty
- user story count is high but state coverage is thin
- implementation has derived fields that are not explicitly tied to a fact source

### 4.3 Skip semantics

Deep may be skipped for:

- static display pages
- simple forms
- stateless utilities
- visual-only changes
- low-risk configuration changes

Skip must be explicit:

```yaml
deep_required: false
skip_reason: low_risk_static_surface
```

## 5. 功能需求

### FR-001 Deep artifact contract

Beacon must define a stable artifact family for deep analysis so the output is reviewable, auditable, and reusable by `test-case`, `qa`, and `release`.

### FR-002 Trigger and skip contract

Beacon must distinguish high-risk features that require deep analysis from low-risk features that can provide an explicit skip reason.

### FR-003 Delta-first contract

Beacon must generate incremental test deltas and risk entries rather than rewriting existing test cases by default.

### FR-004 Truth governance contract

Beacon must route accepted deep findings through `change/refreeze` before altering frozen PRD, user story, or test-case truth.

### FR-005 Release supplement contract

Beacon must let release checks consume deep closure, waiver, or skip reason as supporting evidence without making deep a new lifecycle stage.

### FR-006 Deep loop orchestration contract

Beacon must support `deep` as a loop-capable human support skill/toolkit surface that can iterate across PRD, user-story, test-case, implement evidence, QA evidence, and release evidence without becoming a new main lifecycle stage.

Each `deep run` should execute the smallest complete loop required for the current user intent:

```text
scan_truth
-> model_business
-> challenge_gaps
-> derive_delta
-> classify_findings
-> route_repairs
-> verify_closure
```

The default target is one-pass closure. A `deep run` should continue internally until it either closes all findings for the current intent or routes accepted deltas into the correct Beacon surface.

### FR-007 One-pass convergence contract

Beacon must avoid turning `deep` into an infinite analysis loop.

For the same user intent, deep should close in one run when:

- no new role, entity, business process, state machine, fact source, or cross-surface invariant is discovered
- all findings are classified as `MVP | Deep | Release | Backlog`
- all release-blocking findings are closed, waived, or routed
- all accepted test deltas are attached to test-case or supplemental QA
- all accepted requirement deltas are routed to `change/refreeze`

A new deep loop is justified only when the user introduces a new prompt intent, feature, role, state machine, business process, or release-blocking evidence.

### FR-008 Cross-stage delta routing contract

Deep findings must route to the correct existing Beacon surface instead of creating a new lifecycle stage:

| Finding type | Route |
|---|---|
| PRD gap | `change/refreeze` |
| User story gap | `user-story` supplement or `change/refreeze` |
| Acceptance gap | `test-case` delta |
| Implementation gap | `implement` repair handoff |
| QA evidence gap | supplemental `qa` loop |
| Release risk | release closure, waiver, or backlog |

### FR-009 Human support skill contract

Beacon should expose `deep` as a human-facing support skill and toolkit family, not as a primary lifecycle command.

The user-facing skill should be discoverable as `beacon-deep`. Internal implementation may use support toolkit modules such as:

- `beacon-toolkit-deep-loop`
- `beacon-toolkit-state-machine`
- `beacon-toolkit-test-delta`
- `beacon-toolkit-risk-register`

The public mental model remains one support entry:

```text
beacon deep run
```

### FR-010 Deep QA-preflight contract

Deep test deltas should be usable as a pre-QA iterative evolution surface.

Before QA, deep may derive missing cases from PRD, user stories, state machines, fact-source maps, and existing test cases. After QA, deep may consume defects and evidence to decide whether the issue is a normal bug, a requirement gap, a state-machine gap, a test gap, or a release risk.

## 5A. Artifact Contract

### 5.1 Deep Analysis Report

Path:

```text
docs/beacon/<version>/deep/<feature>-deep-analysis.md
```

Required content:

- feature summary
- role model
- entity model
- main business closure
- cross-story invariant candidates
- fact-source and derived-field map
- deep findings
- proposed next actions

### 5.2 State Machine Report

Path:

```text
docs/beacon/<version>/deep/<feature>-state-machine.md
```

Required content:

- state list
- allowed transition matrix
- forbidden transition matrix
- actor/action/API trigger map
- transition invariants
- idempotency expectations

### 5.3 Deep Test Delta

Path:

```text
docs/beacon/<version>/qa/test-cases/<feature>-deep-delta.md
```

Required content per case:

- delta id
- linked user story or requirement area
- linked deep finding
- scenario
- expected result
- automation candidate
- gate classification: `MVP | Deep | Release | Backlog`
- severity: `P0 | P1 | P2 | P3`
- release blocking: `true | false`

### 5.4 Risk Register

Path:

```text
docs/beacon/<version>/deep/<feature>-risk-register.md
```

Required content:

- risk id
- description
- affected surfaces
- severity
- release blocking status
- owner or stage
- handling: `fix | test-delta | waiver | backlog | reject`

### 5.5 Deep Closure Brief

Path:

```text
docs/beacon/<version>/execution/deep-closure-brief-<feature>.md
```

Required content:

- deep requirement state
- deep verdict
- executed delta cases
- open findings
- waived findings
- accepted backlog risks
- release recommendation

### 5.6 Deep Loop Trace

Path:

```text
docs/beacon/<version>/deep/<feature>-deep-loop-trace.md
```

Required content:

- user intent snapshot
- loop iteration list
- discovered role/entity/state/process changes
- finding classification
- route decision for each finding
- closure decision
- stop reason
- next allowed route

The trace is the audit bridge proving that deep loop converged or intentionally routed work back into Beacon's existing surfaces.

## 6. Command Surface

The first implementation should expose one support entry, a human skill, and optional subcommands.

Human skill:

```text
beacon-deep
```

Minimum:

```bash
beacon deep run "<feature>" --project-root . --version <version>
```

Recommended subcommands:

```bash
beacon deep analyze "<feature>" --project-root . --version <version>
beacon deep state-machine "<feature>" --project-root . --version <version>
beacon deep derive-tests "<feature>" --project-root . --version <version>
beacon deep close-loop "<feature>" --project-root . --version <version>
```

`deep` is a support command family. It must not be presented as a new required lifecycle stage.

`beacon deep run` is the preferred public entry because it can perform scan, model, challenge, derive, route, and closure verification in one guided loop.

## 6A. Deep Loop State Machine

```text
not_started
-> scanning
-> modeling
-> challenging
-> deriving_delta
-> routing
-> verifying
-> closed
```

Allowed reopening conditions:

- user introduces a new feature, role, business process, or state machine
- QA evidence exposes a structural requirement or state gap
- implementation evidence contradicts the deep model
- release evidence exposes an unclosed high-risk finding
- accepted test deltas reveal a new state or invariant

Default stop conditions:

- no unclassified finding remains
- no open release-blocking finding remains
- all accepted deltas are routed
- all waivers and backlog decisions are explicit
- no new state machine or feature was introduced by the current prompt

## 6B. State Axes

The first implementation must keep these state axes explicit through freeze readiness, implementation planning, QA coverage, and release evidence:

- `deep_loop_state`: `not_started | scanning | modeling | challenging | deriving_delta | routing | verifying | closed`
- `finding_state`: `candidate | classified | routed | closed | waived | backlog | rejected`
- `delta_state`: `proposed | accepted | attached_to_test_case | executed_by_qa | closed`
- `risk_state`: `open | release_blocking | waived | accepted_backlog | closed`
- `requirement_package_state`: `prd_only | three_piece_complete | frozen | implement_pending`

These axes must not be compressed into one generic status field.

## 7. Gate Semantics

Deep gate semantics should be additive:

- release may check deep closure for high-risk features
- release may accept explicit skip reason for low-risk features
- P0/P1/P2 release-blocking deep findings must be closed or waived
- backlog findings must not block release unless explicitly promoted

Candidate reason codes:

- `deep_analysis_required`
- `deep_closure_missing`
- `deep_release_blocking_findings_open`
- `deep_skip_reason_missing`
- `deep_test_delta_unexecuted`
- `deep_loop_unclosed`
- `deep_delta_route_missing`
- `deep_new_state_machine_unclassified`

## 7A. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| deep 变成新的主阶段 | 破坏 Beacon 极简主流程 | 明确 deep 是 support surface，并要求 skip reason / trigger rule |
| deep 直接改写 frozen truth | 破坏 canonical truth discipline | 所有 accepted finding 必须走 change/refreeze |
| deep 与 QA 重复 | 扩大流程负担 | deep 只生成结构分析和 test delta，qa 负责执行 |
| low-risk feature 被过度建模 | 降低交付效率 | 允许显式 skip reason，不默认阻塞 release |
| backlog 风险误阻塞 release | release 判断噪音变高 | 风险分类必须区分 `Release` 与 `Backlog` |
| deep loop 无限迭代 | 阻塞交付且削弱主流程心智 | 定义 one-pass closure、stop reason 和 allowed reopening conditions |
| deep 发现无法路由 | finding 留在分析文档中失去执行价值 | 每个 finding 必须有 route decision 和 closure decision |

## 8A. Truth Governance

Deep findings are not truth by themselves.

The allowed path is:

```text
deep finding
-> supplement proposal
-> human acceptance
-> beacon change/refreeze
-> updated PRD/user-story/test-case
-> implementation/QA/release recheck
```

Deep may write supporting artifacts, but it may not directly mutate frozen PRD, user story, or test-case truth.

## 8. 验收标准

- [ ] `v1.4.1` documents `deep` as support surface rather than a new lifecycle stage.
- [ ] High-risk trigger rules are documented.
- [ ] Skip reason semantics are documented.
- [ ] Deep artifact family is documented.
- [ ] Deep test delta format is documented.
- [ ] Release-facing deep closure semantics are documented.
- [ ] Deep findings are routed through change/refreeze before altering frozen truth.
- [ ] MVP / Deep / Release / Backlog classification is documented.
- [ ] First implementation can read PRD, user-story, test-case, QA progress, acceptance brief, and architecture blueprint when present.
- [ ] First implementation can produce at least deep analysis, state-machine report, test delta, and risk register.
- [ ] First implementation can produce a deep loop trace with iteration, route, closure, and stop reason.
- [ ] `beacon-deep` is described as a support skill/toolkit surface rather than a lifecycle stage.
- [ ] `beacon deep run` can converge scan/model/challenge/delta/route/verify in one run for the same user intent.
- [ ] Deep findings can route to PRD, user-story, test-case, implement repair, supplemental QA, release waiver, or backlog.
- [ ] Deep loop reopening requires a new user intent, feature, role, state machine, business process, or release-blocking evidence.
- [ ] Low-risk features can explicitly skip deep without release blockage.
- [ ] High-risk features without deep closure or skip decision can be surfaced as release risk.

## 10. Rollout Plan

### Phase 1: Documentation and manual sample

- Freeze this PRD.
- Produce one manual deep sample from `friend-match`.
- Validate artifact structure with human review.

### Phase 2: CLI generation

- Implement `beacon deep analyze`.
- Implement `beacon deep derive-tests`.
- Implement `beacon deep run` as the preferred one-pass loop orchestrator.
- Materialize `beacon-deep` as a host-visible support skill.
- Keep outputs as draft support artifacts.

### Phase 3: QA and release integration

- Let QA consume adopted deep deltas.
- Let QA defects re-enter deep only when they imply a structural state, fact-source, or requirement gap.
- Add deep closure brief generation.
- Add deep loop trace generation.
- Add release supplement checks for high-risk features.

### Phase 4: Governance hardening

- Add strict reason codes.
- Add skip reason verification.
- Add waiver handling for release-blocking deep findings.

## 11. Implementation Decisions

- `deep` will use its own support command family and human-facing support skill surface: `beacon-deep`.
- The first runtime implementation will treat the documented high-risk trigger categories as advisory diagnostics, then promote strict enforcement after implementation evidence proves stability.
- Human deep artifacts are required first; machine mirrors are allowed as compiled projections and audit evidence, not as a second truth root.
- Deep delta adoption routes through `test-case` for acceptance coverage gaps and through `change/refreeze` for requirement truth gaps.
- Release scorecards should reflect deep closure through closure brief presence, release-blocking finding status, waiver status, and backlog decision status.
- Internal toolkit modules stay hidden behind `beacon-deep` unless a later version proves that separate human surfaces reduce rather than increase operator friction.
- `deep_loop_unclosed`, `deep_delta_route_missing`, and `deep_new_state_machine_unclassified` start as explicit reason codes; strict gate promotion is deferred until implementation and QA evidence converge.

## 12. Final Requirement Statement

Beacon `v1.4.1` must add a loop-capable deep analysis support capability that helps complex business features expose hidden state, transition, invariant, fact-source, and cross-module consistency risks. It must converge those risks into test deltas, route accepted gaps back into the existing Beacon lifecycle, and produce release evidence while preserving Beacon's small human lifecycle, canonical truth discipline, and support-surface boundaries.
