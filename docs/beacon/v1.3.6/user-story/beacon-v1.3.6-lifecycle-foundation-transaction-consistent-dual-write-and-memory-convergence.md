# User Story: beacon-v1.3.6-lifecycle-foundation-transaction-consistent-dual-write-and-memory-convergence

## Story

**As a** Beacon foundation owner / lifecycle owner / memory foundation owner,  
**I want** Beacon 把 lifecycle foundation、memory foundation、LLM stage planning 与 human/machine/runtime 事务一致双写收口到同一套 canonical contract，  
**So that** 人类只看稳定的 `7+3` 生命周期和关键阻断，机器内部可以自由编排，但所有正式信息都由同一事务真相单向投影，避免语义、状态、记忆和投影漂移。

## Story Slices

### US-001: 作为 lifecycle owner，我希望 canonical stages 成为唯一正式状态机

这样 Beacon 的规范、workflow progress、next_stage 和 closure 判断不会继续新旧并存。

### US-002: 作为 migration owner，我希望旧 stage vocabulary 被兼容映射

这样历史 `think / implementation / verify / gate / review / delivery` 能平滑过渡到新 foundation。

### US-003: 作为 memory foundation owner，我希望 evidence memory 与 lifecycle transaction 建立统一 lineage

这样 recall、writeback、stage handoff 和 drift audit 都基于同一条证据链。

### US-004: 作为 LLM orchestration owner，我希望每个 stage 都有 machine-first context pack

这样 LLM 不再依赖裸 prompt 接力，而是基于 requirement refs、evidence refs、decision trace 和 transaction lineage 继续工作。

### US-005: 作为 transaction owner，我希望 human/machine/runtime 多面写入走同一 canonical envelope

这样文档、机器合同和 runtime projection 不会再各写各的。

### US-006: 作为 diagnosis owner，我希望 `help / status / doctor` 只解释 canonical lifecycle 和 transaction-backed truth

这样支持面不会再复制出一套旧状态机或平行真相。

### US-007: 作为 release owner，我希望 `qa / release` 把跨面一致性和 anti-drift 升级为正式 gate

这样 Beacon 不会在单面修补后误判已完成或可发布。

### US-008: 作为 product surface owner，我希望人类界面继续极简

这样用户只看到主链、阻断、下一步和最终 verdict，机器内部复杂度继续被 Beacon 吞掉。

## Acceptance Criteria

- [ ] AC-001 Beacon 对外 canonical lifecycle 统一为 `prd / user-story / test-case / prototype / implement / qa / release`
- [ ] AC-002 历史 `think / implementation / verify / gate / review / delivery` 能被兼容解析并映射到 canonical lifecycle
- [ ] AC-003 workflow progress、next_stage、closure、blocking reason、help/status 输出不再把旧词汇当作正式 stage
- [ ] AC-004 每个 canonical stage 都存在 machine-first stage context pack，并绑定 requirement refs、evidence refs、decision trace 与 transaction lineage
- [ ] AC-005 human/machine/runtime 多面写入必须由同一 canonical transaction envelope 单向投影生成
- [ ] AC-006 任一 sink 写入失败时，系统必须留下失败事务并阻断后续 freeze / qa / release，而不是静默放过
- [ ] AC-007 memory foundation 必须保留 raw evidence linkage，并可为 recall、writeback、handoff、drift audit 提供统一依据
- [ ] AC-008 `help / status / doctor / qa / release` 必须能读取并报告 lifecycle consistency、memory completeness、sink consistency 结论
- [ ] AC-009 人类默认面只暴露最少必要 lifecycle 信息，不要求理解 machine 内部 orchestration 结构

## Metadata

| Field | Value |
|-------|-------|
| Priority | critical |
| Story Points | 13 |
| Status | planning-line |
| Version | v1.3.6 |
| Track | parallel |
| Created | 2026-04-22 |
| Feature Slug | beacon-v1.3.6-lifecycle-foundation-transaction-consistent-dual-write-and-memory-convergence |
| Foundation Anchor | docs/beacon/v1.3.6/prd/beacon-v1-3-6-memory-foundation-and-full-scene-evidence-recall.md |
