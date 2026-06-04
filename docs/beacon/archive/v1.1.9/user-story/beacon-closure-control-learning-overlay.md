# User Story: Beacon 闭环控制层、恢复层与学习层增强（v1.1.9）

**Feature**: beacon-closure-control-learning-overlay  
**Version**: v1.1.9

**As a** 使用 Beacon 管理需求、实现、验证与版本迭代的维护者 / 技术负责人 / AI Agent 协作者  
**I want** Beacon 在现有 `workflow / implement / qa / debug / review / gate / release` 基础上，增加正式的控制层、恢复层与学习层  
**So that** 需求到交付不再只是“能跑通”，而是具备失败升级、证据硬门禁、恢复不失忆、技术事实反哺下一轮版本的真闭环。

## Story Slices

### US-001: Beacon 以 overlay 方式增强现有主链
作为 Beacon 维护者，我希望 v1.1.9 是覆盖在现有主链上的增强层，而不是平行重造一套 lifecycle。

### US-002: Beacon 支持 debug failure escalation
作为 Beacon 使用者，我希望 debug 不只是记录反馈，而是能表达 failure streak、escalation level 与下一步 required action。

### US-003: Beacon 支持 checkpoint / resume 恢复语义
作为 Beacon 使用者，我希望中断后恢复时能带回已尝试路径、已排除原因和下一假设，而不是重复试错。

### US-004: Beacon 区分 implementation_done 与 evidence_done
作为 QA / 技术负责人，我希望 Beacon 能区分“实现做完”和“证据闭环完成”，以避免假完成。

### US-005: Beacon 支持 delta-aware QA rerun
作为 QA / Agent，我希望需求或实现变化后，Beacon 能识别哪些测试和证据需要重跑。

### US-006: Beacon 冻结 requirement → implementation → evidence 三层 trace contract
作为评审人，我希望 requirement、implementation、evidence 之间的关系被明确约束，以便能追责与回溯。

### US-007: Beacon 把 artifact_updates 升级为正式 writeback obligation
作为 Beacon 维护者，我希望 implement/review 产生的 artifact_updates 能进入后续 gate/resume/writeback，而不是停留在摘要提示。

### US-008: Beacon 让技术归档反哺下一轮需求
作为版本负责人，我希望 technical archive 与 debug harvest 能直接反哺 PRD / test-case / version planning。

### US-009: Beacon 为后续 evo harness 提供真实输入面
作为 Beacon 维护者，我希望 v1.1.9 先建立 learning input / keep-discard discipline，而不是贸然进入整仓自治。

### US-010: Beacon skill 文档采用一主一辅固定模板
作为 Beacon 使用者 / 维护者，我希望 root `SKILL.md` 和 `skills/beacon/SKILL.md` 有明确主辅角色与固定结构，以便不同入口看到的产品说明、上手方式与阶段导航一致。

### US-011: Beacon 把全生命周期与全端口防漂移一起治理
作为 Beacon 维护者，我希望 anti-drift 不只盯住 workflow/gate，还覆盖 README、skill、CLI、runtime state、installed copies 与 managed blocks，以便入口与执行不再讲两套话。

### US-012: Beacon QA 支持 feature-aware 用户故事顺序验证
作为 QA / 技术负责人，我希望实现完成后可以基于 feature 自动定位 user-story/test-case，并按用户故事与 AC 顺序依次进行验证，以便 QA 真正服务 requirement closure，而不是只跑 layer/scope。

### US-013: Beacon 把 `qa evolve` 升级为正式 delta 验证能力
作为 QA / Agent，我希望 requirement 或 implementation 变化后，Beacon 能识别受影响 AC/TC 并执行 targeted rerun，而不是只靠人工判断。

### US-014: Beacon 把用户故事编译为场景族
作为 QA / Agent，我希望 Beacon 能把 user-story / AC 自动展开为 happy / negative / boundary / recovery / compatibility 等 scenario families，而不是每个 AC 只对应一个轻量 TC。

### US-015: Beacon 采用双层浏览器证据执行器
作为 QA / 技术负责人，我希望浏览器验证分成“探索执行”和“确定性回放”两层，以避免 agent-only 假通过，并让 evidence 能进入正式 gate。

### US-016: Beacon 在 QA 中引入 PUA 式穷尽控制面
作为 QA / 维护者，我希望 Beacon 能跟踪 failure_streak、escalation_level、missing_axes 与 required_next_action，以便测试不只跑一遍，而是真正穷尽关键路径后再宣称完成。

