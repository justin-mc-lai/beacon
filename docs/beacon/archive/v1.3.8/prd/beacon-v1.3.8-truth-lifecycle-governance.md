# PRD: Beacon v1.3.8 Truth Lifecycle Governance

**Feature**: `beacon-v1.3.8-truth-lifecycle-governance`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version brainstorm anchor:
  - `docs/brainstorms/2026-04-24-beacon-v1-3-8-truth-lifecycle-brainstorm.md`
- Research anchors:
  - `docs/beacon/archive/v1.3.8/research/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation-analysis.md`
  - `docs/beacon/archive/v1.3.8/research/beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace-analysis.md`
  - `docs/beacon/archive/v1.3.8/research/beacon-v1.3.8-prd-executable-diagram-truth-layer-analysis.md`
- Current runtime architecture anchor:
  - `docs/beacon/v1.3.7/execution/architecture-blueprint.md`

## 1. Problem

`v1.3.7` 已经把 Beacon 的真相收敛到更严格的 frozen truth 与 canonical implementation baseline 关系上，但系统仍然缺一条完整的 truth lifecycle 治理线。

当前缺口体现在三个时点：

1. **Truth admission**
   - 复杂业务 feature 在 freeze 前仍可能只是叙述型 PRD。
   - 没有 branch flow、state machine、decision priority 时，复杂语义仍会靠人工口头补齐。
2. **Truth execution**
   - 真实多服务项目已经形成 `team -> ralph` 的冻结后交付顺序。
   - 但 Beacon 还没有把这条顺序做成正式 execution contract。
   - 宿主提示词才是真实驱动面，但 `prompt -> command -> artifact` 没有进入 formal evidence。
3. **Truth retirement**
   - 历史版本需求、历史 feature truth、历史 technical archive 仍容易继续影响当前迭代。
   - Beacon 缺少正式 archive governance 来隔离“历史可追溯”和“当前仍生效”。

此外，Beacon 虽然已经存在 `beacon-real-project-validation` 路径，但它当前更接近：

- 真实项目上的最小 CLI 可用性验证
- `v1.3.4` 并板 / projection 专项验收

它还没有完全随 `v1.3.8` 的发布承诺升级为“当前版本真实项目验收面”，因此仍存在四个缺口：

1. `prototype`、`archive`、`gate check release` 还没有被正式纳入最新 human surface 验收基线。
2. 验收矩阵还没有从 `SUMMARY.md`、`execution/index.md`、`release/<version>.md`、`skills/beacon/SKILL.md` 派生版本级 overlay。
3. `v1.3.8` 新发布的 diagram truth、post-freeze host prompt trace / prompt-boundary closure、archive governance、canonical delivery baseline 收敛，还没有被逐条映射成真实项目验收项。
4. 单项目“最新版本 release proof”和多项目并板专项验收仍容易被混成同一条验证路径。

如果这三段不连起来，Beacon 仍会面临三类风险：

1. 新 truth 进入系统时结构不够强。
2. 冻结后的执行顺序与证据链不够正式。
3. 旧 truth 不会真正退出当前生效面。

## 2. Goals

### 2.1 Primary Goal

把 `v1.3.8` 定义成一条完整的 `truth lifecycle governance` 版本线：

```text
truth admission
-> truth execution
-> truth retirement
```

### 2.2 Expected Result

本线完成后，Beacon 应满足：

1. 复杂业务 feature 在 freeze 前可以进入“可执行真相面”，而不是停留在 narrative PRD。
2. 冻结后的真实交付顺序 `team -> ralph` 可以被正式表达，并被 `status` / HUD / memory 读取。
3. 宿主提示词到 Beacon 命令的映射可作为 formal execution evidence 留存。
4. 历史 feature truth 与历史版本需求可以被正式归档，不再继续污染当前 delivery truth。
5. LLM 在读取历史资料时，能够知道哪些是：
   - active truth
   - learnable archive
   - reference-only archive
6. `beacon-real-project-validation` 能把“当前版本真实项目验收”与“专项 board acceptance”区分开，并以当前版本 human surface + shipped features 作为主验收面。

## 3. Non-goals

本 PRD 不承担：

- 不新增新的公开一级主生命周期 stage
- 不允许 `team`、`ralph` 使用不同 requirement truth
- 不把 `beacon-brainstorm` 变成新的主链 stage
- 不物理删除历史 requirement 文档
- 不要求所有 feature 都强制绘制复杂状态图
- 不把 `beacon-real-project-validation` 升格成新的 Beacon primary stage
- 不要求所有版本都必须先通过多项目并板专项验收，才算当前版本真实项目验收完成

