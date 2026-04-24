# Test Cases: beacon-v1.3.6-lifecycle-foundation-transaction-consistent-dual-write-and-memory-convergence

## Overview

**Feature**: `beacon-v1.3.6-lifecycle-foundation-transaction-consistent-dual-write-and-memory-convergence`  
**Version**: `v1.3.6`  
**Status**: `planning-line`  
**Foundation Anchor**: `docs/beacon/v1.3.6/prd/beacon-v1-3-6-memory-foundation-and-full-scene-evidence-recall.md`

## Scenario Test Set

### TC-001 (AC-001): canonical lifecycle 成为唯一正式状态机

- Given：Beacon 已加载 `global-boundaries` 和 `v1.3.6` 版本物料
- When：检查 workflow 定义、progress 计算、help/status 输出和对外 stage 解释
- Then：系统只把 `prd / user-story / test-case / prototype / implement / qa / release` 作为正式 canonical lifecycle

### TC-002 (AC-002): legacy stage vocabulary 可兼容迁移

- Given：历史 state/profile 仍使用 `think / implementation / verify / gate / review / delivery`
- When：执行 workflow progress、profile stage 解析、help/status 和 read-model 查询
- Then：系统能把旧词汇映射到 canonical lifecycle，而不是继续把它们当作正式对外 stage

### TC-003 (AC-003): next_stage 与 blocker 输出不再泄露旧 canonical stage

- Given：某 feature 处在 `prototype` 之后、`qa` 之前
- When：检查 `next_stage`、blocking reasons、closure state、status 输出
- Then：输出词汇使用 `implement / qa / release`，而不是 `implementation / verify / gate`

### TC-004 (AC-004): 每个 canonical stage 都有 machine-first context pack

- Given：某 feature 完成 requirement truth 并进入后续 lifecycle
- When：读取 stage context 产物
- Then：每个 canonical stage 的 context pack 至少包含 requirement refs、evidence refs、decision trace、transaction lineage 和 blockers

### TC-005 (AC-005): human/machine/runtime 写入共享同一 transaction envelope

- Given：发生一次正式 lifecycle 写入
- When：检查 human docs、machine contract、runtime projection 的提交元数据
- Then：三类 sink 共享同一 `transaction_id / source_hash / projection_seq / sink_checksums`

### TC-006 (AC-006): sink 失败时阻断后续闭环

- Given：某次 transaction 在 machine 或 runtime sink 失败
- When：继续尝试 freeze、qa 或 release
- Then：系统保留失败事务并阻断后续判定，不允许静默继续

### TC-007 (AC-007): memory foundation 保留 raw evidence linkage

- Given：某 feature 在 implement、qa、release 过程中持续写回 evidence
- When：检查 recall、memory writeback、friction evolution 和 stage context pack
- Then：系统能够追溯到 raw evidence、artifact、run、stage 和 transaction lineage，而不是只剩压缩摘要

### TC-008 (AC-008): support/read-model 报告跨面一致性

- Given：`help / status / doctor / qa / release` 读取同一 feature 的 foundation state
- When：检查其输出内容
- Then：系统能报告 lifecycle consistency、memory completeness、sink consistency、drift verdict

### TC-009 (AC-009): 人类界面保持极简

- Given：普通用户通过 Beacon 主流程推进 feature
- When：查看 CLI help、status、next-step guidance 和 release verdict
- Then：人类只需要理解 canonical stage、阻断、下一步和 verdict，而无需理解 machine 内部 orchestration 细节

## Suggested Verification Areas

- `beacon/commands/workflow.py`
- `beacon/utils/workflow_memory.py`
- `beacon/utils/help_support.py`
- `beacon/commands/status.py`
- `beacon/commands/doctor.py`
- `beacon/utils/memory.py`
- `beacon/utils/memory_friction_evolution.py`

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | canonical lifecycle |
| TC-002 | Pending | legacy alias migration |
| TC-003 | Pending | outward vocabulary cleanup |
| TC-004 | Pending | stage context packs |
| TC-005 | Pending | transaction envelope |
| TC-006 | Pending | failure blocking |
| TC-007 | Pending | raw evidence linkage |
| TC-008 | Pending | support/read-model convergence |
| TC-009 | Pending | human surface minimalism |
