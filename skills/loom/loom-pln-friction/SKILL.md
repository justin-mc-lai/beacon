---
name: loom-pln-friction
description: "Loom v2 surface for beacon-pln-friction. Content routes to skills/beacon/beacon-pln-friction (single source). Dual-install; does not replace beacon."
metadata:
  version: "v2.0.0"
  brand: Loom
  track: track_v2
  content_source: skills/beacon/beacon-pln-friction
  dual_install_with: beacon-pln-friction
  entry: progressive
---

# loom-pln-friction

**品牌**：Loom（v2 进化轨）  
**内容权威**：`skills/beacon/beacon-pln-friction/`（Phase-2 前缀镜像；禁止双写两套逻辑）

## 调用

```text
$loom-pln-friction
```

生产轨仍用 `$beacon-pln-friction` / `beacon` CLI。本 skill **不得**覆盖 beacon launcher。

## 路由

实现与合同细节以 `skills/beacon/beacon-pln-friction/SKILL.md` 及 references 为准。  
Host 加载 Loom 轨时应优先解析 `skills/loom/loom-pln-friction`，内容跟随 beacon 源文件。
