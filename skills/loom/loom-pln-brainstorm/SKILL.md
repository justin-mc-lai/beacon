---
name: loom-pln-brainstorm
description: "Loom v2 surface for beacon-pln-brainstorm. Content routes to skills/beacon/beacon-pln-brainstorm (single source). Dual-install; does not replace beacon."
metadata:
  version: "v2.0.0"
  brand: Loom
  track: track_v2
  content_source: skills/beacon/beacon-pln-brainstorm
  dual_install_with: beacon-pln-brainstorm
  entry: progressive
---

# loom-pln-brainstorm

**品牌**：Loom（v2 进化轨）  
**内容权威**：`skills/beacon/beacon-pln-brainstorm/`（Phase-2 前缀镜像；禁止双写两套逻辑）

## 调用

```text
$loom-pln-brainstorm
```

生产轨仍用 `$beacon-pln-brainstorm` / `beacon` CLI。本 skill **不得**覆盖 beacon launcher。

## 路由

实现与合同细节以 `skills/beacon/beacon-pln-brainstorm/SKILL.md` 及 references 为准。  
Host 加载 Loom 轨时应优先解析 `skills/loom/loom-pln-brainstorm`，内容跟随 beacon 源文件。
