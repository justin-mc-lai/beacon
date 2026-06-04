# Change: beacon-v1.4.5-governed-external-skill-sources-and-learning-composition

**Version**: `v1.4.5`  
**Status**: `planned`  
**Generated**: `2026-05-12`

## Why This Change Exists

Beacon currently excels at governing internal software-delivery surfaces, but it does not yet treat external open-source skills as first-class governed capability sources. That blocks Beacon from naturally guiding content, operations, and other non-software work by business outcome.

## Delta

- introduce governed external skill sources as first-class capability inputs
- formalize `core-skills/baoyu-skills` as the canonical sample source for this line
- allow users to declare business goals and result shapes without predeclaring the entire chain
- define learning writeback for successful, failed, and adopted compositions

## Freeze Intent

This change freezes the governance model for external capability sources and learning composition. It does not create an open public marketplace or bypass runtime compatibility controls.

## Traceability

- `docs/beacon/archive/v1.4.5/prd/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.md`
- `docs/beacon/archive/v1.4.5/user-story/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.md`
- `docs/beacon/archive/v1.4.5/qa/test-cases/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.md`
