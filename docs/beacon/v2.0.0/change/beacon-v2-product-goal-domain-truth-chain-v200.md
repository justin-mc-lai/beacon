# Change Intent: beacon-v2-product-goal-domain-truth-chain-v200

**Version**: `v2.0.0`  
**Program**: `beacon-v2-product-goal-parallel-v200`  
**Status**: accepted  
**Promotion ref**: `planner-review:pln-review-20260717t073750z+user-decisions-20260717`

## Why

Planner review confirmed v1.6.7→v2 migration scenario and SE standards draft.  
User locked three decisions and ordered `beacon-gen-change` to land contracts on v2.0.0.

## Locked decisions

1. **DEF-SE-001 Option A** — Domain 真值链 lakes 并入 product-goal program  
2. **V2SE-006** — 完整继承 v1.6.7 ui-state-matrix ship 硬门  
3. **DEF-SE-004** — 拒绝 W4 前默认 `BEACON_V2=1`

## Accepted change surfaces

### Support / execution (binding)

- `docs/beacon/v2.0.0/execution/v2-software-engineering-standards.md` (new)
- `docs/beacon/v2.0.0/execution/v1.6-to-v2-migration-roadmap.md` (Wave W3 section)
- `docs/beacon/v2.0.0/SUMMARY.md`
- `docs/beacon/v2.0.0/fixtures/parity-v167/README.md`

### Program

- `docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json`
- `docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/program-manifest.md`

### Feature packages

| Feature | Action |
|---------|--------|
| `beacon-v2-product-goal-orchestrator` | change R2→R3 |
| `beacon-v2-domain-fsm-authority` | new R1 |
| `beacon-v2-golden-commerce-fixture-parity` | new R1 |
| `beacon-v2-domain-fsm-qa-gate` | new R1 |
| `beacon-v2-ui-state-matrix-ship-gate` | new R1 |
| `beacon-v2-ralph-implement-boundary` | new R1 |
| `beacon-v2-main-star-satellite-pool` | unchanged contract (still phase 2) |

## Non-goals

- No implementation code in this change transaction
- No QA/release verdict
- No early BEACON_V2 default

## Downstream route

After freeze/clarity: `beacon-gen-implement` per topology_order (W0/W1 first on kernel+PGO, W3 lakes after schemas).
