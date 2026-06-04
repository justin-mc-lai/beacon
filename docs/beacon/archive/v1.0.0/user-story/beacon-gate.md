# User Story: Beacon Gate v1.0.0 门控检查

**版本**: v1.0.0
**来源**: 历史 PTK gate Skill 对齐（命令层已统一 Beacon）
**状态**: Draft

---

## US-001: Gate 门控检查

**作为** 研发负责人
**我希望** 获得明确的交付终态判定
**以便** 准确评估项目可发布性

### 验收标准 (AC)

| ID | 标准 | 验证方式 |
|----|------|----------|
| AC-001 | 门控判定结果为 Pass/Blocked/Cancelled 之一 | 多种场景测试 |
| AC-002 | 阻断规则触发时正确判定 Blocked | 阻断场景测试 |
| AC-003 | 支持 strict/normal/debug/dry-run 模式 | 模式切换测试 |
| AC-004 | Blocked 时 reason codes 清晰可查 | 结果校验 |
| AC-005 | 支持 --force 但记录风险 | 风险日志测试 |

---

## US-002: Reason Codes 校验

**作为** 质量工程师
**我希望** 门控返回详细的 reason codes
**以便** 快速定位阻断原因

### 验收标准 (AC)

| ID | 标准 | 验证方式 |
|----|------|----------|
| AC-001 | 支持 20+ 标准 reason codes | 代码审查 |
| AC-001 | blocking_open_question_exists 正确检测 | 场景测试 |
| AC-002 | boundaries_missing 正确检测 | 场景测试 |
| AC-003 | ac_tc_mapping_gap 正确检测 | 场景测试 |
| AC-004 | scope_guard_violation 正确检测 | 场景测试 |
| AC-005 | evidence_sha256_manifest_* 完整性校验 | 场景测试 |

---

## US-003: 证据

**作为** 审计人员
链校验**我希望** 门控验证完整证据链
**以便** 支持交付审计

### 验收标准 (AC)

| ID | 标准 | 验证方式 |
|----|------|----------|
| AC-001 | 校验 raw-command-log.jsonl 存在 | 文件检查 |
| AC-002 | 校验 evidence-manifest.json 完整性 | 完整性测试 |
| AC-003 | 校验 gate-consistency-report.json | 报告测试 |
| AC-004 | 校验 terminal.json schema 有效性 | Schema 校验 |
| AC-005 | 校验 boundaries.md 存在 | 文件检查 |

---

## US-004: Scope Guard 集成

**作为** 项目经理
**我希望** Gate 集成 Scope Guard 检测
**以便** 及时发现范围漂移

### 验收标准 (AC)

| ID | 标准 | 验证方式 |
|----|------|----------|
| AC-001 | strict 模式下检测 out-of-scope 溢出 | 越界测试 |
| AC-002 | 检测 scope_guard_confirmation_pending | 确认测试 |
| AC-003 | 高风险项自动 Blocked | 阻断测试 |
| AC-004 | 支持 --force 绕过但记录风险 | 风险日志 |

---

## US-005: 配置管理

**作为** 运维工程师
**我希望** 通过配置文件管理 Gate 行为
**以便** 适配不同项目需求

### 验收标准 (AC)

| ID | 标准 | 验证方式 |
|----|------|----------|
| AC-001 | 支持 config.yaml 配置 | 配置测试 |
| AC-002 | strict_default: true/false 生效 | 配置测试 |
| AC-003 | warn_on_force: true/false 生效 | 配置测试 |
| AC-004 | scope_guard_enabled: true/false 生效 | 配置测试 |

---

## 元数据

| 字段 | 值 |
|------|-----|
| 版本 | v1.0.0 |
| 状态 | Draft |
| 总 US 数 | 5 |
| 总 AC 数 | 20 |
