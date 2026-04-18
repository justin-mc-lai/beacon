---
name: beacon
version: 1.3.3
description: Evidence-first Product Workflow Kernel for product thinking, user stories, PRDs, test cases, and release workflows
---

# Beacon - Evidence-first Product Workflow Kernel

> **Skill Version**: v1.3.3
> **CLI Version**: v1.3.3
> **Last Updated**: 2026-04-17

Beacon 是 AI 产品工作流内核，把 requirement materials、实现证据、QA 结论和 release 决策统一到一个版本化系统。

## 当前版本 / 发布线

- **当前发布线**：`v1.3.3`
- **当前包版本**：`1.3.3`
- **最新已接受文档线**：`v1.3.3`
- **标准打包入口**：`skills/beacon/`
- **文档主源**：`docs/beacon/{version}/`
- `beacon <subcommand>`（推荐）

如果你只记一条：

> 当前运行时与文档主线统一到 `docs/beacon/v1.3.3/`，主机入口统一走 `beacon <subcommand>` 和 `skills/beacon/`。

## 产品定位

Beacon 不是模板生成器。它是把下面这些面压到同一条可审计链路里的 CLI 内核：

- 需求澄清
- 用户故事与 PRD
- 测试用例与 test-case backfill
- 实现计划、执行证据与 QA
- gate / release 判定

## 适合谁 / 不适合谁

适合：

- 需要 evidence-first 交付闭环的 AI 产品团队
- 需要把 docs、实现、QA、release 对齐到同一版本线的项目
- 需要 Codex / Claude 共享同一套 Beacon 技能入口的仓库

不适合：

- 只想让工具直接写业务代码且不关心 requirement materials 的场景
- 把 Beacon 当作浏览器自动化主平台，而不是 workflow kernel 的场景

## Quick Start / 快速上手

```bash
beacon help --project-root . --version v1.3.3 --feature "<feature>" --json
beacon prd bootstrap "<feature>" --project-root . --version v1.3.3 --dry-run --json
beacon implement plan "<feature>" --project . --version v1.3.3 --json
beacon qa run "<feature>" --project . --version v1.3.3 --json
beacon gate check release --project-root . --version v1.3.3 --json
```

## Workflow Model / 主工作流模型

```text
prd
-> user-story
-> test-case
-> implement
-> qa
-> release
```

辅助导航面：

- `help`
- `status`
- `doctor`

## Current Product Surfaces / 当前产品面

- 最小 6+3 主机面
- `skills/beacon/` 标准 skill 包
- `debug codex-fixed-hud` HUD 输出面
- `doctor setup-codex-hud-hook` / `doctor verify-codex-hud-hook`

## Why This Skill Matters / 为什么重要

- Beacon v1.3.3 把 runtime truth、技能包装、HUD 接线统一到同一条发布线
- QA 的 skill 提示词必须遵守第一性原则，不能跳过 requirement evidence
- 如果关键信号缺失，必须 `stop_for_repair`
- 需要浏览器证据时可以显式接 `browser-use`，但它不是默认主线

## Recommended Reading Order / 推荐阅读顺序

1. `docs/beacon/v1.3.3/SUMMARY.md`
2. `docs/beacon/v1.3.3/execution/index.md`
3. `docs/beacon/v1.3.3/execution/architecture-blueprint.md`
4. `docs/beacon/v1.3.3/execution/project-skill-qa-evolution-blueprint.md`
5. `docs/beacon/v1.3.3/execution/boundaries.md`
6. `docs/beacon/v1.3.3/release/v1.3.3.md`

## Common Usage Modes / 常见使用场景

- 从 feature 想法进入 PRD / user-story / test-case 主链
- 在实现前生成技术计划并核对 gate
- 做 QA 证据闭环与 release readiness 检查
- 修复 context drift、materials drift、Codex HUD drift

## Command Surface / How to Use

```bash
beacon help --project-root . --json
beacon status --board --project-root . --version v1.3.3
beacon doctor verify-context --project-root . --strict --json
beacon doctor setup-codex-hud-hook --project-root . --version v1.3.3 --apply --json
beacon doctor verify-codex-hud-hook --project-root . --version v1.3.3 --json
```

## Lifecycle Navigation Rules

- 不确定下一步时先跑 `help` 或 `status`
- requirement materials 不完整时先补 `prd` / `user-story` / `test-case`
- 实现前先过 `implement plan`
- QA 发现 contract 漂移时不要硬过，直接 `stop_for_repair`
- release 前必须有 doctor / gate / scorecard 证据

## Docs / Troubleshooting / Examples / References

- 标准 skill 包：`skills/beacon/`
- 版本化文档：`docs/beacon/{version}/`
- HUD 诊断：`beacon debug codex-fixed-hud --project-root . --version v1.3.3 --json`
- 技能漂移检查：`python3 scripts/check_skill_drift.py --project-root . --json`
- 安装说明：`.codex/INSTALL.md`

---

**版本**: v1.3.3
