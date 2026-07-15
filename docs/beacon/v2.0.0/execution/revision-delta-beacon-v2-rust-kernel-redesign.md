# Beacon Revision Delta

- feature: `beacon-v2-rust-kernel-redesign`
- version: `v2.0.0`
- revision_id: `R5`
- source_revision_id: `R4`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `9`
- added_requirement_count: `25`

## Removed Requirement Surfaces
- `AC-021` 33 skills 全量
- `AC-015` Python gate 对比
- `AC-102` **（P3）：`beacon doctor verify-truth-integrity` 在 v2 路由到 gate 或 PyO3 compat；`--mode block` exit code 与 v1.6 一致。
- `AC-033` **：`beacon-python` 通过 PyO3 暴露 v1 兼容 API；33 个 host skills 在 P4 前不得破坏路由契约。
- `AC-075` **：`BEACON_V2=1` 启用 Rust 路径；P6 前 opt-in。
- `AC-077` **：Python fallback 时 `--verbose` 打印 `compat_route=python`。
- `AC-034` **：Python 层在 P4 前可继续承载未迁移子命令；新能力优先落 Rust CLI。
- `AC-098` **：skill 回归失败 → `beacon-gov-doctor`，禁止静默 Python 回退。
- `AC-016` opt-in `BEACON_V2=1`

## Added Requirement Surfaces
- `AC-020` 六能力 surface + legacy removal
- `AC-015` legacy projection/import 只读对照
- `AC-106` **（P3）：`beacon doctor verify-truth-integrity` 在 v2 路由到 Rust gate；`--mode block` exit code 与 v1.6 一致，不使用 PyO3 compat。
- `AC-081` **：`beacon harness list --version v2.0.0 --json`（或等价 CLI）只返回六个一等能力及其 contract metadata；不得要求 33 skills smoke 作为 v2 closure。
- `AC-117` **：closure evidence 必须包含可执行行为验证、至少一个有效断言、AC/TC 绑定 artifact 与运行佐证；纯静态 shell、源文本匹配或无行为恢复控件不得满足 closure。
- `AC-102` **：harness surface / legacy removal 回归失败 → `beacon-gov-doctor`，禁止静默 legacy fallback。
- `AC-111` **：implement admission 必须同时验证 truth_frozen、decision_packet_current、design_bound（当 required）、worktree_admitted、program_next_action_aligned、dependencies_closed。
- `AC-109` **：intent confidence 低、强意图冲突、scope 未确认或 deferral 未拍板时，truth freeze fail-closed。
- `AC-114` **：loop guardrails 包含 pattern registry、failure catalog、token budget、readiness audit、workspace lease、protected path denylist。
- `AC-110` **：loop 启动必须读取 `decision_packet.v1`；缺失、过期或引用未接受 prompt snapshot 时不得进入 implement。
- `AC-116` **：QA defect 必须形成 defect -> fix -> regression evidence chain；缺段 `repair_chain_broken` 或 `regression_skipped` 时 release block。
- `AC-115` **：qa-evidence 必须产出 confidence_chain 与 truth-derived business FSM coverage；状态机 gap 削弱或阻断对应 evidence claim。
- `AC-118` **：release human gate 是不变量；`auto_decide=true` 不得触发 release gate 通过。
- `AC-113` **：remediation sandbox 在 governed worktree 内执行 overlay/eval/rollback；不得写 canonical truth，eval pass 后仍需 human review。
- `AC-112` **：stagnation detector 基于 agent trace 确定性识别 repeat_failure / repeat_labor / plateau，输出 `stagnation-report.v1`。
- `AC-107` **：v1 Python / Node / 33 skills compatibility 从 v2 core closure 移除；只保留为 migration/archive reference。
- `AC-037` **：v1 Python / Node / 33 skills 只可作为 migration/archive reference；v2 新能力不得 fallback 到 Python 路由。
- `AC-036` **：v2 core closure **不包含** `beacon-python` / PyO3 / v1 Python runtime fallback；若仓库仍存在历史 scaffold，必须在 P4 前移除或标记为 archive-only，不能作为验收依赖。
- `AC-078` **：v2 默认走 Rust 路径；`BEACON_V2=1` 不再是 opt-in 兼容开关。
- `AC-080` **：任何 v1 Python/legacy skill invocation 在 v2 core 中必须返回 migration/archive route 或 `reason_code=legacy_python_removed`，不得静默 fallback。
- `AC-108` **：每轮 plan/truth/review/brainstorm 必须保存 prompt snapshot hash，并标记 accepted/latest；loop 只能消费 latest accepted snapshot。
- `AC-033` ..114）
- `AC-034` ..116）
- `AC-035` ..123）
- `AC-032` ）
