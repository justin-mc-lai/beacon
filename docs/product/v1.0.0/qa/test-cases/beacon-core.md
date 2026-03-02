# Test Cases: Beacon v1.0.0 核心功能

**版本**: v1.0.0
**来源**: User Story beacon-core
**映射**: AC → TC

---

## TC-001: 需求工作流自动化

**映射 US**: US-001
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|----------|------|
| TC-001-01 | 执行 `/beacon:workflow 点赞功能` | 成功生成 US/PRD/TC 产物 | TBD | Pending |
| TC-001-02 | 检查输出目录结构 | 符合 `docs/product/v{version}/{prd,user-story,qa}/` | TBD | Pending |
| TC-001-03 | 验证 US 模板完整性 | 包含 feature/actor/value/AC | TBD | Pending |
| TC-001-04 | 验证 PRD 模板完整性 | 包含背景/目标/范围/功能/风险 | TBD | Pending |
| TC-001-05 | 验证 TC 模板完整性 | 包含 AC→TC 映射表 | TBD | Pending |
| TC-001-06 | 单独执行 `/beacon:think 点赞` | 产出 think 结果 | TBD | Pending |
| TC-001-07 | 单独执行 `/beacon:user-story 点赞` | 产出用户故事 | TBD | Pending |
| TC-001-08 | 单独执行 `/beacon:prd 点赞` | 产出 PRD 文档 | TBD | Pending |
| TC-001-09 | 单独执行 `/beacon:test-case 点赞` | 产出台词测试用例 | TBD | Pending |

---

## TC-002: 范围守护 Scope Guard

**映射 US**: US-002
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|----------|------|
| TC-002-01 | strict 模式引入越界需求 | deviations.json 记录越界 | TBD | Pending |
| TC-002-02 | normal 模式引入越界需求 | 仅警告，不阻断 | TBD | Pending |
| TC-002-03 | 验证 deviations 格式 | 符合 JSON Schema | TBD | Pending |
| TC-002-04 | 高风险越界触发确认 | 显示 A/B/C 选项 | TBD | Pending |
| TC-002-05 | 选择 A 保留并补充 | 生成补充用户故事 | TBD | Pending |
| TC-002-06 | 选择 B 保留不补充 | 记录但不补充 | TBD | Pending |
| TC-002-07 | 选择 C 撤销 | 回滚越界变更 | TBD | Pending |

---

## TC-003: 交付门控 Gate

**映射 US**: US-003
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|----------|------|
| TC-003-01 | 完整需求通过门控 | 判定 Pass | TBD | Pending |
| TC-003-02 | 有 blocking=true 未关闭 | 判定 Blocked | TBD | Pending |
| TC-003-03 | critical 冲突未解决 | 判定 Blocked | TBD | Pending |
| TC-003-04 | AC→TC 映射缺失 | 判定 Blocked | TBD | Pending |
| TC-003-05 | boundaries.md 关键字段缺失 | 判定 Blocked | TBD | Pending |
| TC-003-06 | 执行 workflow_gate_autorun.sh | 生成 gate-consistency-report.json | TBD | Pending |
| TC-003-07 | 验证 report 包含终态判定 | Pass/Blocked/Cancelled | TBD | Pending |
| TC-003-08 | 验证 Blocked 包含 reason codes | reason codes 非空 | TBD | Pending |

---

## TC-004: 证据链治理

**映射 US**: US-004
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|----------|------|
| TC-004-01 | 执行工作流后检查日志 | raw-command-log.jsonl 存在 | TBD | Pending |
| TC-004-02 | 验证日志包含命令记录 | 每条命令有 timestamp/cmd/result | TBD | Pending |
| TC-004-03 | 执行 evidence-manifest 生成 | evidence-manifest.json 存在 | TBD | Pending |
| TC-004-04 | 验证 manifest 包含产物校验 | 列出所有产物路径 | TBD | Pending |
| TC-004-05 | 执行门控后检查报告 | gate-consistency-report.json 存在 | TBD | Pending |
| TC-004-06 | 验证 report 包含终态信息 | terminal/state/reason | TBD | Pending |
| TC-004-07 | 删除产物后重建证据 | 重新执行可生成完整证据 | TBD | Pending |

---

## TC-005: 版本演进管理

**映射 US**: US-005
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|----------|------|
| TC-005-01 | 执行 `/beacon:version v2.0.0` | 创建 v2.0.0 目录 | TBD | Pending |
| TC-005-02 | 查询版本列表 | 显示所有版本 | TBD | Pending |
| TC-005-03 | 执行 `/beacon:roadmap v2.0.0` | 生成 roadmap.md | TBD | Pending |
| TC-005-04 | 执行 `/beacon:release v1.0.0` | 生成 CHANGELOG.md | TBD | Pending |
| TC-005-05 | 执行 `/beacon:evolution-summary v1.0.0` | 生成演进总结 | TBD | Pending |

---

## TC-006: CLI 统一入口

**映射 US**: US-006
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|----------|------|
| TC-006-01 | 执行 `beacon --version` | 显示 v1.0.0 | TBD | Pending |
| TC-006-02 | 执行 `beacon --help` | 显示帮助信息 | TBD | Pending |
| TC-006-03 | 执行 `beacon run workflow --mode normal` | 正常执行工作流 | TBD | Pending |
| TC-006-04 | 执行 `beacon run workflow --mode strict` | 严格模式执行 | TBD | Pending |
| TC-006-05 | 执行 `beacon status` | 显示状态面板 | TBD | Pending |
| TC-006-06 | 执行 `beacon doctor` | 显示诊断结果 | TBD | Pending |
| TC-006-07 | 执行 `beacon report --human latest` | 生成人类可读报告 | TBD | Pending |

---

## TC-007: Skill 集成

**映射 US**: US-007
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|----------|------|
| TC-007-01 | 触发 `/beacon:workflow` | Skill 正确执行 | TBD | Pending |
| TC-007-02 | 触发 `/beacon:gate` | Skill 正确执行 | TBD | Pending |
| TC-007-03 | 触发 `/beacon:think` | Skill 正确执行 | TBD | Pending |
| TC-007-04 | 触发 `/beacon:user-story` | Skill 正确执行 | TBD | Pending |
| TC-007-05 | 触发 `/beacon:prd` | Skill 正确执行 | TBD | Pending |
| TC-007-06 | 触发 `/beacon:test-case` | Skill 正确执行 | TBD | Pending |
| TC-007-07 | 验证 Skill 定义格式 | 符合 OMC SKILL.md 规范 | TBD | Pending |

---

## 执行摘要

| 统计项 | 数值 |
|--------|------|
| 总 TC 数 | 45 |
| 已执行 | 0 |
| 通过 | 0 |
| 失败 | 0 |
| Pending | 45 |

---

## 下一步

1. 执行主路径: `/beacon:workflow 点赞功能`
2. 执行门控收口
3. 验证产物完整性
4. 标记 TC 状态
