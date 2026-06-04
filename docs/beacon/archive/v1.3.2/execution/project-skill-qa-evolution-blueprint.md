# Beacon v1.3.2 Project Skill / QA Evolution Blueprint

## Goal

Keep the `v1.3.2` delivery line aligned around three accepted workstreams:

```text
human minimal surface
→ implement execution modes
→ iterative browser QA
→ lighthouse single-file analysis
→ release closure
```

This blueprint exists so Beacon can evolve host-visible skill routing and QA evidence without leaking new command burden to humans.

---

## 1. Project-skill boundary in v1.3.2

`v1.3.2` keeps Beacon's public human surface intentionally small:

- primary lifecycle:
  - `prd`
  - `user-story`
  - `test-case`
  - `implement`
  - `qa`
  - `release`
- support surfaces:
  - `help`
  - `status`
  - `doctor`

Host-visible skills should mirror this same boundary:

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`

`v1.3.2` must not expand project-skill routing into a second public workflow tree.

## 2. QA evolution boundary in v1.3.2

QA evolution is now explicitly browser-first and iterative:

- `qa` is the second execution plane after `implement`
- browser execution families remain internal implementation detail
- every QA round must emit evidence, coverage, and next-step guidance
- repair handoff remains formal output, not an informal worker transcript

Allowed:

- materialize `ac-test-matrix`, `qa9-matrix`, and `story-scenario-map`
- execute browser evidence loops through host-native runners or bounded fallbacks
- write scorecards, AC closure, and repair handoff artifacts
- feed accepted findings back into help/release judgment

Not allowed:

- expose `qa-team` as a human-primary command surface
- bypass frozen `prd / user-story / test-case`
- treat external executor choice as user-facing product semantics

## 3. Lighthouse relationship

`lighthouse` is intentionally out of the main delivery loop.

It exists as a single-file analysis toolkit for:

- `system-architecture-map`
- `package-brief`
- `infra-chain-map`
- `feature-slice`

Its role in `v1.3.2` is to accelerate analysis without polluting the requirement and QA closure contracts.

## 4. Shared operator contract

The recommended operator route in `v1.3.2` is:

```text
freeze requirement package
→ implement dev-run / team-run
→ qa team-run
→ review quality
→ review accept
→ gate check release
```

`help` and `status` must keep routing humans back to this same path.

## 5. Artifact contract

### Human docs

- `docs/beacon/archive/v1.3.2/execution/project-skill-qa-evolution-blueprint.md`
- `docs/beacon/archive/v1.3.2/execution/implement-execution-modes-blueprint.md`
- `docs/beacon/archive/v1.3.2/execution/qa-iterative-browser-contract.md`
- `docs/beacon/archive/v1.3.2/execution/lighthouse-analysis-toolkit-blueprint.md`

### Machine/runtime artifacts

- `docs/beacon/archive/v1.3.2/.machine/qa/*.ac-test-matrix.json`
- `docs/beacon/archive/v1.3.2/.machine/qa/*.qa9-matrix.json`
- `docs/beacon/archive/v1.3.2/.machine/qa/*.story-scenario-map.json`
- `docs/beacon/archive/v1.3.2/.machine/execution/implementation-plan-*.json`
- `docs/beacon/archive/v1.3.2/.machine/execution/git-workflow-*.json`
- `.beacon/qa/features/<feature>/scorecard.json`
- `.beacon/qa/features/<feature>/ac-closure.json`

## 6. Source touchpoints

- `beacon/commands/implement.py`
- `beacon/commands/qa.py`
- `beacon/commands/help.py`
- `beacon/commands/lighthouse.py`
- `beacon/utils/help_support.py`
- `beacon/utils/implementation_plan.py`
- `beacon/utils/qa_feature.py`
- `beacon/utils/global_boundaries.py`
- `beacon/utils/lighthouse.py`

## 7. Freeze criteria for this workstream

This workstream is package-complete when:

1. humans can stay on the minimal six-command lifecycle
2. `implement` and `qa` operate as explicit paired execution planes
3. QA evidence closes against the frozen requirement package
4. `lighthouse` remains a bounded toolkit, not a parallel workflow
5. release/governance surfaces can read the resulting package without drift
