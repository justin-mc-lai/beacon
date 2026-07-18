---
artifact_role: support_advisory_to_requirement_binding
version: v2.0.0
status: accepted
promotion_ref: planner-review:pln-review-20260717t073750z+user-decisions-20260717
parser_contract: beacon-execution-note-v1
---

# Beacon v2.0.0 Software Engineering Standards (SE-V2)

> Binding engineering law for the v2 architecture line.  
> Complements `docs/beacon/global-boundaries.md` and frozen feature packages under `docs/beacon/v2.0.0/features/`.  
> User-locked 2026-07-17: Option A domain chain merge; full ui-state-matrix inherit; reject early `BEACON_V2=1`.

## SE-V2-00 Normative Principles

1. **Completion definition outranks runtime shape** — v1/v2 dual-track may differ in implementation; completion semantics must match.
2. **Law is CLI/kernel, not prompt** — soft agent instructions are advisory; gates fail-closed.
3. **Single canonical source + one-way projection + transactional consistency**.
4. **Complexity absorbed by machines** — minimal human main surface.
5. **No fake delivery** — docs-only, zero-assertion, placeholder evidence, self-declared complete are illegal.

## SE-V2-01 Public Surface

| ID | Rule |
|----|------|
| SE-V2-01.1 | Sole user delivery entry: `beacon-goal` / `beacon goal run` (optional `beacon run` alias) |
| SE-V2-01.2 | `beacon-loop-goal` is support/internal discovery only |
| SE-V2-01.3 | Exactly six public abilities: `loop \| truth \| design \| implement \| qa-evidence \| release` |
| SE-V2-01.4 | Ralph/implement-loop must not write truth or emit QA/release verdicts |
| SE-V2-01.5 | Progressive skill load is default; full load is explicit debug only |

## SE-V2-02 Crate Layering

```text
beacon-cli → beacon-gate → beacon-orchestrator → beacon-store → beacon-core
```

| ID | Rule |
|----|------|
| SE-V2-02.1 | Unidirectional deps only; no cycles |
| SE-V2-02.2 | Core closure does not depend on Python/PyO3 for acceptance |
| SE-V2-02.3 | `beacon-core` is zero-IO (types, FSM, evidence primitives, reason codes) |
| SE-V2-02.4 | Authoritative writes only via store DAOs |
| SE-V2-02.5 | Module >500 LOC requires split or ADR exception |
| SE-V2-02.6 | Public errors: typed + stable `reason_code` |

## SE-V2-03 Storage Authority

| Layer | Authority | Forbidden |
|-------|-----------|-----------|
| L1 Truth | MD feature packages + `docs/beacon/<ver>/` | Editable requirement body in SQLite |
| L2 Runtime | `~/.beacon/beacon.db` global WAL | Per-project `beacon.db` as authority |
| L3 Blob | project `.beacon/` files | Default large BLOB columns |

Spine is DB-first; hash mismatch marks `stale`. v1 JSON runtime is migration/export only — no dual-write authority race.

## SE-V2-04 Dual FSM + Domain Truth Chain

| ID | Rule |
|----|------|
| SE-V2-04.1 | Lifecycle/Delivery FSM ≠ Domain FSM |
| SE-V2-04.2 | Domain-bearing features require Domain Model + Domain FSM + entity-precedence + ≥1 illegal transition slot |
| SE-V2-04.3 | Missing 04.2 → freeze/clarity **fail-closed** |
| SE-V2-04.4 | QA requires ≥1 legal walk + ≥1 illegal/precedence expected-fail; coverage on scorecard |
| SE-V2-04.5 | Golden positive+negative fixtures are platform clamps; negatives must fail freeze or QA |
| SE-V2-04.6 | Domain **content** belongs to target business; Beacon enforces schema+gate behavior only |
| SE-V2-04.7 | UX features: full **ui-state-matrix.v1** hard gate (inherits v1.6.7); design_primitives alone is insufficient |

## SE-V2-05 Gate / Evidence

