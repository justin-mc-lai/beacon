# Beacon v1.1.10 Architecture Blueprint

## Intent

`v1.1.10` is the release line that closes three parallel gaps together:

1. QA precision and confidence-aware closure
2. source-architecture anti-drift documentation
3. prototype-to-frontend route closure

It is not a brand-new workflow kernel.

It is the point where the landed `v1.1.9` closure loop becomes a stricter, more auditable delivery system.

## System Shape

The effective architecture is:

```text
requirements
→ machine materials
→ implementation / QA runtime
→ closure judgement
→ release / gate decision
→ learning feedback
```

That architecture now has three explicit control surfaces:

- `execution/qa-confidence-data-contract.md`
- `execution/project-skill-qa-evolution-blueprint.md`
- `execution/prototype-frontend-route-closure-blueprint.md`

And one source-facing sync surface:

- `../source-architecture/index.md`

## Runtime Layers

### Requirement and package layers

- `SUMMARY.md`
- `user-story/`
- `prd/`
- `qa/test-cases/`
- `execution/`
- `source-architecture/`
- `release/`

### Machine layers

- `.machine/user-story/`
- `.machine/qa/`
- `.machine/execution/`

### Runtime layers

- `.beacon/qa/`
- `.beacon/state/`
- `.beacon/evidence/`
- `.beacon/gate-report.json`
- `.beacon/evidence-manifest.json`

## What Changed Relative To v1.1.9

Compared with `v1.1.9`, the architectural delta is:

- QA can emit `closure_outcome` instead of status-only conclusions
- calibrated confidence becomes part of release truth
- low-confidence outcomes have a first-class abstain path
- project-specific verify workflows can participate in the QA mainline
- source architecture is now part of formal materials and anti-drift checks
- prototype route closure is treated as a blocking contract instead of a soft note

## Reading Order

1. `../SUMMARY.md`
2. `./boundaries.md`
3. `./qa-confidence-data-contract.md`
4. `./project-skill-qa-evolution-blueprint.md`
5. `./prototype-frontend-route-closure-blueprint.md`
6. `../source-architecture/index.md`
7. `./qa-confidence-implementation-phasing.md`
8. `../release/v1.1.10.md`

## Directive

Do not describe `v1.1.10` as only a docs line.

It is a delivery line only if:

- runtime QA emits precision-aware outputs
- release/gate consume those outputs
- source architecture remains synced
- prototype route closure remains auditable
