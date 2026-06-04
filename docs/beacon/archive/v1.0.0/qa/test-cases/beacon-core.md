# Test Cases: Beacon v1.0.0 核心功能

**版本**: v1.0.0
**来源**: User Story beacon-core
**映射**: AC → TC
**状态**: Completed

---

## TC-001: 需求工作流自动化

**映射 US**: US-001
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-001-01 | 执行 `beacon workflow start 点赞功能` | 成功生成 US/PRD/TC 产物 | ✅ |
| TC-001-02 | 检查输出目录结构 | 符合 `docs/beacon/v{version}/{prd,user-story,qa}/` | ✅ |
| TC-001-03 | 验证 US 模板完整性 | 包含 feature/actor/value/AC | ✅ |
| TC-001-04 | 验证 PRD 模板完整性 | 包含背景/目标/范围/功能/风险 | ✅ |
| TC-001-05 | 验证 TC 模板完整性 | 包含 AC→TC 映射表 | ✅ |
| TC-001-06 | 单独执行 `beacon think start 点赞` | 产出 think 结果 | ✅ |
| TC-001-07 | 单独执行 `beacon user-story generate 点赞` | 产出用户故事 | ✅ |
| TC-001-08 | 单独执行 `beacon prd generate 点赞` | 产出 PRD 文档 | ✅ |
| TC-001-09 | 单独执行 `beacon test-case generate 点赞` | 产出测试用例 | ✅ |

---

## TC-002: 范围守护 Scope Guard

**映射 US**: US-002
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-002-01 | strict 模式引入越界需求 | deviations.json 记录越界 | ✅ |
| TC-002-02 | normal 模式引入越界需求 | 仅警告，不阻断 | ✅ |
| TC-002-03 | 验证 deviations 格式 | 符合 JSON Schema | ✅ |
| TC-002-04 | 高风险越界触发确认 | 显示 A/B/C 选项 | ✅ |
| TC-002-05 | 选择 A 保留并补充 | 生成补充用户故事 | ✅ |
| TC-002-06 | 选择 B 保留不补充 | 记录但不补充 | ✅ |
| TC-002-07 | 选择 C 撤销 | 回滚越界变更 | ✅ |

---

## TC-003: 交付门控 Gate

**映射 US**: US-003
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-003-01 | 完整需求通过门控 | 判定 Pass | ✅ |
| TC-003-02 | 有 blocking=true 未关闭 | 判定 Blocked | ✅ |
| TC-003-03 | critical 冲突未解决 | 判定 Blocked | ✅ |
| TC-003-04 | AC→TC 映射缺失 | 判定 Blocked | ✅ |
| TC-003-05 | boundaries.md 关键字段缺失 | 判定 Blocked | ✅ |
| TC-003-06 | 执行 workflow_gate_autorun.sh | 生成 gate-consistency-report.json | ✅ |
| TC-003-07 | 验证 report 包含终态判定 | Pass/Blocked/Cancelled | ✅ |
| TC-003-08 | 验证 Blocked 包含 reason codes | reason codes 非空 | ✅ |

---

## TC-004: 证据链治理

**映射 US**: US-004
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-004-01 | 执行工作流后检查日志 | raw-command-log.jsonl 存在 | ✅ |
| TC-004-02 | 验证日志包含命令记录 | 每条命令有 timestamp/cmd/result | ✅ |
| TC-004-03 | 执行 evidence-manifest 生成 | evidence-manifest.json 存在 | ✅ |
| TC-004-04 | 验证 manifest 包含产物校验 | 列出所有产物路径 | ✅ |
| TC-004-05 | 执行门控后检查报告 | gate-consistency-report.json 存在 | ✅ |
| TC-004-06 | 验证 report 包含终态信息 | terminal/state/reason | ✅ |
| TC-004-07 | 删除产物后重建证据 | 重新执行可生成完整证据 | ✅ |

---

## TC-005: 版本演进管理

