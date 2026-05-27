# Research: Beacon Design Human Subskills Closure Contract

**Feature**: `beacon-design-human-subskills-closure-contract`  
**Version**: `v1.4.11`  
**Status**: `research-closed`  
**Date**: `2026-05-27`

## 1. 背景

`beacon-design-product-prototype-rebuild-contract` 已经把旧 prototype 深度重构为 Beacon design 能力。

现有证据显示：

- `beacon design contract` 已经暴露 7 条 deterministic route：`explore`、`extract`、`system`、`review`、`polish`、`library`、`bootstrap`。
- v1.4.11 PRD / user-story 已经承诺对应的人类面入口：`beacon-design-explore`、`beacon-design-extract`、`beacon-design-system`、`beacon-design-review`、`beacon-design-polish`、`beacon-design-library`、`beacon-design-bootstrap`。
- 当前 host-visible skill 实际只有 `beacon-design` 和 `beacon-design-review`。

这导致 design 能力已经在代码和需求里拆开，但人类操作入口仍然主要依赖一个总 skill。

## 2. 现有问题

大白话说：现在 `beacon-design` 像一个总前台，什么设计事都从它进。

问题是：

- 用户想探索方向，AI 可能跑去 review。
- 用户想做组件系统，AI 可能只给视觉建议。
- 用户想做 polish，AI 可能误改产品承诺。
- `library` 参考库可能被误当成项目设计 truth。
- `bootstrap` 能力检查可能被误当成 gate 或 release 证据。

这和 Beacon v1.4.11 的减负目标冲突：固定流程应该下沉成稳定入口、工具和边界，而不是每次靠 AI 重新理解。

## 3. 收敛结论

保留 `beacon-design` 作为总入口，但必须补齐 7 个 host-visible 子 skill：

```text
beacon-design-explore
beacon-design-extract
beacon-design-system
beacon-design-review
beacon-design-polish
beacon-design-library
beacon-design-bootstrap
```

每个子 skill 都只负责一类设计意图，并绑定到现有 CLI route：

```text
beacon design route <intent> "<feature>" --project . --version auto --json
```

## 4. 设计闭环

正确闭环不是“设计 skill 输出了就算 truth”。正确路径是：

```text
beacon-design-* support output
-> accepted design facts
-> PRODUCT.md / DESIGN.md / docs/beacon/<version>/design/* truth binding
-> promise-changing facts route to beacon-change-refreeze
-> prototype adapter binding when needed
-> beacon-implement
```

## 5. 子 skill 分工

| 子 skill | route | 上游能力 | 边界 |
| --- | --- | --- | --- |
| `beacon-design-explore` | `explore` | `vibe-to-ui` | UI 方向、信息层级、布局候选，不是 truth。 |
| `beacon-design-extract` | `extract` | `vibe-to-ui` | 从截图 / 参考拆结构和组件候选，不是 truth。 |
| `beacon-design-system` | `system` | `ui-ux-pro-max` | 组件系统、tokens、状态、响应式、无障碍、栈感知基线。 |
| `beacon-design-review` | `review` | `impeccable` | UX 问题、层级、文案、状态缺口、可访问性 review。 |
| `beacon-design-polish` | `polish` | `impeccable` | 上线前间距、对齐、反馈、信任、microcopy 打磨。 |
| `beacon-design-library` | `library` | `awesome-design-md` | 只做 reference-only，不是执行 skill，不是 truth。 |
| `beacon-design-bootstrap` | `bootstrap` | upstream compatibility | 只检查安装 / mirror / bootstrap 可用性，不是 gate / release。 |

## 6. 不做什么

本 feature 不做：

- 不新增 design CLI route。
- 不改 `beacon design` runtime 语义。
- 不改 prototype adapter 行为。
- 不改 PRODUCT.md / DESIGN.md truth 内容。
- 不改 release verdict。
- 不引入新的 lifecycle stage。
- 不把 upstream design skills 当成 Beacon truth source。

## 7. 推荐下一跳

进入 `beacon-change-refreeze`，冻结一个小 feature：

```text
beacon-design-human-subskills-closure-contract
```

冻结后再实现缺失的 host-visible `beacon-design-*` skill 文件和 discoverability 测试。
