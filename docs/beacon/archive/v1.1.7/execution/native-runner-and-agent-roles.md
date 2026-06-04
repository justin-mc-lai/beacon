# Beacon v1.1.7 Native Runner 与多角色 Agent 设计

## 1. 目标

v1.1.7 要求 Beacon 默认具备原生实现能力，因此需要把 `implement` 从 adapter-only 模式扩展为：

- `native-single`
- `native-team`
- `adapter-*`（保留兼容）

## 2. Native Runner 分层

### `native-single`

适合：
- 小需求
- 单 story
- 单一实现主线

职责：
- 读取 frozen revision
- 选择未完成 items
- 执行实现
- 产出 implementation summary
- 自动 writeback

### `native-team`

适合：
- 多 story
- 复杂需求
- 需要 review / test 并行

职责：
- 以角色方式拆任务
- 汇总 changed files / risks / verification
- 最终统一 writeback

## 3. 最小角色集

### 3.1 Planner / Orchestrator
- 解析 frozen revision
- 选择目标 story / item
- 分派给其他角色
- 统一汇总执行结果

### 3.2 Implementer
- 完成实际代码变更
- 记录 changed files
- 标记 implemented items

### 3.3 Reviewer
- 校验 spec drift
- 校验 architecture/scope drift
- 识别 overbuild / boundary break

### 3.4 Tester
- 运行 verify 所需测试
- 回写 `TEST-*` 与 `AC-*` 结果
- 形成 accept 前判断

## 4. 与现有 Beacon `team.py` 的关系

`team.py` 当前已有：
- `team-plan`
- `team-prd`
- `team-exec`
- `team-verify`
- `team-fix`

v1.1.7 应做的不是另起一个 team 系统，而是：

> 把 team 状态机能力并入 native-team implementation 主链。

## 5. Runner 输出契约

native runner 至少输出：

- `run_id`
- `revision_id`
- `status`
- `summary`
- `changed_files`
- `verification[]`
- `artifact_updates`
- `implemented_items[]`
- `verified_items[]`
- `blocked_items[]`

## 6. 结论

Beacon 的 native runner 不是为了替代所有 adapter，而是为了：

- 保证默认闭环能力存在
- 保证 story item writeback 存在
- 保证 team 模式不是外挂功能，而是 implementation 主链的一部分

