# PRD: QA Browser Memory And Skill Evolution Advisory Loop

**Feature**: `qa-browser-memory-and-skill-evolution-advisory-loop`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Overview

Beacon QA must learn from real browser runs without letting memory become truth. This feature introduces a governed browser QA site-memory loop and a SkillEvolver-style proposal loop. Both can improve future QA execution, but neither can satisfy QA closure, release readiness, or frozen requirement truth by itself.

中文边界说明：该能力属于 QA support intelligence，不属于新的 truth source、gate source 或 lifecycle stage。所有分层验收、恢复路由和风险缓解都必须保留 Beacon 主链的权威顺序。

The product meaning is:

```text
memory influences execution
current evidence proves acceptance
proposals suggest evolution
change/refreeze authorizes behavior changes
```

## Context

- Research anchor: `docs/beacon/archive/v1.4.10/research/embodiskill-skillevolver-qa-attribution-foundation.md`
- Brainstorm anchor: `docs/brainstorms/2026-05-25-beacon-brainstorm-design-browser-multi-round-memory-auto-reuse-and-skillevolver-style-self-evoluti.md`
- Existing QA foundations: `qa-evidence-attribution-layer`, `qa-evo-deep-and-skill-eval-kit-v1410`, `qa-evo-deep-evidence-bound-ac-aware-closure`, `qa-multi-layer-real-browser-e2e-acceptance`
- Runtime anchors: `beacon/commands/auto_test.py`, `beacon/utils/qa_feature.py`, `beacon/utils/qa_evo_deep.py`, `beacon/utils/qa_attribution.py`

## 1. 问题

Beacon can already write browser evidence packs and browser runner learning notes. It can also represent QA round memory as advisory influence. The missing product contract is safe reuse.

Without a frozen contract, Beacon may either:

- ignore useful prior browser evidence and repeat the same runner/admission mistakes; or
- over-trust history and accidentally let memory replace current QA evidence.

SkillEvolver-style improvement has a similar boundary risk. QA traces can reveal missing skill instructions, bad routing, weak runner admission, or missing eval cases. But if Beacon automatically patches skills or runtime behavior from traces, it can pollute the meta-protocol and break truth authority.

## 2. 目标

- AC-001: Browser QA site memory is captured from real current-run browser evidence with AC/test IDs, feature, route, host, browser, runner, auth/session mode, evidence refs, and outcome.
- AC-002: Browser memory admission rejects placeholder-only, listing-only, dry-run, documentation-only, stale, unscoped, or evidence-missing records.
- AC-003: Admitted browser memory can be automatically retrieved for later QA planning and runner admission.
- AC-004: Memory influence can guide runner selection, session bridge recommendation, selector/action hints, repeated failure detection, and browser task compilation.
- AC-005: Memory influence is recorded as advisory/runtime support evidence only and cannot satisfy QA pass, release pass, gate pass, or frozen truth.
- AC-006: Memory conflict, expiry, host/version/browser/auth mismatch, or protected-surface mismatch must downgrade or block reuse with machine-readable reason codes.
- AC-007: SkillEvolver-style trace analysis classifies observations as `Discovery`, `Optimization`, `SkillDefect`, or `ExecutionLapse`.
- AC-008: Skill evolution output is proposal-only and may include skill patch drafts, checklist updates, runner admission rules, or Skill Eval Kit cases, but must not mutate files automatically.
- AC-009: Each proposal must bind to trace refs, affected AC/test IDs, evidence refs, failure family, expected route, and risk.
- AC-010: Independent auditor checks proposals for authority bypass, support evidence promoted to verdict, single-project overfitting, missing evidence binding, silent bypass, and lifecycle-stage sprawl.
- AC-011: Accepted proposals must route through Beacon change/refreeze before implementation; rejected/deferred proposals remain support evidence only.
- AC-012: Release and QA scorecards may summarize memory/proposal support evidence, but only formal current-run QA closure can produce release readiness.

## 3. 设计原则

### 3.1 Truth Boundary

Memory and proposals are below frozen truth. They can influence how Beacon verifies; they cannot define what must be delivered.

边界规则：memory/proposal 只能进入 advisory influence，不得进入 PRD truth、user-story truth、test-case truth、QA verdict、release verdict 或 gate verdict。

### 3.2 Current Evidence Boundary

Historical browser memory can make QA faster and smarter, but every browser-required scenario still needs fresh executable evidence in the current QA run.

分层规则：browser memory 层、SkillEvolver proposal 层、formal QA evidence 层必须分开记录；只有 formal current-run QA evidence 层可以支撑验收闭环。

### 3.3 Proposal-Only Evolution

SkillEvolver-style logic may produce patch drafts and eval cases. Human acceptance plus Beacon change/refreeze is required before any mutation.

### 3.4 Auditability

Every reuse and proposal must explain source evidence, scope, influence, risk, and whether it was applied, downgraded, blocked, accepted, rejected, or deferred.

恢复规则：当 memory 过期、冲突、host/version/browser/auth 不匹配，或 proposal audit 失败时，Beacon 必须恢复到安全状态：降级为 advisory、阻断 reuse、推荐重新运行 QA，或 route 回 `beacon-change` / `beacon-test-case` / `beacon-qa`。

