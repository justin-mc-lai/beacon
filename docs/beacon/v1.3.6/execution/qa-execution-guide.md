# QA 执行指南

**版本**: v1.3.6  
**命令**: `beacon qa`  
**职责**: QA 主表面 - v1.1.10 精度感知验证

---

## 一、命令概览

### 1.1 核心职责

`beacon qa` 是 QA 验证阶段的主表面，负责：

1. **QA9 矩阵验证**: 9种 QA 类型全覆盖
2. **Feature-aware QA**: 特性感知的 QA 执行
3. **Auto-test 集成**: 自动化测试 + 修复循环
4. **Team mode**: QA 团队表面物化
5. **Session 管理**: QA 会话持久化

### 1.2 QA9 矩阵

| QA 类型 | 描述 | 示例 |
|---------|------|------|
| **functional** | 功能测试 | 核心业务逻辑验证 |
| **smoke** | 冒烟测试 | 快速验证基本功能 |
| **unit** | 单元测试 | 函数级别测试 |
| **interface** | 接口测试 | API 契约验证 |
| **contract** | 契约测试 | 服务间契约 |
| **integration** | 集成测试 | 模块间集成 |
| **regression** | 回归测试 | 防止功能退化 |
| **exception** | 异常测试 | 错误处理验证 |
| **compatibility** | 兼容性测试 | 跨版本/平台兼容 |

---

## 二、使用方式

### 2.1 基本用法

```bash
# 运行全部 QA 类型
beacon qa run "feature-name" --version v1.3.6

# 运行特定 QA 类型
beacon qa run "feature-name" --version v1.3.6 --qa-types functional,unit

# 运行 QA9 全矩阵
beacon qa run "feature-name" --version v1.3.6 --scope qa9

# 查看 QA 状态
beacon qa status --feature "feature-name" --version v1.3.6
```

### 2.2 高级用法

```bash
# Team 模式（并行 QA）
beacon qa run "feature-name" --version v1.3.6 --team-mode --team-size 3

# 指定 QA 矩阵路径
beacon qa run "feature-name" --version v1.3.6 --qa-matrix-path docs/beacon/v1.3.6/qa/matrix/feature-name.json

# Auto-test 集成
beacon qa run "feature-name" --version v1.3.6 --auto-test --repair-loop

# 精度感知模式
beacon qa run "feature-name" --version v1.3.6 --precision-aware --calibration-model v1.1.10
```

### 2.3 Session 管理

```bash
# 列出所有 QA session
beacon qa session list

# 查看当前 session
beacon qa session current

# 设置当前 session
beacon qa session set <session_id>

# 恢复 session
beacon qa session resume <session_id>
```

---

## 三、执行流程

### 3.1 完整执行流程

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: 预检查 (Preflight)                                  │
│ - 检查 implement-to-qa handoff                              │
│ - 加载 QA 矩阵                                               │
│ - 验证测试用例完整性                                         │
│ - 评估 delegation readiness                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: 初始化 (Initialization)                             │
│ - 创建 QA session                                            │
│ - 物化 feature QA matrix                                     │
│ - 构建 feature QA plan                                       │
│ - 初始化 QA status                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: 执行 (Execution)                                    │
│ - Standard: 顺序执行 QA9 矩阵                                │
│ - Team: 并行执行，物化 QA team surface                      │
│ - Auto-test: 自动化测试 + 修复循环                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: 验证 (Verification)                                 │
│ - 收集 verification writeback                                │
│ - 更新 feature QA status                                     │
│ - 写入 QA matrix evidence                                    │
│ - 刷新 QA calibration model                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: 收尾 (Finalization)                                 │
│ - 生成 exhaustiveness report                                 │
│ - 更新 coverage summary                                      │
│ - 记录 verification writeback                                │
│ - 保存 QA session                                            │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Feature-aware QA 流程

Feature-aware QA 是 v1.1.10 引入的特性感知 QA：

```python
# 1. 构建 feature QA plan
feature_qa_plan = build_feature_qa_plan(
    feature="feature-name",
    version="v1.3.6",
    qa_types=["functional", "unit", "integration"]
)

# 2. 物化 feature QA matrix
feature_qa_matrix = materialize_feature_qa_matrix(
    feature="feature-name",
    version="v1.3.6",
    plan=feature_qa_plan
)

# 3. 执行 feature-aware QA
for qa_type in feature_qa_plan["qa_types"]:
    result = execute_qa_type(
        feature="feature-name",
        qa_type=qa_type,
        matrix=feature_qa_matrix[qa_type]
    )
    
    # 4. 写入 evidence
    writeback_feature_matrix_evidence(
        feature="feature-name",
        qa_type=qa_type,
        evidence=result["evidence"]
    )

# 5. 更新 feature QA status
write_feature_qa_status(
    feature="feature-name",
    version="v1.3.6",
    status={
        "completed_types": ["functional", "unit", "integration"],
        "passed": True,
        "coverage": 92.5
    }
)
```

