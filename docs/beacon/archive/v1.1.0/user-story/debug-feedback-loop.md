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

### US-007 滚动基线快照
作为版本负责人，我希望每轮迭代沉淀 baseline snapshot（含 fingerprint 与差异摘要），以便跟踪需求演进轨迹。

### US-008 变更触发重生成闭环
作为 PM/QA，我希望需求变更后自动提示或触发 PRD/用户故事/测试矩阵更新任务，以便快速恢复一致性。

### US-009 OMC/OMX Skill 联通提示词模板
作为一线开发者，我希望拿到可直接执行的跨工具提示词模板，以便通过 team 方式完成闭环交付。

### US-010 记忆体治理与可观测
作为平台维护者，我希望看到 memory 分层健康度指标与异常告警，以便避免噪声堆积。

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
| AC-015 | US-007 | 每轮 workflow 结束生成 baseline snapshot，并关联上一轮 revision | Must |
| AC-016 | US-007 | baseline snapshot 包含：fingerprint、open_questions、delta_summary、risk_flags | Must |
| AC-017 | US-008 | 侦测到需求变更时，自动生成“待更新文档链”任务清单（US/PRD/TC） | Must |
| AC-018 | US-008 | gate strict 输出 doc-impl 一致性 verdict 与 mismatch reason_code | Must |
| AC-019 | US-009 | 输出“Beacon + OMC + OMX + Team”全链路提示词模板包 | Must |
| AC-020 | US-009 | `prompt optimize` 支持生成边界安全的推荐命令组合（含 fallback） | Should |
| AC-021 | US-010 | 记忆体三层（raw/candidate/durable）提供 retention 与 dedup 健康指标 | Must |
| AC-022 | US-010 | report summary 输出 baseline drift 与 memory assimilation KPI | Should |

## Blocking Semantics

- 任一 Must AC 未通过：v1.1.0 不可发布；
- Should AC 未通过：可发布但必须登记风险与回补计划。
