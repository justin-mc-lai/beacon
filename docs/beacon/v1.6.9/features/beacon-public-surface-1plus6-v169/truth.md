---
slug: beacon-public-surface-1plus6-v169
version: v1.6.9
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User confirmed Scheme A; freeze 1+6 public surface synonym table for v1.6.9\v2.0.0 parity"
canonical_refs:
  truth: docs/beacon/v1.6.9/features/beacon-public-surface-1plus6-v169/truth.md
  tests: docs/beacon/v1.6.9/features/beacon-public-surface-1plus6-v169/tests.md
  tasks: docs/beacon/v1.6.9/features/beacon-public-surface-1plus6-v169/tasks.md
  evidence: docs/beacon/v1.6.9/features/beacon-public-surface-1plus6-v169/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.9/programs/beacon-public-surface-1plus6-v169/feature-graph.json
ux_required: false
design_deferral: "Public surface naming contract; no product UI"
shared_synonym_table: skills/beacon/references/public-surface-1plus6.md
parity_with: docs/beacon/v2.0.0/features/loom-public-surface-1plus6-v200/truth.md
---

# Requirement Truth: Public Surface 1+6 (v1.6.9 R1)

## 人话

对外只认 **1 个 goal（长程横切）+ 6 个主 harness**。  
v1.6.9（Beacon 生产）与 v2.0.0（Loom 进化）用**同一张同义表**；差别只有品牌与 CLI 实现（Python vs Rust）。

## User Intent

冻结 Scheme A 公开面，使 host-visible skill/命令与 Rust `PUBLIC_ABILITIES` 可对表验收。

## User Decisions（locked 2026-07-20）

| ID | Value |
|----|-------|
| UD-PS-001 | Scheme A：goal 横切 + 6 harness |
| UD-PS-002 | v1.6.9 与 v2.0.0 **同一**同义表 |
| UD-PS-003 | 仅品牌语义差：beacon/Python vs loom/Rust |
| UD-PS-004 | design 留在六能力内（对齐 Rust） |
| UD-PS-005 | 默认 host-visible = goal + 六能力（每品牌） |
| UD-PS-006 | goal **不计入**六 harness；禁止第七公共 harness skill |

## Canonical synonym table

**Single human source**: `skills/beacon/references/public-surface-1plus6.md`

### Goal (transversal)

| | Beacon | Loom |
|--|--------|------|
| Skill | `beacon-goal` | `loom-goal` |
| CLI | `beacon goal` (Python) | `loom` / `beacon-v2` goal (Rust) |
| Pipeline | plan → truth → design? → implement → qa → release | same |
| Longrun | only on goal | only on goal |

### Six harness

| Public id | Rust PUBLIC_ABILITIES | SUMMARY alias | Beacon | Loom |
|-----------|----------------------|---------------|--------|------|
| plan | loop | plan | beacon-plan | loom-plan |
| truth | truth | truth | beacon-truth | loom-truth |
| design | design | design | beacon-design | loom-design |
| implement | implement | generate | beacon-implement | loom-implement |
| qa | qa-evidence | evaluate | beacon-qa | loom-qa |
| release | release | release | beacon-release | loom-release |

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

## done_when

- table frozen in references + dual feature packages  
- contract tests green  
- v2 package parity declared  

## Non-Goals (this lake)

- physical deletion of internal skill directories  
- full rewrite of all SKILL.md bodies to aggregate names  
- changing production beacon Python engine behavior beyond naming contract  
