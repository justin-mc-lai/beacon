# Storage authority (v2)

## Layers

1. **Truth body** — `docs/beacon/<ver>/features/<slug>/{truth,tests,tasks,evidence}.md`
2. **Machine projection** — `.machine/`, optional JSON projections (non-authoritative alone)
3. **Runtime store** — global `~/.beacon/beacon.db` (spine/runs/gates); **not** truth body

## Rules

- Store must **not** hold truth markdown as supremacy source (TC-006/007).
- Per-project DB files forbidden for v2 authority (TC-008).
- TraceSpine is run authority; lifecycle_events / evidence manifests are projections.
- Dual-track: v1 and v2 must not dual-write unlabeled shared state.
