# 测试用例：Beacon v1.3.2 implement 三模式与迭代浏览器 QA 闭环

**Feature**: `beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa`  
**Version**: `v1.3.2`  
**Date**: `2026-04-14`  
**Status**: `planning line`

## 测试工件

- AC Matrix JSON：
  `docs/beacon/v1.3.2/.machine/qa/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.ac-test-matrix.json`
- QA9 Matrix JSON：
  `docs/beacon/v1.3.2/.machine/qa/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.qa9-matrix.json`
- Story Scenario Map JSON：
  `docs/beacon/v1.3.2/.machine/qa/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.story-scenario-map.json`

## 测试目标

这组测试用例要验证三件事：

1. `implement` 三模式的边界是否清晰且可执行
2. `qa` 是否被正式定义成浏览器原生、冻结材料驱动、顺序可迭代演进的第二执行面
3. `ralph` 是否能基于 `implement + qa` 的正式结果持续推进，直到明确终态

## 核心覆盖面

### A. 实现模式

- `single` 的最小执行面
- `team` 的 bounded multi-agent 协作面
- `ralph` 的闭环控制面

### B. QA 执行语义

- 冻结 `prd / user-story / test-case` 输入顺序
- 真实浏览器环境启动
- browser execution family：
  - `browser-cli`
  - `agent-browser`
  - `pageagent`
  - `browser-use`
- 多轮迭代与 auto research 增量

### C. 闭环与可观测性

- repair handoff
- 边界反馈
- 结构推演
- stop states
- `status/help` 的 mode / round / runner 可见性

## 测试用例

## TC-001：`single` 模式必须保持最小执行面

- Given：用户进入 `implement --mode single`
- When：执行一次小范围代码实现
- Then：不得创建 team worker lanes、tmux pane 或 HUD
- And：仍必须保留正式 review / qa / gate 后续动作
- Covers：`AC-001`

## TC-002：`team` 模式必须进入 bounded multi-agent runtime

- Given：用户进入 `implement --mode team`
- When：执行多文件 feature
- Then：必须生成 bounded worker lanes、role reports、worker evidence 与 HUD
- And：正式 writeback 仍由 Beacon stage owner 完成
- Covers：`AC-002`

## TC-003：`ralph` 只围绕 `implement + qa` 闭环推进

- Given：用户进入 `implement --mode ralph`
- When：执行持续闭环
- Then：闭环对象只能是 `implement + qa`
- And：不得直接改写冻结的 `prd / user-story / test-case`
- Covers：`AC-003`

## TC-004：`qa` 必须成为第二执行面

- Given：一次实现完成后进入 QA
- When：Beacon 组织浏览器验收与 repair handoff
- Then：QA 应负责浏览器验收、边界发现、结构推演与 handoff，而不是一次性收尾
- Covers：`AC-004`

## TC-005：QA 必须围绕冻结材料顺序推进

- Given：存在冻结的 `prd / user-story / test-case`
- When：Beacon 编译并执行 QA 场景
- Then：执行顺序必须体现冻结材料依赖
- And：不得脱离冻结材料自由扩 scope
- Covers：`AC-005`

## TC-006：QA 必须启动真实浏览器环境

- Given：目标项目存在真实页面、流程或交互
- When：执行浏览器验收
- Then：必须能够启动 browser execution family
- And：至少纳入 `browser-cli`、`agent-browser`、`pageagent`、`browser-use`
- Covers：`AC-006`

## TC-007：QA 必须支持顺序多轮迭代

- Given：存在第一轮浏览器执行结果
- When：进入第二轮及后续 QA
- Then：每轮必须根据上一轮 findings 调整下一轮场景优先级或重点
- And：每轮都必须保留自己的 summary 与 evidence
- Covers：`AC-007`

## TC-008：每轮 QA 必须带来新的 auto research 增量

