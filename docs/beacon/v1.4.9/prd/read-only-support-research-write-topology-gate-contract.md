# PRD: Read-Only Support Research Write Topology Gate Contract

**Feature**: `read-only-support-research-write-topology-gate-contract`  
**Version**: `v1.4.9`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## Overview

- Research: `docs/beacon/v1.4.9/research/read-only-support-research-write-topology-gate-contract.md`
- Source architecture: `docs/beacon/v1.4.9/source-architecture/read-only-support-research-write-topology-gate-contract.md`
- Prior material effect contract: `docs/beacon/v1.4.8/research/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`

## 1. Problem

Read-only support skills are correctly classified as advisory, but their persisted research output is still not strictly governed. This leaves room for duplicate brainstorm files, sidecar analysis documents, and support receipts that are hard to promote or supersede during requirement clarification.

Beacon needs a single feature-level research write topology for ordinary support reviews, plus explicit exceptions for `beacon-deep` and `beacon-learn`.

## 2. Goals

- AC-001: Ordinary read-only support reviews write to `docs/beacon/<version>/research/<feature>.md`.
- AC-002: `beacon-deep` writes detailed artifacts to `docs/beacon/<version>/deep/<feature>/`, while research stores only an index summary.
- AC-003: `beacon-learn` writes learning audit to `docs/beacon/<version>/learning/<feature>.md` or transaction, while research stores only learning influence summary.
- AC-004: `docs/brainstorms/` fallback is disallowed for explicit Beacon version+feature support analysis.
- AC-005: Repeated clarification in one version updates rounds or supersedes sections instead of creating duplicate sibling files.
- AC-006: Cross-version clarification creates a new version research document with lineage to prior version decisions.
- AC-007: Gate / requirement clarity fails closed when support write topology is violated.
- AC-008: Support output persistence is blocked until the topology gate selects the write target from `version`, `feature`, and support surface class; no legacy fallback target may be used.

## 3. Design Principles

### 3.1 One feature research document

For version-bound, feature-bound ordinary support analysis, `research/<feature>.md` is the human-readable convergence point.

### 3.2 Deep remains evidence-rich and separate

`beacon-deep` can produce multiple routeable evidence artifacts. Those artifacts stay in `deep/<feature>/`; research only indexes their status and route impact.

### 3.3 Learning remains advisory and separate

`beacon-learn` governs memory influence. It must not pollute research truth with raw memory candidates. Research only records influence summary and audit refs.

### 3.4 No fallback for governed support writes

`docs/brainstorms/` is scratch or external-only once `--version` and `--feature` bind the work to Beacon requirement materials.

### 3.5 Gate catches topology drift

Invalid support output placement is a material closure problem. It must surface as fail-closed diagnostics, not as silent documentation drift.

## Scope

### In Scope

- Ordinary support section upsert into `research/<feature>.md`.
- Dedicated deep artifact path and research index.
- Dedicated learning audit / transaction path and research influence summary.
- Round/supersession rules for repeated clarification.
- Cross-version lineage rules.
- Gate diagnostics for invalid support write topology.

### Out Of Scope

- Support skills directly editing PRD, user-story, test-case, freeze state, QA verdict, or release verdict.
- Rewriting historical `docs/brainstorms/` artifacts.
- Making `beacon-deep` or `beacon-learn` lifecycle stages.
- Running implementation, QA, or release.

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Ordinary support skills must upsert their owned section under `## Support Findings` in `docs/beacon/<version>/research/<feature>.md`. |
| FR-002 | AC-002 | `beacon-deep` must keep detailed artifacts under `docs/beacon/<version>/deep/<feature>/` and `.machine/deep/<feature>/`; research may only store a `Deep Summary` index. |
| FR-003 | AC-003 | `beacon-learn` must keep learning audit data under `docs/beacon/<version>/learning/<feature>.md` or support transaction; research may only store `Learning Influence Summary`. |
| FR-004 | AC-004 | Explicit version+feature support analysis must not default to `docs/brainstorms/`; doing so is a topology violation. |
| FR-005 | AC-005 | Repeated same-version support clarification must append a round or supersede the owned section in the same research file. |
| FR-006 | AC-006 | Cross-version clarification must create a new version research file with `previous_research`, `carried_forward`, and `superseded` lineage. |
| FR-007 | AC-007 | Gate and requirement clarity must report invalid support write topology with source skill, expected path, actual path, and repair route. |
| FR-008 | AC-008 | Support writeback must run a pre-write topology gate; if `version`, `feature`, or support surface class cannot be proven, Beacon must fail closed before writing. |

## 6. Diagram Truth Layer

### 6.1 Diagram Types

- `branch-flow`
- `state-machine`
- `decision-priority`

### 6.2 State Axes

- `support_surface_class`
- `write_target`
- `material_effect`
- `adoption_status`
- `version_lineage`

### 6.3 Propagation Contract

Support write topology must stay explicit through requirement clarity, implementation planning, QA, and release evidence. A misplaced support artifact cannot unlock downstream closure.

## 7. Freeze Deliverables

- `docs/beacon/v1.4.9/research/read-only-support-research-write-topology-gate-contract.md`
- `docs/beacon/v1.4.9/source-architecture/read-only-support-research-write-topology-gate-contract.md`
- `docs/beacon/v1.4.9/change/read-only-support-research-write-topology-gate-contract.md`
- `docs/beacon/v1.4.9/prd/read-only-support-research-write-topology-gate-contract.md`
- `docs/beacon/v1.4.9/user-story/read-only-support-research-write-topology-gate-contract.md`
- `docs/beacon/v1.4.9/qa/test-cases/read-only-support-research-write-topology-gate-contract.md`

## 8. Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Research file becomes too large | Human scanning gets harder | Ordinary support sections store summaries, not transcripts. |
| Deep artifacts are hidden from research | Important findings get missed | Research must include `Deep Summary` index and route/adoption status. |
| Learning appears to override truth | Requirement drift | Research only stores influence summary and policy that frozen truth wins. |
| Existing brainstorm fallback survives | Duplicate clarification material | Gate flags version+feature writes to `docs/brainstorms/` as invalid. |

## 9. Success Metrics

- Explicit version+feature brainstorm no longer writes default output to `docs/brainstorms/`.
- Ordinary support review output is discoverable from one feature research document.
- Deep artifacts remain complete and indexed from research.
- Learning audit remains separate and indexed from research.
- Gate diagnostics identify invalid topology before freeze / QA / release can claim closure.
- No read-only support surface can persist output through an implicit legacy fallback when the topology gate cannot determine a governed target.