### 3.3 Team Mode 流程

Team 模式支持并行 QA：

```python
# 1. 物化 QA team surface
qa_team_contract = qa_team_contract(
    feature="feature-name",
    version="v1.3.6",
    qa_types=["functional", "unit", "integration"]
)

# 2. 构建上下文隔离
context_isolation = build_context_isolation(
    feature="feature-name",
    version="v1.3.6",
    handoff=load_implement_to_qa_handoff("feature-name")
)

# 3. 生成 worker spec
workers = []
for qa_type in qa_team_contract["qa_types"]:
    worker = {
        "worker_id": f"qa-{qa_type}",
        "qa_type": qa_type,
        "context": context_isolation,
        "matrix": feature_qa_matrix[qa_type]
    }
    write_worker_spec(worker["worker_id"], worker)
    workers.append(worker)

# 4. 启动 tmux workers
spawn_tmux_workers(workers)

# 5. 等待结果
results = wait_for_worker_results(workers)

# 6. 合并结果
merged_status = merge_qa_results(results)
write_feature_qa_status("feature-name", "v1.3.6", merged_status)
```

### 3.4 Auto-test 修复循环

Auto-test 集成支持自动化测试 + 修复循环：

```python
# 1. 运行 auto-test
auto_test_result = run_auto_test(
    feature="feature-name",
    version="v1.3.6",
    test_types=["unit", "integration"]
)

# 2. 检查失败
if auto_test_result["failed_count"] > 0:
    # 3. 启动修复循环
    for failure in auto_test_result["failures"]:
        # 3.1 分析失败原因
        diagnosis = diagnose_test_failure(failure)
        
        # 3.2 生成修复建议
        repair_suggestion = generate_repair_suggestion(diagnosis)
        
        # 3.3 应用修复
        apply_repair(repair_suggestion)
        
        # 3.4 重新运行测试
        retest_result = rerun_test(failure["test_id"])
        
        # 3.5 更新证据
        update_evidence_manifest(failure["test_id"], retest_result)

# 4. 最终验证
final_result = run_auto_test(
    feature="feature-name",
    version="v1.3.6",
    test_types=["unit", "integration"]
)

# 5. 写入 QA status
write_feature_qa_status("feature-name", "v1.3.6", {
    "auto_test_passed": final_result["failed_count"] == 0,
    "coverage": final_result["coverage"]
})
```

---

## 四、关键概念

### 4.1 QA Session

QA session 是 QA 执行的持久化状态：

```json
{
  "session_id": "<uuid>",
  "feature": "feature-name",
  "version": "v1.3.6",
  "status": "in_progress",
  "qa_types": ["functional", "unit", "integration"],
  "started_at": "2026-04-21T16:00:00Z",
  "current_qa_type": "functional",
  "results": {
    "functional": {
      "status": "completed",
      "passed": true,
      "evidence": {...}
    }
  }
}
```

**Session 状态**:
- `pending`: 等待开始
- `in_progress`: 执行中
- `completed`: 已完成
- `failed`: 失败
- `paused`: 暂停

### 4.2 Feature QA Matrix

Feature QA matrix 是特性级别的 QA 矩阵：

```json
{
  "feature": "feature-name",
  "version": "v1.3.6",
  "qa_types": {
    "functional": {
      "test_cases": [
        {
          "id": "TC-001",
          "description": "验证核心功能",
          "steps": [...],
          "expected": "...",
          "priority": "high"
        }
      ]
    },
    "unit": {
      "test_cases": [...]
    }
  }
}
```

### 4.3 Precision-aware QA

Precision-aware QA 是 v1.1.10 引入的精度感知 QA：

**核心思想**:
- 根据历史数据校准 QA 精度
- 识别高风险区域，增加测试覆盖
- 动态调整 QA 策略

**Calibration Model**:
```json
{
  "model_version": "v1.1.10",
  "feature": "feature-name",
  "calibration_data": {
    "historical_failures": [
      {"qa_type": "functional", "failure_rate": 0.05},
      {"qa_type": "integration", "failure_rate": 0.12}
    ],
    "risk_areas": [
      {"area": "auth", "risk_score": 0.8},
      {"area": "payment", "risk_score": 0.9}
    ]
  },
  "recommended_qa_types": ["functional", "integration", "exception"]
}
```

### 4.4 Exhaustiveness Report

Exhaustiveness report 评估 QA 覆盖的完整性：

```json
{
  "feature": "feature-name",
  "version": "v1.3.6",
  "exhaustiveness_score": 0.92,
  "coverage_breakdown": {
    "functional": 1.0,
    "unit": 0.95,
    "integration": 0.88,
    "exception": 0.85
  },
  "gaps": [
    {
      "qa_type": "exception",
      "missing_scenarios": ["timeout handling", "network failure"]
    }
  ]
}
```

---

## 五、故障排查

