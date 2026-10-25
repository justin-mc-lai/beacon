## [1.6.19] — 2026-09-21 · 实现前置门阶段化 + precheck 判定内容寻址

### Fixed
- `build_material_audit` 增加阶段维度：实现阶段不再要求 `formal_release_present`（消除「实现前就要 release 产物」的鸡生蛋），release 阶段仍然必需
- precheck bundle 写入 `inputs_digest`（git HEAD + feature 包内容 + release 目录清单），判定与输入绑定
- `record_standard_execution_precheck` 对陈旧 CLI bundle 自动重跑，不再信任旧结论

### Notes
- 单 lake：`beacon-precheck-stage-and-bundle-freshness`

## [1.6.18] — 2026-09-21 · truth FSM 门禁收口

### Fixed
- 生成器对自己的门禁封闭：`render_truth_package` 与 `render_intent_first_truth` 产出的骨架经 `validate_truth_fsm` 判定 `blocked=False`
- `truth review` Check B 与 `freeze` 共用同一校验函数，对同一包判定一致（domain 缺 FSM 双拦，非 domain 双跳过）
- 终态按结构判定：无转出边的目标状态只告警不硬拦；转移缺目标（空 To）硬拦
- 非法转移仅认 `- illegal: a -> b` 前缀与 `from|to` 表格行，含箭头的散文不再触发 `illegal_declared_as_legal`
- `attach_fsm_mermaid` 对过期投影重算，且不改写 FSM 标题之前的无关 mermaid 块；被拦的 `freeze` 不改写 truth.md

### Notes
- 单 lake：`beacon-truth-fsm-terminal-unification`

## [1.6.17] — 2026-08-28 · 能力验证兑现 + 分层边界审计

### Added
- A1 全量 live benchmark 验证：eval `live_skill_pass` 目标 ≥30/37，补齐 prompt fixture 与 surface 解析，按真执行而非 surface 检查
- A2 分层边界审计：产出 import 依赖图 + God Module 清单，用于可维护性风险判断

### Notes
- 两个 lake：`beacon-v1617-live-benchmark-verify`、`beacon-v1617-layering-audit`
- 出处冲突如实记：1.6.16 与 1.6.17 的 SUMMARY 都写了「live_skill_pass 1/37 → ≥30/37」；本条按「验证态」收录，1.6.16 按「落地态」收录

## [1.6.16] — 2026-08-27 · 能力验证补强（对抗式审查落地）

### Added
- skill 级 live 冒烟：37 skill 全跑真实执行
- eval 案例集引入外部锚点（真实失败 / 社区标准），来源可追溯
- gate 判定独立裁判：`coverage_rate` 等关键值重算比对，偏差可审计
- 失败模式目录 5 → 20+ 条，支撑对抗式审查
- auto-merge 后 bad-merge 率基线可比对

### Notes
- 五个 lake：`beacon-v1616-live-skill-smoke`、`beacon-v1616-eval-external-anchor`、`beacon-v1616-gate-independent-judge`、`beacon-v1616-failure-mode-expansion`、`beacon-v1616-bad-merge-baseline`

## [1.6.15] — 2026-08-27 · QA 类型覆盖升级 + 自动合并前置门禁

### Added
- `coverage_rate` 从数量覆盖升级为类型加权：只测 happy path 时 rate < 1.0，并列出 `missing_families`
- 非浏览器（contract / docs / unit）场景展开类型 family（happy + negative + boundary），不再 primary-only
- 自动合并前置门禁：类型覆盖 + 失败模式回归命中 0 + 对抗式审查通过，三条件全过才允许合并 main
- 含 1.6.14 补丁：三个 lake 的 `scenario_family` 标注 + 重跑 QA

### Notes
- runtime 升 `v1.6.15`（`story_scenarios.py` / `qa_feature.py` / `coverage.py` + 新 gate）
- release 人类 gate 保持不变（不自动打 tag / 部署 / 发布）

## [1.6.14] — 2026-08-27 · 批次1：FSM 升级 + FSM 测试生成 + Feature Map

