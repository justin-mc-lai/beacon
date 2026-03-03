# Boundaries: Beacon v1.0.0

**版本**: v1.0.0
**日期**: 2026-02-28
**状态**: Completed

---

## In Scope

### 功能范围

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 需求工作流 | think → user-story → prd → test-case 主路径 | Must |
| 范围守护 | Scope Guard 越界检测与记录 | Must |
| 交付门控 | Gate Pass/Blocked/Cancelled 终态判定 | Must |
| 证据治理 | raw-command-log/evidence-manifest/gate-report | Must |
| 版本演进 | version/roadmap/release/evolution-summary | Should |
| CLI 入口 | beacon 命令行工具 | Must |
| Skill 集成 | /beacon:* 技能调用 | Must |

### 交付产物

- PRD 文档: `docs/beacon/v1.0.0/prd/beacon-core.md`
- 用户故事: `docs/beacon/v1.0.0/user-story/beacon-core.md`
- 测试用例: `docs/beacon/v1.0.0/qa/test-cases/beacon-core.md`
- 证据三件套
- Gate 终态报告

---

## Out of Scope

| 功能 | 原因 |
|------|------|
| 具体代码实现 | 定位为产品工作流工具，非开发框架 |
| 第三方集成 | v1.0.0 聚焦核心能力 |
| 云服务化 | 本地工具，暂无SaaS计划 |
| 移动端 | 非核心场景 |

---

## Done Criteria

| 条件 | 验证方式 |
|------|----------|
| 主流程可执行 | `beacon workflow start` 无报错 |
| 产物完整 | US/PRD/TC 三类文档齐全 |
| 证据可查 | 证据三件套可生成 |
| 门控可用 | Gate 判定准确 |
| 版本管理可用 | version/roadmap 命令正常 |

---

## Blocked Criteria

| 条件 | 状态 |
|------|------|
| open_question.blocking=true 未关闭 | Blocked |
| critical/high 冲突未解决 | Blocked |
| AC→TC 映射缺失 | Blocked |
| boundaries.md 关键字段缺失 | Blocked |
| 架构关键产物缺失 | Blocked |

---

## Dependencies

- 历史 PTK v3.7.0 成熟能力作为基础（命令层已统一 Beacon）
- Claude Code / Codex 环境
- Python 3.8+ / Typer

---

## 输入约束

| 参数 | 类型 | 范围 | 默认值 |
|------|------|------|--------|
| feature | string | 1-100 chars | required |
| topic | string | 1-200 chars | required |
| project | path | 有效目录 | cwd |
| mode | enum | strict/normal/debug/dry-run | strict |
| stage | enum | think/user-story/prd/test-case/release | all |

---

## Gate 门控约束

### Reason Codes (20+)

| Code | 说明 | 阻断级别 |
|------|------|---------|
| blocking_open_question_exists | 阻塞性问题存在 | Blocked |
| boundaries_missing | 边界文档缺失 | Blocked |
| boundaries_schema_invalid | 边界 schema 无效 | Blocked |
| terminal_artifact_missing | terminal 产物缺失 | Blocked |
| terminal_schema_invalid | terminal schema 无效 | Blocked |
| ac_tc_mapping_gap | AC→TC 映射缺口 | Blocked |
| scope_guard_violation | 范围守护违规 | Blocked |
| scope_guard_confirmation_pending | 范围守护确认待定 | Blocked |
| evidence_sha256_manifest_missing | 证据清单缺失 | Warn |
| evidence_sha256_manifest_mismatch | 证据清单不匹配 | Blocked |
| raw_command_log_missing | 命令日志缺失 | Warn |
| gate_consistency_report_missing | 门控报告缺失 | Warn |

---

## Team 团队约束

### 状态机

```
team-plan → team-prd → team-exec → team-verify → team-fix → terminal
```

### 运行时形态

| 形态 | 说明 |
|------|------|
| file | 纯文件状态机 (保底) |
| tmux | 多 worker 进程协作 |
| auto | 按配置自动选择 |

### 终态

| 终态 | 说明 |
|------|------|
| Pass | 所有阶段通过 |
| Blocked | max_fix_loops 达上限 |
| Cancelled | 手动取消 |

---

**Completed**: 2026-03-02
