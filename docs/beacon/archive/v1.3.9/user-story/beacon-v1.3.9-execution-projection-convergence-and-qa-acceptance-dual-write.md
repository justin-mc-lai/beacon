# User Story: Beacon v1.3.9 execution projection convergence and QA acceptance dual-write

**Feature**: `beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write`  
**Version**: `v1.3.9`

## Story

作为 Beacon 的版本治理者、真实项目操作者与命令面维护者，我希望 Beacon 把 `qa / release / gate / support` 的交付面收敛成：

- 一个 canonical truth source
- 少量高信号 human-readable projection
- 可审计的 transaction dual-write

这样我既能保留 host-native LLM 与 machine truth 的自动化能力，又不会继续在 `docs/beacon/<version>/execution/` 里积累大量模板型低信号文件。

## Requirement Description

`v1.3.9` 的核心不是新增命令，而是让剩余 public subcommands 与 `architecture-blueprint.md` 体现出的交付模式保持一致：

1. canonical envelope 才是唯一 truth source
2. human-readable docs 只是单向 projection
3. 文档必须解释 public command 如何调用与如何落证
4. QA 一旦得出 evidence-backed verdict，就自动 dual-write
5. release / gate / support 全部消费同一 acceptance/readiness truth
6. `prototype` 不再以静默模板回退冒充 requirement-derived compile 成功
7. promised operator surface 与 shipped implementation surface 之间的 drift 会被正式 gate 阻断
8. `beacon prd create` 的成功语义只对应 requirement-aware compile，而不是 generic placeholder 输出

## User Stories

### US-001: QA 验收应自动产出事务双写

作为 QA 操作者，我希望 `qa` 在得到 evidence-backed verdict 后，自动写出同一笔 acceptance transaction 的 machine sink 与 human-readable execution artifact，这样我不需要再手工补验收文档。

### US-002: Release 与 Gate 应消费同一 readiness truth

作为 release owner，我希望 `release check / release scorecard / gate check release` 消费同一 acceptance/readiness envelope，而不是各自产生平行结论。

### US-003: Execution human docs 应直接服务操作者

作为 Beacon 命令使用者，我希望 execution 文档不是模板壳，而是直接告诉我：

- 这个 public command 什么时候用
- 输入是什么
- 输出是什么
- evidence / transaction 在哪里
- 下一步应该做什么

### US-004: Support commands 应退回解释层

作为 `help / status / doctor / archive` 的使用者，我希望这些命令优先读取统一 read-model / canonical truth，并只输出解释型结果，而不是继续制造大量 execution 模板文档。

### US-005: 旧 execution 模板应被明确归类和收敛

作为版本治理者，我希望 execution 目录里的旧文件被明确划分为：

- 必须保留
- 合并收敛
- 失败/告警时按需生成
- 废弃

这样 `docs/beacon/<version>/execution/` 的人类面可以长期保持可读。

### US-006: Prototype 默认不得静默退化为固定模板产出

作为 Beacon 的 requirement owner，我希望 `prototype auto` 在 host/LLM compile 不可用或 contract 校验失败时，显式报告 downgrade 或阻断，而不是继续产出看似完整的固定模板 wireframe。

这样 `prototype` 阶段仍然是 requirement truth 推导的闭环产物，而不是把模板兜底误判成需求已收敛。

### US-007: QA acceptance 必须升级为三写事务

作为 release owner / diagnosis owner，我希望 QA acceptance 除 machine sink 与 human sink 之外，还把 runtime projection sink 纳入同一 transaction contract。

这样 `status / doctor / gate / release` 才能基于同一笔 acceptance truth 做 anti-drift 阻断，而不是读取不同步的多源结果。

### US-008: 事务消费者必须共享同一阻断标准

作为 support surface owner，我希望 `status / doctor / gate / release` 对 prototype/acceptance transaction 使用同一组 metadata、checksum、failed-transaction 判断规则。

这样任何单面修补、sink 缺失、runtime projection 漏写都不会被误判为 pass。

### US-009: 承诺交付面与实际交付面之间必须有正式 drift gate

作为版本治理者 / release owner，我希望 Beacon 能正式比较 requirement/change/release 面承诺的 operator-visible surface 与 implement/review/evidence 面真实已交付的 shipped surface。

这样 requirement promise 一旦超前于已交付实现，就会在 gate/release 前被系统阻断，而不是依赖人工在末端兜底。

### US-010: PRD 生成不能再把 generic placeholder 当成功

作为 requirement author，我希望 `beacon prd create` 的成功结果必须是 version-aware、boundary-aware、scenario-aware 的 PRD 骨架。

这样 PRD 入口不会再把 generic placeholder template 误判成 requirement truth 已准备完成。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | artifact-taxonomy | `v1.3.9` 明确 execution artifact taxonomy，至少区分 canonical envelope、required human projection、optional derived projection、deprecated template artifact。 |
| AC-002 | qa-envelope | `qa` 在 evidence-backed verdict 后会生成 machine-readable acceptance envelope。 |
| AC-003 | qa-dual-write | 同一笔 QA acceptance transaction 会自动双写 machine sink 与 human-readable execution artifact。 |
| AC-004 | release-gate-convergence | `release` 与 `gate` 消费同一 acceptance/readiness truth，不再各自产生平级 readiness source。 |
| AC-005 | operator-facing-docs | 保留的 execution human docs 必须直接说明 public command usage、inputs、outputs、evidence refs 与 next step。 |
| AC-006 | support-surface-simplification | `help / status / doctor / archive` 作为解释层复用统一 read-model truth，不再默认扩张模板文档。 |
| AC-007 | template-reduction | execution 目录存在一份明确迁移策略，说明哪些旧模板保留、合并、按需生成或废弃。 |
| AC-008 | capability-reuse | 新方案复用 Beacon 既有 writeback、transaction lineage、canonical projection 与 host-native orchestration 能力。 |
| AC-009 | prototype-non-template | `prototype auto` 在 host/LLM compile 失败时不会静默落到固定模板成功路径；系统会显式 downgrade 或阻断。 |
| AC-010 | qa-three-sink-transaction | QA acceptance transaction 共享一致事务元数据，并覆盖 machine sink、human sink、runtime projection sink。 |
| AC-011 | transaction-contract-consumers | `status / doctor / gate / release` 读取同一 transaction contract，并在 drift / failed transaction / missing projection 时阻断 pass verdict。 |
| AC-012 | promised-vs-shipped-drift-gate | Beacon 会正式比较 promised operator surface 与 shipped implementation surface，并在 drift 未收敛时阻断 pass / release-ready。 |
| AC-013 | prd-non-generic-compile | `beacon prd create` 成功结果必须是 requirement-aware PRD compile；generic placeholder 只能作为 downgrade/fail 信号。 |