### Added
- truth 的 FSM 五元组自动附带 `stateDiagram-v2` mermaid 投影，文档可渲染
- FSM 机器校验进入 freeze 门禁：状态未定义 / 转移不合法 / illegal 未声明 → `truth_fsm_invalid` fail-closed
- 行为变化 digest 与措辞变化 digest 分离（措辞改动不改变行为 digest）
- 从合法 FSM 自动生成 legal-walk 测试用例（vertex=断言、illegal 路径不生成）
- 每个 feature 派生 `feature-map.md`：入口 + 验证命令绑定 AC，单向投影不改 truth

### Notes
- runtime 仍 `v1.6.12`（本批次以 docs/truth 面 + beacon 框架代码交付，runtime 语义未破坏）
- 三个 lake：mermaid 校验 / legal-walk 生成 / feature-map

## [1.6.13] — 2026-08-27 · 批次1：人话契约 + spend 账本 + 失败模式回归 + skill 文案卫生

### Added
- 7 个 beacon core skill 输出契约强制 `plain_language_delivery_summary`
- goal 预算从回合上限升级为 spend 账本（幂等 CAS、quiet skip 不扣、配额耗尽 halt）
- 失败模式目录（≥5 条 + rubric）接入 QA / release 对抗式审查

### Fixed
- 共享守则单一来源、复制 bug 清零、过期版本锚点清理、`truth-review` → `eval-truth-review` 改名

### Notes
- runtime 仍 `v1.6.12`（本批次以 docs/truth 面交付为主，runtime 未升级）
- 四个 lake：F4 人话契约 / D2 spend 账本 / D3 失败模式用例库 / F2-F3-F5 文案扫尾

## [1.6.12] — 2026-08-17 · main delivery-surface recovery + goal LoopX acceptance closure

### Added
- Program-level lake driver: `beacon/utils/program_driver.py` + `beacon program drive <slug>` CLI. Consumes `build_program_orchestrator_state` routes and dispatches one lake-stage per turn (truth → implement → qa) to the host agent; release is never dispatched (human gate). Stops emit `reason_code` + `resume_action` (+ `recommended_command`) per AC-039, with blocked-streak (≥3) / turn-budget guards and filesystem-evidence crash resume. Drive state lives at `docs/beacon/<v>/programs/<slug>/program-drive-state.json`; lock at `.beacon/state/program-drive/<slug>.lock`.
- Goal run terminal takeover hint (`program_takeover` in facade payload + `recommended_next.program`): when the program route has a pending next lake, goal output points to `beacon program drive`; prompt-level only, goal never auto-spawns the driver.
- P0 audit fixes (08-26-p0-audit-fixes): truth-promotion receipts are discovered under either `lakes/<row-slug>/` or `lakes/<feature-slug>/`; orchestrator closure evidence is keyed by the canonical `feature_slug` (row slug kept for display, graph deps alias-resolved); unbound goal payloads carry an additive `program_binding` diagnostic (`reason_code`: `program_not_frozen` / `feature_not_in_graph` / `graph_invalid`, with per-program `checked[]` and a hint; bound goals report `{status:"bound", program_slug}`; no `programs/` dir attaches nothing); goal complete backfills missing `.machine/execution/implementation-summary-<slug>.json` and `qa-acceptance-<slug>.json` citing only real evidence (verifier refs / on-disk QA scorecards), skipping with a `closure_backfill_skipped:<reason>` history event instead of fabricating.

### Fixed
- Restore deleted `pyproject.toml`, `tests/` tree (484 files incl. 25 v1.6.12 goal canaries), and `scripts/` from the pre-checkpoint snapshot; main is installable and testable again.
- Track the canonical `skills/beacon/` package (1+6 public surface + patterns/incidents) in git; remove implicit untracked symlink dependency.
- Close the v1.6.12 goal feature acceptance: 26 canary + 16 life-cycle guardrail tests green on main, implement/QA evidence recorded, feature-graph + authenticated program freeze pass, program state aligned (`program_frozen`/all-lakes-complete).
- Rebuild `test-contract-index` from frozen truth; fix TC-007 to reference the real tracked legacy state bundle.
- Align version surfaces: onboarding/python/README to v1.6.12, catalog active window converged to v1.6.10/11/12, stale top-level delivery roots relocated to `docs/beacon/archive/`.
- Add ignore rules for `packages/**` build artifacts and `*.egg-info/`; untrack generated backups and egg-info metadata.

