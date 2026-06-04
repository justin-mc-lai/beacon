# User Story: Beacon v1.3.8 Truth Lifecycle Governance

**Feature**: `beacon-v1.3.8-truth-lifecycle-governance`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Story

作为 Beacon 的版本治理者与真实项目操作者，我希望 Beacon 不只是知道“当前谁是真相”，还知道：

- 真相应该如何进入系统
- 真相应该如何驱动冻结后的实现
- 历史真相应该如何退出当前生效面

这样我才能在复杂业务、多服务交付、以及长期迭代里，既保留追溯能力，又避免历史需求继续污染当前交付。

## Requirement Description

`v1.3.8` 需要围绕 `truth lifecycle governance` 收敛成一条完整的 requirement line：

1. **truth admission**
   - 对复杂业务 feature，PRD 需要升级成可执行真相面。
2. **truth execution**
   - 冻结后的 `team -> ralph` 顺序与宿主提示词驱动面需要进入 formal execution evidence。
3. **truth retirement**
   - 历史 truth 需要可归档、可追溯，但不能继续进入当前 active delivery plane。
4. **truth proof on real projects**
   - 当前版本真实项目验收必须证明 Beacon 的最新 human surface 与已发布特性，而不是只停留在旧版本专项验收模型。

## User Stories

### US-001: 复杂业务 feature 在 freeze 前应进入可执行真相面

作为需求冻结前的产品与工程协作者，我希望复杂业务 feature 的 PRD 能表达 branch flow、state machine、decision priority 和 state axes，这样多服务实现不会继续靠口头对齐。

### US-002: 冻结后的真实交付顺序应被产品化

作为在 Codex / Claude 中推进多服务交付的操作者，我希望 `team -> ralph` 不再只是人工共识，而是 Beacon 可表达、可追踪、可投影的正式 execution contract。

### US-003: 宿主提示词必须被正式留证

作为 Beacon 的演进维护者，我希望宿主提示词到 Beacon 命令与产物的映射被记录下来，这样 memory/friction 系统才能学习真实使用模式。

### US-004: 历史 truth 必须退出当前实现面，但仍可学习和追溯

作为长期维护 Beacon 版本线的治理者，我希望历史 requirement、历史 feature truth、历史 technical archive 可以被区分为 active、learnable archive 和 reference-only archive，避免旧线持续污染当前迭代。

### US-005: 当前版本真实项目验收必须跟随最新 Beacon surface 与 shipped features

作为在真实项目上验证 Beacon 发布质量的操作者，我希望 `beacon-real-project-validation` 默认先证明当前版本单项目 release proof，再按需进入专项 board acceptance，这样我能知道：

- 当前 human surface 是否完整可用
- 当前版本新 ship 的能力是否真能在真实项目上被证明
- 多项目并板专项验收是不是只是某类 feature 的附加路径，而不是默认替代物

## Acceptance Criteria

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

## Metadata

- version: `v1.3.8`
- feature: `Beacon v1.3.8 truth lifecycle governance`
- status: `draft`
