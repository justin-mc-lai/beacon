# 版本规划：Beacon Plan Goal Task Closure

## 版本定位

- target_version: `v1.6.11`
- base_version: `v1.6.11`
- strategy: `manual`
- owner: `Beacon maintainers`
- generated_at: `2026-07-27 03:59:46Z`

## 目标与范围

- 主题：Beacon Plan Goal Task Closure
- 目标：将大目标完整拆解为可执行任务图，建立路径级进度、偏差人工门禁、取消重排与最终收敛验证
- 范围：对齐 think/user-story/prd/test-case/workflow/gate 闭环

## 版本演进规则

1. 默认 `--version auto` 取当前最大语义版本。
2. 指定 `--base-version + --bump` 计算下一目标版本。
3. 指定 `--version vX.Y.Z` 走手动版本锁定。

## 追溯

- 推荐随后执行：
  - `beacon evolution-summary create v1.6.11`
  - `beacon workflow start "Beacon Plan Goal Task Closure" --version v1.6.11`

