# Beacon v1.3.8 Real-Project Validation Alignment

- feature: `beacon-v1.3.8-truth-lifecycle-governance`
- version: `v1.3.8`
- purpose: `把 beacon-real-project-validation 对齐到当前版本真实项目验收面`
- status: `frozen-change-alignment`

## 0. Alignment Intent

`beacon-real-project-validation` 不能只证明 Beacon 在真实项目上“命令能跑”，还必须证明 Beacon 在 `v1.3.8` 里正式发布的能力，能够通过真实项目的公开人类 surface 被验证。

本对齐清单收敛三条原则：

1. 当前版本单项目 release proof 是默认验收路径。
2. 当前版本 shipped features 必须有 version-specific acceptance overlay。
3. 多项目 board acceptance 只保留为专项兼容验收，不替代当前版本默认真实项目验收。

## 1. Default Acceptance Layers

### 1.1 Base Human-Surface Baseline

真实项目只读验收的默认基线至少包含：

- `beacon help --project-root ROOT --version VERSION --feature FEATURE --json`
- `beacon doctor --json --project-root ROOT`
- `beacon status show-status --project-root ROOT --version VERSION --feature FEATURE --board`
- `beacon prd list -p ROOT -v VERSION`
- `beacon user-story list -p ROOT -v VERSION`
- `beacon test-case list -p ROOT -v VERSION`
- `beacon test-case gate FEATURE -p ROOT -v VERSION`
- `beacon prototype list -p ROOT -v VERSION`
- `beacon prototype status FEATURE -p ROOT -v VERSION --json`
- `beacon implement status FEATURE -p ROOT -v VERSION --json`
- `beacon qa status -p ROOT --json`
- `beacon qa evolve FEATURE -p ROOT -v VERSION --no-write-matrix --json`
- `beacon release check VERSION -p ROOT`
- `beacon release scorecard VERSION -p ROOT --json`
- `beacon archive status -p ROOT -v VERSION --feature FEATURE --json`
- `beacon archive explain -p ROOT -v VERSION --json`
- `beacon archive plan -p ROOT -v VERSION --feature FEATURE --json`
- `beacon gate check prototype --project-root ROOT --version VERSION --json`
- `beacon gate check release --project-root ROOT --version VERSION --json`

规则：

- 默认保持 read-only
- `blocked` / `warn` / `release_ready=false` 先视为项目状态结果，不直接视为 Beacon defect
- 只有崩溃、错版本、错 run、未文档化参数依赖、只读命令改写 tracked files，才进入 CLI defect 分类

### 1.2 Version-Specific Acceptance Overlay

当前版本的真实项目验收项，必须从以下材料单向投影：

- `docs/beacon/<version>/SUMMARY.md`
- `docs/beacon/<version>/execution/index.md`
- `docs/beacon/<version>/release/<version>.md`
- `skills/beacon/SKILL.md`

不允许只沿用旧版本固定 matrix，然后把它误当作“最新版本已覆盖”。

### 1.3 Specialized Acceptance Overlay

只有目标能力本身是：

- cross-project board
- runtime projection
- portfolio / homepage projection

时，才进入多项目 board acceptance。

这条路径当前仍可复用 `v1.3.4` capture script / record template，但它只属于专项覆盖，不属于 `v1.3.8` 默认 release proof。

## 2. v1.3.8 Feature Overlay

### 2.1 Diagram Truth Admission

真实项目验收需要补证：

- 目标 feature 的 PRD 是否存在 branch-flow / state-machine / decision-priority / state-axis truth
- `prototype` / `gate prototype` 是否还能感知 requirement-driven freeze readiness
- 若目标 feature 不属于复杂状态型 feature，应明确返回 `not_applicable`，而不是伪造通过

### 2.2 Post-Freeze Prompt Trace And Prompt Boundary

真实项目验收需要补证：

- `implement run --mode team --dry-run --json`
- `implement run --mode ralph --dry-run --json`
- `implement ralph-status FEATURE --json`
- `doctor verify-subagent-runtime --host-runtime codex|claude --json`
- `doctor verify-subagent-delegation FEATURE --version VERSION --json`
- `release scorecard`
- `gate check release`
- `release check`

验收判断必须能说明：

- host prompt trace 是否被 formalized
- prompt-boundary verdict 是否进入 gate / release
- `team -> ralph` 顺序是否仍被公开 surface 正确解释

### 2.3 Archive Governance

真实项目验收需要补证：

- `archive status`
- `archive explain`
- `archive plan`

并判断：

- archive 是不是 support command，而不是新 lifecycle stage
- active truth 与 archived truth 是否被清晰隔离
- `help / status / implement / gate / brainstorm / memory-friction-evolution` 的读取边界是否一致

### 2.4 Canonical Delivery Baseline Convergence

真实项目验收需要补证：

- implement / qa / release 公开 surface 是否仍围绕冻结 requirement truth
- canonical delivery baseline 是否仍是 implementation plan、deterministic implementation contract、git workflow contract 的单向投影源
- gate 与 release 是否消费同一 prompt-boundary / baseline / change-doc closure 结论

## 3. Classification Rule

### 3.1 Project-State Blocker

以下情况默认归类为项目状态问题：

- 命令退出正常，且输出结构化、版本感知
- 当前 feature 尚未 release-ready
- 当前 version line 仍缺 change-doc / package closure
- browser / session / runner prerequisite 缺失
- archive / prototype / gate 返回缺证据或未准备好

### 3.2 Beacon Defect

以下情况才归类为 Beacon defect：

- 命令 crash
- 忽略显式 version
- 选错 feature / run
- 需要未文档化参数才能工作
- 读路径命令修改 tracked docs / code
- `help / status / release scorecard / gate` 和 authoritative feature scorecard 明显矛盾
- 版本 overlay 没有覆盖当前版本 release note 已明确 ship 的能力

## 4. Board-Acceptance Boundary

`v1.3.4` 多项目 board acceptance 仍保留，但应被明确标注为：

- specialized path
- compatibility acceptance
- not sufficient for latest release proof on its own

因此，不允许再出现以下混淆：

- 用 `v1.3.4` board capture 结果替代 `v1.3.8` 当前版本单项目验收
- 只验证 portfolio board，就宣称 `prototype / archive / gate / prompt-boundary` 已覆盖

## 5. Expected Deliverable Update

对 `beacon-real-project-validation` 的后续实现对齐，至少需要更新：

- `skills/beacon/beacon-real-project-validation/SKILL.md`
- `skills/beacon/beacon-real-project-validation/references/command-matrix.md`
- `skills/beacon/beacon-real-project-validation/references/board-acceptance-record-template.md`
- `skills/beacon/beacon-real-project-validation/scripts/run_real_project_board_validation.sh`（仅限专项 board acceptance）

默认目标不是把 board 脚本扩张成全部版本通用入口，而是先把：

`current-version real-project proof`

和

`specialized board acceptance`

分成两个清晰层次。
