# PRD：Beacon v1.3.3 记忆进化与摩擦演进 Toolkit（并行）

**Feature**: `beacon-v1.3.3-memory-friction-evolution-toolkit`  
**Version**: `v1.3.3`  
**Date**: `2026-04-16`  
**Status**: `planning line`

## 1. 问题

Beacon 已有 `remember/recall/workflow_memory/debug_feedback/learning_loop`，但“运行摩擦 -> 候选改进 -> 写回记忆”的演进路径仍分散：

1. 摩擦证据在 debug 与 memory 文件中分散，缺少统一候选输出。
2. `beacon-toolkit-lighthouse` 只能给静态结构图，不能给动态摩擦演进候选。
3. 维护者难以快速判断“哪些问题在复发，下一步应该改什么”。

## 2. 目标

在不扩张主 `6+3` 路径下，新增并行 toolkit：

1. **并行定位**
   - 作为 optional analysis toolkit，与主链并行
   - 不替代 `prd -> user-story -> test-case -> implement -> qa -> release`
2. **双输入融合**
   - 静态：`beacon-toolkit-lighthouse` 结构图
   - 动态：memory/debug friction 证据
3. **最小闭环**
   - 输出 Top-N 候选（含证据与推荐命令）
   - 可选写回 `remember add --upsert`

## 3. 用户故事

| As a | I want to | So that |
|------|-----------|---------|
| Beacon 维护者 | 看到高频摩擦候选及证据 | 决定下轮应该优先修哪里 |
| 目标项目 owner | 看到“为何反复卡住 + 下一步命令” | 降低定位与恢复成本 |
| 版本负责人 | 在发布前对比复发摩擦是否下降 | 用证据而非感觉判断演进效果 |

## 4. 功能需求

### FR-001 Toolkit 必须与 Lighthouse 并行

Toolkit 必须支持与 `beacon-toolkit-lighthouse` 并行运行：

- Lighthouse 负责单文件静态结构图
- Toolkit 负责动态摩擦候选
- 最终在统一报告层汇合

### FR-002 Toolkit 必须复用现有记忆能力

必须复用以下现有能力：

- `remember`
- `recall`
- `workflow_memory`
- `debug_feedback`
- `learning_loop`

不得新建第二套 memory plane 或平行记忆目录标准。

### FR-003 输出候选必须可执行

每条候选至少包含：

- `friction_summary`
- `evidence_refs`
- `recommendation`（keep/review/discard）
- `recommended_command`

禁止输出不可执行或无证据的泛化建议。

### FR-004 命令面必须保持可选

命令仅允许在可选 analysis 面暴露（例如 `labs/hidden`）：

- 不得新增公开主命令
- 不得改变普通用户默认主链

### FR-005 必须支持最小回写闭环

当候选被选中（keep/review）时，支持：

- `remember add --upsert`
- 写回条目必须带来源与证据引用

### FR-006 必须有轮次与退出保护

参考 GenericAgent loop 的轻量原则：

- 每轮必须输出结构化决策（继续/停止）
- 必须支持 `max_turns` 防无限循环
- 每轮输入/输出都要可回放

## 5. 最小数据契约

```json
{
  "schema_version": "1.0",
  "run_id": "mfe-20260416T000000Z",
  "docs_version": "v1.3.3",
  "mode": "memory|friction|both",
  "inputs": {
    "memory_refs": [],
    "debug_refs": [],
    "lighthouse_ref": ""
  },
  "candidates": [
    {
      "candidate_id": "debug_policy:xxx",
      "category": "debug_policy|rewrite_policy|qa_policy",
      "friction_summary": "",
      "evidence_refs": [],
      "score": 0,
      "recommendation": "keep|review|discard",
      "recommended_command": ""
    }
  ],
  "decision": {
    "next_prompt": "",
    "should_exit": false
  }
}
```

## 6. 实施切片

### Slice A：命令编排层

- 新增 `beacon/commands/memory_friction_evolution.py`
- 提供 `run/report` 两个最小入口

### Slice B：证据聚合层

- 复用 `beacon.utils.memory`
- 复用 `beacon.utils.debug_feedback`
- 复用 `beacon.utils.learning_loop`

### Slice C：并行 Lighthouse 层

- 复用 `beacon.utils.lighthouse`
- 支持 `--with-lighthouse --target <path>`

### Slice D：写回层

- 候选选中后复用 `remember add --upsert`
- 统一写入证据路径与 source_session_id

## 7. 测试要求

最小新增测试：

1. memory-only 模式输出候选
2. friction-only 模式输出候选
3. both 模式合并候选且去重
4. `--with-lighthouse` 可并行产物不冲突
5. `--max-turns` 能阻止无限循环
6. writeback 仅通过 `remember` 写回，不创建新 memory 文件

## 8. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 与 learning_loop 重复建设 | 中 | 先做薄编排层，禁止重写已有判分逻辑 |
| 候选建议过泛化 | 中 | 强制 evidence_refs + recommended_command |
| 工具面膨胀干扰主链 | 高 | 限制在 labs/hidden，可选启用 |
| 并行运行造成输出分裂 | 中 | 统一 run_id 与合并报告路径 |

## 9. 成功标准

1. toolkit 能与 lighthouse 并行运行并稳定产物
2. 基于真实 memory/debug 数据输出 Top-N 候选
3. 候选都有证据引用与推荐命令
4. 写回闭环复用 remember/recall，不新增 memory silo
5. 主 `6+3` 默认路径无新增认知负担

---

**Created**: 2026-04-16  
**Version**: v1.3.3  
**Status**: Draft  
**Memory Context**: N/A
