# User Story: Beacon v1.3.9 beacon-friction-intake and sqlite governance queue

## Story Boundary

- version: `v1.3.9`
- feature: `beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue`
- status: `frozen`
- upstream_prd: `docs/beacon/archive/v1.3.9/prd/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`

本故事线只覆盖 Beacon 的摩擦录入与治理入口，不扩展成新的主生命周期 stage，也不自动改写 requirement truth。

## Story 1: 统一摩擦录入入口

作为 Beacon 使用者，我希望存在一个语义明确的 `beacon-friction-intake` 入口，以便我在记录或扫描摩擦时，不再把它理解成一次“分析报告生成”动作。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | naming | Beacon 对外存在统一的 `beacon-friction-intake` 能力定义，作为长期推荐入口。 |
| AC-002 | compatibility | 旧的 `memory-friction-evolution` 可以作为兼容实现来源存在，但不再作为长期主语义。 |
| AC-003 | boundary | `beacon-friction-intake` 被定义为 support-surface 入口，而不是新的主 Beacon stage。 |

## Story 2: Beacon 源码项目自动扫描摩擦

作为 Beacon 维护者，我希望在 Beacon 源码项目中运行 `scan` 模式，自动扫描项目摩擦、阻塞、bug 与重复问题，以便把产品演进线索沉淀进统一治理队列。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | scan-mode | 在 Beacon 源码项目中可以执行 `scan` 模式，自动提取项目摩擦、阻塞、bug 或重复问题。 |
| AC-102 | evidence | `scan` 结果能够绑定项目内证据来源，如 `.beacon/debug/`、`.beacon/memory/`、`.beacon/analysis/` 或等价运行证据。 |
| AC-103 | classification | `scan` 结果会被标准化成统一 friction item，而不是只产出一次性的分析报告。 |

## Story 3: 目标开发项目人工记录摩擦

作为目标开发项目操作者，我希望在项目根目录通过 `capture` 模式记录一次上下文摩擦，以便将我的人工输入交给 LLM 归一化、分类并纳入治理。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | capture-mode | 在目标开发项目中可以执行 `capture` 模式，记录一次人工输入的上下文摩擦。 |
| AC-202 | llm-normalization | 系统会对人工记录执行 summary 规范化、分类、严重级别判断、领域判断与证据引用绑定。 |
| AC-203 | source-type | 人工记录项与自动扫描项会通过 `source_type` 或等价字段区分，但进入同一治理队列。 |

## Story 4: 统一 sqlite 队列治理

作为 Beacon 治理者，我希望 `scan` 与 `capture` 两种来源都进入同一个全局 sqlite 队列，以便进行 claim、resolve、reopen 与后续持续治理。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | dual-write | 任一 `scan` 或 `capture` 完成后，项目内证据可保留，同时全局 sqlite 中出现对应 friction item。 |
| AC-302 | queue-state | friction item 至少具有可治理的状态流，如 `queued`、`claimed`、`resolved`、`reopened` 或等价状态。 |
| AC-303 | sqlite-recovery | 当 sqlite 暂时不可用时，dual-write 失败会显式记录，且后续支持恢复与重放。 |

## Story 5: 分类模型可直接服务产品治理

作为 Beacon 产品演进负责人，我希望每条 friction item 都具有可比较、可排序、可过滤的治理字段，以便判断它是否属于阻塞 bug、改进或优化增强。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | item-class | 每条 friction item 至少会落入 `blocking_bug`、`improvement`、`optimization_enhancement` 之一。 |
| AC-402 | governance-fields | 每条 friction item 至少具备 summary、source_type、severity、domain、queue_status、project_root、evidence_refs、first_seen_at、last_seen_at 或等价字段。 |
| AC-403 | projection-boundary | `debug_issues` 保持 runtime projection 快照定位，不能直接替代治理队列。 |

## Story 6: requirement/change 路由必须显式接受

作为 Beacon requirement owner，我希望摩擦项默认只停留在治理队列，只有显式接受后才进入 `beacon-prd` 或 `beacon-change`，以便保护 frozen requirement truth。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | default-queue-only | 新摩擦项默认只进入治理队列，不自动进入 `prd`、`user-story`、`test-case`、`implement`、`qa` 或 `release`。 |
| AC-502 | explicit-gate | 只有进入 `accepted_for_requirement` 或等价显式接受状态后，摩擦项才允许路由到 `beacon-prd` 或 `beacon-change`。 |
| AC-503 | truth-protection | requirement truth 的更新仍由正式 requirement/change surface 负责，而非 intake 入口直接写入。 |

## Story 7: 原始证据 truth 必须可恢复

作为 Beacon 维护者，我希望项目内原始证据始终保留并可用于恢复治理队列，以便全局 sqlite 不是唯一真相来源。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-601 | local-truth | `.beacon/debug/`、`.beacon/memory/`、`.beacon/analysis/` 或等价项目内产物继续承担原始证据 truth。 |
| AC-602 | no-second-truth | 全局 sqlite 只存治理必需的索引、分类、状态与引用，不存第二份完整正文 truth。 |
| AC-603 | replay | 当全局 sqlite 被删除、重建或临时不可用时，系统仍可从项目内原始证据重新驱动 intake/replay。 |
