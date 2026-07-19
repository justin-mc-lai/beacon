# Loom (v2 evolution brand)

Production track remains **Beacon** (`beacon` CLI, `skills/beacon/*`, v1.6.x).

v2 evolution track is **Loom**:

| Surface | Location |
|---------|----------|
| CLI | `loom` (Python facade), `loom-v2` (Rust kernel) |
| Skills | `skills/loom/loom-*` (prefix mirror → content in `skills/beacon/*`) |
| State isolation | `.loom/worktrees` for isolated worktree mode |
| Requirements docs | still under `docs/beacon/v2.0.0/` during transition (UD-LOOM-008) |

Dual-install: installing Loom must **not** overwrite `beacon`.
