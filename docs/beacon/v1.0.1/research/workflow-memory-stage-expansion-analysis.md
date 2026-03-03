# 预研：workflow_memory 阶段扩展与 release 专用校验（v1.0.1）

## 背景

当前 `workflow_memory` 的闭环阶段列表是 4 阶段（think/user-story/prd/test-case），但 `workflow.start --auto` 实际执行 6 阶段（含 implementation/verify）。

## 结论

### 1) 阶段列表应扩展为 6 阶段（先不含 release）

推荐闭环阶段：

- think
- user-story
- prd
- test-case
- implementation
- verify

不将 `release` 直接纳入统一闭环列表，避免事件模型不一致导致误判。

### 2) 新增 release 专用 memory 校验函数

release 当前事件模型偏“决策事件”（如 `release_decision_recorded`），与 workflow 阶段事件（start/context/finish/writeback）不同。

因此应新增 release 专用函数（示例：`check_release_memory_profile`），只校验 release 语义下的最小证据：

- release 决策事件存在
- 对应 evidence_ref 可追溯
- 与 gate/test 执行产物一致

### 3) 修 `compute_memory_metrics` 的 run_id 选择策略

默认“取最后事件 run_id”会被 `release:vX` 覆盖，导致 workflow run 被误判缺阶段。

应改为：

1. 优先使用显式传入 run_id
2. 否则优先选择最近的 workflow run（如 `run-*` 且包含 think/stage_started）
3. 再 fallback 到旧策略

### 4) 更新测试夹具与断言

- `tests/test_workflow_memory_lifecycle.py`：由 4 阶段断言升级为 6 阶段
- `tests/test_gate_memory_closure_contract.py`：fixture seed 从 4 阶段升级为 6 阶段
- 增加 release 专用 memory profile 测试，避免与 workflow 闭环混淆

## 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 直接把 release 加入统一阶段列表 | 高误判/假阻断 | 使用 release 专用校验函数 |
| run_id 选择不准 | 指标失真 | 采用 workflow run 优先策略 |
| 测试未同步 | 回归失败 | 同步升级 fixture 与断言 |

## 与 MVS 方案关系

该调整是 `beacon-fidelity-mvp-solution.md` 的工程落地点，确保：

- 不失真：指标反映真实 workflow run
- 不偏移：release 与 workflow 分层校验
- 可演进：memory 闭环覆盖实现与验证阶段