## 4. Core Product Semantics

### 4.1 Version Theme

`v1.3.8` 的版本主题不是单点命令增强，而是：

```text
Beacon Truth Lifecycle Governance
```

它由三条内聚的 feature line 组成：

1. `beacon-v1.3.8-prd-executable-diagram-truth-layer`
2. `beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace`
3. `beacon-v1.3.8-archive-governance-and-historical-requirement-isolation`

### 4.2 Truth Admission Contract

对复杂业务 feature，PRD 不能只承担“说明书”角色，还必须承担“实现约束真相面”角色。

最小要求：

- branch-flow
- state-machine
- decision-priority
- state axes where applicable

### 4.3 Truth Execution Contract

冻结后的真实交付应支持：

```text
freeze pass
-> implement team-plan
-> implement team-run
-> implement ralph
-> qa
-> release
```

并且需要额外写出：

- host prompt trace
- phase state
- actionable branch/service relocation guidance

### 4.4 Truth Retirement Contract

历史 truth 必须继续可追溯，但必须退出当前 active plane。

Beacon 至少要能区分：

- active truth
- superseded truth
- archived-learnable
- archived-reference-only

### 4.5 Real-Project Acceptance Contract

`v1.3.8` 发布后的真实项目验收，不能只证明 Beacon “能跑起来”，还必须证明 Beacon “当前版本声称 ship 的能力”能在真实项目上被读路径和公开 surface 证明。

最小验收模型应分三层：

1. **Base human-surface baseline**
   - 至少覆盖：
     - `help`
     - `status`
     - `doctor`
     - `prd`
     - `user-story`
     - `test-case`
     - `prototype`
     - `implement`
     - `qa`
     - `release`
     - `archive`
     - `gate check release`
2. **Version-specific acceptance overlay**
   - 必须从当前版本的：
     - `docs/beacon/<version>/SUMMARY.md`
     - `docs/beacon/<version>/execution/index.md`
     - `docs/beacon/<version>/release/<version>.md`
     - `skills/beacon/SKILL.md`
   - 派生“本版本到底承诺了什么真实项目验收项”
3. **Specialized acceptance overlay**
   - 只有在目标能力本身是 cross-project board / runtime projection / portfolio board 时，才进入多项目并板专项验收
   - 多项目并板专项验收不能替代当前版本单项目 release proof

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon 必须把 `v1.3.8` 定义成一条版本级 `truth lifecycle governance` 线，并清晰表达 admission、execution、retirement 三段关系。 |
| FR-002 | AC-002 | 对复杂业务 feature，PRD 必须支持 branch-flow、state-machine、decision-priority 等可执行图层，并允许显式建模多条 state axis。 |
| FR-003 | AC-003 | freeze readiness 或 brainstorm convergence 必须能判断某个 feature 是否需要 diagram truth layer 才能安全冻结。 |
| FR-004 | AC-004 | Beacon 必须支持冻结后 `team -> ralph` 的正式执行顺序表达，而不是继续依赖人工重复说明。 |
| FR-005 | AC-005 | Beacon 必须把 `host prompt -> mapped command -> produced artifact` 记录为结构化 execution evidence。 |
| FR-006 | AC-006 | `status` 或 HUD 必须能投影冻结后当前 phase，包括 freeze、team、ralph、next_action 和 stop_state。 |
| FR-007 | AC-007 | branch preflight 必须输出服务级 branch mismatch 与推荐安全迁移动作，而不只是 generic block message。 |
| FR-008 | AC-008 | Beacon 必须新增 archive governance，定义 active truth、superseded、archived-learnable、archived-reference-only 的最小状态模型。 |
| FR-009 | AC-009 | history/archive 状态必须被 `help`、`status`、`brainstorm`、`memory-friction-evolution`、`implement`、`gate` 等消费面读取，避免历史需求继续污染当前实现面。 |
| FR-010 | AC-010 | `beacon-real-project-validation` 必须把当前 Beacon human surface 真实项目验收基线扩展到 `prototype`、`archive` 与 `gate check release`，并保持默认读路径验证。 |
| FR-011 | AC-011 | `beacon-real-project-validation` 必须从当前版本 `SUMMARY / execution index / release note / beacon skill` 派生 version-specific acceptance overlay，而不是只依赖固定历史命令矩阵。 |
| FR-012 | AC-012 | 对 `v1.3.8`，真实项目验收 overlay 必须显式覆盖 diagram truth admission、post-freeze host prompt trace / prompt-boundary closure、archive governance surface，以及 canonical delivery baseline 与 gate / release 收敛。 |
| FR-013 | AC-013 | 单项目当前版本真实项目验收必须是默认 release proof；多项目 board acceptance 只能作为专项兼容验收路径，不能被误判为完整最新版本覆盖。 |