### US-017: Beacon 以故事闸门方式推进浏览器验证
作为 Release owner / QA，我希望 `qa run <feature>` 能按 user-story / AC / scenario 顺序推进，并在 scenario 粒度回写状态，以便 requirement closure 真正绑定浏览器执行事实。

### US-014: Beacon 把用户故事编译为场景族
作为 QA / Agent，我希望 Beacon 能把 user-story / AC 自动展开为 happy / negative / boundary / recovery / compatibility 等 scenario families，而不是每个 AC 只对应一个轻量 TC。

### US-015: Beacon 采用双层浏览器证据执行器
作为 QA / 技术负责人，我希望浏览器验证分成“探索执行”和“确定性回放”两层，以避免 agent-only 假通过，并让 evidence 能进入正式 gate。

### US-016: Beacon 在 QA 中引入 PUA 式穷尽控制面
作为 QA / 维护者，我希望 Beacon 能跟踪 failure_streak、escalation_level、missing_axes 与 required_next_action，以便测试不只跑一遍，而是真正穷尽关键路径后再宣称完成。

### US-017: Beacon 以故事闸门方式推进浏览器验证
作为 Release owner / QA，我希望 `qa run <feature>` 能按 user-story / AC / scenario 顺序推进，并在 scenario 粒度回写状态，以便 requirement closure 真正绑定浏览器执行事实。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Overlay Strategy | v1.1.9 明确以 overlay 方式增强现有主链，而非新造平行 lifecycle |
| AC-002 | Delivery Plane | 文档明确沿用 `workflow / implement / qa / review / gate / release / debug` 作为 delivery plane |
| AC-003 | Exhaustion State | debug 支持 failure_streak / escalation_level / required_next_action 一类语义 |
| AC-004 | Checkpoint Resume | resume 语义包含 tried approaches / excluded causes / next hypothesis / evidence gap |
| AC-005 | Completion Split | Beacon 明确区分 `implementation_done` 与 `evidence_done` |
| AC-006 | Delta QA | Beacon 定义 requirement / implementation / evidence 变化后的 targeted rerun 语义 |
| AC-007 | Trace Contract | Beacon 冻结 requirement → implementation → evidence 三层 trace contract |
| AC-008 | Artifact Updates | `artifact_updates` 被定义为正式 writeback obligation |
| AC-009 | Archive Feedback | `technical-implementation-*` 能作为 requirement rewrite / version research 输入 |
| AC-010 | Debug Feedback | `debug harvest` 能作为 issue / idea / baseline uplift 输入 |
| AC-011 | Evo Boundary | Beacon 定义 evo harness 输入与 keep/discard 纪律，但不承诺整仓自治 |
| AC-012 | Stability | v1.1.9 不破坏 v1.1.8 现有主命令面和发布线语义 |
| AC-013 | Design Scope | 当前 v1.1.9 先冻结设计物料，不误报已实现 |
| AC-014 | Skill Roles | root `SKILL.md` 与 `skills/beacon/SKILL.md` 明确主文档 / 辅文档角色 |
| AC-015 | Skill Structure | 两份 skill 文档遵循统一固定结构模板，不再自由漂移 |
| AC-016 | Operator Clarity | skill 文档能清晰说明发布线、产品定位、workflow 模型、推荐阅读、命令入口、导航规则与故障排查 |
| AC-017 | Port Anti-Drift | anti-drift requirement 明确覆盖 CLI / README / skill / runtime / installed copies / managed blocks |
| AC-018 | Baseline Canonicalization | baseline / fingerprint / drift contract 明确 canonical source 与 projection 边界 |
| AC-019 | QA Feature-aware Entry | `qa run <feature>` 被定义为正式目标语义，而非仅 scope-driven alias |
| AC-020 | Story-Sequential QA | QA requirement 明确支持按 user-story / AC 顺序依次验证 |
| AC-021 | Per-item Writeback | QA/verification 最终需要支持 AC / TEST item 粒度 writeback，而不只是整体通过汇总 |
| AC-022 | QA Evolve | `qa evolve` 进入正式 requirement scope，用于 delta-aware rerun |
| AC-023 | Scenario Expansion | browser-relevant AC 能被展开为正式 scenario families，而不是仅保留 AC→单一 TC |
| AC-024 | Scenario Families | 最小场景族至少覆盖 happy / negative / boundary / recovery / compatibility |
| AC-025 | Scenario Map | Beacon 为 feature 生成 `story-scenario-map` machine artifact |
| AC-026 | Story Exhaustive Mode | `qa run <feature> --mode story-exhaustive` 进入正式 requirement scope |
| AC-027 | Browser Dual Runner | 浏览器验证明确拆为 exploratory runner + deterministic evidence runner |
| AC-028 | Non-Agent-Only Truth | P0/P1 浏览器 claim 不能只靠 agent 探索通过，必须有 deterministic replay 或等价证据 |
| AC-029 | Browser Evidence Pack | browser scenario 具有标准 evidence pack（screenshot / url / dom / transcript / result 等） |
| AC-030 | Story Gate | QA 可按 user-story / AC / scenario 顺序推进，并支持 dependency-aware stop/block |
| AC-031 | Scenario Writeback | verification 最终支持 scenario-level status writeback，而不只停留在 AC / TEST 粒度 |
| AC-032 | Scenario Delta Rerun | `qa evolve` 能识别受影响 scenarios / browser flows，而不是只返回粗粒度 AC/TC |
| AC-033 | Exhaustiveness Control | QA 具备 missing_axes / failure_streak / escalation_level / required_next_action 等正式语义 |
| AC-034 | Release Exhaustiveness Gate | gate / release 能因场景族缺失、browser replay 缺失或 exhaustiveness 低于阈值而阻断放行 |
| AC-023 | Scenario Expansion | browser-relevant AC 能被展开为正式 scenario families，而不是仅保留 AC→单一 TC |
| AC-024 | Scenario Families | 最小场景族至少覆盖 happy / negative / boundary / recovery / compatibility |
| AC-025 | Scenario Map | Beacon 为 feature 生成 `story-scenario-map` machine artifact |
| AC-026 | Story Exhaustive Mode | `qa run <feature> --mode story-exhaustive` 进入正式 requirement scope |
| AC-027 | Browser Dual Runner | 浏览器验证明确拆为 exploratory runner + deterministic evidence runner |
| AC-028 | Non-Agent-Only Truth | P0/P1 浏览器 claim 不能只靠 agent 探索通过，必须有 deterministic replay 或等价证据 |
| AC-029 | Browser Evidence Pack | browser scenario 具有标准 evidence pack（screenshot / url / dom / transcript / result 等） |
| AC-030 | Story Gate | QA 可按 user-story / AC / scenario 顺序推进，并支持 dependency-aware stop/block |
| AC-031 | Scenario Writeback | verification 最终支持 scenario-level status writeback，而不只停留在 AC / TEST 粒度 |
| AC-032 | Scenario Delta Rerun | `qa evolve` 能识别受影响 scenarios / browser flows，而不是只返回粗粒度 AC/TC |
| AC-033 | Exhaustiveness Control | QA 具备 missing_axes / failure_streak / escalation_level / required_next_action 等正式语义 |
| AC-034 | Release Exhaustiveness Gate | gate / release 能因场景族缺失、browser replay 缺失或 exhaustiveness 低于阈值而阻断放行 |

