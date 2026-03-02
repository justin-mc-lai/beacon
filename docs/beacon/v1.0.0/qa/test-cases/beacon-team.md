# Test Cases: Beacon Team v1.0.0 团队协作

**版本**: v1.0.0
**映射**: AC → TC
**状态**: Draft

---

## TC-001: Team 状态机

**映射 US**: US-001
**映射 AC**: AC-001 ~ AC-007

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-001-01 | 启动 team-plan | 进入 plan 阶段 | ⏳ |
| TC-001-02 | plan → prd 流转 | 进入 prd 阶段 | ⏳ |
| TC-001-03 | prd → exec 流转 | 进入 exec 阶段 | ⏳ |
| TC-001-04 | exec → verify 流转 | 进入 verify 阶段 | ⏳ |
| TC-001-05 | verify → fix 流转 (有缺陷) | 进入 fix 阶段 | ⏳ |
| TC-001-06 | fix → terminal 流转 | 进入 terminal 终态 | ⏳ |
| TC-001-07 | 所有阶段通过 | terminal: Pass | ⏳ |
| TC-001-08 | max_fix_loops 达上限 | terminal: Blocked | ⏳ |
| TC-001-09 | 手动取消 | terminal: Cancelled | ⏳ |

---

## TC-002: 运行时形态

**映射 US**: US-002
**映射 AC**: AC-001 ~ AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-002-01 | file 形态启动 | 使用文件状态机 | ⏳ |
| TC-002-02 | tmux 形态启动 | 启动 tmux 会话 | ⏳ |
| TC-002-03 | auto 形态启动 | 自动选择 file | ⏳ |
| TC-002-04 | 运行时切换形态 | 切换成功 | ⏳ |
| TMUX-002-05 | tmux worker 通信 | 消息正确传递 | ⏳ |
| TC-002-06 | tmux 会话断开 | 自动重连 | ⏳ |
| TC-002-07 | file 损坏恢复 | 自动重建 | ⏳ |

---

## TC-003: 双审查 Gate

**映射 US**: US-003
**映射 AC**: AC-001 ~ AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-003-01 | spec 未 pass 提交 quality | 阻断提交 | ⏳ |
| TC-003-02 | critical 未清零 evaluation | Blocked | ⏳ |
| TC-003-03 | high 未清零 evaluation | Blocked | ⏳ |
| TC-003-04 | critical/high 已清零 | Pass | ⏳ |
| TC-003-05 | --force 绕过 | Pass + Risk | ⏳ |
| TC-003-06 | spec pass + quality pass | evaluation Pass | ⏳ |
| TC-003-07 | 重新审查触发 | 重新计算 | ⏳ |

---

## TC-004: 状态管理

**映射 US**: US-004
**映射 AC**: AC-001 ~ AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-004-01 | 启动任务保存状态 | manifest.json 存在 | ⏳ |
| TC-004-02 | resume 恢复任务 | 状态正确恢复 | ⏳ |
| TC-004-03 | shutdown 终止任务 | 终态正确保存 | ⏳ |
| TC-004-04 | 状态文件损坏 | 自动重建空状态 | ⏳ |
| TC-004-05 | 并发写入状态 | 原子写入成功 | ⏳ |
| TC-004-06 | 状态文件权限错误 | 报错退出 | ⏳ |
| TC-004-07 | 磁盘满时保存 | 报错提示 | ⏳ |

---

## TC-005: Handoff 与报告

**映射 US**: US-005
**映射 AC**: AC-001 ~ AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-005-01 | plan→prd 迁移 | 生成 handoff 文档 | ⏳ |
| TC-005-02 | prd→exec 迁移 | 生成 handoff 文档 | ⏳ |
| TC-005-03 | 报告 Markdown 格式 | 正确生成 | ⏳ |
| TC-005-04 | 报告 JSON 格式 | 正确生成 | ⏳ |
| TC-005-05 | team report 命令 | 生成完整报告 | ⏳ |
| TC-005-06 | 报告包含耗时统计 | 数据正确 | ⏳ |
| TC-005-07 | 报告包含工作项 | 内容完整 | ⏳ |

---

## TC-006: Workers 管理

**映射 US**: US-006
**映射 AC**: AC-001 ~ AC-004

| TC ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-006-01 | 添加 Worker | workers 列表增加 | ⏳ |
| TC-006-02 | 移除 Worker | workers 列表移除 | ⏳ |
| TC-006-03 | 查询 Worker 状态 | 状态正确返回 | ⏳ |
| TC-006-04 | Worker 异常 | 自动告警 | ⏳ |
| TC-006-05 | Worker 超时 | 超时告警 | ⏳ |
| TC-006-06 | Worker 数量限制 | 超过限制报错 | ⏳ |
| TC-006-07 | Worker 优先级 | 按优先级调度 | ⏳ |

---

## 执行摘要

| 统计项 | 数值 |
|--------|------|
| 总 TC 数 | 37 |
| 已执行 | 0 |
| 通过 | 0 |
| 失败 | 0 |
| Pending | 37 |

---

**Status**: Draft
**Total**: 37 test cases
