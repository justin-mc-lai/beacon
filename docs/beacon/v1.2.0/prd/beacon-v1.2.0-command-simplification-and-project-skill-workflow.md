# PRD: Beacon v1.2.0 主链简化、项目适配与需求锚定增强

**Feature**: Beacon v1.2.0 - Command Simplification and Project-Skill Workflow Enhancement  
**Version**: v1.2.0  
**Date**: 2026-04-08  
**Status**: Frozen  
**Owner**: Beacon Core Team

---

## 1. Product statement

### 1.1 What `v1.2.0` is

Beacon `v1.2.0` is the line that re-centers Beacon around its root chain:

```text
PRD
→ user-story
→ QA
→ implementation evidence
→ review / gate / release
```

It should make this chain:

- easier to operate
- easier to adapt per-project
- harder to drift

### 1.2 What `v1.2.0` is not

It is not:

- a generic command cleanup release
- a project-skill platform expansion release
- a prototype-centric release
- a memory or learning-plane expansion release

Those may appear as workstreams, but they are not the product center.

---

## 2. Problem statement

Beacon `v1.1.12` already has a strong mainline, but `v1.2.0` must address three forms of friction that weaken that mainline in practice:

### 2.1 Operator friction

- too many commands
- too much command-surface ambiguity
- difficulty learning the mainline path quickly

### 2.2 Project adaptation friction

- project skill workflows are powerful but still too manual
- project-local verify/delivery surfaces are not easy enough to discover and bind

### 2.3 Requirement drift

- prototype and other advanced surfaces can drift away from PRD/story truth
- there is not yet enough explicit `PRD/story/QA`-anchored traceability packaging

### 2.4 QA evolution friction

- current QA surfaces are strong, but story-native QA baselines are not yet packaged as reusable bundles
- Beacon lacks a clearly bounded `qa auto harness` that can iterate on QA policy surfaces without drifting into repo-wide self-modification
- there is not yet a formal contract connecting:
  - story-QA baseline bundles
  - coverage scorecards
  - keep/discard-driven QA policy evolution

---

## 3. Goals

### 3.1 Primary goal

Strengthen the `PRD → story → QA` chain as the stable center of Beacon.

### 3.2 Secondary goals

1. simplify the command surface so the mainline is more discoverable
2. improve project-skill workflow so projects can adopt the mainline more easily
3. strengthen prototype anchoring so UI/interaction outputs remain requirement-bound
4. establish a bounded `qa auto harness` that can improve story-native QA quality without breaking the root chain

### 3.3 Non-goals

1. moving project execution logic into Beacon core
2. expanding memory or learning-plane as separate product centers
3. adding more top-level commands unless they reduce mainline complexity
4. treating prototype/design governance as a peer center to `PRD/story/QA`
5. allowing self-iteration to mutate arbitrary product surfaces outside a bounded QA policy scope
6. promoting a generic codebase-wide `beacon discover` analysis platform into the v1.2.0 core frozen scope
7. requiring an explicit agent-platform rewrite or large-module decomposition as a prerequisite for closing this line

### 3.4 Architecture constraints imported from deep analysis

The architecture deep analysis adds three hard constraints to this line:

1. `v1.2.0` is a selective hardening line, not a greenfield reinvention
2. the four-layer architecture (`Requirement / Evidence / Adapter / Learning`) remains the governing system shape
3. agent-orchestration expansion, large-module refactors, and broader testing-platform work remain follow-on improvements unless they are directly required to protect the mainline contract

---

## 4. Mainline anchor contract

`v1.2.0` should explicitly formalize the following traceability chain:

### 4.1 Required traceability

- PRD requirement → story
- story → AC
- AC → test case
- story / AC → scenario families
- test execution → evidence
- evidence → review / gate / release

### 4.2 Required new contracts

`v1.2.0` should explicitly define:

1. `PRD-story-QA anchor contract`
2. `story-QA baseline bundle contract`
3. `coverage scorecard contract`
4. `qa auto harness contract`

These are the real foundational deliverables of the line.

---

## 5. Workstream A: command-surface simplification

This workstream exists only to reduce friction around the mainline.

### 5.1 Goal

- make core commands easier to discover
- make `help` and `status` stronger stage-aware routers
- hide low-frequency command surfaces by default

### 5.2 Requirements

1. mainline commands must stay stable and recognizable
2. command simplification must preserve backward compatibility or provide a clear migration path
3. the default command surface should prioritize the mainline
4. `help` must recommend the next mainline action from current project state

### 5.3 Success criteria

