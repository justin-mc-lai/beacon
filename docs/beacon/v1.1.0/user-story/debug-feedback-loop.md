# User Story: debug-feedback-loop

## Epic

作为 Beacon 维护者，我希望在真实业务环境中自动沉淀可优化反馈，并在需求持续变更场景下保持文档与实现强一致，从而持续提升 Beacon 的路由准确性、协作闭环能力与发布可信度。

## Stories

### US-001 Debug 原始采集
作为 Beacon 使用者，我希望在 ask/prompt/workflow/run/gate/team 过程自动采集调试信号，以便后续分析与迭代。

### US-002 自动归因 Candidate
作为产品负责人，我希望系统可自动将反馈归类为 reason_code，以便形成可统计、可追踪的问题池。

### US-003 Durable Memory 入库演进
作为研发团队，我希望反馈进入 memory-v1 且支持去重与修订，以便建立可复用知识资产。

### US-004 Prompt 触发清单治理
作为开发者，我希望有“可直达/需显式命令”清单，以便稳定触发 Beacon 功能。

### US-005 OMC/OMX/Team 程序级联通
作为交付负责人，我希望 workflow 终态可选程序桥接 OMC/OMX/team，并记录执行证据。

### US-006 持续变更下文档-实现强一致
作为质量负责人，我希望每轮变更都校验 spec 与实现证据一致，避免漂移。

## Acceptance Criteria

| AC ID | User Story | Description | Priority |
| --- | --- | --- | --- |
| AC-001 | US-001 | 生成 `.beacon/state/debug-feedback/<run_id>.jsonl`，并记录标准字段 | Must |
| AC-002 | US-001 | ask/prompt/workflow/run/gate/team 均可写入 debug 采集事件 | Must |
| AC-003 | US-002 | 支持 reason_code 自动归因并输出候选到 `feedback-candidates` | Must |
| AC-004 | US-002 | 支持人工补充 note/override，并保留原始归因轨迹 | Should |
| AC-005 | US-003 | `feedback apply/sync` 可将 debug 候选写入 `memory-v1` | Must |
| AC-006 | US-003 | memory 入库支持 `upsert + revision_of + superseded_by` | Must |
| AC-007 | US-004 | 输出完整提示词清单（直达 intents + 显式命令） | Must |
| AC-008 | US-004 | 对非直达命令给出明确 fallback 推荐命令 | Should |
| AC-009 | US-005 | workflow 终态支持 bridge 开关：默认仅提示，显式开启可执行 | Must |
| AC-010 | US-005 | OMC/OMX/team bridge 执行结果写入 memory + lifecycle + evidence_ref | Must |
| AC-011 | US-006 | 生成 spec fingerprint（user-story/prd/test-case）并持久化 | Must |
| AC-012 | US-006 | gate strict 校验 fingerprint 与实现证据一致，不一致则 blocked | Must |
| AC-013 | US-006 | docs-example CI 可执行校验（README/SKILL 命令样例） | Must |
| AC-014 | US-006 | `report --write-summary` 能输出可审计一致性摘要 | Should |

## Blocking Semantics

- 任一 Must AC 未通过：v1.1.0 不可发布；
- Should AC 未通过：可发布但必须登记风险与回补计划。
