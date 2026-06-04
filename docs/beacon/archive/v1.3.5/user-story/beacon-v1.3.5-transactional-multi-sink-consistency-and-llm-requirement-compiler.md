# User Story: beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler

## Story

**As a** Beacon 维护者与交付负责人,  
**I want** Beacon 在需求材料生成与多写入投影时，统一采用 canonical 驱动事务提交，并把 `prd create` 升级为“模板约束 + LLM 语义编译 + 校验降级”闭环,  
**So that** `human/machine/sqlite` 三写入点不再漂移，且 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release` 主链保持稳定可审计。

## Story Slices

### US-001: 多写入必须先 canonical 后投影并统一事务提交

As a maintainer, I want all cross-sink writes to follow one transaction coordinator contract so that partial commit does not silently pass.

### US-002: 跨面一致性元数据必须可核对

As a reviewer, I want `transaction_id/source_hash/projection_seq` to be consistent across human/machine/sqlite so that drift can be detected deterministically.

### US-003: PRD 生成要从模板填空升级为语义编译

As a requirement author, I want `prd create` to produce boundary/layer/recovery/acceptance-complete output so that generated PRDs are directly usable.

### US-004: LLM 不可用或输出不达标时必须可审计降级

As a release owner, I want fallback reasons and compile evidence to be recorded so that degraded output can be governed by gate/review.

### US-005: 执行 lane 不得改写 requirement truth

As a product owner, I want implement single/team/ralph to share one requirement truth contract so that runtime mode does not change acceptance semantics.

## Acceptance Criteria

- [ ] AC-001 事务一致性：构造单 sink 失败场景时，不允许静默部分成功；必须阻断 freeze/release 并留下失败事务记录。
- [ ] AC-002 跨面一致性：同一提交后，human/machine/sqlite 的 `transaction_id/source_hash/projection_seq` 一致；否则标记 `drift`。
- [ ] AC-003 PRD 编译质量：`prd create --mode llm` 输出必须覆盖边界、分层、恢复策略、验收链与风险缓解，不得退化为占位模板。
- [ ] AC-004 可审计降级：LLM 不可用或 contract 校验失败时，`mode=auto` 可降级 `rule`，且 machine 面保留 `fallback_reason` 与编译证据。
- [ ] AC-005 主链闭环不变形：不新增公开一级主命令；`implement single/team/ralph` 在同一 requirement truth 下执行与验收。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 8 |
| Status | frozen-pending-implementation |
| Version | v1.3.5 |
| Track | parallel |
| Created | 2026-04-20 |
