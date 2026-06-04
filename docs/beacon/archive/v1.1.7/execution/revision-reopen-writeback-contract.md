# Beacon v1.1.7 Revision / Reopen / Writeback Contract

## 1. 核心原则

### 原则 1：冻结后的一切实现都必须绑定 revision

任何实现动作都必须能回答：
- 当前实现的是哪个 revision？
- 当前 revision 是由哪个 source revision 派生来的？
- 当前 revision 是否 superseded 了旧 revision？

### 原则 2：需求变更不能直接污染已冻结基线

正确行为：
- 提交 change / reopen
- 生成新 revision
- 旧 revision 保留历史
- 新 revision 重新 refined / freeze / implement / verify / accept

### 原则 3：writeback 不只是 summary，而是正式状态变化

必须允许以下写回：
- `implemented_by_run_id`
- `verified_by_run_id`
- `accepted_at`
- item status
- story status
- revision delivery status

## 2. Reopen 场景矩阵

| 场景 | 当前状态 | 期望行为 |
|------|----------|----------|
| A | Frozen | 创建新 revision，旧 frozen revision → superseded |
| B | Implementing | 当前 run 标记 superseded，新 revision 重新进入 refined/freeze |
| C | Verifying | 当前 revision 标记待重构，新 revision 重新 implement/verify |
| D | Accepted | 保留 accepted 历史，新 revision 重新闭环 |

## 3. Writeback 范围

### 3.1 Implement writeback

最少回写：
- `TASK-*` -> implemented
- `AC-*` -> implemented（若被覆盖）
- `implemented_by_run_id`
- `changed_files`

### 3.2 Verify writeback

最少回写：
- `TEST-*` -> passed / failed
- `AC-*` -> verified / failed
- `verified_by_run_id`
- verify evidence ref

### 3.3 Accept writeback

最少回写：
- story status -> accepted
- revision delivery_status -> accepted
- `accepted_at`
- `accepted_by`

## 4. Human / Machine 双面契约

### Human Surface
- `docs/beacon/<version>/user-story/*.md`
- `docs/beacon/<version>/prd/*.md`
- `docs/beacon/<version>/qa/test-cases/*.md`

### Machine Surface（目标）
- `docs/beacon/<version>/.machine/user-story/*.json`
- `docs/beacon/<version>/.machine/prd/*.json`（可后续扩展）
- `docs/beacon/<version>/.machine/qa/*.json`
- `docs/beacon/<version>/.machine/execution/*.json`

规则：
- machine JSON 是状态真相
- Markdown 是 projection，不得成为唯一状态源

## 5. 状态计算规则

### closure_complete = true 的必要条件
- 所有 required AC = verified
- 所有 required TEST = passed
- 无 blocking open items
- 当前 revision 未被 superseded

### next_stage 计算原则
- Draft / Refined -> Freeze
- Frozen -> Implementing
- Implemented -> Verifying
- Verifying -> Accepted / Blocked
- Accepted -> Released / Reopened

## 6. 结论

如果没有 revision / reopen / writeback contract：
- implement 只是临时执行
- verify 只是附加报告
- accepted 只是推测状态
- workflow 无法形成确定性闭环

因此 v1.1.7 必须把这三件事正式冻结为平台契约。