## 6. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | version-theme | `v1.3.8` requirement package 明确表达 `truth admission -> truth execution -> truth retirement` 的版本级治理主题。 |
| AC-002 | diagram-truth | 复杂业务 feature 的 PRD 可以正式承载 branch-flow、state-machine、decision-priority 和 state axis，不再只依赖叙述型文本。 |
| AC-003 | freeze-readiness | 在 freeze 前，系统能判断某个 feature 是否因缺少 diagram truth layer 而不适合继续冻结。 |
| AC-004 | execution-sequence | 冻结后的 `team -> ralph` 顺序可以被 Beacon 公开表达为正式 execution contract。 |
| AC-005 | prompt-trace | 宿主提示词到命令、产物的映射可被结构化记录，并进入 execution evidence。 |
| AC-006 | phase-projection | `status` / HUD 能明确显示当前处于 freeze、team、ralph 哪一阶段，以及 `stop_state` / `next_action`。 |
| AC-007 | branch-actionability | branch preflight 能指出具体服务、当前分支、目标分支、脏工作树风险与推荐操作，而不只是泛化阻断。 |
| AC-008 | archive-contract | Beacon 存在 machine-readable archive contract，能区分 active truth、superseded、archived-learnable、archived-reference-only。 |
| AC-009 | archive-consumption | 读取历史资料的主要消费面能够识别 archive 状态，避免历史需求继续进入当前实现与验证路径。 |
| AC-010 | human-surface-acceptance | `beacon-real-project-validation` 把 `prototype`、`archive`、`gate check release` 纳入当前版本真实项目验收基线，并默认保持只读。 |
| AC-011 | version-overlay | `beacon-real-project-validation` 能从当前版本 docs / release / skill 面派生 shipped-feature acceptance overlay。 |
| AC-012 | v138-feature-proof | `v1.3.8` 的 diagram truth、prompt trace / prompt-boundary、archive governance、canonical baseline / gate / release convergence 都存在明确真实项目验收映射。 |
| AC-013 | specialized-acceptance-boundary | 单项目当前版本真实项目验收与多项目 board acceptance 被清晰分层，后者不能替代前者。 |

## 7. Freeze Deliverables

- `docs/brainstorms/2026-04-24-beacon-v1-3-8-truth-lifecycle-brainstorm.md`
- `docs/beacon/archive/v1.3.8/research/README.md`
- `docs/beacon/archive/v1.3.8/research/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation-analysis.md`
- `docs/beacon/archive/v1.3.8/research/beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace-analysis.md`
- `docs/beacon/archive/v1.3.8/research/beacon-v1.3.8-prd-executable-diagram-truth-layer-analysis.md`
- `docs/beacon/archive/v1.3.8/SUMMARY.md`
- `docs/beacon/archive/v1.3.8/prd/beacon-v1.3.8-truth-lifecycle-governance.md`
- `docs/beacon/archive/v1.3.8/user-story/beacon-v1.3.8-truth-lifecycle-governance.md`
- `docs/beacon/archive/v1.3.8/qa/test-cases/beacon-v1.3.8-truth-lifecycle-governance.md`
- `docs/beacon/archive/v1.3.8/execution/real-project-validation-alignment.md`

## 8. Risks

- 如果 archive governance 先行，但 admission truth 仍弱，系统会归档一批低质量 requirement truth。
- 如果 `team -> ralph` 只做执行顺序，不做 prompt trace，memory 仍学不到真实宿主使用模式。
- 如果 diagram truth layer 只留在 PRD，不传导到 implement 与 QA，就会停留在文档增强层。
- 如果真实项目验收仍停留在旧版本命令矩阵，Beacon 会出现“版本已发布，但最新能力无法在真实项目上被证明”的 release 假闭环。

## 9. Release Guard

- 本 requirement line 的冻结前提是：
  - 无 unresolved requirement clarity findings
  - PRD / user-story / test-case 对 AC-001 到 AC-013 一一映射
  - freeze deliverables 全部存在
- 真实项目验收对齐必须明确区分：
  - 当前版本单项目 release proof
  - 多项目 board / projection 专项验收
- 本 line 的 release readiness 需要后续 feature-level implement / QA / release 收口，不在本 PRD 阶段直接宣告。
