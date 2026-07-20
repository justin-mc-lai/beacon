---
slug: loom-public-surface-1plus6-v200
version: v2.0.0
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "Loom parity of beacon-public-surface-1plus6-v169 for dual-track QA/release"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-public-surface-1plus6-v200/truth.md
  tests: docs/beacon/v2.0.0/features/loom-public-surface-1plus6-v200/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-public-surface-1plus6-v200/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-public-surface-1plus6-v200/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
parity_of: docs/beacon/v1.6.9/features/beacon-public-surface-1plus6-v169/truth.md
ux_required: false
design_deferral: "No product UI for this platform lake"
---

# Requirement Truth: loom-public-surface-1plus6-v200

## 人话

与 v1.6.9 **同一张** 1+6 同义表。Loom 只换品牌与 **Rust CLI**；不另发明第七公共 harness。

## Intent

Shared synonym table: `skills/beacon/references/public-surface-1plus6.md`.


Loom/v2.0.0 parity of `beacon-public-surface-1plus6-v169` — same UD/AC; brand Loom / Rust CLI track.

## Parity

`parity_of: docs/beacon/v1.6.9/features/beacon-public-surface-1plus6-v169/truth.md`

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-PS-001 | synonym table file exists and lists goal + exactly 6 harness rows |
| AC-PS-002 | Rust PUBLIC_ABILITIES length == 6 and maps 1:1 to table Rust column |
| AC-PS-003 | goal is documented as transversal; not a 7th PUBLIC_ABILITY |
| AC-PS-004 | v1.6.9 and v2.0.0 packages both freeze same table content (brand columns differ only by prefix) |
| AC-PS-005 | INTERNAL_DENYLIST entries are not listed as public harness ids |
| AC-PS-006 | default host-visible whitelist text present (goal+6 per brand) |
| AC-PS-007 | illegal: seventh public harness skill |
| AC-PS-008 | install docs/scripts may reference whitelist (implement phase) |

## Non-goals

- Duplicate Python runtime implementation under a second code path
- Auto-release

