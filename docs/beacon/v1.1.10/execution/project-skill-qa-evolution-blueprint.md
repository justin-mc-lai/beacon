# Beacon v1.1.10 Project Skill QA Evolution Blueprint

## Goal

Explain how v1.1.10 should compose three already-landed Beacon capability planes into one project-aware closure loop:

1. project-specific skill/profile/orchestration
2. browser QA session/auth persistence
3. implement to technical-architecture feedback

This blueprint exists so that `v1.1.10` does not stay as a generic QA precision line.

It should become a project-aware precision line.

---

## 1. Existing foundations to reuse

### v1.1.7

Already provides:

- skill registry
- project profile
- feature/profile binding
- verify orchestration
- required evidence gate

### v1.1.8

Already provides:

- technical implementation archive
- requirement rewrite input
- architecture blueprint / implementation archive surfaces

### v1.1.9

Already provides:

- feature-aware QA
- story-exhaustive scenario map
- browser evidence chain
- release scorecard
- keep/discard skeleton

v1.1.10 should compose these three layers instead of replacing any of them.

---

## 2. Target loop

```text
user-story / prd / test-case
→ feature bound to target project profile
→ verify orchestration through project skill workflow
→ browser QA session/auth persistence
→ story-exhaustive scenario execution
→ evidence pack + coverage_current
→ continue_decision
→ closure outcome + calibrated confidence
→ release/gate decision
→ QA defect or abstain routed to implement
→ technical implementation archive
→ requirement rewrite input / architecture feedback
→ benchmark truth / keep-discard / next iteration
```

---

## 3. Project-specific skill workflow layer

### What Beacon should read

- `beacon skill registry list`
- project `beacon.config.yaml`
- feature profile binding
- verify orchestration nodes
- required evidence / required cases

### Why this matters

For many real projects, “the QA path” is not:

```text
run a generic test
→ declare done
```

It is:

```text
run the project's own verify workflow
→ collect project-specific evidence
→ then judge closure/confidence
```

If Beacon ignores the target project’s real verify path, its QA precision layer will optimize the wrong thing.

---

## 4. Browser auth/session persistence layer

### Canonical surface

The QA session surface should be used as the project-aware browser auth memory:

- session manifest
- profile ref
- cookies ref
- storage-state ref
- scopes
- expiry

### Why this matters

Without persistent auth/session records:

- story-exhaustive browser QA repeats login/setup work
- delta rerun becomes noisy
- replay stability drops
- evidence chains fragment across runs

### Boundary

Persist:

- refs
- manifests
- scope metadata

Do not persist:

- uncontrolled raw credential dumps in release/docs artifacts

### Default runner expectation

For browser-driven QA, the intended default path is:

```text
compiled browser task
→ built-in browser-use
→ session-aware evidence pack
→ deterministic replay requirement
```

Project-specific runners may override this path, but the override must not remove:

- compiled task
- session continuity
- browser evidence pack
- replay boundary

---

## 5. QA defect to implement loop

When QA concludes:

- `implementation_reopened`
- `bug_filed`
- `needs_more_evidence`
- `needs_replay`

the next step should not be an informal note.

It should become a formal Beacon loop:

```text
qa finding
→ implement task
→ implementation summary
→ technical implementation archive
→ requirement rewrite input
```

This is how QA stops being a dead-end and becomes a delivery control surface.

---

## 6. Technical architecture feedback layer

The technical archive should feed two levels:

### Feature-local feedback

- changed files
- modules touched
- verification evidence
- known risks
- rollback notes

### Cross-feature architecture feedback

- repeated failure patterns
- repeated evidence gaps
- repeated session/auth instability
- repeated project workflow gaps

Those repeated patterns should be promoted into:

- architecture blueprint updates
- execution baseline uplift
- project-skill contract refinements

---

## 7. Suggested artifacts for this loop

| Artifact | Role |
| --- | --- |
| `beacon.config.yaml` | target project skill/profile/orchestration definition |
| `.machine/execution/<feature>.profile.json` | feature to profile binding |
| `.beacon/qa/sessions/<session_id>/manifest.json` | browser auth/session persistence |
| `.beacon/qa/features/<feature>/status.json` | scenario/feature QA status |
| `.beacon/qa/features/<feature>/scorecard.json` | feature precision summary |
| `.beacon/state/qa-audits/...` | sampled audit truth |
| `docs/beacon/<version>/execution/technical-implementation-<feature>.md` | feature-local technical archive |
| `docs/beacon/<version>/.machine/execution/technical-implementation-<feature>.json` | machine archive truth |
| `docs/beacon/<version>/.machine/execution/requirement-rewrite-input-<feature>.json` | next-round rewrite input |
| architecture blueprint feedback doc | repeated defect uplift surface |

---

## 8. Recommended operator workflow

1. bind the feature to the target project profile
2. save/reuse the browser QA session if auth is needed
3. run project-aware verify orchestration
4. run feature-aware/story-exhaustive QA
5. judge closure/confidence
6. if blocked or abstained, route to implement
7. inspect technical archive and writeback artifacts
8. update architecture feedback and next experiment set
9. if a severe blocker stops the round, repair it first and then use
   `beacon help --project-root <root> --version <version> --feature "<feature>"`
   to resume the next QA round
10. before the resumed round claims better coverage, supplement missing test cases / scenario families / replay obligations

---

## 9. Guardrails

1. do not bypass project evidence gates because a skill “seems to have run”
2. do not leak raw auth material into docs/release artifacts
3. do not stop at QA findings without implement/archive follow-up
4. do not evolve project workflows without keep/discard evidence
5. do not continue a QA round after severe blockers have made downstream evidence untrustworthy
6. do not claim better coverage if the new round did not backfill previously missing test cases

---

## 10. Final statement

`v1.1.10` becomes materially stronger when it is read as:

```text
project-aware QA precision closure
```

not merely:

```text
generic confidence scoring for tests
```
