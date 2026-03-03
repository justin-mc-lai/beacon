# PRD: Beacon Gate v1.0.0 门控检查

**状态**: Draft
**版本**: v1.0.0
**日期**: 2026-03-02

---

## 1. 背景与目标

### 1.1 背景

Beacon Gate 从历史 PTK gate Skill 升级而来，是交付门控检查的核心组件。当前命令入口统一为 Beacon。

### 1.2 目标

- **主要目标**: 实现 20+ 标准 reason codes 的门控校验
- **次要目标**: 支持 strict/normal/debug/dry-run 模式，集成 Scope Guard

---

## 2. 功能需求

### 2.1 门控判定

**FR-001**: 终态判定

- 执行结果判定: Pass / Blocked / Cancelled
- 支持 --force 绕过但记录风险

**FR-002**: 阻断规则

| 规则 | 说明 |
|------|------|
| blocking_open_question_exists | blocking=true 的 open question 未关闭 |
| boundaries_missing | boundaries.md 缺失 |
| ac_tc_mapping_gap | AC→TC 映射缺口 |
| scope_guard_violation | Scope Guard 检测到高风险溢出 |

### 2.2 Reason Codes

**FR-003**: 标准 Reason Codes (20+)

| Code | 说明 |
|------|------|
| blocking_open_question_exists | 阻塞性问题存在 |
| boundaries_missing | 边界文档缺失 |
| boundaries_schema_invalid | 边界 schema 无效 |
| terminal_artifact_missing | terminal 产物缺失 |
| ac_tc_mapping_gap | AC→TC 映射缺口 |
| scope_guard_violation | 范围守护违规 |
| scope_guard_confirmation_pending | 范围守护确认待定 |
| evidence_sha256_manifest_* | 证据完整性校验 |
| raw_command_log_missing | 命令日志缺失 |
| gate_consistency_report_* | 门控一致性报告 |

### 2.3 证据链校验

**FR-004**: 证据三件套

| 证据类型 | 文件 | 描述 |
|----------|------|------|
| 命令日志 | raw-command-log.jsonl | 所有命令记录 |
| 证据清单 | evidence-manifest.json | 产物完整性 |
| 门控报告 | gate-consistency-report.json | 终态判定 |

### 2.4 模式支持

**FR-005**: 运行模式

| 模式 | 说明 |
|------|------|
| strict | 默认，阻断不合格流转 |
| normal | 警告但不阻断 |
| debug | 调试模式，详细输出 |
| dry-run | 模拟执行，不实际修改 |

---

## 3. 配置

```yaml
# .beacon/config.yaml
gate:
  strict_default: true
  mode: strict
  warn_on_force: true
  log_risks: true
  scope_guard_enabled: true
```

---

## 4. CLI 命令

```bash
# 门控检查
beacon gate check think
beacon gate check user-story --strict
beacon gate check prd --json
beacon gate check test-case --force

# 列出所有门控项
beacon gate list
```

---

## 5. 验收标准

- [ ] 20+ reason codes 正确返回
- [ ] strict/normal/debug/dry-run 模式生效
- [ ] 证据链完整校验
- [ ] Scope Guard 集成
- [ ] 配置持久化

---

**Created**: 2026-03-02
**Version**: 1.0.0
**Status**: Draft
