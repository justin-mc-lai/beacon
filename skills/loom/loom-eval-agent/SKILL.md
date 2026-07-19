---
name: loom-eval-agent
description: "Loom v2 surface for beacon-eval-agent. Content routes to skills/beacon/beacon-eval-agent (single source). Dual-install; does not replace beacon."
metadata:
  version: "v2.0.0"
  brand: Loom
  track: track_v2
  content_source: skills/beacon/beacon-eval-agent
  dual_install_with: beacon-eval-agent
  entry: progressive
---

# loom-eval-agent

**品牌**：Loom（v2 进化轨）  
**内容权威**：`skills/beacon/beacon-eval-agent/`（Phase-2 前缀镜像；禁止双写两套逻辑）

## 调用

```text
$loom-eval-agent
```

生产轨仍用 `$beacon-eval-agent` / `beacon` CLI。本 skill **不得**覆盖 beacon launcher。

## 路由

实现与合同细节以 `skills/beacon/beacon-eval-agent/SKILL.md` 及 references 为准。  
Host 加载 Loom 轨时应优先解析 `skills/loom/loom-eval-agent`，内容跟随 beacon 源文件。
