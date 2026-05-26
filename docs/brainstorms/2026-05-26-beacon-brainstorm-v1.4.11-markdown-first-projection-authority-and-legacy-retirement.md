# Beacon Brainstorm：v1.4.11 Markdown-first 投影权威与旧版兼容退场

**Date**: `2026-05-26`  
**Mode**: `requirement-convergence`  
**Version**: `v1.4.11`  
**Feature candidate**: `markdown-first-projection-authority-and-legacy-retirement-contract`  
**Versioned research**: `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`

## 收敛结论

Beacon 不应该删除 `.machine`。

Beacon 应该删除围绕 `.machine` 的权威歧义。

核心模型应是：

```text
Markdown truth
  -> deterministic projection
  -> evidence / gate / release read model
```

而不是：

```text
Markdown truth <-> machine truth
```

## 为什么重要

当前 `main` 分支已经有 Markdown-first helpers 和版本化 Markdown truth paths。但同时仍保留 policy 文案，称 machine artifacts remain source of truth。这会造成概念断裂：

- operator 听到的是 Markdown-first。
- status / gate / policy surface 仍暴露 machine source of truth。
- legacy fallback path 在 current-version 应显式的地方可能静默 pass。
- P0 friction `friction:cd1809c3220a` 进一步证明：当 accepted `ui-ux-dev` UI/UX facts 未写回 `PRODUCT.md` / `DESIGN.md` / PRD / user-story / test-cases 时，automation 会按旧 frozen truth 回滚已验收前端事实。Markdown-first 不能等于“盲信旧 Markdown”，而应要求 accepted human facts 进入正确 truth surface，否则 implement / QA / release fail closed。

这不只是文案问题。它会影响 gate trust、support surface 边界、QA closure 解释，以及后续源码清理工作的方向。

## 推荐范围

冻结一个聚焦的 v1.4.11 feature：

```text
markdown-first-projection-authority-and-legacy-retirement-contract
```

范围保持收窄：

- authority vocabulary cleanup。
- projection / evidence naming。
- compatibility registry。
- `v1.4.11+` hidden fallback fail-closed defaults。
- machine-as-truth wording regression tests。
- accepted UI/UX facts 未写回 truth 的 blocker / gate 调研：`accepted_ui_ux_truth_gap_gate`。

不要把它与新的 QA 扩容、Ralph loop、learn skill injection 合并。

## 路由

```bash
beacon change-refreeze "markdown-first-projection-authority-and-legacy-retirement-contract" --project . --version v1.4.11
```

本 brainstorm 是 advisory support material，不冻结 requirement truth。
