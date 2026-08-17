---
slug: beacon-public-surface-progressive-merge-v169
version: v1.6.9
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User confirmed implement lake: progressive map + aggregate shells + self-heal + examples + whitelist"
canonical_refs:
  truth: docs/beacon/archive/v1.6.9/features/beacon-public-surface-progressive-merge-v169/truth.md
  tests: docs/beacon/archive/v1.6.9/features/beacon-public-surface-progressive-merge-v169/tests.md
  tasks: docs/beacon/archive/v1.6.9/features/beacon-public-surface-progressive-merge-v169/tasks.md
  evidence: docs/beacon/archive/v1.6.9/features/beacon-public-surface-progressive-merge-v169/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
ux_required: false
design_deferral: "No product UI for this platform lake"
---

## 人话

把 1+6 公开面映射到 progressive skill 加载，能力不降级。

# Requirement Truth: Progressive merge of 1+6 public surface

## Intent

合并对外 skill 面后：**能力渐进加载不降级**；gov 在 goal 流程自愈；用户不背框架 skill 名。

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

- Deleting internal fine-grained skill directories
- Making gov a 7th public harness
