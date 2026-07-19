---
name: loom-pln-program
description: "Loom v2 surface for beacon-pln-program. Content routes to skills/beacon/beacon-pln-program (single source). Dual-install; does not replace beacon."
metadata:
  version: "v2.0.0"
  brand: Loom
  track: track_v2
  content_source: skills/beacon/beacon-pln-program
  dual_install_with: beacon-pln-program
  entry: progressive
---

# loom-pln-program

**品牌**：Loom（v2 进化轨）  
**内容权威**：`skills/beacon/beacon-pln-program/`（Phase-2 前缀镜像；禁止双写两套逻辑）

## 调用

```text
$loom-pln-program
```

生产轨仍用 `$beacon-pln-program` / `beacon` CLI。本 skill **不得**覆盖 beacon launcher。

## 路由

实现与合同细节以 `skills/beacon/beacon-pln-program/SKILL.md` 及 references 为准。  
Host 加载 Loom 轨时应优先解析 `skills/loom/loom-pln-program`，内容跟随 beacon 源文件。
