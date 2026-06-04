# Beacon v1.3.5 Project Skill / QA Evolution Blueprint

## Goal

Freeze a deterministic requirement chain for prototype before implementation starts.

```text
prd -> user-story -> test-case
-> prototype (wireframe freeze)
-> implement -> qa -> release
```

`v1.3.5` focuses on the prototype-stage closure and drift control, not final UI delivery.

## 1. Public skill surface contract

Human-facing lifecycle remains bounded:

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-prototype`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
- `beacon-status`
- `beacon-doctor`

`beacon-prototype` is the only public prototype stage entrypoint.

## 2. Prototype closure contract

Prototype output must be requirement-driven and freeze-ready:

- `wireframe-summary.md`
- `navigation-map.md/json`
- `state-flow-map.md/json`
- `component-catalog.md/json`
- `pages/*.md`
- `freeze.json`
- `prototype-review.json`

No HTML high-fidelity output is considered required or authoritative in this line.

## 3. Requirement traceability contract

Every frozen page/state/component artifact must map back to:

- PRD promised surface
- user-story AC
- test-case scenario

If mapping is missing, prototype review/freeze must fail.

## 4. QA linkage contract

`test-case` remains the executable acceptance bridge and must stay synchronized with the frozen user-story AC set.

Mandatory outputs:

- human-readable test case markdown
- `.machine/qa/*.ac-test-matrix.json`
- `.machine/qa/*.qa9-matrix.json`
- `.machine/qa/*.story-scenario-map.json`

## 5. Multi-sink consistency contract

Prototype/runtime artifacts follow canonical-first projection:

- canonical envelope as single source
- human/machine/sqlite derived projections
- shared transaction metadata

Any sink mismatch is a release blocker for this feature line.

## 6. Doctor responsibilities in this line

`beacon doctor` must be able to verify:

- formal material completeness for `v1.3.5`
- feature slug consistency across PRD/story/test-case/machine artifacts
- drift indicators for multi-sink projection metadata
- context/version alignment before implementation and QA

## 7. Freeze criteria

`v1.3.5` requirement closure is considered frozen when:

1. strict material verification passes
2. one canonical feature slug is used consistently
3. PRD/user-story/test-case AC mapping is complete
4. prototype-stage boundaries are documented and auditable
5. release checklist exists and references this closure state
