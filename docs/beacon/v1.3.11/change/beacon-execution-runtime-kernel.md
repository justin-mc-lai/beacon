# Beacon Feature Change Document

- feature: `beacon-execution-runtime-kernel`
- feature_slug: `beacon-execution-runtime-kernel`
- version: `v1.3.11`
- status: `reopened-for-runtime-closure`

## Scope
- version-level baseline host stabilization
- host-driven implementation ordering
- runtime truth boundary and recovery closure

## Added
- `version-level-baseline-host` 作为同版本多 feature 的唯一稳定宿主，禁止 feature baseline 因共享版本容器互相覆盖。
- `host-driven-implementation-ordering` 作为正式 requirement line，统一输出 `ordered_feature_slugs / waves / conflict_reason_codes / manual_intervention_required`。
- runtime kernel admission 必须显式校验 `baseline host / workspace scope / writable services / evidence sink / blocked dependency`，不满足时 fail-closed。
- runtime read model 必须作为 operator workbench 的唯一权威运行态来源之一，禁止 UI 或散落 surface 自行拼装“当前状态”。
- `prototype-host-native-runtime-admission-and-execution` 作为正式 requirement line，要求 prototype compiler 优先走 `codex|claude` host runtime，而不是继续把 env/file 注入 JSON 误当作默认宿主执行面。

## Removed / Reduced
- 降低“同版本多个 feature 只要 markdown block 不互相覆盖即可”的错误假设。
- 降低“实现顺序可由 implement surface 临时推导”的隐式机制依赖。
- 降低“recovery 只靠人工理解 workspace 与状态残留”的操作风险。

## Fixed
- 明确 runtime kernel 不只是长任务调度包装层，还必须承担版本级 baseline host、ordering、recovery、workspace/evidence isolation 的统一约束面。
- 明确 feature ordering 的稳定输入面必须回到 baseline host registry，而不是继续散落在 `change payload / technical review contract / surface-local fallback`。
- 明确同版本多 feature 共存时，baseline、workspace、evidence、run 状态必须一起受 feature-aware host 校验约束。
- 明确 runtime drift、workspace drift、blocked dependency、retry orphan 需要 reason code 与 repair path，而不是继续依赖人工排查。
- 明确 prototype 的 `host_semantic_ready` 不得再等价为“存在 `BEACON_HOST_*_RESPONSE_JSON/FILE` 注入”，而必须表达“宿主运行时可执行 host-native compile”。
- 明确 prototype host path 的 transport 可以兼容旧注入协议，但 admission 和 execution 默认面必须是 shared host-native runtime contract。
- 明确当 `codex|claude` host runtime 可用且 provider bridge 可执行时，prototype compile 必须先走 host path，再决定是否降级 rule。

## Not Added
- 未新增新的公开一级生命周期 stage。
- 未引入脱离 requirement truth 的独立 runtime truth source。
- 未把 Beacon 扩张为通用 CI/CD 或分布式调度平台。

## Refresh Route
- `prd revise`: `docs/beacon/v1.3.11/prd/beacon-execution-runtime-kernel.md`
- `user-story refresh`: `docs/beacon/v1.3.11/user-story/beacon-execution-runtime-kernel.md`
- `test-case refresh`: `docs/beacon/v1.3.11/qa/test-cases/beacon-execution-runtime-kernel.md`
- `prototype impact`: `docs/beacon/v1.3.11/prototype/beacon-operator-workbench-and-board-launcher/`

## Traceability Refs
- `docs/beacon/v1.3.11/prd/beacon-execution-runtime-kernel.md`
- `docs/beacon/v1.3.11/user-story/beacon-execution-runtime-kernel.md`
- `docs/beacon/v1.3.11/qa/test-cases/beacon-execution-runtime-kernel.md`
- `docs/beacon/v1.3.11/prd/beacon-operator-workbench-and-board-launcher.md`
- `docs/beacon/v1.3.11/execution/revision-delta-beacon-execution-runtime-kernel.md`
