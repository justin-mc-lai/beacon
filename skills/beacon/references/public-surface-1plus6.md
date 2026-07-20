# Public surface 1+6 synonym table (locked)

**Scheme A**: `goal` is transversal long-run facade (not a 7th harness ability).  
**Harness public count**: exactly **6** (no 7th public skill).  
**Parity**: v1.6.9 (Beacon production line) and v2.0.0 (Loom evolution line) share this table; only **brand** names differ.

## Goal (transversal — not counted in the six)

| Role | Human verb | Beacon brand | Loom brand | CLI production | CLI evolution |
|------|------------|--------------|------------|----------------|---------------|
| Long-run facade | goal | `$beacon-goal` / `beacon-goal` | `$loom-goal` / `loom-goal` | `beacon goal` (Python) | `loom goal` / `beacon-v2 goal` (Rust) |

Default pipeline owned by goal:

```text
plan → truth(freeze) → design? → implement → qa → release
```

- longrun / supervise / driver attach **only** on goal  
- complete requires verifier; release remains human gate  
- design stage runs when `ux_required` / visual delivery

## Six public harness abilities

| # | Stable public id | Human / skill verb | Rust `PUBLIC_ABILITIES` | SUMMARY alias | Beacon skill id | Loom skill id |
|---|------------------|--------------------|-------------------------|---------------|-----------------|---------------|
| 1 | plan | plan | `loop` | plan | `beacon-plan` | `loom-plan` |
| 2 | truth | truth (freeze) | `truth` | truth | `beacon-truth` | `loom-truth` |
| 3 | design | design | `design` | design | `beacon-design` | `loom-design` |
| 4 | implement | implement | `implement` | generate | `beacon-implement` | `loom-implement` |
| 5 | qa | qa | `qa-evidence` | evaluate | `beacon-qa` | `loom-qa` |
| 6 | release | release | `release` | release | `beacon-release` | `loom-release` |

### Synonym rules (Must)

1. `plan` ≡ Rust `loop` ≡ human “plan / loop-goal orchestration surface” (not the long-run goal facade).  
2. `qa` ≡ Rust `qa-evidence` ≡ human “evaluate / qa”.  
3. `implement` ≡ SUMMARY `generate` (code generation stage).  
4. Host-visible **default install** may only include: goal + these six ids (per brand).  
5. Prefix mirrors (`beacon-gen-implement`, `loom-eval-qa-deep`, …) are **internal** unless allow-listed advanced profile.  
6. INTERNAL_DENYLIST remains non-public: doctor, router, hooks, metadata, debug, archive, status, gov, library, lighthouse.  
7. Brand is the only intentional difference: `beacon-*` + Python CLI vs `loom-*` + Rust CLI.

## Illegal

- Seventh public harness skill  
- Exposing full gov/* as first-class public skills by default  
- Default install of 26+ loom prefix shells  
- Claiming goal is a harness ability counted inside the six  
- Divergent synonym tables between v1.6.9 and v2.0.0  

## User decisions

| ID | Value |
|----|-------|
| UD-PS-001 | Scheme A: goal transversal + 6 harness |
| UD-PS-002 | v1.6.9 and v2.0.0 share one synonym table |
| UD-PS-003 | Brand-only differences (beacon/Python vs loom/Rust) |
| UD-PS-004 | design stays in the six (align Rust PUBLIC_ABILITIES) |
| UD-PS-005 | Default host-visible whitelist = 1 goal + 6 abilities per brand |

## Progressive load (capability non-regression)

Machine map: `skills/beacon/references/public-surface-progressive-map.v1.json`

- Public aggregate shells load first, then internal fine-grained skills.
- Goal attaches `self_heal` pre/mid/post (gov auto; users do not memorize gov skill names).
- Default install whitelist = host_visible_whitelist in the map (`INSTALL_ALL=1` to install everything).
