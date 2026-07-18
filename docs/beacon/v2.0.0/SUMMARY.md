# Beacon v2.0.0 Summary

v2.0.0 opens the **Beacon Rust kernel rewrite** line and the **Product Goal + Domain Truth Chain** parallel program.

Human-facing lifecycle language remains v1.6.0 compatible:

```text
plan -> truth -> generate -> evaluate -> release
```

Package-authoritative truth:

```text
truth-map resolver -> features/<slug>/{truth,tests,tasks,evidence}.md
```

## Primary kernel feature

- `beacon-v2-rust-kernel-redesign` — Rust core; global `~/.beacon/beacon.db`; unified orchestrator; Operator Spine API; six public abilities

Source plan (support advisory):

- `docs/plans/beacon-v2-redesign.md`

## Program: Product Goal Parallel + Domain Truth Chain (v2)

- **program**: `docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/`
- **scope_mode**: `full_parity` with v1.6.7 Product Goal Domain Delivery
- **locked decisions (2026-07-17)**:
  - DEF-SE-001 **Option A** — domain truth chain lakes merge into this program
  - V2SE-006 **full inherit** v1.6.7 ui-state-matrix ship hard gate
  - DEF-SE-004 **reject** early default `BEACON_V2=1` until Wave W4

| Order | Lake | Role |
|-------|------|------|
| 1 | `beacon-v2-product-goal-orchestrator` | single entry + progressive load + subagent |
| 2 | `beacon-v2-main-star-satellite-pool` | main-star / satellite worktrees |
| 3 | `beacon-v2-domain-fsm-authority` | domain FSM freeze hard gate |
| 4 | `beacon-v2-golden-commerce-fixture-parity` | positive/negative clamps |
| 5 | `beacon-v2-domain-fsm-qa-gate` | QA legal/illegal walks |
| 6 | `beacon-v2-ui-state-matrix-ship-gate` | full ui-state-matrix ship gate |
| 7 | `beacon-v2-ralph-implement-boundary` | Ralph implement-only |
| 8 | `beacon-v2-goal-durable-longrun` | one-shot longrun AgentDriver + v1.6.7 durable supervisor parity |

## Engineering standards

- `docs/beacon/v2.0.0/execution/v2-software-engineering-standards.md` (SE-V2-00..13)
- Migration waves incl. W3: `docs/beacon/v2.0.0/execution/v1.6-to-v2-migration-roadmap.md`
- Parity fixture index: `docs/beacon/v2.0.0/fixtures/parity-v167/`

## Goal long-run (2026-07-18)

- **Lake**: `beacon-v2-goal-durable-longrun` (requirements frozen R1; implement pending)
- **User ask**: `$beacon-goal` one-shot uninterrupted long agent execution
- **Contract**: `--longrun` attaches AgentDriver auto-requeue; resume-pack digest on context full; 120s heartbeat; verifier + human release
- **Upstream**: v1.6.7 `beacon-goal-durable-supervisor-v167` (shipped)
- **Truth**: `docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md`

## Delivery readiness (2026-07-18)

| Layer | Status |
|-------|--------|
| Feature packages (8 product-goal lakes + rust kernel) | **truth frozen** |
| Python compat / parity contracts | **landed** (`tests/test_v200_product_goal_parity.py`, `beacon/utils/v2_product_goal_parity.py`) |
| `$beacon-goal` skill | **stable** (v1.6.7 runtime; same skill serves v2.0.0 docs line) |
| Durable/longrun behavior | **parity via v1.6.7 runtime** (AC-V2-DLR ↔ AC-DGS map) |
| Rust Operator Spine | **scaffold** `packages/beacon-rs` (W0–W1); not default runtime |
| `BEACON_V2=1` default | **forbidden** until W4 |
| Formal runtime promotion | **pending** human gate after W4 |

Goal run (longrun): see `.beacon/state/product-goal/` for active pgr when running delivery.

## Docs-line delivery GO (2026-07-18)

- **status**: package ready for human GO (`docs/beacon/v2.0.0/release/v2.0.0-docs-line-delivery-go.md`)
- **release check**: `blocked` / release_ready=False
- **pytest run_id**: `run-v200-20260718T065506`
- **runtime promotion**: still blocked until W4

