---
slug: loom-public-surface-progressive-merge-v200
version: v2.0.0
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "Loom parity of beacon-public-surface-progressive-merge-v169 for dual-track QA/release"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-public-surface-progressive-merge-v200/truth.md
  tests: docs/beacon/v2.0.0/features/loom-public-surface-progressive-merge-v200/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-public-surface-progressive-merge-v200/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-public-surface-progressive-merge-v200/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
parity_of: docs/beacon/v1.6.9/features/beacon-public-surface-progressive-merge-v169/truth.md
ux_required: false
design_deferral: "No product UI for this platform lake"
---

# Requirement Truth: loom-public-surface-progressive-merge-v200

## 人话

Loom progressive 映射与 Beacon 对齐。

# truth

Parity implement of progressive merge with Beacon v1.6.9; brand Loom + Rust CLI only.

## Intent

Loom/v2.0.0 parity of `beacon-public-surface-progressive-merge-v169` — same UD/AC; brand Loom / Rust CLI track.

## Parity

`parity_of: docs/beacon/v1.6.9/features/beacon-public-surface-progressive-merge-v169/truth.md`

## Acceptance Criteria
| AC ID | Description |
|----|-------------|
| AC-PM-001 | progressive map JSON exists and lists loads for all 6 harness + goal |
| AC-PM-002 | progressive_skills_for_stage(plan|truth|…) returns aggregate shell + internals |
| AC-PM-003 | aggregate SKILL.md exists for beacon and loom 1+6 shells |
| AC-PM-004 | goal create payload includes self_heal pre/mid/post |
| AC-PM-005 | host_visible whitelist length 7 per brand |
| AC-PM-006 | examples surface-*-30s exist for goal+6+selfheal |
| AC-PM-007 | openai.yaml present on aggregate shells |
| AC-PM-008 | install scripts default whitelist (INSTALL_ALL=1 opt-out) |
| AC-PM-009 | capability non-regression: each harness progressive_loads non-empty |

## Non-goals

- Duplicate Python runtime implementation under a second code path
- Auto-release