### Notes
- Release gate: still awaits human confirmation on v1.6.12 (loop-goal release is human-gated).

## [1.6.11] — 2026-07-27 · Plan/Goal Task Closure

### Added
- planning-only 交付线（运行时仍 `v1.6.10`）：把「口头大目标」升级为可追溯、可委派、真实 worktree 隔离、可人工纠偏、可取消重排、可验证收敛的 Program
- Program `beacon-plan-goal-task-closure-v1611`：九湖（L0–L8）由 R1 重冻为 R2，加入 CLI scaffold + Host Agent（skill-authored fill）全包填充与 authenticated Program freeze 要求
- 大目标先绑定主分支代码、冻结 truth 与测试/历史 change 基线；意图递归拆全后生成 Before→After change 与状态机差异
- Journey / AC / 状态差异编译成可承载 100+ 节点的原子任务 DAG；取消任务后重算 ready set，无替代依赖时阻断路径
- 子代理只产出 finding/patch/evidence，主代理保留状态转换与 goal 完成权；无宿主并行能力时诚实降级
- truth 只在 `main` 冻结；direct / goal / team / ralph 的实现任务统一经过真实 git worktree admission
- CLI 只确定性创建四文件 scaffold；Host Agent 通过结构化 response 填充需求，不允许直接覆盖 Markdown
- Program freeze 必须校验 PAC→AC→TC→task/evidence→R2/hash、双门报告、human ack 与 promotion receipt，不能只看状态字符串
- 旧 package/ledger 不兼容读取；保留旧冻结真相作为 lineage，通过新 revision 重冻向前迁移

### Notes
- Program manifest: `docs/beacon/v1.6.11/programs/beacon-plan-goal-task-closure-v1611/program-manifest.md`
- Feature graph: `docs/beacon/v1.6.11/programs/beacon-plan-goal-task-closure-v1611/feature-graph.json`
- baseline commit: `30b9adffc8ec5442a7691a88faf64a251d97b98f`
- Draft add-on `design-craft-absorption-v1611` 为 R0 draft，不改 L0–L8 program freeze

## [1.6.10] — 2026-07-22 · Truth Authority + Humanizer + Truth Review Gate

### Added
- Plan → Truth 成为首冻前的最高优先级强制评审门；implement / qa 只从已冻结 truth 派生
- Truth Review Gate：Intent 矩阵 + FSM 审计 + 可测性 + Humanizer 润色，然后才 freeze；post-freeze 走 reopen → verify-materials → refreeze，tests / tasks 级联 stale
- FSM 口径：State | Event | Guard | To | Action（含 illegal，无挂起状态）
- Gold 样本：订单支付 / 超时关单 / 退款 + Intent×AC 矩阵；Humanizer 走 oss-sync 全文，默认 zh / en
- Host plan-review VoltPack（R1，已冻结）：`plan-review` = 10 个 VoltAgent 精选角色，默认单线程；套件 `tests/test_v1610_plan_host_subagent_voltpack.py`

### Notes
- Program `beacon-truth-authority-humanizer-v1610`：truth-core R3 / truth-gold R3 / humanizer R2 / trace-lifecycle-binding R1 / compat-debt-cut R1 / unified-implement-admission R1
- 状态：runtime / package / docs 线到 `v1.6.10`；unified implement admission 为 truth 已冻、实现待落；release 仍人工门
- 锁定决策 UD-T1610-008..010：Plan→Truth 为强制评审门、Draft→Review(A/B/C+Humanizer)→Freeze 三步、`beacon truth review` 未 pass 不得 freeze

## [1.6.9] — 2026-07-20 · Public Surface 1+6 Alignment

### Added
- 冻结与 `v2.0.0` Loom 共享的 Scheme A 宿主可见公开面：1 个横向 goal（长跑）+ 6 个 harness 能力（plan / truth / design / implement / qa / release）
- 规范表落在 `skills/beacon/references/public-surface-1plus6.md`

### Notes
- Program `beacon-public-surface-1plus6-v169`，含 10 个已冻结 feature lake：1+6 同义表、渐进加载无能力损失、plan 强意图路由、plan artifact + goal 软门、goal implement 硬准入、implement lane 强制（git hooks 拦 main 业务提交）、版本/热修默认 + skill 瘦身、运行时与项目 docs 双轴默认、项目定时任务与执行日志、关闭 goal/hooks main 旁路