- a new user can identify the mainline within minutes
- low-frequency commands stop competing with core flow
- command routing becomes more explainable

### 5.4 Imported operator decisions from the simplification research

The April 8 command simplification research adds these concrete requirement decisions:

1. `ask` and `help` should become the primary smart-entry surfaces
2. default visible commands should privilege the mainline over advanced/labs surfaces
3. advanced/labs capability should be progressively disclosed rather than removed
4. compatibility aliases and staged deprecation should absorb future command consolidation

This workstream therefore needs a **command-surface blueprint**, not only a general simplification statement.

---

## 6. Workstream B: project-skill workflow strengthening

This workstream exists only to make the mainline easier to adapt to real projects.

### 6.1 Goal

- reduce friction when connecting project-local verify/delivery/debug surfaces

### 6.2 Requirements

1. support stronger project feature detection and project-skill discovery
2. support starter templates for common project types
3. preserve capability/evidence/stage boundaries
4. avoid moving project-private execution logic into Beacon core
5. expose `beacon skill discover` as the canonical discovery/binding entrypoint for this workstream
6. make discovery preview-first, explainable, and explicitly apply-driven
7. persist bounded discovery state/artifacts instead of returning only free-form analysis
8. ensure `help / profile / skill doctor` consume the same discovery result model

### 6.3 Success criteria

- more projects can bind into Beacon's verify/release flow with less manual work
- bindings remain explicit, bounded, and auditable

### 6.4 `skill discover` operator contract

Recommended surface:

```bash
beacon skill discover \
  --project-root . \
  --template <name> \
  --from-memory \
  --apply-recommended \
  --dry-run \
  --json
```

Required semantics:

1. detect project features statically
2. recommend templates / skills / profile bindings that still serve the mainline
3. preview config/result by default
4. apply only on explicit opt-in
5. explain every recommendation with evidence, reasons, and scores

### 6.5 Discovery artifact contract

Discovery should produce one bounded state artifact, for example:

```text
.beacon/state/skill-discovery/<project-or-feature>.json
```

The artifact should at minimum contain:

- `project_features`
- `recommended_templates`
- `recommended_skills`
- `recommendation_scores`
- `recommendation_reasons`
- `source_evidence`
- `config_diff`
- `applied` / `applied_at`

Any config changes should merge into `beacon.config.yaml` only through explicit apply.

### 6.6 Mainline linkage

This workstream is only complete if:

1. `help` can recommend `beacon skill discover --project-root .` when project-skill onboarding is the correct next step
2. `profile` can review or consume discovery-produced profile data without creating a second model
3. `skill doctor` can validate discovery-produced templates, registry entries, and capability/evidence contracts
4. the workstream has a formal execution blueprint and source-architecture map before freeze

### 6.7 Imported project-skill directives from deep analysis

The deeper project-skill research also adds:

- template-library candidates for common project types
- memory-aware recommendation inputs as a future bounded optimization layer
- stronger forward/reverse prototype-anchor validation expectations
- a future generic `beacon discover` concept that should stay outside the v1.2.0 core requirement center

The correct requirement decision is therefore:

> freeze `beacon skill discover` as the project-onboarding surface for this line, while keeping generic codebase-wide discover as a future advanced/labs direction.

---

## 7. Workstream C: prototype requirement anchoring

This workstream exists only to reduce requirement drift.

### 7.1 Goal

- make prototype outputs explicitly accountable to PRD/story truth

### 7.2 Requirements

1. support forward validation:
   - PRD/story → prototype
2. support reverse validation:
   - prototype → PRD/story
3. detect orphan requirements and orphan prototypes
4. generate UI module information templates when PRD/story are structurally incomplete

### 7.3 Success criteria

- prototype coverage can be described in requirement terms
- prototype review results can feed review/gate surfaces
- prototype cannot drift silently

---

## 8. Story-QA baseline bundle

This is the most important reusable artifact direction in `v1.2.0`.

### 8.1 Bundle contents

- `prd/<feature>.md`
- `user-story/<feature>.md`
- `.machine/user-story/<feature>.json`
- `qa/test-cases/<feature>.md`
- `.machine/qa/<feature>.ac-test-matrix.json`
- `.machine/qa/<feature>.story-scenario-map.json`
- `.machine/qa/<feature>.qa9-matrix.json`
- coverage / evidence scorecard

### 8.2 Required baseline dimensions

1. PRD-to-story traceability
2. story coverage
3. AC coverage
4. executable test coverage
5. scenario-family coverage
6. browser / non-browser coverage
7. evidence completeness
8. replayability completeness

