# Research Closure: beacon-loop v1.6.1 Unified Long-Task Entry

- version: `v1.6.1`
- feature: `beacon-loop-goal-closed-loop-orchestrator`
- diagram_types: architecture, business_flow, state_machine
- state_axes: scope_axis, program_outer_fsm, per_lake_delivery_fsm
- user_decision: **confirmed** (2026-06-16)
- planner_review_id: `pln-review-20260616t023732z`

## User Decisions (locked for change)

| ID | Decision | Value |
|----|----------|-------|
| UD-001 | Long-task public entry | **Single** `beacon-loop goal "<utterance>"` (beacon-run thin delegate) |
| UD-002 | Sea utterance | Default **embedded program P0–P4** then per-lake delivery |
| UD-003 | Lake utterance | **Skip program**; direct per-lake Truth Freeze → generate → evaluate → release |
| UD-004 | `beacon plan start` | **Scaffold + plan_mode only**; long-run FSM owned by `goal` resume |
| UD-005 | Agent Eval | **Opt-in supplement** (`--eval-matrix` / `--eval-scorecard`); never gate qa/release |
| UD-006 | Change landing | **loop v161 R1** + **program plan R3** (tighten AC-PBP-016) |
| UD-007 | Sea/lake ambiguous | **One** multiple-choice question; record in `program-manifest` or `intent-contract` |

## Architecture

| Layer | Owner | Canonical write | Read-only |
|-------|-------|-----------------|-----------|
| Host | Cursor/Codex + skills | none | route hints |
| Long-task CLI | `beacon-loop` → `beacon-run` | run-dir state, phase artifacts | skills |
| Program outer FSM | `beacon-run --mode program` | `programs/<slug>/`, `program-run-state.json` | pln-program skills |
| Per-lake truth | `beacon-gen-truth` harness | `features/<slug>/` via freeze | program artifacts |
| Formal verdict | Beacon evaluator CLI | qa/release verdict files | loop runner |

**Integration principle:** loop is orchestration shell; program is planner harness **inside** sea path; eval is supplement **beside** qa phase.

## Business Flow

```text
utterance
  → intent_capture (verbatim)
  → scope_classify (湖 | 海) [UD-007 if low confidence]
  → [海] program P0–P4 (mandatory P2 pln-review at P2)
  → per_lake (topo order from feature-graph):
        truth (7-round harness + truth_freeze_gate)
        → generate (implement harness)
        → evaluate (beacon qa run; optional eval supplement)
        → release (beacon release check)
  → [海] program P6 when all lakes terminal
  → terminal_closed (evaluator authority only)
```

`beacon plan start` may run **before** `goal` to create `programs/<slug>/` and `plan_mode`; `goal` must **resume** from manifest without re-scaffolding.

## State Machine

### Scope axis

`utterance_received` → `scope_classified` → …

Illegal: `utterance_received` → `generate` without classify + freeze.

### Program outer (sea)

Align `ProgramPlanState` from `beacon-harness-program-plan-v161`: through `program_frozen` → `program_delivery`.

### Per-lake inner

`truth` → `generate` → `repair?` → `qa` → `release` (existing beacon-run; AC-068, AC-071 preserved).

### Eval supplement (opt-in)

Not a lifecycle stage. Artifacts: `run-dir/eval-matrix.json`, `eval-scorecard.json` with `formal_verdict_authority=false`.

## Decision Priority

1. User deferral without `accepted` → block freeze / program freeze
2. `truth_not_frozen` / TIG block → no generate
3. Formal qa/release evaluator → only terminal authority
4. Agent self-report / eval scorecard → never alone terminates loop
5. Planner artifacts → advisory until promote + change

## Parity Matrix (target vs current)

| Capability | v1.6.1 normative | Current code | After R11+R3 |
|------------|------------------|--------------|--------------|
| Unified `goal` entry | UD-001 | partial (lake only) | required |
| Program outer FSM | AC-PBP-016 | **missing** (false done) | required |
| P2 review in program path | AC-PBP-014 | skill-only | harness checkpoint |
| Per-lake nested delivery | program contract P5 | beacon-run `--beacon` | nested in program mode |
| Eval supplement | AC-AE-006 opt-in | not wired | `--eval-matrix` flags |
| R10 worktree/spine/stop-when | AC-069..071 | **done** | preserve |

## Deferral Ledger

| ID | Item | user_decision | route |
|----|------|---------------|-------|
| D-LOOP-161-001 | eval live runner default in loop | **rejected** | opt-in replay/matrix only |
| D-LOOP-161-002 | eval score gates qa | **rejected** | AC-AE-006 |
| D-LOOP-161-003 | AST full OSS inventory | **accepted defer** | post-v1.6.1 PB-001 |
| D-LOOP-161-004 | Unified goal + program | **accepted in-scope** | loop v161 R1 + program R3 |

## Proposed AC Themes (promoted — v1.6.1 + pre-main)

### loop orchestrator v161 R1

- AC-072..AC-075 → `docs/beacon/archive/v1.6.1/features/beacon-loop-goal-closed-loop-orchestrator-v161/truth.md` (revision R1)
- Upstream: `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md` **frozen R10**（不 reopen）

### program plan R3

- AC-PBP-016 (tightened), AC-PBP-027 (goal entry), AC-PBP-029, AC-PBP-030 → `docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md` (revision R3)

## Open Questions (resolved)

All brainstorm open questions closed by UD-001..UD-007.

## Promotion Notes

**Status (2026-06-15):** Route **A** complete — v1.6.1 + **pre-main**. `beacon-loop-goal-closed-loop-orchestrator-v161` **frozen R1** + `beacon-harness-program-plan-v161` **frozen R3** via `beacon freeze`（`refreeze-chain` blocked on legacy_cutover / revision_not_frozen for new package）。

Prior promote checklist:

1. `beacon-gen-change` on **`beacon-loop-goal-closed-loop-orchestrator-v161`** (R1) — v1.6.1 docs line
2. `beacon-gen-change` on program plan (R3)
3. Round 2 `beacon-pln-review` on **draft AC** before freeze
4. `tests.md` illegal transition cases for program+lake composite FSM

## Support Findings

### Brainstorm — 2026-06-16

- route: `beacon-gen-change`
- summary: One utterance → unified goal; sea embeds program; lake skips; eval supplement only

### Planner Review — pln-review-20260616t023732z

- execution_mode: `single_process_multi_reviewer` (fallback)
- synthesis recommended_route: `beacon-gen-change`
- P1: intent fidelity, state-machine → truth change required before implement
- human synthesis: User decisions remove product ambiguity; implementation still blocked until governed change + AC in tests.md
