# Beacon v1.3.3 Source Architecture Index

本索引用于标记 `v1.3.3` 版本线的核心源码承载面，确保“core slimming + compatibility demotion”可追踪。

## Release themes

`v1.3.3` 由三条需求线共同构成：

1. core slimming 与 external skill demotion（主 PRD）
2. minimal HUD 场景与实现（并行 PRD）
3. memory/friction evolution toolkit（并行 PRD）

## Command surfaces

- `beacon/commands/help.py`
  - stage-aware next-step 路由
  - minimal HUD 输出整合
- `beacon/commands/status.py`
  - board 聚合
  - HUD 行输出
- `beacon/commands/implement.py`
  - host-native implement 面
  - team/runtime 契约与写回
- `beacon/commands/qa.py`
  - feature-aware QA
  - qa-team 执行与证据写回
- `beacon/commands/review.py`
  - quality / accept 正式评审与写回

## Shared kernel modules

- `beacon/utils/help_support.py`
  - blocking reason、next-step、minimal HUD payload
- `beacon/utils/minimal_hud.py`
  - HUD 1~3 行生成逻辑
- `beacon/utils/coverage.py`
  - story/ac/tc 覆盖率计算
- `beacon/utils/material_audit.py`
  - formal package closure 校验
- `beacon/utils/qa_feature.py`
  - scorecard、ac-closure、repair handoff

## Canonical contracts

- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.3.3/SUMMARY.md`
- `docs/beacon/v1.3.3/execution/index.md`
- `docs/beacon/v1.3.3/execution/architecture-blueprint.md`
- `docs/beacon/v1.3.3/execution/project-skill-qa-evolution-blueprint.md`
- `docs/beacon/v1.3.3/prd/*.md`
- `docs/beacon/v1.3.3/user-story/*.md`
- `docs/beacon/v1.3.3/qa/test-cases/*.md`

## Boundary note

`v1.3.3` 的边界原则：

- 主链不扩张：继续保持 `6+3` 心智模型
- 兼容面不消失：保留但不默认曝光
- 质量治理不降级：coverage、review、accept、release gate 持续生效

