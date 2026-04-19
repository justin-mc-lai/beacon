# Beacon v1.3.4 Project Skill / QA Evolution Blueprint

## Goal

Keep the Beacon human surface stable while `v1.3.4` adds a runtime projection and management board behind it.

```text
PRD / user-story / test-case
→ implement / qa / release
→ local truth
→ runtime projector
→ sqlite ledger
→ PocketBase board
```

This blueprint exists so the new runtime and board work stays subordinate to Beacon's requirement-first lifecycle.

## 1. Human entrypoints remain bounded

The public operator surface remains:

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
- `beacon-status`
- `beacon-doctor`

`v1.3.4` may enrich these surfaces with projection-aware summaries and diagnostics, but it must not turn the board into a new human workflow center.

## 2. Project skill routing contract

The board and doctor may recommend lifecycle-aware skills:

- requirement gap:
  - `beacon-prd`
  - `beacon-user-story`
  - `beacon-test-case`
- implementation active:
  - `beacon-implement`
- verification active:
  - `beacon-qa`
- release readiness:
  - `beacon-release`
- state drift or broken context:
  - `beacon-doctor`

The recommendation engine serves human clarity, not command proliferation.

## 3. QA and projection linkage

`v1.3.4` must preserve one requirement closure chain:

- PRD
- user-story
- test-case
- AC matrix
- implementation summary / review-spec
- QA status / gate report / release evidence

Runtime projection may summarize this chain, but it cannot replace any link in it.

## 4. Required machine bundle

Each formal feature line in `v1.3.4` should retain the minimal bundle:

- `prd/<feature>.md`
- `user-story/<feature>.md`
- `qa/test-cases/<feature>.md`
- `.machine/qa/<feature>.ac-test-matrix.json`

Recommended when available:

- `.machine/user-story/<feature>.json`
- `.machine/qa/<feature>.story-scenario-map.json`
- `.machine/change/<feature>.json`

## 5. Drift-closure rule

The board must not drift away from shipped requirement materials.

At minimum:

- board project cards reflect requirement-material completeness
- runtime lane state never changes requirement truth
- release closure can still run when projection is missing
- debug issues can be mapped into parallel PRDs instead of living only in `.beacon/debug`

## 6. Real-project validation rule

The evolution blueprint is not complete unless it works across:

- `beacon`
- `rolo`
- `slow_uni_bmtop`
- `shopxo_canada`

This requirement exists to stop Beacon from optimizing only for synthetic fixtures.

## 7. Doctor integration

`beacon doctor` is the architecture guard for this line. It must be able to:

- verify split runtime/docs context
- verify formal material completeness
- rebuild runtime ledger from local truth
- report PocketBase binary/admin availability
- keep gitignore and machine/runtime boundaries aligned

## 8. Freeze criteria

This blueprint is considered closed when:

1. release-line docs converge under `docs/beacon/v1.3.4/`
2. actual feature packages have minimal requirement/QA closure materials
3. release documents and change payloads exist for `v1.3.4`
4. `doctor verify-materials` passes for `v1.3.4`
5. `release check v1.3.4` passes against the repository state
