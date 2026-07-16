# Beacon Revision Delta

- feature: `beacon-v2-rust-kernel-redesign`
- version: `v2.0.0`
- revision_id: `R17`
- source_revision_id: `R16`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `9`
- added_requirement_count: `19`

## Removed Requirement Surfaces
- `AC-015` legacy projection/import 只读对照
- `AC-084` **：`beacon harness list --version v2.0.0 --json`（或等价 CLI）只返回六个一等能力及其 contract metadata；不得要求 33 skills smoke 作为 v2 closure。
- `AC-106` **：benchmark 相对 baseline 回退 >10% 阻断 P6 switch-over。
- `AC-105` **：harness surface / legacy removal 回归失败 → `beacon-gov-doctor`，禁止静默 legacy fallback。
- `AC-110` **：v1 Python / Node / 33 skills compatibility 从 v2 core closure 移除；只保留为 migration/archive reference。
- `AC-040` **：v1 Python / Node / 33 skills 只可作为 migration/archive reference；v2 新能力不得 fallback 到 Python 路由。
- `AC-081` **：v2 默认走 Rust 路径；`BEACON_V2=1` 不再是 opt-in 兼容开关。
- `AC-083` **：任何 v1 Python/legacy skill invocation 在 v2 core 中必须返回 migration/archive route 或 `reason_code=legacy_python_removed`，不得静默 fallback。
- `AC-014` beacon-loop 并行

## Added Requirement Surfaces
- `AC-015` 迁移为可选对照，不强迫退役 v1
- `AC-086` **：`beacon harness list --version v2.0.0 --json`（或等价 CLI）只返回六个一等能力及其 contract metadata；不得要求 33/37 skills smoke 作为 v2 closure；v1 skill 矩阵验收留在 v1 轨。
- `AC-141` **：Beacon 产品策略为长期双轨：`track_v1`（Python CLI + v1 skill 面）与 `track_v2`（Rust kernel + 六 public skill）对等并存；任一轨的 release/成熟度门禁 **不得** 隐含关停另一轨。
- `AC-146` **：skill 评分产物权威为 `runtime_evidence_only`；**不得**替代 `qa-evidence` formal QA，**不得**替代 `release` 人放行；scorecard 必须声明该边界。
- `AC-148` **：v1 `beacon eval` 既有 scorecard 维度可映射进统一 schema，但发布门必须以统一 schema 的稳定字段为准；字段漂移须走 change，不得静默改权重冒充同比。
- `AC-112` **：v1 Python / Node / v1 skill 面 **不进入 v2 core closure 的验收依赖**；它们作为 **并行产品轨** 继续交付。v2 closure 不得把「全量 v1 skill 回归」或「PyO3 兼容层」列为必过项；也不得把「删除 v1 轨」列为 v2.0.0 必过项。
- `AC-108` **：v2 benchmark 相对 baseline 回退 >10% 阻断 **v2 P6 成熟度出口**；不授权、不要求关停 v1 轨。
- `AC-107` **：v2 harness surface / cross-track isolation 回归失败 → `beacon-gov-doctor`（或 v2 等价诊断），禁止静默 cross-track fallback。
- `AC-083` **：双轨运行时选择必须 **显式**（例如独立 `beacon-v2` 二进制，或 `beacon --runtime v2` / 等价显式 flag）。禁止用「环境默认偷偷切轨」替代用户/CI 的显式选择；`BEACON_V2=1` 若保留，只能作为 **显式选择的别名**，不得暗示 v1 已退役。
- `AC-142` **：双轨隔离契约——代码树、CLI 入口、skill 根、docs version tree、CI job 必须可分轨合并；同一 PR 若同时修改两轨「发布真源」，必须显式 `dual_track_shared_contract` admission，否则 fail-closed（`reason_code=dual_track_mixed_source`）。
- `AC-085` **：在 **v2 runtime 路径内**，任何把 v1 Python/legacy skill 当执行后端的请求必须 fail-closed，返回 `reason_code=cross_track_fallback_forbidden`（或等价），stdout/stderr **不得** 含 `compat_route=python`。v1 runtime 路径内对 v1 skills 的正常调用 **不受** 本条退休。
- `AC-145` **：统一评分必须包含 **结构质量**（SKILL.md/package/HARD GATE/progressive 合规，对齐 skill-creator / Beacon skill-package-standard）与 **实效质量**（固定 test-prompts 上的路由/边界/越权 negative；with_skill vs baseline 或等价对照），参考 Anthropic skill-creator 与 darwin-skill 的双评思想。
- `AC-147` **：评分执行者与被评 skill 的「修改建议作者」在流程上必须可分离（独立评分会话或独立 grader）；禁止同一无审计步骤既改 skill 又自评涨分。
- `AC-144` **：迁移/导入工具可以只读对照另一轨状态，但不得在双写期成为第二写者（延续 AC-093 单写者原则，按轨分别强制）。
- `AC-143` **：运行时选择必须显式（对齐 AC-060）；禁止 v2 路径执行 v1 backend，禁止 v1 路径把请求静默升级为 v2 并改写用户未请求的行为。
- `AC-014` beacon-loop / v1 CLI 并行
- `AC-030` 禁止 Darwin 式自动改 SKILL.md
- `AC-029` 落地稳依赖可测 skill 资产
- `AC-028` v1/v2 skill+CLI 语言分叉，需合并互不影响
