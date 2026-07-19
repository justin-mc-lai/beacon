---
name: loom
description: "Loom v2 brand host — full loom-* public skill surface; content routes to skills/beacon/*."
metadata:
  version: "v2.0.0"
  brand: Loom
  track: track_v2
---

# Loom host skill

## Public entry

**`$loom-goal`** — 唯一公共交付入口（v2 进化轨）

## Skill 前缀

v2 全品牌使用 **`loom-*`** 前缀（`skills/loom/loom-*`）。  
内容单源仍在 `skills/beacon/beacon-*`（CONTENT_SOURCE 指针），**禁止**双写两套逻辑。

见 `skills/loom/mirror-manifest.json`。

## 双装

- 生产：`$beacon-goal` / `beacon` CLI / `skills/beacon/*`
- 进化：`$loom-goal` / `loom` CLI / `skills/loom/loom-*`
- **禁止** loom 安装覆盖 `beacon` launcher；W4 前禁止默认替换

## Support

`$loom-loop-goal` — support only，勿先 loop 再 goal。
