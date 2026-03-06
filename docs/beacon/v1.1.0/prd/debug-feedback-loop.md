# PRD: Debug Feedback Loop（v1.1.0）

## 1. 背景

Beacon v1.0.3 已具备：

- prompt/ask 路由安全闸；
- workflow 7 阶段闭环与 memory 生命周期；
- feedback reason_code 入库与 revision 能力；
- gate strict 的 coverage/memory/evidence 校验。

但在“业务环境调试反馈产品化”方面仍有缺口：

1. debug 模式未形成专门反馈闭环；
2. debug 命令仅 watch，缺少采集/归因/入库；
3. OMC/OMX/team 主要是提示级联通；
4. 持续变更下文档-实现一致性缺少 fingerprint 强绑定。

## 2. 目标

1. 构建 Debug Feedback 三层架构（Raw/Candidate/Durable）；
2. 建立 OMC/OMX/team 程序级桥接（可控开关）；
3. 建立滚动基线一致性机制（spec fingerprint + gate 校验 + docs CI）；
4. 输出可复用的 Beacon 开发通用提示词清单。

## 3. 范围

### 3.1 In Scope（v1.1.0）

- debug feedback 原始采集、候选归因、memory 入库；
- reason_code 规则扩展与可配置化；
- workflow 终态 bridge 执行开关与证据记录；
- spec fingerprint 生成与 gate strict 校验；
- docs-example CI 命令样例回归；
- v1.1.0 用户故事/PRD/测试矩阵/发布清单完整物料。

### 3.2 Out of Scope（v1.1.0）

- 全自动生产部署；
- 向量数据库或独立检索服务化；
- 全量历史 reason_code 自动回填。

## 4. 角色与场景

- PM：追踪可优化点并规划迭代；
- Dev：调试时可获得可执行修复建议；
- QA：确保反馈回灌可审计；
- Release Owner：在持续变更下仍可判定“文档=实现=证据”。

## 5. 功能需求（FR）

### FR-1 Debug Raw Collector

- 新增 debug 反馈记录器，挂载到 ask/prompt/workflow/run/gate/team；
- 输出 `.beacon/state/debug-feedback/<run_id>.jsonl`；
- 字段至少包含：
  - `ts/run_id/source/goal/intent/confidence/boundary_state/block_reason/recommended_command/executed/exit_code/note`。

### FR-2 Attribution Engine

- 基于规则把 raw 信号聚合为 reason_code 候选；
- 输出 `.beacon/state/feedback-candidates/<run_id>.json`；
- 支持人工 override 与最终 reason_code 保留。

### FR-3 Memory Assimilation

- `feedback apply/sync` 可消费 debug 候选；
- 写入 memory-v1：type=feedback/insight/decision；
- 支持 `upsert + revision_of`。

### FR-4 Prompt Catalog Governance

- 产出“全量通用提示词清单”：
  - A 组：可直达 intents；
  - B 组：需显式命令。
- 提供每个 B 组命令的推荐 CLI fallback。

### FR-5 Bridge Execution（OMC/OMX/Team）

- workflow 终态新增 bridge 执行策略：
  - 默认：只提示（safe default）；
  - 开关开启：程序执行（并捕获 exit code/stdout/stderr）。
- bridge 执行结果写入 lifecycle 与 memory，并关联 evidence_ref。

### FR-6 Strong Consistency Guard

- 生成 spec fingerprint：
  - user-story/prd/test-case 内容哈希；
- gate strict 新增一致性校验：
  - fingerprint 与实现证据不一致 => blocked；
- docs 示例命令回归测试，防止 README/SKILL 漂移。

## 6. 数据结构

### 6.1 Debug Raw Event（新增）

文件：`.beacon/state/debug-feedback/<run_id>.jsonl`

```json
{
  "ts": "2026-03-06T00:00:00Z",
  "run_id": "run-xxxx",
  "source": "prompt",
  "goal": "请先检查 gate 再直接写代码上线",
  "intent": "gate",
  "confidence": 0.59,
  "boundary_state": "mixed_need_confirm",
  "block_reason": "mixed-boundary-needs-confirmation",
  "recommended_command": "beacon gate check release --project-root ...",
  "executed": false,
  "exit_code": null,
  "note": ""
}
```

### 6.2 Candidate Feedback（复用）

文件：`.beacon/state/feedback-candidates/<run_id>.json`

```json
{
  "schema_version": "1.0",
  "run_id": "run-xxxx",
  "source": "debug",
  "feedback": [
    {
      "reason_code": "missing_intent_mapping",
      "note": "brainstorm/debug 等命令非直达，建议显式 fallback"
    }
  ]
}
```

### 6.3 Memory v1（复用）

关键字段：`type/status/content/content_hash/reason_codes/source_session_id/evidence_ref/revision_of/superseded_by`。

## 7. 非功能需求（NFR）

1. **安全性**：默认不自动执行 bridge；
2. **可追踪性**：所有反馈链路均有 evidence_ref；
3. **可恢复性**：失败不丢事件，支持重放；
4. **兼容性**：保持现有 ask/prompt/workflow/gate 命令契约向后兼容。

## 8. 验收与发布

### 8.1 验收门

- Must AC 全通过；
- gate strict 通过；
- feedback sync 能写回 memory 并可 recall；
- report summary 可输出一致性摘要。

### 8.2 发布建议顺序

1. 灰度开启 debug raw collector；
2. 验证 reason_code 准确率；
3. 再开启 bridge 程序执行开关；
4. 最后启用 strict fingerprint 阻断。

## 9. 风险与回滚

- 风险：归因过拟合导致噪声 reason_code；
- 风险：bridge 执行失败引入误阻断；
- 回滚：关闭 bridge 执行开关，保留提示模式；
- 回滚：fallback 到 legacy feedback sync pipeline。