| ID | Rule |
|----|------|
| SE-V2-05.1 | Hard gate results written to `gate_results` with reason_codes |
| SE-V2-05.2 | reason_codes string-compatible with v1 where claimed |
| SE-V2-05.3 | Evidence chain break → fail-closed |
| SE-V2-05.4 | Orchestrator must not self-set QA/release pass or Closed |
| SE-V2-05.5 | Release remains human gate |
| SE-V2-05.6 | Every stop/block emits `reason_code` + `resume_action` |
| SE-V2-05.7 | Precheck verification bundles are CLI-produced only |

## SE-V2-06 Operator Spine

| ID | Rule |
|----|------|
| SE-V2-06.1 | Primary runtime read surface: `spine show/list/artifacts/gate` + `projects *` |
| SE-V2-06.2 | No default operator workflow of hand-assembling multi-file JSON |
| SE-V2-06.3 | TraceSpine vs BranchContext/decision_packet mismatch fail-closed |
| SE-V2-06.4 | Long tasks support resume/stop/interrupt; crash/timeout recorded |

## SE-V2-07 Topology / Worktree

| ID | Rule |
|----|------|
| SE-V2-07.1 | `GitScopeGraph.v1` projects to `BranchContext.v1` |
| SE-V2-07.2 | Topology: single_repo \| monorepo \| multi_git_workspace; any blocked scope → aggregate blocked |
| SE-V2-07.3 | Missing `topology_gate_ref` cannot pass standard precheck |
| SE-V2-07.4 | Truth only on `truth_canonical`; satellites cannot write feature truth authority |
| SE-V2-07.5 | Satellite merges only to main-star integration |
| SE-V2-07.6 | Never infer target project from cwd alone |

## SE-V2-08 Dual-Track Runtime

| ID | Rule |
|----|------|
| SE-V2-08.1 | v1 and v2 are long-lived dual tracks |
| SE-V2-08.2 | No silent fallback v2→v1 Python or reverse |
| SE-V2-08.3 | Cross-track calls are explicit and audited |
| SE-V2-08.4 | **Reject default `BEACON_V2=1` before Wave W4 exit evidence** (DEF-SE-004 locked) |
| SE-V2-08.5 | Compatibility priority: truth package format, lifecycle language, reason_codes, completion definition |

## SE-V2-09 Proof Shape

Allowed closure evidence: contract tests, golden fixtures, behavior tests, migration tests, E2E samples.  
Forbidden: existence-only asserts, zero-assertion smoke, agent self-complete claims, single hard-coded fixture as multi-round proof.

## SE-V2-10 Migration Waves (W0–W5)

| Wave | Exit proof | Forbidden |
|------|------------|-----------|
| W0 Parse/Spine | Python/Rust fixture parity JSON + reason_code dictionary | Business capability claims |
| W1 Goal facade | PGO ACs + product-goal-state parity | Dual public entry regression |
| W2 Topology | BranchContext↔GitScopeGraph + topology_gate fail | Parallel worktrees without gate |
| W3 Domain truth chain | Domain freeze/QA/golden/ui-matrix/ralph contracts + negatives | Skip negative fixtures |
| W4 Runtime authority | DB authority + migration + no silent fallback | Half-default cutover |
| W5 Default/Perf | Bench gates + E2E | Perf masking semantic gaps |

## SE-V2-11 Program Admission

Before implement: program surfaces present; canonical refreeze committed; BranchContext; decision_packet; TraceSpine preconditions; design/ui-matrix when required.

## SE-V2-12 Change Hygiene

Requirement changes use truth/change/refreeze. Runtime cannot reverse-write truth. Version aggregate change docs are read models. Deferrals need explicit user decision before freezing a reduced scope. ADRs required for dependency/LOC/storage exceptions.

## SE-V2-13 Rust Coding Floor

1. Public API returns typed Result + reason_code  
2. State as enums + explicit transition tables  
3. No busy-wait; cancellable async boundaries  
4. Layered tests: unit / integration / contract  
5. Structured logs; no secrets  
6. Feature flags explicit; default switch only at W5 after W4  

## Locked User Decisions Binding This Document

| Decision | Value |
|----------|-------|
| DEF-SE-001 | Option A — domain truth chain lakes live under `beacon-v2-product-goal-parallel-v200` |
| V2SE-006 | Full inherit v1.6.7 ui-state-matrix hard gate for v2 ship |
| DEF-SE-004 | Reject early default `BEACON_V2=1` until W4 complete |
