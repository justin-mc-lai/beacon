---
name: beacon
description: Evidence-first Product Workflow Kernel for product thinking, user stories, PRDs, test cases, and release workflows
---

# Beacon - Evidence-first Product Workflow Kernel

> **Skill Version**: v1.1.5
> **CLI Version**: v1.1.5
> **Last Updated**: 2026-03-23

Beacon 是 AI 产品工作流内核，提供需求澄清、用户故事、PRD、测试用例、证据闭环与发布门禁的统一工作流。

## 命令触发（CLI/Skill 单一事实源）

**命令口径（统一）**：
- `beacon <subcommand>`（推荐）
- 脚本方式（兼容）：`python3 -m beacon.main <subcommand> ...`
- 历史模块入口（兼容）：`python3 -m beacon.think ...`（保留兼容，但不作为推荐入口）

> 注意：对外建议统一使用 `beacon <subcommand>`；正式交付文档统一读取 `docs/beacon/<version>/`。
> 标准 skill 包目录位于 `skills/beacon/`；根 `SKILL.md` 保留为兼容入口。

命令清单由 `beacon/command_catalog.py::SUPPORTED_SUBCOMMANDS` 自动生成，使用：

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
| `beacon ask` | `ask` |
| `beacon analyze` | `analyze` |
| `beacon api-design` | `api-design` |
| `beacon auto-test` | `auto-test` |
| `beacon brainstorm` | `brainstorm` |
| `beacon data-dictionary` | `data-dictionary` |
| `beacon debug` | `debug` |
| `beacon design` | `design` |
| `beacon doctor` | `doctor` |
| `beacon evolution-summary` | `evolution-summary` |
| `beacon feedback` | `feedback` |
| `beacon gate` | `gate` |
| `beacon implement` | `implement` |
| `beacon init` | `init` |
| `beacon jtbd` | `jtbd` |
| `beacon kano` | `kano` |
| `beacon moscow` | `moscow` |
| `beacon persona` | `persona` |
| `beacon prototype` | `prototype` |
| `beacon prompt` | `prompt` |
| `beacon prd` | `prd` |
| `beacon ralph-bridge` | `ralph-bridge` |
| `beacon recall` | `recall` |
| `beacon release` | `release` |
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
| `beacon version` | `version` |
| `beacon wireframe` | `wireframe` |
| `beacon work` | `work` |
| `beacon workflow` | `workflow` |

### 完整子命令清单（自动同步）

| 子命令 | 推荐触发 |
|-------|----------|
| `ask` | `beacon ask` |
| `analyze` | `beacon analyze` |
| `api-design` | `beacon api-design` |
| `auto-test` | `beacon auto-test` |
| `brainstorm` | `beacon brainstorm` |
| `data-dictionary` | `beacon data-dictionary` |
| `debug` | `beacon debug` |
| `design` | `beacon design` |
| `doctor` | `beacon doctor` |
| `evolution-summary` | `beacon evolution-summary` |
| `feedback` | `beacon feedback` |
| `gate` | `beacon gate` |
| `implement` | `beacon implement` |
| `init` | `beacon init` |
| `jtbd` | `beacon jtbd` |
| `kano` | `beacon kano` |
| `moscow` | `beacon moscow` |
| `persona` | `beacon persona` |
| `prototype` | `beacon prototype` |
| `prompt` | `beacon prompt` |
| `prd` | `beacon prd` |
| `ralph-bridge` | `beacon ralph-bridge` |
| `recall` | `beacon recall` |
| `release` | `beacon release` |
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
| `version` | `beacon version` |
| `wireframe` | `beacon wireframe` |
| `work` | `beacon work` |
| `workflow` | `beacon workflow` |
<!-- AUTO-COMMANDS:END -->

### CLI 调用示例（workflow）

```bash
# 推荐
beacon workflow start "Beacon v1.1.5 layered delivery" --project /abs/path/to/project --version v1.1.5

# 兼容
python3 -m beacon.main workflow start "Beacon v1.1.5 layered delivery" --project /abs/path/to/project --version v1.1.5
```

## Gate 检查

| 阶段 | 门控项 | 判定标准 |
|------|--------|---------|
| think | 收敛门 | 无 blocking=true 的未决项 |
| user-story | AC门 | 七维 AC 完整 |
| prd | 风险门 | critical/high 冲突已解决 |
| test-case | 覆盖门 | AC→TC 覆盖矩阵完整 |
| release | 放行门 | formal package / delivery / evidence / gate contract 通过 |

## 输出目录

```
docs/beacon/{version}/
├── SUMMARY.md
├── prd/{feature}.md
├── user-story/{feature}.md
├── qa/test-cases/{feature}.md
├── release/{version}.md
├── execution/index.md
├── execution/boundaries.md
└── .machine/execution/terminal.json
```

## 参考文档

- `docs/beacon/v1.1.5/SUMMARY.md`
- `docs/beacon/v1.1.5/execution/boundaries.md`
- `docs/beacon/v1.1.5/execution/index.md`
- `docs/beacon/v1.1.5/execution/human-machine-collaboration-norm.md`
- `docs/beacon/v1.1.5/execution/memory-architecture-and-projection.md`
- `docs/beacon/v1.1.5/execution/doctor-repair-scope.md`
- `docs/beacon/v1.1.5/execution/safe-implementation-plan.md`
- `docs/beacon/v1.1.5/execution/eval-lab-benchmark-surface.md`
- `docs/beacon/v1.1.5/execution/keep-discard-policy.md`
- `docs/beacon/v1.1.5/execution/drift-auditor-minimum-loop.md`
- `docs/beacon/v1.1.5/release/v1.1.5.md`
- `skills/beacon/SKILL.md`
- `references/acceptance-criteria.md`
- `references/user-story-mapping.md`

---

**版本**: v1.1.5
