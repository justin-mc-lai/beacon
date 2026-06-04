# Beacon v1.3.1 QA Autoresearch Usage Guide

`v1.3.1` 不再把 autoresearch 暴露成独立人类主入口。

它的定位是：

- 保持在 `qa` 背后的 machine lane
- 围绕冻结用户故事补 coverage
- 不偏离正式 requirement package

## Human-facing rule

对人类只保留：

- `qa`

不要把 autoresearch 当成长期主命令记忆面。

## Runtime note

当 `qa run <feature>` 需要补 coverage、发现新边界或产出 repair handoff 时，
Beacon 可以在内部继续使用 learning / autoresearch。
