---
name: loom-qa
description: >
  loom public harness surface for `qa`.
  Progressive-loads internal skills without dropping capability.
  Dual-install; does not replace the other brand. Longrun only on goal.
metadata:
  version: "v1.6.9"
  brand: Loom
  public_surface: true
  public_id: "qa"
  harness: "qa"
  progressive_map: skills/beacon/references/public-surface-progressive-map.v1.json
  progressive_loads: ["loom-eval-qa", "loom-eval-qa-deep", "loom-eval-real-project", "loom-eval-agent"]
  dual_install_with: beacon-qa
  longrun: false
---

# loom-qa

**公开面（Scheme A）**：`qa`  
**渐进加载（能力不降级）**：`loom-eval-qa`, `loom-eval-qa-deep`, `loom-eval-real-project`, `loom-eval-agent`

本 skill **不**负责多小时 longrun；长程只用 `$beacon-goal` / `$loom-goal`。

## When to use

- 需要 **qa** 场景的稳定入口（host-visible 白名单内）
- 细粒度旧名（如 gen-implement）仍可用作兼容，但默认安装不再暴露

## Progressive load

按 `public-surface-progressive-map.v1.json` 加载内部 skill；**禁止**为了合并而跳过原有 HARD GATE。

| Internal skill | Role |
|----------------|------|
| `loom-eval-qa` | progressive |
| `loom-eval-qa-deep` | progressive |
| `loom-eval-real-project` | progressive |
| `loom-eval-agent` | progressive |

## Boundary

- 不成为第二公共 goal 流水线
- harness HARD GATE 继承被加载的内部 skill
- gov/doctor 不由用户背名；goal 自愈带自动调度

## Examples

见 `skills/beacon/examples/surface-qa-30s.md`（若存在）与 `goal-one-shot-30s.md`。

## Dual brand

| Beacon | Loom |
|--------|------|
| `beacon-qa` | `loom-qa` |
