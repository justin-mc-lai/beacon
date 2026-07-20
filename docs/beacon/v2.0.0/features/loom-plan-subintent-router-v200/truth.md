---
slug: loom-plan-subintent-router-v200
version: v2.0.0
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "Loom parity of beacon-plan-subintent-router-v169 for dual-track QA/release"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-plan-subintent-router-v200/truth.md
  tests: docs/beacon/v2.0.0/features/loom-plan-subintent-router-v200/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-plan-subintent-router-v200/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-plan-subintent-router-v200/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
parity_of: docs/beacon/v1.6.9/features/beacon-plan-subintent-router-v169/truth.md
ux_required: false
design_deferral: "No product UI for this platform lake"
---

# Requirement Truth: loom-plan-subintent-router-v200

## 人话

Loom plan 子意图路由与 Beacon 同 AC。

# Loom parity: Plan Subintent Router

Same AC as v1.6.9; brand Loom / Rust track.

## Intent

Loom/v2.0.0 parity of `beacon-plan-subintent-router-v169` — same UD/AC; brand Loom / Rust CLI track.

## Parity

`parity_of: docs/beacon/v1.6.9/features/beacon-plan-subintent-router-v169/truth.md`

## Acceptance Criteria
| AC ID | Description |
|----|-------------|
| AC-PSI-001 | review intent → pln-review |
| AC-PSI-002 | brainstorm → pln-brainstorm |
| AC-PSI-003 | source → pln-source |
| AC-PSI-004 | default → pln-program |
| AC-PSI-005 | primary first + full set retained |
| AC-PSI-006 | build_stage_plan attaches plan_subintent |
| AC-PSI-007 | three examples exist |
| AC-PSI-008 | Rust plan loads include review/brainstorm/source/friction |
| AC-PSI-009 | HARD GATE flags false |

## Non-goals

- Duplicate Python runtime implementation under a second code path
- Auto-release

