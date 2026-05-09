# Beacon v1.4.1 Boundaries

## In Scope

- `beacon-deep` as a human-facing support skill and toolkit surface
- `beacon deep run` as the preferred one-pass deep loop orchestrator
- deep analysis artifacts for state machine, test delta, risk register, loop trace, and closure brief
- high-risk trigger and low-risk skip reason semantics
- cross-stage routing from deep findings back into existing Beacon surfaces
- QA preflight test-delta generation and supplemental QA handoff
- release supplement evidence for deep closure, waiver, backlog, or skip decisions
- frozen `prd / user-story / test-case` requirement baseline for v1.4.1 planning

## Out of Scope

- adding `deep` as a new primary lifecycle stage
- replacing `prd / user-story / test-case / implement / qa / release`
- allowing deep artifacts to directly rewrite frozen truth
- allowing `.machine` or `.beacon` projections to become a second truth root
- promoting `v1.4.1` to current runtime release line or docs default line during planning
- executing implementation before the `implement` surface accepts the frozen handoff
- requiring prototype as a default stage for this non-UI support capability

## Explicit Constraints

- `docs/beacon/<version>/**/*.md` remains the canonical frozen truth root
- `implement` remains the only implementation entry
- `qa` remains the only acceptance entry
- `gate` remains the final blocking and completion judge
- `deep` may explain, analyze, route, and propose deltas, but may not override gate truth
- accepted requirement gaps must route through `change/refreeze`
- accepted test gaps must route through `test-case` or supplemental `qa`
- release risks must close through closure, waiver, explicit backlog, or skip evidence
- v1.4.1 remains a planning-only line until version governance intentionally promotes it
