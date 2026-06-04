# 版本规划：semantic contract check

## 版本定位

- target_version: `v1.3.0`
- base_version: `v1.3.0`
- strategy: `manual`
- owner: `TBD`
- generated_at: `2026-04-10 08:38:06Z`

## 目标与范围

- 主题：semantic contract check
- 目标：迭代改进
- 范围：对齐 think/user-story/prd/test-case/workflow/gate 闭环

## 版本演进规则

1. 默认 `--version auto` 取当前最大语义版本。
2. 指定 `--base-version + --bump` 计算下一目标版本。
3. 指定 `--version vX.Y.Z` 走手动版本锁定。

## 追溯

- 推荐随后执行：
  - `beacon evolution-summary create v1.3.0`
  - `beacon workflow start "semantic contract check" --version v1.3.0`

