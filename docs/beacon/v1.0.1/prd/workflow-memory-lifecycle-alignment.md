# PRD: Workflow Memory Lifecycle 对齐（v1.0.1）

## 1. 目标

将 Beacon 的 workflow memory 闭环从 4 阶段提升到 6 阶段，并将 release 校验改为专用 profile，避免指标与 gate 判定失真。

## 2. 范围

### In Scope

1. 扩展 workflow 闭环阶段为：`think/user-story/prd/test-case/implementation/verify`
2. 新增 release 专用 memory 校验函数（独立于 workflow 闭环）
3. 修复 `compute_memory_metrics` 默认 run_id 选择策略
4. 同步更新相关测试 fixture 与断言

### Out of Scope

- 将 release 强行并入通用阶段闭环
- 改造 memory 数据模型版本（保持 schema_version=1.0）

## 3. 功能需求

### FR-001 阶段列表扩展（6 阶段）

- 闭环阶段列表升级为：
  `("think", "user-story", "prd", "test-case", "implementation", "verify")`
- closure_complete 判定必须包含上述 6 阶段完整事件链。

### FR-002 release 专用 memory 校验

- 新增 release 专用校验逻辑（建议函数名：`check_release_memory_profile`）
- 仅校验 release 决策语义与证据一致性，不要求 release 具备 workflow 四件套。

### FR-003 run_id 选择策略修复

默认计算指标时：
1. 优先显式 run_id
2. 否则优先最近 workflow run（`run-*` 且具备 workflow 起始事件）
3. 最后 fallback 到全局最后事件 run_id

### FR-004 测试同步

- workflow_memory 生命周期测试升级为 6 阶段
- gate memory closure fixture 升级为 6 阶段
- 增加 release 专用校验路径测试

## 4. 验收标准（AC）

| AC ID | 验收项 |
|------|--------|
| AC-001 | 6 阶段 workflow run 在 memory_metrics 中可闭环（closure_complete=true） |
| AC-002 | release 事件不再导致 workflow 闭环误判缺阶段 |
| AC-003 | release 专用校验在证据缺失时阻断，在证据完整时通过 |
| AC-004 | 未传 run_id 时默认选择 workflow run 而非 release run |
| AC-005 | 指定 run_id 时仍可正确计算该 run 指标（兼容） |
| AC-006 | 相关测试 fixture 与断言均已升级并通过 |

## 5. 风险

| 风险 | 级别 | 缓解 |
|------|------|------|
| 回归影响旧测试 | 中 | 分层迁移 fixture + 增量测试 |
| release 校验逻辑遗漏 | 中 | 增加 release profile 专项测试 |
| run_id 选择误判 | 高 | 引入明确筛选条件与 fallback |

## 6. 关联文档

- `research/workflow-memory-stage-expansion-analysis.md`
- `research/beacon-fidelity-mvp-solution.md`
- `research/anti-overdesign-min-spec.md`
