---
slug: dual-track-leaf-admit-injectbundle-parity
version: v1.6.8
status: support_advisory
authority: beacon-goal
promotion_ref: "user:2026-07-20 dual-track parallel v1.6.8\\v2.0.0"
---

# Dual-track parity (v1.6.8 runtime ← shared with v2.0.0)

## Shared runtime (already shipped on main)

| Capability | Module | v1.6.8 | v2.0.0 |
|------------|--------|--------|--------|
| Leaf-only admit | `branch_ref_hierarchy` + `workspace_admission` | yes | yes (truth R2) |
| No main soft-fallback | `gate_workspace_admission_or_block` | yes | yes |
| InjectBundle longrun | `goal_steering` + `goal_agent_driver` | yes (runtime) | yes (truth R3) |
| Multi-version intent | `multi_version_intent` | yes | yes |

## Multi-version utterance

```text
v1.6.8\v2.0.0
v1.6.8/v2.0.0
双轨并行 v1.6.8 与 v2.0.0
```

```bash
beacon goal multi-version-plan "v1.6.8\\v2.0.0 双轨修复" --json
beacon goal run "双轨 v1.6.8\\v2.0.0 ..." --project . --version auto
```

## Default lakes

- v1.6.8: worktree progressive, longrun contract align, version fleet
- v2.0.0: loom-git-worktree hierarchy, durable-longrun steering, version fleet ops

## Non-goals

- Auto complete/release per track
- Default BEACON_V2=1
