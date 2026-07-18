# Change: beacon-v2-goal-durable-longrun

- version: v2.0.0
- kind: new lake in program beacon-v2-product-goal-parallel-v200
- date: 2026-07-18
- intent: one-shot long-running agent for beacon-goal + inherit v1.6.7 durable supervisor

## Scope

- AgentDriver auto-requeue
- `--longrun` on same public entry
- parity with v1.6.7 durable supervisor
- budget halt, verifier, human release

## Downstream

freeze → implement (Rust spine + Python shim) → QA → release (W-gated with BEACON_V2 policy)
