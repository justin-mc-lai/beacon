# PRD: Beacon Team v1.0.0 团队协作

**状态**: Draft
**版本**: v1.0.0
**日期**: 2026-03-02

---

## 1. 背景与目标

### 1.1 背景

Beacon Team 从 PTK team Skill 升级而来，是多代理协作的核心组件。支持 N 个协调代理的并行工作，实现高效团队协作。

### 1.2 目标

- **主要目标**: 实现完整的状态机流转 (plan→prd→exec→verify→fix→terminal)
- **次要目标**: 支持 file/tmux/auto 多种运行时形态

---

## 2. 功能需求

### 2.1 状态机

**FR-001**: 阶段流转

```
team-plan → team-prd → team-exec → team-verify → team-fix → terminal
```

**FR-002**: 终态语义

| 终态 | 说明 |
|------|------|
| Pass | 所有阶段通过 |
| Blocked | 被阻断 (max_fix_loops 达上限) |
| Cancelled | 手动取消 |

### 2.2 运行时形态

**FR-003**: 运行时支持

| 形态 | 说明 |
|------|------|
| file | 纯文件状态机 (保底) |
| tmux | 多 worker 进程协作 |
| auto | 按配置自动选择 |

### 2.3 双审查 Gate

**FR-004**: 审查流程

```
spec gate → quality gate → evaluation
```

规则：
1. spec 未 pass，quality 不可提交
2. critical/high 未清零，evaluation = Blocked

### 2.4 状态管理

**FR-005**: 状态目录

```
.beacon/state/team/<name>/
├── manifest.json
├── tasks/task-001.json
├── workers/<id>/status.json
├── mailbox/*.json
├── review-gates.json
└── reports/*.md|json
```

### 2.5 Handoff 与报告

**FR-006**: Handoff 文档

- 阶段迁移自动生成: `.beacon/handoffs/<team>-<from>-to-<to>.md`
- 运行报告支持 Markdown/JSON 格式

---

## 3. CLI 命令

```bash
# 团队任务
beacon team start "登录功能开发"
beacon team start "登录功能开发" --members 5
beacon team status
beacon team stop
beacon team resume

# Workers 管理
beacon team add @member1
beacon team remove @member1
beacon team workers

# 审查 Gate
beacon team gate spec --status pass
beacon team gate quality --status pass
beacon team gate evaluate

# 报告
beacon team report
beacon team report --format json
```

---

## 4. 验收标准

- [ ] 完整状态机流转
- [ ] file/tmux/auto 运行时支持
- [ ] 双审查 Gate
- [ ] 状态持久化与恢复
- [ ] Handoff 报告生成

---

**Created**: 2026-03-02
**Version**: 1.0.0
**Status**: Draft
