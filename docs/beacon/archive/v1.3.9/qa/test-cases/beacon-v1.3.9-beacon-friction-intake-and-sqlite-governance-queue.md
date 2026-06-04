# Test Cases: Beacon v1.3.9 beacon-friction-intake and sqlite governance queue

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | `beacon-friction-intake` 对外作为统一入口展示，文档与帮助面不再把主语义描述成“分析报告工具” | unit | 用户看到的主入口语义是“摩擦录入入口” |
| TC-002 | AC-002 | 旧的 `memory-friction-evolution` 仍可作为兼容实现来源存在 | integration | 旧入口不会立即失效，但会被标记为兼容实现或内部机制 |
| TC-003 | AC-003 | 入口被放在 support surface，而不是新的主生命周期 stage | unit | 命令/文档层不会把该能力误注册成 `prd/user-story/test-case/implement/qa/release` 同级主阶段 |
| TC-004 | AC-101 | 在 Beacon 源码项目执行 `scan` 模式 | integration | 系统能自动抽取项目摩擦、阻塞、bug 或重复问题 |
| TC-005 | AC-102 | `scan` 模式存在项目内证据输入 | integration | 生成的 friction item 绑定 `.beacon/debug/`、`.beacon/memory/`、`.beacon/analysis/` 或等价证据引用 |
| TC-006 | AC-103 | `scan` 结束后不只产出报告，还生成统一 friction item | integration | 输出进入统一治理模型，而不是仅落一次 markdown/json 报告 |
| TC-007 | AC-201 | 在目标开发项目执行 `capture` 模式并输入一次人工上下文摩擦 | integration | 系统接受人工输入并生成对应 friction item |
| TC-008 | AC-202 | `capture` 触发 LLM 标准化与分类 | integration | 输出包含规范化 summary、分类、严重级别、领域与证据绑定 |
| TC-009 | AC-203 | `scan` 与 `capture` 都写入同一队列但保留来源差异 | unit | item 带有 `source_type=scan` 或 `source_type=manual_capture`，并进入同一治理表族 |
| TC-010 | AC-301 | `scan` 正常 dual-write | integration | 项目内证据保留，同时全局 sqlite 中出现对应 friction item |
| TC-011 | AC-301 | `capture` 正常 dual-write | integration | 项目内记录与全局 sqlite 队列项同时成立 |
| TC-012 | AC-302 | item 经历 `queued -> claimed -> resolved` 的正常治理流 | integration | 队列状态可推进，并保留事件轨迹 |
| TC-013 | AC-302 | 已解决项被新证据触发 reopen | integration | item 可重新打开并继续治理，而不是保持错误 closed |
| TC-014 | AC-303 | sqlite 暂时不可用时执行 `capture` | integration | 项目内 truth 仍落盘，dual-write 失败有显式诊断，后续允许 replay |
| TC-015 | AC-401 | friction item 分类到 `blocking_bug` | unit | 分类结果命中允许集合之一 |
| TC-016 | AC-401 | friction item 分类到 `improvement` 或 `optimization_enhancement` | unit | 非阻塞项仍被正确纳入允许集合 |
| TC-017 | AC-402 | item 字段完整性校验 | unit | 至少包含 summary、source_type、severity、domain、queue_status、project_root、evidence_refs、first_seen_at、last_seen_at 或等价字段 |
| TC-018 | AC-403 | `debug_issues` 与 friction queue 分层边界校验 | integration | runtime projection 快照不会被直接覆盖成治理队列语义 |
| TC-019 | AC-501 | 新摩擦项默认不自动路由到 `prd/user-story/test-case/implement/qa/release` | integration | item 只进入治理队列，无 requirement truth 改写 |
| TC-020 | AC-502 | item 被显式推进为 `accepted_for_requirement` | integration | 系统只在显式接受后开放 `beacon-prd` 或 `beacon-change` 路由 |
| TC-021 | AC-503 | 未显式接受时尝试 requirement/change 路由 | integration | 路由被拒绝或要求显式接受，不允许静默进入 requirement truth |
| TC-022 | AC-601 | 全局 sqlite 删除后，本地证据仍存在 | integration | `.beacon/debug/`、`.beacon/memory/`、`.beacon/analysis/` 或等价本地产物仍可读取 |
| TC-023 | AC-602 | sqlite 不保存第二份完整正文 truth | unit | 全局表只保留治理索引与 refs，不保存大段原始正文 |
| TC-024 | AC-603 | 基于本地 truth 的 replay 恢复 | integration | 系统可从项目内证据重新驱动 intake/replay，重建治理队列项 |

## Regression Focus

- `scan` 与 `capture` 不能分裂成两套不兼容流程
- `debug_issues` 不得被重定义为 friction queue
- sqlite 失败时不能丢失项目内 truth
- `accepted_for_requirement` 之前不得自动污染 frozen requirement truth

## Execution Notes

- version: `v1.3.9`
- upstream_user_story: `docs/beacon/archive/v1.3.9/user-story/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`
- 本测试矩阵优先覆盖治理闭环，而不是提前冻结具体命令拼写或具体表结构实现细节