### 5.1 常见错误

#### 错误 1: Implement-to-QA handoff 不存在

```
Error: Implement-to-QA handoff not found
- Expected: .beacon/implement/<run_id>/implement-to-qa-handoff.json
```

**解决方案**:
```bash
# 先运行 implement
beacon implement run "feature-name" --version v1.3.6

# 再运行 qa
beacon qa run "feature-name" --version v1.3.6
```

#### 错误 2: QA 矩阵不完整

```
Error: QA matrix incomplete
- Missing qa_types: ["exception", "compatibility"]
```

**解决方案**:
```bash
# 重新生成测试用例（包含 QA9 矩阵）
beacon test-case create "feature-name" --version v1.3.6 --qa9

# 再运行 qa
beacon qa run "feature-name" --version v1.3.6
```

#### 错误 3: Auto-test 失败

```
Error: Auto-test failed
- Failed tests: 3
- Coverage: 65% (below threshold 80%)
```

**解决方案**:
```bash
# 启动修复循环
beacon qa run "feature-name" --version v1.3.6 --auto-test --repair-loop

# 或者手动修复后重新运行
beacon qa run "feature-name" --version v1.3.6 --auto-test
```

### 5.2 调试技巧

#### 查看 QA session

```bash
# QA session 保存在
cat .beacon/qa/status.json

# 查看当前 session
beacon qa session current
```

#### 查看 feature QA status

```bash
# Feature QA status 保存在
cat .beacon/qa/features/<feature-slug>/status.json
```

#### 查看 QA matrix evidence

```bash
# QA matrix evidence 保存在
cat .beacon/qa/features/<feature-slug>/matrix-evidence.json
```

---

## 六、最佳实践

### 6.1 选择合适的 QA 类型

| 特性类型 | 推荐 QA 类型 | 理由 |
|---------|-------------|------|
| 核心业务逻辑 | functional + unit + integration | 全面覆盖 |
| API 接口 | interface + contract + exception | 契约验证 + 异常处理 |
| UI 交互 | functional + smoke + compatibility | 快速验证 + 兼容性 |
| 数据处理 | unit + integration + regression | 防止数据错误 |

### 6.2 使用 Team Mode

对于大型特性，建议使用 Team mode 并行 QA：

```bash
# Team mode 并行执行
beacon qa run "feature-name" --version v1.3.6 --team-mode --team-size 3
```

**优势**:
- 并行执行，提高效率
- 上下文隔离，避免干扰
- 结果合并，统一报告

### 6.3 启用 Precision-aware QA

对于高风险特性，建议启用 precision-aware QA：

```bash
# Precision-aware QA
beacon qa run "feature-name" --version v1.3.6 --precision-aware --calibration-model v1.1.10
```

**优势**:
- 根据历史数据校准精度
- 识别高风险区域
- 动态调整 QA 策略

### 6.4 使用 Auto-test 修复循环

对于自动化测试，建议启用修复循环：

```bash
# Auto-test + 修复循环
beacon qa run "feature-name" --version v1.3.6 --auto-test --repair-loop
```

**优势**:
- 自动诊断失败原因
- 自动生成修复建议
- 自动重新运行测试

---

## 七、与其他命令的集成

### 7.1 与 Implement 的集成

```bash
# Implement 完成后，自动写入 implement-to-qa handoff
beacon implement run "feature-name" --version v1.3.6

# QA 读取 handoff
beacon qa run "feature-name" --version v1.3.6
```

### 7.2 与 Test Case 的集成

```bash
# Test Case 生成 QA9 矩阵
beacon test-case create "feature-name" --version v1.3.6 --qa9

# QA 读取矩阵
beacon qa run "feature-name" --version v1.3.6
```

### 7.3 与 Release 的集成

```bash
# QA 完成后，更新 coverage summary
beacon qa run "feature-name" --version v1.3.6

# Release 读取 coverage
beacon release check --version v1.3.6
```

---

## 八、参考

### 8.1 相关文件

- `beacon/commands/qa.py`: QA 命令主文件
- `beacon/utils/qa_feature.py`: Feature-aware QA 工具
- `beacon/utils/qa_runtime.py`: QA session 管理
- `beacon/utils/qa_precision.py`: Precision-aware QA
- `beacon/utils/exhaustiveness.py`: Exhaustiveness report

### 8.2 相关命令

- `beacon implement`: 实现执行
- `beacon test-case`: 测试用例生成
- `beacon auto-test`: 自动化测试
- `beacon release`: 发布管理

### 8.3 相关文档

- `docs/beacon/global-boundaries.md`: 全局边界约束
- `docs/beacon/v1.3.6/qa/test-cases/`: 测试用例目录
- `docs/beacon/v1.3.6/execution/architecture-blueprint.md`: 架构蓝图

---

**文档版本**: v1.3.6  
**最后更新**: 2026-04-21  
**维护者**: Beacon Team
