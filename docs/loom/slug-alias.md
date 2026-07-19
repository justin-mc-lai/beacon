# Loom feature slug alias / display map

**Policy**: external brand is **Loom**; frozen package **identity** may remain `beacon-v2-*` under `docs/beacon/v2.0.0/features/` until a dedicated migration wave.

| Concept | Value |
|---------|--------|
| `canonical_slug` | Package id / path segment (stable) |
| `display_name` | Human Loom name |
| `aliases` | Host/user shorthand → resolves to canonical |

```bash
loom slug list --json
loom slug resolve loom-product-goal-orchestrator --json
```

Do **not** rewrite frozen truth slugs for brand-only reasons.