## [1.6.8] — 2026-07-19 · Production Ops Hardening

### Added
- 生产热修车道、release self-heal profile、longrun 默认、版本舰队运维；工程哲学同步到 v2 / Loom
- 公开入口只留 `$beacon-goal` / `beacon goal run`
- Hotfix：`beacon goal run "…" --mode hotfix --from-version <tag>`；Longrun：项目级 `goal.longrun_default`（新项目默认 true）

### Notes
- Program `beacon-prod-ops-hardening-v168`，6 个 lake 按 Wave 0–4 交付：版本舰队 + 双版本产品化、release profile 自愈、hotfix 车道（含 forward-port 与 rollback）、longrun 默认 + auto driver、goalrun 主轴挂载、v2/Loom 运维哲学同步
- Promotion 来源：`docs/beacon/v1.6.7/research/beacon-v168-prod-ops-hardening-pln-review.md`
- 状态：truth 六湖全冻 R1；implement 已落 main（`e3d63efe` / merge `844739e4`）

## [1.6.7] — 2026-07-16 · version-surface + catalog cutover

### Fixed
- Promote package/runtime/docs default line to **v1.6.7** via `beacon/version-truth.json` and `beacon doctor sync-version-surfaces`
- Align public entry surfaces (README current-line claims, root `SKILL.md`, host skill metadata) with package truth
- Advance version-truth-catalog active window to `v1.6.5 / v1.6.6 / v1.6.7` (archive older delivery roots)

### Notes
- Feature program `beacon-unified-topology-loop-goal-v167` remains the v1.6.7 capability delivery (GitScopeGraph + loop-goal R7)
- This entry closes the release-entry consistency gap called out after comprehensive project diagnosis

## [1.6.1] — 2026-06-23 · fix/p0-p1-p2 (P0/P1/P2 fix batch)

### Added (P1)
- `scripts/beacon-install.sh` — idempotent symlink installer for all 10 host surfaces (agents, codex, cursor, trae, windsurf, opencode, pi, qoder, trellis, reasonix); guards against duplicate real-directory installs; supports `DRY_RUN=true`
- `scripts/generate-host-surfaces.py` — single-spec host surface generator driven by `beacon/version-truth.json`; supports `--check` (CI) and `--dry-run` (preview) modes; replaces manual maintenance of 10+ host directories
- `.github/workflows/version-gate.yml` — CI gate that fails the build when `pyproject.toml`, `README.md`, or `SKILL.md` diverge from `beacon/version-truth.json`; triggered on every push to main/pre-main/beacon/v*/fix/*/feat/* and every PR targeting main

### Fixed (P0)
- `.gitignore` — added rules to stop tracking Python build artifacts (`__pycache__/`, `*.egg-info/`, `dist/`, `build/`), Node artifacts (`node_modules/`, `packages/*/dist/`, `*.tsbuildinfo`), Beacon runtime state (`test-results/`, `.beacon/state/`, `.reasonix/truncated-results/`, `.omc/sessions/`), and IDE/OS noise (`.DS_Store`, `.idea/`)

### Pending (requires local git CLI — cannot be done via web editor)
- Remove already-tracked generated artifacts: `git rm -r --cached test-results/ beacon.egg-info/ .reasonix/truncated-results/ .omc/sessions/`
- Fix README.md version references: `sed -i 's/v1\.6\.0/v1\.6\.1/g' README.md && git commit -m "docs(p0): update README version v1.6.0 -> v1.6.1"`

<!--
日期口径：新增条目（1.6.8–1.6.11、1.6.13–1.6.19）的日期取该版本 SUMMARY.md 首次提交日，复跑命令：
  git log --follow --diff-filter=A -1 --format=%ad --date=short -- docs/beacon/v<ver>/SUMMARY.md
（1.6.8 与 1.6.9 的 SUMMARY 在 docs/beacon/archive/ 下，命令里换成 archive/ 路径）
1.6.12 条目沿用原有日期 2026-08-17（其 SUMMARY 首次提交日为 2026-08-09），未改动原记录。
1.6.8–1.6.19 十二个版本的 SUMMARY 全部存在（含 archive/ 下两个），故无「无 SUMMARY 记录」条目。
-->