## 4. 范围

### In Scope

- Site-memory schemas and lifecycle: `discovered -> admitted -> reusable -> applied -> validated | expired | conflicted`.
- Memory keys for project, feature, route, target URL/host, browser, runner, auth/session mode, AC IDs, test IDs, and version.
- Memory influence records inside QA plan/status/scorecard.
- Runner/admission hints for Playwright, Playwright CLI, Playwright CDP, browser-use, agent-browser, attached browser, web-access, and Obscura CDP.
- Skill evolution proposal lifecycle: `observed -> attributed -> proposed -> audited -> accepted_for_change | rejected | deferred`.
- Auditor checks and Skill Eval Kit regression hooks.

### Out Of Scope

- Automatic code/skill/truth mutation.
- Treating memory as current-run evidence.
- Treating proposals as implementation evidence.
- Creating a new lifecycle stage.
- Replacing formal QA, release, gate, or requirement clarity verdicts.

## 5. 功能需求

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon must capture browser site-memory candidates from real browser evidence packs and current QA results. |
| FR-002 | AC-002 | Beacon must admit only scoped, fresh, evidence-bound memory and reject non-acceptance evidence. |
| FR-003 | AC-003 | Beacon must retrieve admitted memory for matching feature/host/route/browser/auth/session contexts. |
| FR-004 | AC-004 | Beacon must apply memory only as planning, runner, selector, session, or task-compilation influence. |
| FR-005 | AC-005 | Beacon must mark memory influence as advisory/runtime evidence with no truth, QA verdict, release verdict, or gate authority. |
| FR-006 | AC-006 | Beacon must detect stale/conflicting/mismatched memory and produce reason-coded downgrade or block outcomes. |
| FR-007 | AC-007 | Beacon must classify trace observations using EmbodiSkill-compatible reflection families. |
| FR-008 | AC-008 | Beacon must generate SkillEvolver-style proposals without mutating skills, code, or truth. |
| FR-009 | AC-009 | Beacon must bind proposals to traces, AC/test IDs, evidence refs, failure family, route, and risk. |
| FR-010 | AC-010 | Beacon must audit proposals before they can be recommended for change/refreeze. |
| FR-011 | AC-011 | Beacon must require accepted proposals to route through change/refreeze before implementation. |
| FR-012 | AC-012 | Beacon must keep memory/proposal evidence out of QA/release pass evidence unless fresh formal QA closure exists. |

## 6. Data, State, and Integration

### 6.1 Browser Memory Record

Required fields:

- `memory_id`
- `project_id`
- `feature`
- `version`
- `target_host`
- `route_or_url`
- `browser`
- `runner`
- `auth_mode`
- `session_ref`
- `ac_ids`
- `test_ids`
- `source_run_id`
- `evidence_refs`
- `outcome`
- `admission_status`
- `expires_at`
- `influence_allowed`
- `truth_authority: false`
- `verdict_authority: false`
- `release_pass_evidence: false`

### 6.2 Skill Evolution Proposal

Required fields:

- `proposal_id`
- `reflection_family`
- `failure_family`
- `trace_refs`
- `affected_ac_ids`
- `affected_test_ids`
- `evidence_refs`
- `target_surface`
- `patch_draft_refs`
- `eval_case_refs`
- `risk`
- `auditor_status`
- `recommended_route`
- `mutation_executed: false`

### 6.3 Integrations

- `beacon qa`
- `beacon auto-test create qa9`
- `beacon qa evo-deep`
- `beacon release check`
- `beacon change/refreeze`
- Skill Eval Kit
- Browser evidence pack and runner admission surfaces

## 7. 风险与缓解

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Historical memory is mistaken for current proof | False QA/release pass | Memory is advisory only; current evidence remains mandatory. |
| A stale site memory breaks browser QA | False failure or wasted run | TTL, host/version/browser/auth matching, conflict downgrade, and reason-coded blocks. |
| SkillEvolver overfits one project | Global Beacon behavior drift | Independent auditor checks for single-project overfitting and requires change/refreeze. |
| Proposal silently mutates skills | Meta-protocol contamination | Mutation is forbidden; accepted proposals route to change/refreeze. |
| Support evidence becomes verdict evidence | Truth boundary erosion | Scorecards expose support evidence separately from QA/release verdicts. |

### 7.1 风险缓解原则

Browser memory and SkillEvolver proposal outputs are support evidence. Boundary enforcement, layered QA accounting, recovery routing, and acceptance criteria must preserve the split between advisory influence and formal current-run evidence.

## 8. 验收标准

Acceptance criteria are AC-001 through AC-012 in section 2 and must be covered by executable test-case truth.

## 9. Success Metrics

- Browser QA reruns can show whether memory was retrieved, applied, downgraded, or blocked with evidence refs.
- No QA/release pass can be produced from memory or proposal evidence without fresh formal QA closure.
- Skill evolution proposals produce auditable change candidates without direct mutation.

## 10. Boundary

This feature adds governed support intelligence. It does not change Beacon's main lifecycle or authority model.
