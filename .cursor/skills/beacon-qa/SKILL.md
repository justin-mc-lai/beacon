---
name: beacon-qa
description: >
  beacon public harness surface for `qa`.
  Progressive-loads internal skills without dropping capability.
  Dual-install; does not replace the other brand. Longrun only on goal.
metadata:
  version: "v1.6.9"
  brand: Beacon
  public_surface: true
  public_id: "qa"
  harness: "qa"
  progressive_map: skills/beacon/references/public-surface-progressive-map.v1.json
  progressive_loads: ["beacon-eval-qa", "beacon-eval-qa-deep", "beacon-eval-real-project", "beacon-eval-agent"]
  dual_install_with: loom-qa
  longrun: false
---

# beacon-qa

**公开面（Scheme A）**：`qa`  
**渐进加载（能力不降级）**：`beacon-eval-qa`, `beacon-eval-qa-deep`, `beacon-eval-real-project`, `beacon-eval-agent`

本 skill **不**负责多小时 longrun；长程只用 `$beacon-goal` / `$loom-goal`。

## When to use

- 需要 **qa** 场景的稳定入口（host-visible 白名单内）
- 细粒度旧名（如 gen-implement）仍可用作兼容，但默认安装不再暴露

## Progressive load

按 `public-surface-progressive-map.v1.json` 加载内部 skill；**禁止**为了合并而跳过原有 HARD GATE。

| Internal skill | Role |
|----------------|------|
| `beacon-eval-qa` | progressive |
| `beacon-eval-qa-deep` | progressive |
| `beacon-eval-real-project` | progressive |
| `beacon-eval-agent` | progressive |

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
