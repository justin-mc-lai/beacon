---
name: loom-eval-qa-deep
description: "Loom v2 surface for beacon-eval-qa-deep. Content routes to skills/beacon/beacon-eval-qa-deep (single source). Dual-install; does not replace beacon."
metadata:
  version: "v2.0.0"
  brand: Loom
  track: track_v2
  content_source: skills/beacon/beacon-eval-qa-deep
  dual_install_with: beacon-eval-qa-deep
  entry: progressive
---

# loom-eval-qa-deep

**品牌**：Loom（v2 进化轨）  
**内容权威**：`skills/beacon/beacon-eval-qa-deep/`（Phase-2 前缀镜像；禁止双写两套逻辑）

## 调用

```text
$loom-eval-qa-deep
```

生产轨仍用 `$beacon-eval-qa-deep` / `beacon` CLI。本 skill **不得**覆盖 beacon launcher。

## 路由

实现与合同细节以 `skills/beacon/beacon-eval-qa-deep/SKILL.md` 及 references 为准。  
Host 加载 Loom 轨时应优先解析 `skills/loom/loom-eval-qa-deep`，内容跟随 beacon 源文件。
