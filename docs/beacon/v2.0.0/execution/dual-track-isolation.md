# Dual-track isolation (track_v1 / track_v2)

| Track | Brand | Paths (heuristic) | Public entry |
|-------|-------|-------------------|--------------|
| `track_v1` | Beacon production | `beacon/`, `skills/beacon/`, `docs/beacon/v1.6.*` | `$beacon-goal` / `beacon` |
| `track_v2` | Loom evolution | `packages/beacon-rs/`, `skills/loom/`, `loom/`, `docs/beacon/v2.*` | `$loom-goal` / `loom` / `beacon-v2` |

## Rules

1. Mixed v1+v2 paths in one change set without admission → `dual_track_mixed_source` (fail-closed).
2. v2 runtime must not silent-fallback to v1 (`cross_track_fallback_forbidden`).
3. W4 前禁止默认 `BEACON_V2=1` / loom 替换 beacon (`early_default_beacon_v2_forbidden`).
4. `beacon-python` crate is **archive-only** — not a v2 runtime fallback.

## CLI

```bash
beacon-v2 dual-track --path beacon/foo.py --path packages/beacon-rs/x --json
# exit 2 if mixed without --admit-mixed
```
