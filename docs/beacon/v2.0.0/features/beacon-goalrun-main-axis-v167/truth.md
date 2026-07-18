---
slug: beacon-goalrun-main-axis-v167
version: v2.0.0
status: frozen
revision_id: R1-v2-sync
language: zh
change_reason: "Sync UD-AXIS main-axis contract to v2.0.0 program; embed loom subagent+trace mounts"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/beacon-goalrun-main-axis-v167/truth.md
  tests: docs/beacon/v2.0.0/features/beacon-goalrun-main-axis-v167/tests.md
  tasks: docs/beacon/v2.0.0/features/beacon-goalrun-main-axis-v167/tasks.md
  evidence: docs/beacon/v2.0.0/features/beacon-goalrun-main-axis-v167/evidence.md
  shared_v167: docs/beacon/v1.6.7/features/beacon-goalrun-main-axis-v167/truth.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
ux_required: false
---

# Requirement Truth: GoalRun Main Axis on v2.0.0 (R1-v2-sync)

## Overview

**Same GoalRun main-axis policy as v1.6.7 (UD-AXIS-001..005).**  
v2 program embeds **Loom** lakes: brand dual-install, optional subagent fan-out, trace bundle.

Canonical generated artifact:

```text
docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/goalrun-main-axis.md
```

Shared state names with v1.6.7 (created…release_confirmed). Submachines (including **SubagentSession**, **AgentDriver**) cannot complete GoalRun.

## User Intent

v2/Loom change 后仍重生主轴；并行子代理与 trace 只是主轴旁路，不能变成独立插件完成定义。

## User Decisions

Inherits UD-AXIS-001..005 and Loom GO (brand dual-install, opt-in subagent, trace).

## v2-specific mounts

| Lake | Mount | Role |
|------|-------|------|
| beacon-v2-product-goal-orchestrator | main axis owner | facade |
| loom-brand-surface | L0 | dual install |
| loom-goal-optional-subagent | implement fan-out | opt-in spawn/merge |
| loom-goal-trace-bundle | longrun obs | agent_trace + CLI |
| beacon-v2-goal-durable-longrun | longrun | supervisor+driver |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-AXIS-V2-001 | `beacon goal axis generate -v v2.0.0 --program beacon-v2-product-goal-parallel-v200` succeeds (**Must**) |
| AC-AXIS-V2-002 | axis md lists all program lakes including loom-* (**Must**) |
| AC-AXIS-V2-003 | axis documents SubagentSession + agent_trace mounts (**Must**) |
| AC-AXIS-V2-004 | validate_main_axis pass for v2 program (**Must**) |
| AC-AXIS-V2-005 | Wave order includes Wave0 brand → Wave2 subagent → Wave3 trace (**Must**) |
| AC-AXIS-V2-006 | change trigger policy same CHANGE_TRIGGERS as v1.6.7 (**Must**) |

## CLI

```bash
beacon goal axis generate -v v2.0.0 --program beacon-v2-product-goal-parallel-v200
beacon goal axis validate -v v2.0.0 --program beacon-v2-product-goal-parallel-v200
```

## Non-Goals

- Implementing full subagent spawn in this lake (see loom-goal-optional-subagent)
- Replacing beacon package name