## 风险与提醒

- 若只新增研究文档、不落成 requirement 物料，v1.1.9 仍难真正推进实现
- 若不明确 implementation_done / evidence_done，Beacon 仍可能出现假完成
- 若 checkpoint/resume 不保留排除路径与下一假设，debug 仍会重复试错
- 若 technical archive 不能反哺 requirement rewrite，学习层仍然断裂
- 若过早进入“自改整仓”，会在没有固定预算与 scorecard 时放大风险
- 若 root/package 两份 skill 文档继续漂移，用户会在入口层就走偏 stage 与命令
- 若 QA 继续停留在 scope/layer 心智，文档里的 feature-oriented QA 将持续与实现错位
- 若只把 agent-browser/browser-use 接进来，而不引入 deterministic replay，v1.1.9 会放大 browser QA 假通过风险
- 若 scenario expansion 不形成 machine artifact，`qa evolve` 很难升级为真正的 scenario-level targeted rerun
- 若穷尽度没有正式评分与 gate 契约，“story-exhaustive” 很容易退化为新的口号层
- 若仍停留在 AC→单个 TC 映射，Beacon 很难达到“按用户故事进行发散测试”的目标语义
- 若只把 agent-browser/browser-use 接进来，而不引入 deterministic replay，v1.1.9 会放大 browser QA 假通过风险
- 若 scenario expansion 不形成 machine artifact，`qa evolve` 很难升级为真正的 scenario-level targeted rerun
- 若穷尽度没有正式评分与 gate 契约，“story-exhaustive” 很容易退化为新的口号层
- 若仍停留在 AC→单个 TC 映射，Beacon 很难达到“按用户故事进行发散测试”的目标语义
