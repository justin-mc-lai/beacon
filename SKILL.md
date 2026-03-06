---
name: beacon
description: AI Product Workflow Toolkit for product thinking, user stories, PRDs, test cases, and release workflows
---

# Beacon - AI Product Workflow Toolkit

> **Skill Version**: v1.0.3
> **CLI Version**: v1.0.3
> **Last Updated**: 2026-03-06

Beacon 是 AI 产品工作流工具包，提供需求澄清、用户故事、PRD、测试用例、技术方案与发布清单的完整工作流。

## 命令触发（CLI/Skill 单一事实源）

**命令口径（统一）**：
- `beacon-<subcommand>`（推荐）
- `beacon <subcommand>`（兼容）
- 脚本方式（兼容）：`python3 -m beacon.main <subcommand> ...`
- 历史模块入口（兼容）：`python3 -m beacon.think ...`（保留兼容，但不作为推荐入口）

> 注意：对外建议与“下一步”提示统一使用 `beacon` 前缀，不再推荐历史 PTK 命令（`ptk`）；目录仍保持兼容（`.ptk`、`docs/product`）。

命令清单由 `beacon/prefixed.py::SUPPORTED_SUBCOMMANDS` 自动生成，使用：

```bash
python3 scripts/sync_skill_commands.py
```

或校验：

```bash
python3 scripts/sync_skill_commands.py --check
```

<!-- AUTO-COMMANDS:START -->
### 可触发关键词（自动同步）

| 关键词 | 对应子命令 |
|--------|------------|
| `beacon-ask` | `ask` |
| `beacon-analyze` | `analyze` |
| `beacon-api-design` | `api-design` |
| `beacon-auto-test` | `auto-test` |
| `beacon-brainstorm` | `brainstorm` |
| `beacon-data-dictionary` | `data-dictionary` |
| `beacon-debug` | `debug` |
| `beacon-design` | `design` |
| `beacon-doctor` | `doctor` |
| `beacon-evolution-summary` | `evolution-summary` |
| `beacon-feedback` | `feedback` |
| `beacon-gate` | `gate` |
| `beacon-init` | `init` |
| `beacon-jtbd` | `jtbd` |
| `beacon-kano` | `kano` |
| `beacon-moscow` | `moscow` |
| `beacon-persona` | `persona` |
| `beacon-prompt` | `prompt` |
| `beacon-prd` | `prd` |
| `beacon-ralph-bridge` | `ralph-bridge` |
| `beacon-recall` | `recall` |
| `beacon-release` | `release` |
| `beacon-remember` | `remember` |
| `beacon-report` | `report` |
| `beacon-resume` | `resume` |
| `beacon-roadmap` | `roadmap` |
| `beacon-run` | `run` |
| `beacon-save` | `save` |
| `beacon-status` | `status` |
| `beacon-team` | `team` |
| `beacon-test-case` | `test-case` |
| `beacon-test-progress` | `test-progress` |
| `beacon-think` | `think` |
| `beacon-ui-spec` | `ui-spec` |
| `beacon-user-story` | `user-story` |
| `beacon-version` | `version` |
| `beacon-wireframe` | `wireframe` |
| `beacon-work` | `work` |
| `beacon-workflow` | `workflow` |

### 完整子命令清单（自动同步）

| 子命令 | 推荐触发 |
|-------|----------|
| `ask` | `beacon-ask` |
| `analyze` | `beacon-analyze` |
| `api-design` | `beacon-api-design` |
| `auto-test` | `beacon-auto-test` |
| `brainstorm` | `beacon-brainstorm` |
| `data-dictionary` | `beacon-data-dictionary` |
| `debug` | `beacon-debug` |
| `design` | `beacon-design` |
| `doctor` | `beacon-doctor` |
| `evolution-summary` | `beacon-evolution-summary` |
| `feedback` | `beacon-feedback` |
| `gate` | `beacon-gate` |
| `init` | `beacon-init` |
| `jtbd` | `beacon-jtbd` |
| `kano` | `beacon-kano` |
| `moscow` | `beacon-moscow` |
| `persona` | `beacon-persona` |
| `prompt` | `beacon-prompt` |
| `prd` | `beacon-prd` |
| `ralph-bridge` | `beacon-ralph-bridge` |
| `recall` | `beacon-recall` |
| `release` | `beacon-release` |
| `remember` | `beacon-remember` |
| `report` | `beacon-report` |
| `resume` | `beacon-resume` |
| `roadmap` | `beacon-roadmap` |
| `run` | `beacon-run` |
| `save` | `beacon-save` |
| `status` | `beacon-status` |
| `team` | `beacon-team` |
| `test-case` | `beacon-test-case` |
| `test-progress` | `beacon-test-progress` |
| `think` | `beacon-think` |
| `ui-spec` | `beacon-ui-spec` |
| `user-story` | `beacon-user-story` |
| `version` | `beacon-version` |
| `wireframe` | `beacon-wireframe` |
| `work` | `beacon-work` |
| `workflow` | `beacon-workflow` |
<!-- AUTO-COMMANDS:END -->

### CLI 调用示例（think）

```bash
# 推荐
./beacon-cli think start "分析 xxx 业务闭环" --project /abs/path/to/project

# 兼容
python3 -m beacon.main think start "分析 xxx 业务闭环" --project /abs/path/to/project
```

## Gate 检查

| 阶段 | 门控项 | 判定标准 |
|------|--------|---------|
| think | 收敛门 | 无 blocking=true 的未决项 |
| user-story | AC门 | 七维 AC 完整 |
| prd | 风险门 | critical/high 冲突已解决 |
| test-case | 覆盖门 | AC→TC 覆盖矩阵完整 |
| release | 测试门 | 冒烟测试 100% 通过 |

## 输出目录

```
docs/product/{version}/
├── SUMMARY.md
├── prd/{feature}.md
├── user-story/{feature}.md
├── qa/test-cases/{feature}.md
├── execution/boundaries.md
└── execution/terminal.json
```

## 参考文档

- `references/socratic-questioning.md`
- `references/acceptance-criteria.md`
- `references/user-story-mapping.md`

---

**版本**: v1.0.3
