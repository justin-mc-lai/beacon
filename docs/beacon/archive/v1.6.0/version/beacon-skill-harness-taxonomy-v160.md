# 版本规划：beacon-skill-harness-taxonomy-v160

## 版本定位

- target_version: `v1.6.0`
- base_version: `v1.5.2`
- strategy: `bump:minor`
- owner: `beacon`
- generated_at: `2026-06-08 06:53:07Z`

## 目标与范围

- 主题：beacon-skill-harness-taxonomy-v160
- 目标：v1.6.0 breaking skill harness taxonomy, shared preamble, and planner/generator/evaluator/governor rename migration
- 范围：对齐 think/user-story/prd/test-case/workflow/gate 闭环

## 版本演进规则

1. 默认 `--version auto` 取当前最大语义版本。
2. 指定 `--base-version + --bump` 计算下一目标版本。
3. 指定 `--version vX.Y.Z` 走手动版本锁定。

## 追溯

- 推荐随后执行：
  - `beacon evolution-summary create v1.6.0`
  - `beacon workflow start "beacon-skill-harness-taxonomy-v160" --version v1.6.0`

