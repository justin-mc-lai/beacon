# Beacon v1.1.12 Architecture Blueprint

## Intent

`v1.1.12` 将 Beacon Prototype 从“结构 truthful reference pack”升级为“设计也被正式治理、执行边界也被正式治理的 reference pack”。

它不是新的 renderer。

它是对 prototype generation/review loop、project execution routing、learning-plane boundary 的治理升级。

## System Shape

目标系统形态：

```text
version truth
→ project mode
→ execution surface binding
→ bounded learning surfaces
→ story / prd / research
→ bounded autoresearch divergence
→ design brief compiler
→ design-system contract compiler
→ prototype plan / page specs
→ reference-pack-v2 renderer
→ web guideline audit
→ design review outcome
→ implement branch preflight
→ keep/discard-backed next iteration
→ freeze / gate
```

## Primary layers

### Product boundary layers

1. Requirement kernel
2. Delivery evidence kernel
3. Project execution adapters
4. Learning plane

Directive:

- Layer 3 stays external/project-specific
- Layer 4 may optimize policy/contract/evaluation surfaces only
- Layer 1 and Layer 2 remain Beacon core truth surfaces

### Requirement layers

- `SUMMARY.md`
- `research/`
- `user-story/`
- `prd/`
- `qa/test-cases/`
- `execution/`
- `release/`

### Machine / runtime design-governance layers

- `design-brief.json`
- `design-system-contract.json`
- `web-guideline-review.json`
- `prototype-review.json`
- keep/discard ledger refs

## Architectural delta relative to v1.1.11

- adds design brief as compiled truth
- adds design-system contract as renderer input
- adds formal web-guideline audit as review/gate input
- adds bounded design finding writeback to next iteration
- adds implement-time exact version branch enforcement before runner execution
- adds single-source version truth as a first-class delivery precondition
- adds profile-aware execution routing before native fallback
- adds typed learning surfaces for design / qa / contract policy optimization
- adds takeover baseline gating before implementation expansion

## Directive

Do not describe `v1.1.12` as “make the prototype prettier”.
Do not describe it as “Beacon should become a universal shell orchestrator” either.

It is only successful if Beacon can truthfully answer:

- what version line is current, planning, and runtime-real
- what project mode and execution surface were selected
- what design direction was compiled
- what shared visual/token rules were enforced
- what formal web-interface findings remain
- what next iteration should change and why
- whether implement execution started on `beacon/<version>` instead of an arbitrary branch