### 8.3 Why it matters

Without a fixed baseline bundle:

- QA remains less reusable
- project adaptation remains less comparable
- self-iteration has no stable evaluation target

### 8.4 Relationship to `qa auto harness`

The story-QA baseline bundle is the required input to any future `qa auto harness`.

The harness must not invent its own benchmark target.
It must consume:

- PRD
- user story
- AC matrix
- scenario map
- QA9 matrix
- coverage / evidence scorecard

In other words:

```text
PRD/story/QA baseline bundle
→ qa auto harness
→ bounded policy experiment
→ keep/discard
→ updated QA policy / scorecard
```

Without the baseline bundle, the harness is undefined.

---

## 9. QA auto harness

This workstream is derived directly from the `awesome-design-md` and `autoagent` research line, but constrained by Beacon's root chain.

### 9.1 Product role

The `qa auto harness` is not a general self-improving agent platform.

It is a bounded evaluation-and-iteration loop whose only job is to improve how Beacon performs story-native QA against a fixed baseline bundle.

### 9.2 Allowed subject surfaces

The harness may optimize only bounded QA policy surfaces such as:

- story scenario expansion policy
- coverage threshold policy
- continue / stop-for-repair decision policy
- evidence sufficiency policy
- release-readiness scoring policy

### 9.3 Forbidden subject surfaces

The harness may not directly mutate:

- arbitrary Beacon core command behavior outside QA policy scope
- project-specific execution commands
- release verdict overrides
- repository-wide product surfaces unrelated to QA
- memory/knowledge systems as independent centers

### 9.4 Required benchmark inputs

Every QA auto harness experiment must be grounded in:

1. PRD clauses
2. user stories
3. acceptance criteria
4. scenario-family expectations
5. evidence expectations
6. false-complete risk signals

### 9.5 Required outputs

Every run must emit:

- changed QA policy surface
- affected stories / ACs
- coverage delta
- evidence closure delta
- false-complete delta
- keep/discard verdict

### 9.6 Success criteria

The harness is only successful if it improves one or more of the following without breaking traceability:

- PRD-to-story fidelity
- story coverage
- AC coverage
- scenario-family coverage
- evidence completeness
- false-complete reduction

### 9.7 Why this belongs in `v1.2.0`

`v1.2.0` is the right line to define the harness contract because:

- the root chain is already mature enough in `v1.1.12`
- the baseline bundle contract is being introduced here
- command simplification and project adaptation can make QA iteration easier to operate

But implementation of the harness should remain subordinate to the mainline-hardening sequence:

1. anchor contract
2. baseline bundle
3. coverage scorecard
4. bounded QA auto harness

---

## 10. Risks and mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| `v1.2.0` becomes too broad | High | Re-state the mainline anchor in every major document |
| command simplification breaks expert workflows | Medium | preserve compatibility + staged migration |
| project-skill workflow pulls project logic into core | High | enforce adapter boundary and capability contracts |
| prototype work overshadows mainline | Medium | keep prototype anchoring explicitly subordinate |
| advanced layers drift away from product center | High | require all advanced work to map back to `PRD/story/QA` |
| qa auto harness becomes a generic self-iteration platform | High | constrain to QA policy surfaces + baseline-bundle inputs only |

---

## 11. Recommended implementation order

### Phase 1

1. anchor contract
2. story-QA baseline bundle
3. coverage scorecard contract

### Phase 2

4. command simplification / help routing improvements
5. project-skill discovery and starter packs

### Phase 3

6. prototype requirement-anchor validation
7. bounded qa auto harness contract and execution prototype

This ordering matters.
It keeps the center stable before improving the edges.

---

## 12. Requirement freeze criteria

The v1.2.0 requirement package is only freeze-ready when all of the following are true:

1. summary / think / user-story / prd / qa docs agree on the mainline anchor
2. `skill discover` is documented as preview-first, explainable, and bounded
3. execution guidance exists for the project-skill workstream
4. source-architecture touchpoints are explicit
5. `.machine/user-story/<feature>.json` and `.machine/qa/*` can be generated for the frozen feature line
6. release notes can state what is frozen now versus what remains implementation work

## 13. Final statement

The right way to summarize `v1.2.0` is:

> Beacon `v1.2.0` is the line that hardens and clarifies the `PRD → user-story → QA` mainline, then reshapes command surface, project-skill adaptation, prototype validation, and bounded QA auto-iteration so that this chain becomes easier to run and harder to drift.
