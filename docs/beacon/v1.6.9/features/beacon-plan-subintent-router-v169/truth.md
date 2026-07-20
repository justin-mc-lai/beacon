---
slug: beacon-plan-subintent-router-v169
version: v1.6.9
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO: plan-subintent-router for review/brainstorm/source intent stability"
canonical_refs:
  truth: docs/beacon/v1.6.9/features/beacon-plan-subintent-router-v169/truth.md
  tests: docs/beacon/v1.6.9/features/beacon-plan-subintent-router-v169/tests.md
  tasks: docs/beacon/v1.6.9/features/beacon-plan-subintent-router-v169/tasks.md
  evidence: docs/beacon/v1.6.9/features/beacon-plan-subintent-router-v169/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
ux_required: false
design_deferral: "No product UI for this platform lake"
---

## 人话

plan 阶段按强意图路由到 review/brainstorm/source/program/friction，不写 truth。

# Requirement Truth: Plan Subintent Router

## Intent

plan 公开面下按强用户意图选择 primary progressive skill；全量 loads 不降级；不写 truth / 不实现 / 不裁决 QA·release。

## UD

| ID | Value |
|----|-------|
| UD-PSI-001 | primary_first by utterance tokens |
| UD-PSI-002 | default = program |
| UD-PSI-003 | source secondary includes review |
| UD-PSI-004 | writes_truth/may_implement/may_qa always false |
| UD-PSI-005 | beacon-plan/loom-plan description is trigger surface |
| UD-PSI-006 | Rust plan loads include full progressive set |

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

- New public harness skill; auto freeze; full LLM benchmark loop