- Given：连续两轮或多轮 QA
- When：比较各轮输出
- Then：每轮必须至少新增一种价值：
  - 新边界
  - 新页面状态
  - 新异常路径
  - 新 coverage closure
  - 新 repair handoff
- Covers：`AC-008`

## TC-009：QA 必须输出边界反馈与结构推演

- Given：Beacon 完成一轮浏览器验收
- When：检查 round summary 与 repair handoff
- Then：必须包含边界反馈、流程或页面结构推演、未覆盖区域说明
- Covers：`AC-009`

## TC-010：多轮 QA 必须逐轮打磨产品功能

- Given：功能仍未达到 release-ready
- When：继续执行下一轮 QA
- Then：下一轮目标应是提升功能正确性、验收路径完整性或产品边界清晰度
- And：不得只是重复跑同一套页面脚本
- Covers：`AC-010`

## TC-011：`ralph` 必须具备明确终态

- Given：`ralph` 驱动 `implement + qa` 闭环
- When：达到结束条件
- Then：必须进入 `release_ready`、`human_blocked` 或 `budget_exhausted` 之一
- Covers：`AC-011`

## TC-012：`status/help` 必须显示 mode / round / runner

- Given：系统处于任意执行轮次
- When：用户查看 `status` 或 `help`
- Then：至少应看到当前 mode、当前轮次、当前 browser runner / executor、当前 blocker 与推荐下一步
- Covers：`AC-012`

## TC-013：极简人类主流程必须继续沿袭

- Given：用户在 `v1.3.2` 中使用 Beacon
- When：查看对外公开主流程
- Then：主心智面仍应保持 `prd -> user-story -> test-case -> implement -> qa -> release`
- And：不得因 subagent/team 能力增强而扩张主流程
- Covers：`AC-013`

## TC-014：不得新增新的公开 team/subagent 主命令

- Given：`v1.3.2` 引入宿主原生 subagent/team 能力
- When：检查对外命令面
- Then：不得新增新的公开一级主命令来要求人类操作 team/subagent/precheck
- Covers：`AC-014`

## TC-015：Codex/Claude 路径必须使用宿主原生能力

- Given：Beacon 作为 skill 运行在 Codex 或 Claude 中
- When：进入 `team` 或 `ralph + team executor`
- Then：必须调用宿主原生 subagent/team 能力
- And：不得把 `omx` 作为正式目标运行时
- Covers：`AC-015`

## TC-016：两段预检查必须默认内嵌在 `implement/qa`

- Given：用户执行 `implement` 或 `qa`
- When：系统需要调起宿主原生 team subagent
- Then：必须先自动执行 `runtime-readiness` 与 `delegation-readiness`
- And：这些检查不应要求人类手动记忆为主流程命令
- Covers：`AC-016`

## TC-017：预检查对人类输出必须极简

- Given：precheck 或 delegation 失败
- When：系统向人类返回结果
- Then：应只返回极简阻断原因、推荐下一步与 fallback
- And：复杂 runtime / delegation 细节应保留在 machine-readable 输出中
- Covers：`AC-017`

## TC-018：宿主上下文必须唯一，不引入多运行时选择叙事

- Given：Beacon 作为 skill 运行在某一宿主环境中
- When：系统判断是否可进入原生 team subagent
- Then：只应判断当前宿主是否满足条件
- And：不得扩展成 Codex/Claude/OMX 多运行时选择或桥接叙事
- Covers：`AC-018`

## 建议执行节奏

### Round 1

- 验证 `single / team / ralph` 基本语义
- 验证 `qa` 是否成为第二执行面

### Round 2

- 验证冻结材料驱动顺序
- 验证 browser execution family 启动

### Round 3

- 验证多轮迭代、auto research 增量、边界反馈与结构推演

### Round 4

- 验证 Ralph stop states、repair handoff 与 `status/help` 可观测性

### Round 5

- 验证极简人类主流程是否保持稳定
- 验证宿主原生 subagent/team 调起与两段预检查是否被内嵌且对人类输出保持克制
