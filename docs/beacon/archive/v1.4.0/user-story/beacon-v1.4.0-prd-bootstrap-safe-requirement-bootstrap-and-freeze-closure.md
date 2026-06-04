# User Story: Beacon v1.4.0 PRD bootstrap safe requirement bootstrap and freeze closure

## Story Boundary

- version: `v1.4.0`
- feature: `beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure`
- status: `freeze-ready`
- upstream_prd: `docs/beacon/archive/v1.4.0/prd/beacon-v1.4.0-prd-bootstrap-safe-requirement-bootstrap-and-freeze-closure.md`
- current_revision: `R1`
- source_revision: `R0`

本故事线覆盖 `beacon-prd-bootstrap` 在 `v1.4.0` 中的正式 requirement freeze。目标不是把它升级成新的生命周期，而是把它收敛成一个安全、可审计、可路由回主流程的 requirement bootstrap support surface。

## Diagram Truth

- `branch-flow`
  - `feature intent -> bootstrap draft package -> review/refreeze -> frozen requirement package`
  - bootstrap 不得绕过主链，也不得直接宣称 implement-ready
- `decision-priority`
  - `frozen truth > bootstrap draft > state artifact`
  - `context/gate safety > convenience`
  - `mainline lifecycle > optional support skill`

## Story 1: `beacon-prd-bootstrap` 必须继续是 optional support skill，而不是新的主流程

作为 Beacon 产品 owner，我希望 `prd-bootstrap` 继续留在 optional skill 层，而不是升级成新的 public mainline，这样 Beacon 的轻量主面不会再次膨胀。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | optional-surface | `beacon-prd-bootstrap` 必须明确标记为 optional support skill。 |
| AC-002 | no-public-stage | 系统不得把 `prd-bootstrap` 升格为新的 public lifecycle stage。 |
| AC-003 | no-mainline-replacement | `prd-bootstrap` 不得替代 `prd / user-story / test-case` 的正式主链语义。 |
| AC-004 | lightweight-alignment | 该能力必须与 `v1.4.0` 轻量内核原则保持一致。 |

## Story 2: 系统必须支持一键生成 requirement draft package

作为需求操作者，我希望一次运行即可生成 `prd + user-story + test-case`，这样我可以快速初始化 requirement package，而不是手工先搭三份空文档。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | three-doc-bootstrap | 一次运行必须可生成 `prd / user-story / test-case` 三份文档。 |
| AC-102 | canonical-paths | 文档必须写入当前版本 canonical docs tree。 |
| AC-103 | shared-identity | 三份文档必须共享一致的 feature slug、version 与 generation identity。 |
| AC-104 | no-side-truth | bootstrap 只生成 requirement draft package，不得新增旁路 truth tree。 |

## Story 3: 默认安全防线必须完整保留

作为维护者，我希望 bootstrap 默认仍然 fail-closed，而不是为了方便降低风控，这样 requirement 启动摩擦下降时不会同时放大真相漂移风险。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | strict-context-verify | 运行前必须默认执行 `doctor verify-context --strict`。 |
| AC-202 | dry-run-default | 默认必须是 `dry-run`，只有显式 `--apply` 才允许写盘。 |
| AC-203 | no-overwrite-default | 默认必须 `no-overwrite`，遇到既有文档必须阻断。 |
| AC-204 | fail-closed | context、quality、consistency、lock 任一失败都必须 fail-closed。 |

## Story 4: Apply 写入必须原子、可回滚、可并发防护

作为平台维护者，我希望 apply 路径具备锁、原子写入、状态记录和回滚计划，这样 bootstrap 失败时不会留下半成品 requirement truth。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | lock-protection | 运行期间必须持有 `prd-bootstrap.lock` 防并发冲突。 |
| AC-302 | atomic-write | 写入必须使用原子替换，不得留下半成品文档。 |
| AC-303 | state-artifact | 运行后必须写出 state artifact。 |
| AC-304 | rollback-manifest | apply 结果必须附带 rollback manifest。 |

## Story 5: bootstrap 产物必须显式标记为 draft，而不是自动 frozen truth

作为 requirement governance owner，我希望 bootstrap 输出在状态语义上明确“还需要 review / refreeze”，这样自动生成不会伪装成已冻结真相。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | bootstrap-generated-status | 产物必须显式表达 `bootstrap-generated` 语义。 |
| AC-402 | review-required-status | 产物必须显式表达 `review-required` 语义。 |
| AC-403 | not-yet-frozen | 产物不得默认表达已经 frozen 或 implement-ready。 |
| AC-404 | route-to-refreeze | support output 必须把后续动作路由回 review/refreeze 主链。 |

## Story 6: bootstrap 产物必须具备最小 traceability 与结构对齐

作为后续 implement/qa 使用者，我希望 bootstrap 产物即便还是 draft，也已经具备最小可追踪结构，这样它能平滑进入后续 requirement 补齐，而不是必须全部重写。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | shared-metadata | 三份文档必须共享 version、feature、generated identity 等元信息。 |
| AC-502 | ac-tc-traceability | user-story 与 test-case 必须至少具备最小 AC/TC traceability。 |
| AC-503 | v140-format-alignment | 输出必须对齐 `v1.4.0` 的文档结构与状态口径。 |
| AC-504 | downstream-readable | change/review/refreeze/gate 必须能读取这些最小结构。 |

## Story 7: bootstrap 运行必须有质量和一致性门禁

作为治理 owner，我希望系统能在 bootstrap 阶段就阻断明显不合格产物，而不是把问题推到后面的 implement 或 qa 阶段。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-601 | placeholder-threshold | placeholder 超阈值时必须阻断。 |
| AC-602 | ac-mapping-complete | story AC 与 test-case 覆盖映射不完整时必须阻断。 |
| AC-603 | overwrite-risk-blocked | 默认覆盖风险必须阻断并给单一恢复命令。 |
| AC-604 | state-not-truth | quality/state artifact 只能做审计依据，不得成为 truth source。 |

## Story 8: 输出必须对人类清晰解释下一步

作为使用者，我希望 bootstrap 的结果能告诉我当前状态、为什么被阻断、接下来该做什么，这样它才是真正降低摩擦，而不是只输出一堆内部细节。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-701 | current-status-visible | 输出必须清晰展示当前状态。 |
| AC-702 | blocked-reason-visible | 如被阻断，必须展示阻断原因。 |
| AC-703 | next-command-visible | 输出必须提供建议下一步命令。 |
| AC-704 | freeze-gap-visible | 输出必须说明距进入 freeze 主链还缺什么。 |

## Delivery Notes

- 这条 feature 线不要求重做主流程，而是把一个已经存在的 optional bootstrap capability 正式收编到 `v1.4.0`。
- 重点是：
  - 定位边界
  - 安全默认值
  - draft/frozen 语义分离
  - traceability
  - human next-step clarity

## Freeze Notes

- 当前冻结目标不是证明 `prd-bootstrap` 代码已经完全符合 `v1.4.0`，而是把它需要符合的 contract 正式冻结。
- 如果后续实现仍继续：
  - 生成旧式模板化文档
  - 混淆 draft 与 frozen truth
  - 缺少统一 next-step guidance
  则该 feature 不应视为完成。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 8 |
| Status | freeze-ready-bootstrap-r1 |
| Created | 2026-05-06 |
| Change Scope | optional-skill / requirement-bootstrap / safety-defaults / traceability / draft-status / review-routing |
