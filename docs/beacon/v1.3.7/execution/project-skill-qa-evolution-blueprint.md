# Beacon v1.3.7 Project-Skill QA Evolution Blueprint

## Purpose

This blueprint explains how the `v1.3.7` runtime line keeps Beacon's packaged skills, frozen version materials, and QA evidence aligned after public runtime promotion to `v1.3.7`.

## Current Contract

- Human-facing routing still follows `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`.
- `beacon-implement`, `beacon-qa`, and `beacon-release` remain the only public delivery entrypoints.
- `beacon-brainstorm` is a built-in sidecar skill: host-visible, version-grounded, read-only against frozen truth, and excluded from the main lifecycle chain.

## Skill Layering

1. Beacon public host skills
   - `using-beacon`
   - `beacon-prd`
   - `beacon-user-story`
   - `beacon-test-case`
   - `beacon-implement`
   - `beacon-qa`
   - `beacon-release`
   - `beacon-help`
   - `beacon-status`
   - `beacon-doctor`
2. Built-in supplemental skills
   - `beacon-brainstorm`
   - bootstrap, lighthouse, memory/friction evolution, real-project validation
3. Project-local helpers
   - allowed only as execution support
   - cannot replace Beacon's delivery contract, version truth, or release gate

## QA Evolution Rules

- Feature-aware QA must resolve evidence against the feature's expected `matrix.qa9.json`, not just the latest global QA status file.
- QA writeback refreshes the active spec fingerprint and records canonical feature scorecards, closure artifacts, and team surface outputs.
- If evidence, matrix selection, or projection metadata drift, the correct path is repair plus rerun; manual cross-document reconciliation is not accepted as truth.

## Release Alignment

- `docs/beacon/v1.3.7/` is the canonical delivery tree for this line.
- Formal release closure requires summary, boundaries, source architecture, release document, and feature-level execution evidence to align.
- Version release readiness remains a governance surface above feature QA pass.
