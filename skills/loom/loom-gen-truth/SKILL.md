---
name: loom-gen-truth
description: "Loom v2 surface for beacon-gen-truth. Content routes to skills/beacon/beacon-gen-truth (single source). Dual-install; does not replace beacon."
metadata:
  version: "v2.0.0"
  brand: Loom
  track: track_v2
  content_source: skills/beacon/beacon-gen-truth
  dual_install_with: beacon-gen-truth
  entry: progressive
---

# loom-gen-truth

**品牌**：Loom（v2 进化轨）  
**内容权威**：`skills/beacon/beacon-gen-truth/`（Phase-2 前缀镜像；禁止双写两套逻辑）

## 调用

```text
$loom-gen-truth
```

生产轨仍用 `$beacon-gen-truth` / `beacon` CLI。本 skill **不得**覆盖 beacon launcher。

## 路由

实现与合同细节以 `skills/beacon/beacon-gen-truth/SKILL.md` 及 references 为准。  
Host 加载 Loom 轨时应优先解析 `skills/loom/loom-gen-truth`，内容跟随 beacon 源文件。
