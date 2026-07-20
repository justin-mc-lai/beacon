---
name: beacon-plan
description: >
  beacon public harness surface for `plan`.
  Progressive-loads internal skills without dropping capability.
  Dual-install; does not replace the other brand. Longrun only on goal.
metadata:
  version: "v1.6.9"
  brand: Beacon
  public_surface: true
  public_id: "plan"
  harness: "plan"
  progressive_map: skills/beacon/references/public-surface-progressive-map.v1.json
  progressive_loads: ["beacon-pln-program", "beacon-pln-program-auto", "beacon-pln-program-interactive", "beacon-pln-review", "beacon-pln-friction", "beacon-pln-brainstorm", "beacon-pln-source"]
  dual_install_with: loom-plan
  longrun: false
---

# beacon-plan

**公开面（Scheme A）**：`plan`  
**渐进加载（能力不降级）**：`beacon-pln-program`, `beacon-pln-program-auto`, `beacon-pln-program-interactive`, `beacon-pln-review`, `beacon-pln-friction`, `beacon-pln-brainstorm` …(+1)

本 skill **不**负责多小时 longrun；长程只用 `$beacon-goal` / `$loom-goal`。

## When to use

- 需要 **plan** 场景的稳定入口（host-visible 白名单内）
- 细粒度旧名（如 gen-implement）仍可用作兼容，但默认安装不再暴露

## Progressive load

按 `public-surface-progressive-map.v1.json` 加载内部 skill；**禁止**为了合并而跳过原有 HARD GATE。

| Internal skill | Role |
|----------------|------|
| `beacon-pln-program` | progressive |
| `beacon-pln-program-auto` | progressive |
| `beacon-pln-program-interactive` | progressive |
| `beacon-pln-review` | progressive |
| `beacon-pln-friction` | progressive |
| `beacon-pln-brainstorm` | progressive |
| `beacon-pln-source` | progressive |

## Boundary

- 不成为第二公共 goal 流水线
- harness HARD GATE 继承被加载的内部 skill
- gov/doctor 不由用户背名；goal 自愈带自动调度

## Examples

见 `skills/beacon/examples/surface-plan-30s.md`（若存在）与 `goal-one-shot-30s.md`。

## Dual brand

| Beacon | Loom |
|--------|------|
| `beacon-plan` | `loom-plan` |
