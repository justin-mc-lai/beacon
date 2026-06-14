# Beacon Rust Kernel (v2.0.0 P0)

Workspace at `packages/beacon-rs/` — six crates per frozen truth AC-022:

| Crate | P0 scope |
|-------|----------|
| `beacon-core` | Types, FSM, `AgentBackend`, `IterationResult` |
| `beacon-store` | Global SQLite schema v1, WAL, DAO skeletons, migration skeleton |
| `beacon-orchestrator` | Stub (P2+) |
| `beacon-gate` | Stub (P2+) |
| `beacon-cli` | Stub (P1+) |
| `beacon-python` | Stub (P4+) |

## Build & test

```bash
cd packages/beacon-rs
cargo test --workspace
```

## Authority

- Schema: frozen `truth.md` AC-067..AC-075 (integer id model)
- Single DB: `~/.beacon/beacon.db` (global authority)
- Full migration from legacy stores: P0 skeleton only (backup hook + `user_version`)
