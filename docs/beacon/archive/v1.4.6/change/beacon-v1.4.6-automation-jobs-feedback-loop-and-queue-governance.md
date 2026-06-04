# Change: beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance

**Version**: `v1.4.6`  
**Status**: `planned`  
**Generated**: `2026-05-14`

## Why This Change Exists

Beacon already had a host-scheduled automation capability explanation and queue validation surface, but project-local scheduled QA still lacked a frozen feedback loop that could feed the next QA or gated implement window in a governed way.

## Delta

- freeze a project-local QA feedback ledger for automation/jobs
- expose public automation entrypoints for summarizing QA and updating queue state
- wire nightly QA and gated implement wrappers into the formal feedback loop
- expose a public scaffold bootstrap surface so projects can generate local automation assets
- freeze executor capability tiers so scaffold generation does not overclaim native runtime symmetry
- freeze one shared automation summary schema so wrappers and notification adapters share the same contract
- expose a human-facing automation toolkit support surface for project bootstrap and maintenance
- keep queue update rule-driven and bounded, not opportunistic

## Freeze Intent

This change strengthens project-local automation/jobs governance without creating a new lifecycle stage, without rewriting requirement truth from automation state, and without absorbing scheduler runtime into Beacon core.

## Traceability

- `docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- `docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- `docs/beacon/archive/v1.4.6/qa/test-cases/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
