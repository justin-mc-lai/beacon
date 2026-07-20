---
name: beacon-design
description: >
  beacon public harness surface for `design`.
  Progressive-loads internal skills without dropping capability.
  Dual-install; does not replace the other brand. Longrun only on goal.
metadata:
  version: "v1.6.9"
  brand: Beacon
  public_surface: true
  public_id: "design"
  harness: "design"
  progressive_map: skills/beacon/references/public-surface-progressive-map.v1.json
  progressive_loads: ["beacon-gen-design", "beacon-gen-design-init", "beacon-gen-design-system", "beacon-gen-design-explore", "beacon-gen-design-polish", "beacon-gen-prototype"]
  dual_install_with: loom-design
  longrun: false
---

# beacon-design

**公开面（Scheme A）**：`design`  
**渐进加载（能力不降级）**：`beacon-gen-design`, `beacon-gen-design-init`, `beacon-gen-design-system`, `beacon-gen-design-explore`, `beacon-gen-design-polish`, `beacon-gen-prototype`

本 skill **不**负责多小时 longrun；长程只用 `$beacon-goal` / `$loom-goal`。

## When to use

- 需要 **design** 场景的稳定入口（host-visible 白名单内）
- 细粒度旧名（如 gen-implement）仍可用作兼容，但默认安装不再暴露

## Progressive load

按 `public-surface-progressive-map.v1.json` 加载内部 skill；**禁止**为了合并而跳过原有 HARD GATE。

| Internal skill | Role |
|----------------|------|
| `beacon-gen-design` | progressive |
| `beacon-gen-design-init` | progressive |
| `beacon-gen-design-system` | progressive |
| `beacon-gen-design-explore` | progressive |
| `beacon-gen-design-polish` | progressive |
| `beacon-gen-prototype` | progressive |

## Boundary

- 不成为第二公共 goal 流水线
- harness HARD GATE 继承被加载的内部 skill
- gov/doctor 不由用户背名；goal 自愈带自动调度

## Examples

见 `skills/beacon/examples/surface-design-30s.md`（若存在）与 `goal-one-shot-30s.md`。

## Dual brand

| Beacon | Loom |
|--------|------|
| `beacon-design` | `loom-design` |

## Design philosophy checklist (P2)

Progressive load **must not** skip HARD GATE. Attach human checklist:

- `skills/beacon/references/design-philosophy-checklist.md`

Goal `build_stage_plan` also lists this under stage `references` when stage matches.

