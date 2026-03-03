---
name: beacon
description: AI Product Workflow Toolkit for product thinking, user stories, PRDs, test cases, and release workflows
---

# Beacon - AI Product Workflow Toolkit

> **Skill Version**: v1.0.0
> **CLI Version**: v1.0.0
> **Last Updated**: 2026-03-02

Beacon 是 AI 产品工作流工具包，提供需求澄清、用户故事、PRD、测试用例、技术方案与发布清单的完整工作流。

## 关键词触发

默认使用 `beacon-<subcommand>` 触发技能（避免与其他技能同名命令冲突）：

| 关键词 | 技能 |
|--------|------|
| `beacon-think` | 产品思考 vNext |
| `beacon-work` | 一键工作流 |
| `beacon-workflow` | 一键工作流 |
| `beacon-doctor` | 环境/版本检查 |
| `beacon-status` | 状态面板 |
| `beacon-report` | 测试/版本报告 |
| `beacon-run` | 运行工作流 |
| `beacon-gate` | 门控检查 |
| `beacon-debug` | 调试模式 |
| `beacon-feedback` | 测试反馈同步 |
| `beacon-resume` | 恢复会话 |

**命令口径（统一）**：
- `beacon-<subcommand>`（推荐）
- `beacon <subcommand>`（兼容）
- 脚本方式（兼容）：`python3 -m beacon.main <subcommand> ...`
- **不要使用**：`python -m beacon.think ...` / `python3 -m beacon.think ...`（历史写法，易报 `No module named beacon.think`）

> 注意：对外建议与“下一步”提示统一使用 `beacon` 前缀，不再推荐历史 PTK 命令（`ptk`）；目录仍保持兼容（`.ptk`、`docs/product`）。

### CLI 调用示例（think）

```bash
# 推荐
./beacon-cli think start "分析 xxx 业务闭环" --project /abs/path/to/project

# 兼容
python3 -m beacon.main think start "分析 xxx 业务闭环" --project /abs/path/to/project
```

## 子命令

| 子命令 | 说明 |
|-------|------|
| `beacon-think [问题]` | 产品思考 vNext |
| `beacon-workflow [功能]` | 一键产品工作流 |
| `beacon-user-story [功能]` | 生成用户故事 |
| `beacon-prd [功能]` | 生成 PRD |
| `beacon-test-case [功能]` | 生成测试用例 |
| `beacon-doctor` | 环境诊断 |
| `beacon-status` | 状态面板 |
| `beacon-report [版本]` | 生成报告 |
| `beacon-gate [阶段]` | 门控检查 |
| `beacon-debug` | 调试模式 |
| `beacon-feedback` | 反馈同步 |

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

**版本**: v1.0.0
