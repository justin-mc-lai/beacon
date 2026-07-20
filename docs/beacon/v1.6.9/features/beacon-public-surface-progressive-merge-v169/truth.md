---
slug: beacon-public-surface-progressive-merge-v169
version: v1.6.9
status: frozen
revision_id: R1
language: zh
change_reason: "User confirmed implement lake: progressive map + aggregate shells + self-heal + examples + whitelist"
shared_map: skills/beacon/references/public-surface-progressive-map.v1.json
parity_with: v2.0.0 loom public aggregates
---

# Requirement Truth: Progressive merge of 1+6 public surface

## Intent

合并对外 skill 面后：**能力渐进加载不降级**；gov 在 goal 流程自愈；用户不背框架 skill 名。

## AC

| ID | Description |
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
