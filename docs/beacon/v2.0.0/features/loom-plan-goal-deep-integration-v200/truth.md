---
slug: loom-plan-goal-deep-integration-v200
version: v2.0.0
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "Loom parity of beacon-plan-goal-deep-integration-v169 for dual-track QA/release"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-plan-goal-deep-integration-v200/truth.md
  tests: docs/beacon/v2.0.0/features/loom-plan-goal-deep-integration-v200/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-plan-goal-deep-integration-v200/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-plan-goal-deep-integration-v200/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
parity_of: docs/beacon/v1.6.9/features/beacon-plan-goal-deep-integration-v169/truth.md
ux_required: false
design_deferral: "No product UI for this platform lake"
---

# Requirement Truth: loom-plan-goal-deep-integration-v200

## 人话

Loom plan↔goal 深集成与 Beacon 同 AC。

# Loom parity: Plan ↔ Goal Deep Integration (P0–P2)

Same AC as v1.6.9. Brand Loom / Rust CLI track for public surface; Python runtime modules remain shared for goal facade until Rust ports land.

Python package must not own PATH name `loom` (only `loom-py` / Rust binary).

## Intent

Loom/v2.0.0 parity of `beacon-plan-goal-deep-integration-v169` — same UD/AC; brand Loom / Rust CLI track.

## Parity

`parity_of: docs/beacon/v1.6.9/features/beacon-plan-goal-deep-integration-v169/truth.md`

## Acceptance Criteria
| AC ID | Description |
|----|-------------|
| AC-PA-001 | artifact schema + deep_want + options + recommended_next |
| AC-PA-002 | plan_progressive_loads 附带 plan_artifact |
| AC-PA-003 | build_stage_plan hoist plan_artifact |
| AC-PA-004 | plan_to_truth_gate soft；missing/incomplete 不 hard-block |
| AC-PA-005 | create_goal_run 顶层 plan_artifact |
| AC-P1-001 | 无关键词 → host_subagent.gate_on false |
| AC-P1-002 | 「子代理」→ gate_on true，不自完成 goal |
| AC-P1-003 | tick plan→truth 写入 plan_to_truth_hint + stage_trace |
| AC-P2-001 | 两份 checklist 文件存在 |
| AC-P2-002 | design/truth stage references 含 checklist |
| AC-P2-003 | SKILL 提及 artifact / checklist |

## Non-goals

- Duplicate Python runtime implementation under a second code path
- Auto-release

