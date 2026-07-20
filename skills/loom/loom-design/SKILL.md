---
name: loom-design
description: >
  loom public harness surface for `design`.
  Progressive-loads internal skills without dropping capability.
  Dual-install; does not replace the other brand. Longrun only on goal.
metadata:
  version: "v1.6.9"
  brand: Loom
  public_surface: true
  public_id: "design"
  harness: "design"
  progressive_map: skills/beacon/references/public-surface-progressive-map.v1.json
  progressive_loads: ["loom-gen-design", "loom-gen-design-init", "loom-gen-design-system", "loom-gen-design-explore", "loom-gen-design-polish", "loom-gen-prototype"]
  dual_install_with: beacon-design
  longrun: false
---

# loom-design

**公开面（Scheme A）**：`design`  
**渐进加载（能力不降级）**：`loom-gen-design`, `loom-gen-design-init`, `loom-gen-design-system`, `loom-gen-design-explore`, `loom-gen-design-polish`, `loom-gen-prototype`

本 skill **不**负责多小时 longrun；长程只用 `$beacon-goal` / `$loom-goal`。

## When to use

- 需要 **design** 场景的稳定入口（host-visible 白名单内）
- 细粒度旧名（如 gen-implement）仍可用作兼容，但默认安装不再暴露

## Progressive load

按 `public-surface-progressive-map.v1.json` 加载内部 skill；**禁止**为了合并而跳过原有 HARD GATE。

| Internal skill | Role |
|----------------|------|
| `loom-gen-design` | progressive |
| `loom-gen-design-init` | progressive |
| `loom-gen-design-system` | progressive |
| `loom-gen-design-explore` | progressive |
| `loom-gen-design-polish` | progressive |
| `loom-gen-prototype` | progressive |

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
