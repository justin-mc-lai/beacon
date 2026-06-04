# Beacon Implementation Tasks Ledger

- feature: `beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor`
- version: `v1.4.0`
- plan_id: `plan-beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor-r1`
- revision_id: `R1`
- progress: `18/18`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/archive/v1.4.0/.machine/execution/implementation-plan-beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.progress.json`
- canonical_plan_json: `docs/beacon/archive/v1.4.0/.machine/execution/implementation-plan-beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` FR-001 Beacon 必须冻结一套正式的 v2 轻量内核分层
  - tests=TC-001,TC-060,TC-061,TC-062,TC-063,TC-064,TC-065,TC-066,TC-067,TC-068,TC-002
[x] `ITASK-002` FR-002 Beacon 必须正式定义 minimal machine contract
  - tests=TC-058 | depends_on=ITASK-001
[x] `ITASK-003` FR-003 machine contract 必须由 markdown 单向编译得出
  - tests=TC-003,TC-004 | depends_on=ITASK-002
[x] `ITASK-004` FR-004 Beacon 必须重新定义事务性双写为“canonical 驱动的单向投影”
  - tests=TC-059,TC-057 | depends_on=ITASK-003
[x] `ITASK-005` FR-005 基础 code gate 基座能力必须完整保留
  - tests=TEST-028 | depends_on=ITASK-004
[x] `ITASK-006` FR-006 `implement` 与 `qa` 仍必须是唯一执行入口
  - tests=TEST-019,TEST-018 | depends_on=ITASK-005
[x] `ITASK-007` FR-007 Host-LLM Kernel 必须保留并减耦
  - tests=TEST-013 | depends_on=ITASK-006
[x] `ITASK-008` FR-008 Learning Plane Kernel 必须保留 typed contract，而不是被删掉
  - tests=TEST-008 | depends_on=ITASK-007
[x] `ITASK-009` FR-009 Metadata / Topology Kernel 必须继续作为工程运行底座
  - tests=TEST-009,TEST-025 | depends_on=ITASK-008
[x] `ITASK-010` FR-010 Memory / Workflow Memory Kernel 必须保留统一 envelope
  - tests=TEST-010 | depends_on=ITASK-009
[x] `ITASK-011` FR-011 Archive / Support Surface 必须保留，但不再膨胀为主路径复杂度
  - tests=TEST-056,TEST-051,TEST-011,TEST-012 | depends_on=ITASK-010
[x] `ITASK-012` FR-012 Brainstorm 必须作为只读收敛层被正式保留
  - tests=TEST-045,TEST-054 | depends_on=ITASK-011
[x] `ITASK-013` FR-013 Brainstorm 必须支持统一 route matrix，而不是继续做模板生成器
  - tests=TEST-035 | depends_on=ITASK-012
[x] `ITASK-014` FR-014 Beacon 必须正式分离 core commands 与 plugin/domain commands
  - tests=TEST-014,TEST-053,TEST-023,TEST-041,TEST-050,TEST-015,TEST-042,TEST-046,TEST-057 | depends_on=ITASK-013
[x] `ITASK-015` FR-015 Beacon 必须允许在 requirement freeze 基座上扩展更多场景，但不把扩展默认塞回 core
  - tests=TEST-016,TEST-017,TEST-020,TEST-021,TEST-022,TEST-024,TEST-026 | depends_on=ITASK-014
[x] `ITASK-016` FR-016 `doctor sync-materials` 类历史能力应向 contract compile / verify 语义收敛
  - tests=TEST-027,TEST-029,TEST-030,TEST-031,TEST-032,TEST-033,TEST-034 | depends_on=ITASK-015
[x] `ITASK-017` FR-017 Beacon 必须以“先双读、后单读”的方式迁移，避免 gate 漂移
  - tests=TEST-036,TEST-037,TEST-038,TEST-039,TEST-040,TEST-043,TEST-044 | depends_on=ITASK-016
[x] `ITASK-018` FR-018 `v1.4.0` 必须保留 Python 作为主实现语言
  - tests=TEST-047,TEST-058,TEST-059,TEST-049,TEST-048,TEST-052,TEST-055 | depends_on=ITASK-017
