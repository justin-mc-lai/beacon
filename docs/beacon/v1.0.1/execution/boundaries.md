# Execution Boundaries - v1.0.1

## Scope In

- UI 假通过防护规则增强
- 关键动作证据强校验
- Verify/Gate 证据链闭环
- Workflow memory 闭环阶段扩展为 6 阶段（不含 release）
- 新增 release 专用 memory 校验 profile
- 修复 compute_memory_metrics 默认 run_id 选择失真
- 升级 workflow_memory / gate_memory_closure 测试夹具

## Scope Out

- 全量视觉回归平台
- 跨仓库测试基建重构

## Guardrails

- 不得引入 silent pass
- 失败必须产出 reason_code
- 关键动作证据缺失必须失败

## Test Status (2026-03-03)

### Current Test Coverage

| 指标 | 数值 |
|------|------|
| 测试总数 | 151 |
| 通过 | 150 |
| 失败 | 1 |
| 执行时间 | 3.54s |

### Failing Test

```
tests/test_compat_regression_docs_examples.py::test_pyproject_should_expose_ptk_console_script
```

**Root Cause**: `pyproject.toml` 缺少 console script 配置

**Fix Required**:
```toml
[project.scripts]
ptk = "beacon.main:app"
beacon-think = "beacon.commands.think:app"
```

### AC Test Matrix Status

| AC ID | 测试状态 | 说明 |
|-------|----------|------|
| AC-001 | Pending | UI层无命令不得PASS |
| AC-002 | Pending | 关键动作证据缺失即FAIL |
| AC-003 | Pending | 证据文件必须存在且可解析 |
| AC-004 | Pending | status输出应包含可诊断字段 |
| AC-005 | Pending | gate strict/debug必须识别执行缺口 |
| AC-006 | Pending | workflow verify与auto-test行为一致 |
| AC-007 | Pending | 参数/断言异常不得silent pass |
| AC-008 | Pending | workflow memory 6阶段闭环 |
| AC-009 | Pending | release 专用 memory 校验函数 |
| AC-010 | Pending | 默认 run_id 优先 workflow run |
| AC-011 | Pending | workflow_memory fixture 升级为6阶段 |
| AC-012 | Pending | gate_memory_closure fixture 升级为6阶段 |

### Coverage Gap Analysis

| 分类 | 命令数 | 测试覆盖 |
|------|--------|----------|
| 工作流 (workflow) | 3 | ✅ 已有 |
| 思考 (think) | 7 | ⚠️ 少量 |
| 文档生成 (user-story, prd, test-case) | 6 | ❌ 缺失 |
| 分析 (brainstorm, design, jtbd) | 3 | ❌ 缺失 |
| 优先级 (kano, moscow, roadmap) | 3 | ❌ 缺失 |
| 测试发布 (auto-test, test-progress, release) | 3 | ✅ 部分 |
| 运维 (doctor, status, debug) | 6 | ❌ 缺失 |
| 记忆 (save, recall, remember) | 3 | ✅ 已有 |

### v1.0.1 Test Priorities

1. **P0 (Immediate)**: 修复 pyproject.toml 失败测试
2. **P1 (This Sprint)**: 实现 AC-001 ~ AC-012 对应 TC 与 gate 校验
3. **P2 (Next Sprint)**: 补充 release memory profile 专项回归
