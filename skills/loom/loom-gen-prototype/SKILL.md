---
name: loom-gen-prototype
description: "Loom v2 surface for beacon-gen-prototype. Content routes to skills/beacon/beacon-gen-prototype (single source). Dual-install; does not replace beacon."
metadata:
  version: "v2.0.0"
  brand: Loom
  track: track_v2
  content_source: skills/beacon/beacon-gen-prototype
  dual_install_with: beacon-gen-prototype
  entry: progressive
---

# loom-gen-prototype

**品牌**：Loom（v2 进化轨）  
**内容权威**：`skills/beacon/beacon-gen-prototype/`（Phase-2 前缀镜像；禁止双写两套逻辑）

## 调用

```text
$loom-gen-prototype
```

生产轨仍用 `$beacon-gen-prototype` / `beacon` CLI。本 skill **不得**覆盖 beacon launcher。

## 路由

实现与合同细节以 `skills/beacon/beacon-gen-prototype/SKILL.md` 及 references 为准。  
Host 加载 Loom 轨时应优先解析 `skills/loom/loom-gen-prototype`，内容跟随 beacon 源文件。
