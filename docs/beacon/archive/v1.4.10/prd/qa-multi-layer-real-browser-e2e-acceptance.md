# PRD: QA Multi-Layer Real Browser E2E Acceptance

**Feature**: `qa-multi-layer-real-browser-e2e-acceptance`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-25`

## Overview

Beacon is a truth-delivery protocol. Frozen truth defines what must be delivered; QA proves whether it was actually delivered. This feature makes QA the supreme closure-verification authority under frozen truth definition authority.

QA cannot silently rewrite PRD, user-story, test-case, freeze state, release verdict, or gate truth. QA can reject closure, block release, and route back to change, test-case, implement, or QA rerun when evidence is weak, incomplete, contradicted, or falsified by real execution.

## Context

- Global boundary source: `docs/beacon/global-boundaries.md`
- Source-driven implementation anchors: `beacon/commands/qa.py`, `beacon/commands/auto_test.py`, `beacon/utils/qa_feature.py`, `beacon/utils/exhaustiveness.py`
- Real-project pressure signal: `slow_uni_bmtop` has project-native Playwright E2E scripts and reports that were not fully bound into canonical Beacon QA truth.
- Browser runner references: Playwright CLI and Obscura are mirrored under `/Users/apple/Developer/Personal/oss-sync`.

## 1. 问题

Current Beacon QA has important foundations: QA9 matrix execution, human layer command overrides, UI runner selection, browser admission, browser evidence pack, exhaustiveness checks, and attribution support. The missing product commitment is that these mechanisms are not yet frozen as Beacon QA's core promise.

Real project evidence shows the gap. A project may have strong Playwright E2E suites, package scripts, and historical browser reports, while Beacon's formal QA matrix still records generic pytest fallback commands, omits `browser_required`, accepts thin `verdict: passed` transactions, or treats `playwright test --list` as close to evidence.

That weakens Beacon's requirement certainty, implementation certainty, acceptance certainty, and release certainty.

## 2. 目标

- AC-001: QA supports a finite full-range layer taxonomy: `unit`, `interface`, `contract`, `integration`, `smoke`, `functional`, `regression`, `exception`, `compatibility`, and `browser_e2e`.
- AC-002: QA profiles distinguish `basic`, `complete`, `closure`, and `browser`; complete closure must state which layers were required, executed, skipped, blocked, or not applicable.
- AC-003: Human operators can explicitly select layers and commands, and Beacon records whether the run is partial or complete.
- AC-004: Non-browser service features dynamically run or justify all applicable non-browser layers.
- AC-005: Browser/front-end/H5/miniapp/admin features require real browser E2E evidence for function, UI, UX, compatibility, session, and state/data consistency.
- AC-006: Beacon can discover or accept project-native E2E scripts and bind them to QA matrix entries instead of merely noting that scripts exist.
- AC-007: Browser runner registry includes Playwright, Playwright CLI, Playwright CDP, browser-use, agent-browser, attached browser, web-access, and Obscura CDP candidates.
- AC-008: `playwright test --list`, dry listings, placeholder transcripts, and documentation-only pass notes cannot satisfy QA acceptance.
- AC-009: QA acceptance transactions include run ID, source commands, runner/browser identity, accepted test IDs, evidence refs, and formal failure attribution.
- AC-010: Browser-required scenarios without valid browser evidence pack, report, trace/screenshot/console/network evidence, or admitted session bridge block QA/release.
- AC-011: QA failure attribution routes deterministically to implement, test-case, change/refreeze, QA rerun, or blocked runner admission.
- AC-012: Release consumes formal QA closure only; support evidence and raw runner output cannot directly become release pass evidence.

## 3. 设计原则

### 3.1 Truth Defines, QA Proves

Frozen truth owns the promised behavior. QA owns the right to reject closure when reality does not prove that promise.

### 3.2 Dynamic Full Range, Not One Fixed Script

QA must derive the required test range from feature type, touched surfaces, frozen test-case truth, and operator-selected profile. "Not applicable" is allowed only with explicit reason.

### 3.2.1 分层验收

QA verdict 必须按分层证据合成：基础层负责单元、接口、合约、集成、smoke、回归、异常、兼容性；浏览器层负责真实用户功能、UI、UX、会话、状态和数据一致性。任何一层缺失都不能被另一层静默替代。

### 3.3 Real Browser Means User-Observable Closure

For browser surfaces, backend success is not enough. QA must verify function, UI, UX, interaction state, layout stability, browser/session behavior, and data consistency.

### 3.4 Project-Native Tests Are First-Class

Beacon should orchestrate and evidence project-native suites instead of replacing them. Existing Playwright, Cypress, API, unit, or service scripts become governed commands with evidence binding.

### 3.5 Evidence Before Verdict

QA verdicts must be backed by executable evidence. Missing evidence, placeholder-only evidence, stale reports, or ambiguous attribution must fail closed.

### 3.6 边界与恢复

QA 的边界是验证和否决闭环，不是改写 frozen truth。QA 发现证据不足、runner admission 阻塞、测试脚本错误或 truth drift 时，必须进入恢复路径：回到 `beacon-qa` 重跑、`beacon-implement` 修实现、`beacon-test-case` 补覆盖，或 `beacon-change` 重新冻结 truth。

## 4. 范围

### In Scope

- QA profile model: `basic`, `complete`, `closure`, `browser`.
- Full layer taxonomy and required/applicable/not-applicable accounting.
- Human-selected command admission for layers and browser runner commands.
- Project E2E discovery/import contract for package scripts, Playwright config, E2E directories, and report paths.
- Browser runner registry with Playwright CLI and Obscura CDP as supported candidates.
- Browser evidence contract for Playwright JSON/JUnit/report, traces, screenshots, video, console/network summaries, DOM/current URL snapshots, storage state, and session bridge.
- Failure attribution and route recommendation for product bug, implementation gap, test script bug, environment blocker, auth/session blocker, runner admission blocker, coverage gap, truth drift, and evidence insufficient.
- Release boundary: incomplete QA cannot produce release readiness.

### Out Of Scope

- QA silently changing frozen truth.
- Hidden automatic browser execution without an explicit QA command.
- Replacing every project test stack with a Beacon-owned framework.
- Guaranteeing every runner is installed on every host.
- Turning browser runner tools into verdict authorities.

## 5. 功能需求

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon must model the full QA layer taxonomy and reject unknown layer names unless explicitly mapped. |
| FR-002 | AC-002 | Beacon must support `basic`, `complete`, `closure`, and `browser` profiles with explicit completeness semantics. |
| FR-003 | AC-003 | `beacon qa run` must accept human-selected layer commands and persist command, layer, profile, partial/complete status, and evidence refs. |
| FR-004 | AC-004 | Non-browser features must run or justify all applicable non-browser layers before closure. |
| FR-005 | AC-005 | Browser features must require browser E2E plus UI/UX evidence, not only functional or backend evidence. |
| FR-006 | AC-006 | Beacon must discover or import project-native E2E scripts and bind them to AC/test IDs. |
| FR-007 | AC-007 | Beacon must expose a governed browser runner registry and record selected runner/browser identity. |
| FR-008 | AC-008 | Listing commands and placeholder evidence must be classified as non-acceptance evidence. |
| FR-009 | AC-009 | QA acceptance writeback must include run ID, source command, accepted test IDs, evidence refs, and attribution. |
| FR-010 | AC-010 | Missing or invalid browser evidence for browser-required scenarios must block QA/release. |
| FR-011 | AC-011 | Failure attribution must produce deterministic route recommendation. |
| FR-012 | AC-012 | Release readiness must consume formal QA closure, not raw support or runner output. |

## 6. Data, State, and Integration

### 6.1 Inputs

- Frozen PRD, user-story, and test-case materials.
- Feature QA matrix and story-scenario map.
- Project metadata, touched services, and surface classification.
- Human-selected QA profile/layers/commands.
- Project-native test scripts and reports.
- Browser session state, CDP endpoint, or attached browser admission evidence when needed.

### 6.2 Outputs

- QA run status with profile completeness.
- Layer execution results.
- Browser evidence packs and imported report refs.
- Acceptance transaction with accepted AC/test IDs.
- Failure attribution and route recommendation.
- Release-facing blocker summary.

### 6.3 Integrations

- `beacon qa run`
- `beacon auto-test create qa9`
- `beacon qa session`
- `beacon test-case create`
- `beacon release check`
- Playwright / Playwright CLI / Playwright CDP
- browser-use / agent-browser / attached browser / web-access / Obscura CDP

## 7. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| QA becomes a hidden truth author | Requirement drift | QA can veto and route, but cannot write truth directly. |
| Browser tests are flaky or environment-bound | False failures | Admission, session bridge, and blocker attribution distinguish environment from product failure. |
| Operators run partial QA and overclaim closure | False release confidence | Persist partial/complete status and block closure unless required layers are satisfied. |
| Project-native reports are stale | Stale pass evidence | Require run ID, timestamp, source command, and current evidence refs. |
| Runner tools are treated as verdicts | Boundary erosion | Runner output is evidence only; Beacon QA owns verdict synthesis. |

### 7.1 风险缓解原则

所有风险缓解都必须保留 Beacon 主链边界：QA 可以阻断 release、要求恢复、要求补证据或要求 refreeze，但不能把 support evidence、runner output、hook evidence 或手工记录直接提升为 truth 或 release pass。

## 8. 验收标准

### AC-001 Full layer taxonomy

QA recognizes and validates the full layer taxonomy.

### AC-002 QA profiles and completeness

QA reports profile, required layers, executed layers, skipped layers, blocked layers, not-applicable layers, and partial/complete status.

### AC-003 Human-selected commands

Operator-selected commands are recorded as evidence inputs without overclaiming closure.

### AC-004 Non-browser full range

Non-browser features run or justify all applicable non-browser layers before closure.

### AC-005 Browser function UI UX

Browser features require real browser E2E evidence for function, UI, UX, compatibility, session, and state/data consistency.

### AC-006 Project-native E2E binding

Project-native scripts and reports bind to AC/test IDs.

### AC-007 Runner registry

The supported browser runner registry is visible and evidence-bound.

### AC-008 Non-acceptance evidence

Listing commands, placeholder evidence, and documentation-only pass notes fail closed.

### AC-009 Acceptance transaction evidence

QA acceptance transactions include run ID, source commands, runner/browser identity, accepted test IDs, evidence refs, and attribution.

### AC-010 Missing browser evidence blocker

Browser-required scenarios without valid browser evidence block QA/release.

### AC-011 Failure attribution route

Failure attribution routes deterministically to the correct next surface.

### AC-012 Release boundary

Release consumes formal QA closure only.

## 9. Success Metrics

- Browser-required features cannot pass without browser evidence.
- Complete QA runs expose required, executed, skipped, blocked, and not-applicable layers.
- Project-native E2E suites are bound to AC/test IDs.
- Release blockers distinguish product failure, truth drift, coverage gap, runner admission, and test script failure.
- Thin `verdict: passed` transactions are no longer enough for closure.
