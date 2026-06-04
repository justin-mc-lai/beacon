# Test Cases: Beacon Gate v1.0.0 门控检查

**版本**: v1.0.0
**映射**: AC → TC
**状态**: Draft

---

## TC-001: 门控判定

**映射 US**: US-001
**映射 AC**: AC-001, AC-002, AC-003, AC-004, AC-005

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-001-01 | 完整需求通过门控 | 判定 Pass | ⏳ |
| TC-001-02 | 有 blocking=true 未关闭 | 判定 Blocked | ⏳ |
| TC-001-03 | critical 冲突未解决 | 判定 Blocked | ⏳ |
| TC-001-04 | strict 模式阻断 | 正确 Blocked | ⏳ |
| TC-001-05 | normal 模式警告 | 仅警告不阻断 | ⏳ |
| TC-001-06 | --force 绕过 | Pass + Risk | ⏳ |
| TC-001-07 | debug 模式输出 | 详细调试信息 | ⏳ |
| TC-001-08 | dry-run 模式 | 模拟执行 | ⏳ |

---

## TC-002: Reason Codes 校验

**映射 US**: US-002
**映射 AC**: AC-001 ~ AC-005

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-002-01 | blocking=true 未关闭 | blocking_open_question_exists | ⏳ |
| TC-002-02 | boundaries.md 缺失 | boundaries_missing | ⏳ |
| TC-002-03 | AC→TC 映射缺失 | ac_tc_mapping_gap | ⏳ |
| TC-002-04 | terminal.json 缺失 | terminal_artifact_missing | ⏳ |
| TC-002-05 | Schema 无效 | boundaries_schema_invalid | ⏳ |
| TC-002-06 | Scope Guard 违规 | scope_guard_violation | ⏳ |
| TC-002-07 | 确认待定 | scope_guard_confirmation_pending | ⏳ |
| TC-002-08 | 命令日志缺失 | raw_command_log_missing | ⏳ |
| TC-002-09 | 证据清单缺失 | evidence_sha256_manifest_missing | ⏳ |
| TC-002-10 | 清单不完整 | evidence_sha256_manifest_incomplete | ⏳ |
| TC-002-11 | 清单不匹配 | evidence_sha256_manifest_mismatch | ⏳ |

---

## TC-003: 证据链校验

**映射 US**: US-003
**映射 AC**: AC-001 ~ AC-005

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-003-01 | 校验命令日志存在 | raw-command-log.jsonl 存在 | ⏳ |
| TC-003-02 | 校验清单完整 | evidence-manifest.json 完整 | ⏳ |
| TC-003-03 | 校验门控报告 | gate-consistency-report.json 存在 | ⏳ |
| TC-003-04 | 校验 terminal schema | terminal.json schema 有效 | ⏳ |
| TC-003-05 | 校验 boundaries 存在 | boundaries.md 存在 | ⏳ |
| TC-003-06 | 校验证据路径一致 | evidence_ref_path_style_consistent | ⏳ |
| TC-003-07 | 证据文件损坏 | 正确报错 | ⏳ |
| TC-003-08 | SHA256 校验失败 | evidence_sha256_manifest_mismatch | ⏳ |

---

## TC-004: Scope Guard 集成

**映射 US**: US-004
**映射 AC**: AC-001 ~ AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-004-01 | strict 模式 out-of-scope | Blocked | ⏳ |
| TC-004-02 | normal 模式 out-of-scope | 仅警告 | ⏳ |
| TC-004-03 | confirmation_pending | Blocked | ⏳ |
| TC-004-04 | --force 绕过 | Pass + Risk | ⏳ |
| TC-004-05 | 低风险越界 | Pass | ⏳ |
| TC-004-06 | 高风险越界确认 A | 补充范围 | ⏳ |
| TC-004-07 | 高风险越界确认 B | 记录但不补充 | ⏳ |
| TC-004-08 | 高风险越界确认 C | 回滚变更 | ⏳ |

---

## TC-005: 配置管理

**映射 US**: US-005
**映射 AC**: AC-001 ~ AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-005-01 | strict_default=true | 严格模式生效 | ⏳ |
| TC-005-02 | strict_default=false | 宽松模式生效 | ⏳ |
| TC-005-03 | warn_on_force=true | Force 时警告 | ⏳ |
| TC-005-04 | scope_guard_enabled=true | 范围守护生效 | ⏳ |
| TC-005-05 | scope_guard_enabled=false | 范围守护禁用 | ⏳ |
| TC-005-06 | 配置文件缺失 | 使用默认值 | ⏳ |
| TC-005-07 | 配置文件损坏 | 报错退出 | ⏳ |

---

## 执行摘要

| 统计项 | 数值 |
|--------|------|
| 总 TC 数 | 32 |
| 已执行 | 0 |
| 通过 | 0 |
| 失败 | 0 |
| Pending | 32 |

---

**Status**: Draft
**Total**: 32 test cases