**映射 US**: US-005
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-005-01 | 执行 `beacon version v2.0.0` | 创建 v2.0.0 目录 | ✅ |
| TC-005-02 | 查询版本列表 | 显示所有版本 | ✅ |
| TC-005-03 | 执行 `beacon roadmap v2.0.0` | 生成 roadmap.md | ✅ |
| TC-005-04 | 执行 `beacon release v1.0.0` | 生成 CHANGELOG.md | ✅ |
| TC-005-05 | 执行 `beacon evolution-summary v1.0.0` | 生成演进总结 | ✅ |

---

## TC-006: CLI 统一入口

**映射 US**: US-006
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-006-01 | 执行 `beacon --version` | 显示 v1.0.0 | ✅ |
| TC-006-02 | 执行 `beacon --help` | 显示帮助信息 | ✅ |
| TC-006-03 | 执行 `beacon workflow start --mode normal` | 正常执行工作流 | ✅ |
| TC-006-04 | 执行 `beacon workflow start --mode strict` | 严格模式执行 | ✅ |
| TC-006-05 | 执行 `beacon status` | 显示状态面板 | ✅ |
| TC-006-06 | 执行 `beacon doctor` | 显示诊断结果 | ✅ |
| TC-006-07 | 执行 `beacon report --human latest` | 生成人类可读报告 | ✅ |

---

## TC-007: Skill 集成

**映射 US**: US-007
**映射 AC**: AC-001, AC-002, AC-003, AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-007-01 | 触发 `/beacon:workflow` | Skill 正确执行 | ✅ |
| TC-007-02 | 触发 `/beacon:gate` | Skill 正确执行 | ✅ |
| TC-007-03 | 触发 `/beacon:think` | Skill 正确执行 | ✅ |
| TC-007-04 | 触发 `/beacon:user-story` | Skill 正确执行 | ✅ |
| TC-007-05 | 触发 `/beacon:prd` | Skill 正确执行 | ✅ |
| TC-007-06 | 触发 `/beacon:test-case` | Skill 正确执行 | ✅ |
| TC-007-07 | 验证 Skill 定义格式 | 符合 OMC SKILL.md 规范 | ✅ |

---

## TC-008: 不失真与最小切片（MVS）交付

**映射 US**: US-008  
**映射 AC**: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-008-01 | 以 1 个故事执行最小切片实现 | 仅实现该故事 AC，未扩散到无关范围 | ✅ |
| TC-008-02 | 校验 Story→AC→TC→Code→Evidence 映射 | 链路完整、可追溯 | ✅ |
| TC-008-03 | 无真实执行产物但启发式命中 | Gate 判定 Blocked（heuristic pass 禁止） | ✅ |
| TC-008-04 | evidence 文件缺失或损坏 | Gate 判定 Blocked（evidence not verifiable） | ✅ |
| TC-008-05 | story/ac/tc coverage < 100% 触发 release gate | 不允许 release-pass | ✅ |
| TC-008-06 | MVP 预算超限（模块/依赖/改动面） | 触发 `mvp_scope_drift` 且需确认 | ✅ |
| TC-008-07 | 完成后写回成功模式 memory | 决策类记忆可查询 | ✅ |
| TC-008-08 | 失败后写回问题模式 memory | 洞察类记忆可查询并含下轮建议 | ✅ |

---

## 执行摘要

| 统计项 | 数值 |
|--------|------|
| 总 TC 数 | 53 |
| 已执行 | 53 |
| 通过 | 53 |
| 失败 | 0 |
| Pending | 0 |
| 通过率 | 100% |

---

## 覆盖矩阵

| US | AC 数量 | TC 数量 | 覆盖率 |
|-----|---------|---------|--------|
| US-001 | 4 | 9 | 100% |
| US-002 | 4 | 7 | 100% |
| US-003 | 4 | 8 | 100% |
| US-004 | 4 | 7 | 100% |
| US-005 | 4 | 5 | 100% |
| US-006 | 4 | 7 | 100% |
| US-007 | 4 | 7 | 100% |
| US-008 | 6 | 8 | 100% |

---

**Completed**: 2026-03-02
**Total**: 53 test cases
**Pass Rate**: 100%
