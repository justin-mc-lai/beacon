# Think: Debug Feedback Loop（v1.1.0）

## 1. 目标陈述

在业务环境下使用 Beacon 时，建立“可优化点自动回收”的闭环：

1. 采集真实使用过程中的路由/执行/阻断信号；
2. 自动归因为标准 reason_code；
3. 沉淀到 memory-v1 并支持 revision 演进；
4. 回灌 workflow/gate，驱动下一轮功能迭代。

## 2. 现状事实（基于 v1.0.3 实现）

- `run --mode debug` 已存在枚举，但当前与 normal 模式行为基本一致，未形成专门 debug 反馈能力。
- `debug` 命令仅有 `watch` 事件观察，不具备采集/归因/入库功能。
- `prompt/ask` 已记录路由历史（`.beacon/memory/prompt-router-history.jsonl`），具备原始信号基础。
- `feedback sync` 已具备 reason_code -> memory 同步能力（含去重与 lifecycle 事件）。
- prompt 路由覆盖增强后，可直达 30 intents，但仍有 9 个子命令不在直达主路由。
- workflow 已具备 OMC/OMX/Team 下一步选择器，但主要是“提示级联通”。

## 3. 核心问题

1. 缺少统一 debug 反馈数据模型（raw/candidate/durable）。
2. 缺少“采集->归因->入库->验证”的单命令闭环。
3. 缺少文档变更与实现证据的强绑定机制（持续变更场景下易漂移）。
4. 缺少 OMC/OMX/team 的程序级桥接执行策略与审计记录。

## 4. 思路分解（3 层架构）

### 4.1 采集层（Raw）

- 采集来源：ask / prompt / workflow / run / gate / team。
- 输出文件：`.beacon/state/debug-feedback/<run_id>.jsonl`。
- 关键字段：goal、intent、confidence、boundary_state、block_reason、recommended_command、exit_code、source、ts。

### 4.2 归因层（Candidate）

- 从 raw 信号生成可执行候选：`.beacon/state/feedback-candidates/<run_id>.json`。
- reason_code 示例：
  - `router_false_positive`
  - `boundary_mixed_ambiguous`
  - `missing_intent_mapping`
  - `docs_example_drift`
  - `team_runtime_not_spawned`
  - `bridge_execution_not_recorded`

### 4.3 记忆层（Durable）

- 写入 `.beacon/memory/memory-v1.json`（type: feedback/insight/decision）。
- 采用 `upsert + revision_of`，避免重复污染并支持演进链。

## 5. 关键决策

1. `beacon ask` 继续保持默认 plan-only，避免误执行放大噪声。
2. debug feedback 不直接替代 gate 规则，而是进入 feedback 管道后由 gate 使用 reason_code 校验。
3. OMC/OMX bridge 默认“仅提示不执行”，通过显式开关开启程序级调用。
4. 文档-实现一致性采用“滚动基线 + fingerprint + gate 强校验”。

## 6. 开放问题

1. reason_code 的最小稳定集合与命名规范是否冻结在 v1.1.0？
2. OMC/OMX 程序调用失败时是否阻断主流程，还是降级为 warn？
3. debug feedback 的 retention 周期与清理策略（例如 30/90 天）如何设定？
4. 多项目共享 memory 时如何避免 reason_code 语义冲突？

## 7. 退出标准（Think Done）

- 问题空间、边界、开放问题已明确；
- 用户故事与 AC 已可直接产出；
- PRD 可按 FR/NFR 拆解实现。
