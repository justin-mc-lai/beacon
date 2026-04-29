---
name: beacon
version: 1.3.9
description: Evidence-first Product Workflow Kernel for product thinking, user stories, PRDs, test cases, and release workflows
---

# Beacon - Evidence-first Product Workflow Kernel

> **Skill Version**: v1.3.9
> **CLI Version**: v1.3.9
> **Last Updated**: 2026-04-21

Beacon 是 AI 产品工作流内核，把 requirement materials、实现证据、QA 结论和 release 决策统一到一个版本化系统。

## 当前版本 / 发布线

- **当前发布线**：`v1.3.9`
- **当前包版本**：`1.3.9`
- **最新已接受文档线**：`v1.3.9`
- **标准打包入口**：`skills/beacon/`
- **文档主源**：`docs/beacon/{version}/`
- `beacon <subcommand>`（推荐）
- `python3 -m beacon.think ...`（兼容入口，仍可使用）

如果你只记一条：

> 当前运行时与文档主线统一到 `docs/beacon/v1.3.9/`，主机入口统一走 `beacon <subcommand>` 和 `skills/beacon/`。

当前对外口径：

> `docs/beacon/v1.3.9/` 是 Beacon 当前 runtime、host-native orchestration、delivery kernel 和 read-model 的统一文档线。

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
beacon help --project-root . --version v1.3.9 --feature "<feature>" --json
beacon prd bootstrap "<feature>" --project-root . --version v1.3.9 --dry-run --json
beacon implement plan "<feature>" --project . --version v1.3.9 --json
beacon qa run "<feature>" --project . --version v1.3.9 --json
beacon gate check release --project-root . --version v1.3.9 --json
```

## Workflow Model / 主工作流模型

```text
prd
-> user-story
-> test-case
-> prototype
-> implement
-> qa
-> release
```

辅助导航面：

- `help`
- `status`
- `doctor`
- `archive`

## Current Product Surfaces / 当前产品面

- 最小 7+3 主机面
- `archive` 历史 truth 归档治理面
- `skills/beacon/` 标准 skill 包
- `debug codex-fixed-hud` HUD 输出面
- `doctor setup-codex-hud-hook` / `doctor verify-codex-hud-hook`
- `prototype` requirement-driven wireframe freeze 阶段

## Why This Skill Matters / 为什么重要

- Beacon v1.3.9 把 runtime truth、技能包装、HUD 接线统一到同一条发布线
- Beacon v1.3.9 把 diagram truth、prompt boundary gate、archive 治理一起收敛进当前运行线
- QA 的 skill 提示词必须遵守第一性原则，不能跳过 requirement evidence
- 如果关键信号缺失，必须 `stop_for_repair`
- 需要浏览器证据时可以显式接 `browser-use`，但它不是默认主线

## Current Runtime Line / 当前运行线

`v1.3.9` 现在就是 Beacon 的正式 runtime 口径，本线要求以下叙事与实现保持一致：

- skill 运行在 Claude / Codex 中时，默认优先复用宿主原生 LLM
- Beacon CLI 退回到结构化执行内核：
  - truth read
  - diagram truth admission
  - semantic envelope validation
  - canonical projection
  - prompt boundary gate
  - freeze / review / gate / release
- `implement / qa / release / help / status / doctor / archive` 共享统一 delivery contract 与 read model
- `BEACON_LLM_API_KEY` 退居 provider fallback，而不是宿主默认前提

## Recommended Reading Order / 推荐阅读顺序

1. `docs/beacon/v1.3.9/SUMMARY.md`
2. `docs/beacon/v1.3.9/execution/index.md`
3. `docs/beacon/v1.3.9/execution/architecture-blueprint.md`
4. `docs/beacon/v1.3.9/execution/project-skill-qa-evolution-blueprint.md`
5. `docs/beacon/v1.3.9/execution/boundaries.md`
6. `docs/beacon/v1.3.9/release/v1.3.9.md`

## Common Usage Modes / 常见使用场景

- 从 feature 想法进入 PRD / user-story / test-case 主链
- 在实现前生成技术计划并核对 gate
- 做 QA 证据闭环与 release readiness 检查
- 修复 context drift、materials drift、Codex HUD drift
- 查看当前 host-native runtime 叙事与实现边界

## Command Surface / How to Use

```bash
beacon help --project-root . --json
beacon status --board --project-root . --version v1.3.9
beacon doctor verify-context --project-root . --strict --json
beacon doctor setup-codex-hud-hook --project-root . --version v1.3.9 --apply --json
beacon doctor verify-codex-hud-hook --project-root . --version v1.3.9 --json
```

<!-- AUTO-COMMANDS:START -->
### 可触发关键词（自动同步）

| 关键词 | 对应子命令 |
|--------|------------|
| `beacon ask` | `ask` |
| `beacon analyze` | `analyze` |
| `beacon api-design` | `api-design` |
| `beacon auto-test` | `auto-test` |
| `beacon qa` | `qa` |
| `beacon brainstorm` | `brainstorm` |
| `beacon data-dictionary` | `data-dictionary` |
| `beacon debug` | `debug` |
| `beacon design` | `design` |
| `beacon doctor` | `doctor` |
| `beacon evolution-summary` | `evolution-summary` |
| `beacon feedback` | `feedback` |
| `beacon freeze` | `freeze` |
| `beacon help` | `help` |
| `beacon gate` | `gate` |
| `beacon implement` | `implement` |
| `beacon init` | `init` |
| `beacon jtbd` | `jtbd` |
| `beacon kano` | `kano` |
| `beacon lighthouse` | `lighthouse` |
| `beacon memory-friction-evolution` | `memory-friction-evolution` |
| `beacon moscow` | `moscow` |
| `beacon persona` | `persona` |
| `beacon prototype` | `prototype` |
| `beacon prompt` | `prompt` |
| `beacon profile` | `profile` |
| `beacon prd` | `prd` |
| `beacon qa` | `qa` |
| `beacon orchestrate` | `orchestrate` |
| `beacon ralph-bridge` | `ralph-bridge` |
| `beacon recall` | `recall` |
| `beacon release` | `release` |
| `beacon reopen` | `reopen` |
| `beacon remember` | `remember` |
| `beacon report` | `report` |
| `beacon review` | `review` |
| `beacon resume` | `resume` |
| `beacon roadmap` | `roadmap` |
| `beacon run` | `run` |
| `beacon save` | `save` |
| `beacon skill` | `skill` |
| `beacon status` | `status` |
| `beacon team` | `team` |
| `beacon test-case` | `test-case` |
| `beacon test-progress` | `test-progress` |
| `beacon think` | `think` |
| `beacon ui-spec` | `ui-spec` |
| `beacon user-story` | `user-story` |
| `beacon verify` | `verify` |
| `beacon version` | `version` |
| `beacon work` | `work` |
| `beacon workflow` | `workflow` |

### 完整子命令清单（自动同步）

| 子命令 | 推荐触发 |
|-------|----------|
| `ask` | `beacon ask` |
| `analyze` | `beacon analyze` |
| `api-design` | `beacon api-design` |
| `auto-test` | `beacon auto-test` |
| `qa` | `beacon qa` |
| `brainstorm` | `beacon brainstorm` |
| `data-dictionary` | `beacon data-dictionary` |
| `debug` | `beacon debug` |
| `design` | `beacon design` |
| `doctor` | `beacon doctor` |
| `evolution-summary` | `beacon evolution-summary` |
| `feedback` | `beacon feedback` |
| `freeze` | `beacon freeze` |
| `help` | `beacon help` |
| `gate` | `beacon gate` |
| `implement` | `beacon implement` |
| `init` | `beacon init` |
| `jtbd` | `beacon jtbd` |
| `kano` | `beacon kano` |
| `lighthouse` | `beacon lighthouse` |
| `memory-friction-evolution` | `beacon memory-friction-evolution` |
| `moscow` | `beacon moscow` |
| `persona` | `beacon persona` |
| `prototype` | `beacon prototype` |
| `prompt` | `beacon prompt` |
| `profile` | `beacon profile` |
| `prd` | `beacon prd` |
| `qa` | `beacon qa` |
| `orchestrate` | `beacon orchestrate` |
| `ralph-bridge` | `beacon ralph-bridge` |
| `recall` | `beacon recall` |
| `release` | `beacon release` |
| `reopen` | `beacon reopen` |
| `remember` | `beacon remember` |
| `report` | `beacon report` |
| `review` | `beacon review` |
| `resume` | `beacon resume` |
| `roadmap` | `beacon roadmap` |
| `run` | `beacon run` |
| `save` | `beacon save` |
| `skill` | `beacon skill` |
| `status` | `beacon status` |
| `team` | `beacon team` |
| `test-case` | `beacon test-case` |
| `test-progress` | `beacon test-progress` |
| `think` | `beacon think` |
| `ui-spec` | `beacon ui-spec` |
| `user-story` | `beacon user-story` |
| `verify` | `beacon verify` |
| `version` | `beacon version` |
| `work` | `beacon work` |
| `workflow` | `beacon workflow` |
<!-- AUTO-COMMANDS:END -->

## Lifecycle Navigation Rules

- 不确定下一步时先跑 `help` 或 `status`
- requirement materials 不完整时先补 `prd` / `user-story` / `test-case`
- 实现前先过 `implement plan`
- QA 发现 contract 漂移时不要硬过，直接 `stop_for_repair`
- release 前必须有 doctor / gate / scorecard 证据

## Docs / Troubleshooting / Examples / References

- 标准 skill 包：`skills/beacon/`
- 版本化文档：`docs/beacon/{version}/`
- 当前 host-native runtime 文档线：`docs/beacon/v1.3.8/`
- 当前 runtime release note：`docs/beacon/v1.3.8/release/v1.3.8.md`
- 当前架构蓝图：`docs/beacon/v1.3.8/execution/architecture-blueprint.md`
- HUD 诊断：`beacon debug codex-fixed-hud --project-root . --version v1.3.8 --json`
- 技能漂移检查：`python3 scripts/check_skill_drift.py --project-root . --json`
- 安装说明：`.codex/INSTALL.md`

---

**版本**: v1.3.8
