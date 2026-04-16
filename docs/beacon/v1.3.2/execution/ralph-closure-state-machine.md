# Beacon v1.3.2 Ralph 闭环状态机

## 目标

把 `ralph` 从“bridge 状态记录”提升成正式的 closure controller，并明确它只围绕：

- `implement`
- `qa`

进行持续推进。

## 核心判断

`ralph` 不是：

- 新的实现执行器
- 通用多代理系统
- 可以绕过 review / qa / gate 的自治平台

`ralph` 是：

- 围绕正式阶段结果做持续推进决策的控制层

## 状态机总览

```text
start
→ preflight
→ implement_round
→ review_gate
→ qa_round
→ closure_evaluate
→ continue_loop | stop
```

## 状态定义

### `start`

输入：

- feature
- docs version
- selected executor (`single|team`)
- runtime preference

输出：

- Ralph run id
- round = 0
- initial state payload

### `preflight`

检查：

- frozen requirement materials 是否存在
- implementation plan 是否可用
- git workflow contract 是否存在
- required QA baseline bundle 是否存在

若不满足：

- 进入 `human_blocked`

### `implement_round`

动作：

- 调用 `implement` executor
- `single` 或 `team`

输出：

- implement run result
- changed files / implementation summary
- review candidates

### `review_gate`

动作：

- 消费 formal review outputs

规则：

- 若 review 明确阻断，则进入 repair decision
- 若 review 可继续，则进入 `qa_round`

### `qa_round`

动作：

- 调用 `qa run`
- 必要时结合 `qa team-run`
- 轮次结束后可调用 `qa evolve`

输出：

- execution mode
- current round findings
- coverage / exhaustiveness
- continue decision
- repair handoff
- delta-aware rerun plan

### `closure_evaluate`

至少检查：

1. gate 是否通过
2. qa 是否达到 release-ready
3. 当前轮是否有新增边界/结构/coverage 增量
4. 是否存在明确 repair handoff
5. failure streak 是否达到上限
6. required_next_action 是什么

### `continue_loop`

如果满足继续条件：

- round + 1
- 选择下一轮 executor / qa path
- 进入下一轮 `implement_round` 或直接 `qa_round`

### `stop`

终态只允许：

- `release_ready`
- `human_blocked`
- `budget_exhausted`

## 转移规则

### `start -> preflight`

总是发生。

### `preflight -> implement_round`

条件：

- 冻结 requirement materials 完整
- implementation plan 完整
- QA baseline bundle 可用

### `preflight -> human_blocked`

条件：

- requirement truth 缺失
- git workflow contract 缺失
- QA baseline bundle 缺失

### `implement_round -> review_gate`

条件：

- implement 执行完成

### `review_gate -> qa_round`

条件：

- formal review 未阻断

### `review_gate -> continue_loop`

条件：

- review 给出明确 repair action

### `qa_round -> closure_evaluate`

条件：

- 当前轮 QA 结束

### `closure_evaluate -> release_ready`

条件：

- gate pass
- qa ready for release
- evidence 与 exhaustiveness 充足

### `closure_evaluate -> continue_loop`

条件：

- 仍有 repair handoff
- 或仍有可追的边界 / 覆盖增量空间
- 且 failure streak 未超限

### `closure_evaluate -> budget_exhausted`

条件：

- failure streak / budget / round cap 达上限

### 任意状态 -> `human_blocked`

条件：

- 遇到必须人类决定的 blocker
- requirement scope 需要重开
- 环境或权限缺失导致无法继续

## 控制面复用

Ralph 必须复用现有：

- `failure_streak`
- `escalation_level`
- `required_next_action`
- `checkpoint`

而不是新造一套并行控制面。

## 每轮最小输出合同

每一轮至少应记录：

- `round_id`
- `executor`
- `qa_execution_mode`
- `browser_runner_family`
- `new_findings_count`
- `new_boundary_count`
- `new_structure_inference_count`
- `coverage_delta`
- `repair_handoff_ref`
- `recommended_next_action`

## 终态合同

### `release_ready`

表示：

- implement / qa / gate 已闭合
- 当前轮没有阻断性缺口
- 可以进入 formal release decision

### `human_blocked`

表示：

- 需要人类补 requirement、环境、权限或方向决策

### `budget_exhausted`

表示：

- 闭环在当前预算或 failure streak 上限内未达到 release-ready
- 系统应输出 stop reason 与建议的人类下一步

## Guardrails

1. Ralph 不得直接改写冻结 requirement truth
2. Ralph 不得绕过 formal review / qa / gate
3. Ralph 不得无限循环
4. Ralph 必须把 stop reason 和 recommended next action 留为 durable artifact
