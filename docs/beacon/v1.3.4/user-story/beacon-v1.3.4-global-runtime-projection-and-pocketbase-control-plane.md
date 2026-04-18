# User Story: beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane

## Story

**As a** 一人公司中的 CEO / 项目负责人 / Beacon 运行态治理者,  
**I want** Beacon 用 `Beacon Runtime Ledger` 管理机器内部多项目运行态，并通过 `Beacon 管理看板` 以生命周期优先的方式展示项目进度、交付状态、运行模式、恢复状态与治理信息,  
**So that** 我可以在不破坏 `docs/beacon` 与 `.beacon` 真相边界的前提下，先看清多项目推进，再下钻查看某个项目当前版本、并行 PRD、需求物料补齐情况、`single/team/ralph` 运行态、git/worktree 规范与恢复路径。

## Story Slices

### US-001: CEO 首页总览必须先看生命周期与交付

作为 CEO，我希望首页先看到项目名、当前版本、当前主 feature、生命周期阶段、总进度、交付状态、blocker、下一步，而不是先看到 worker 或调度细节。

### US-002: 项目详情必须能服务项目负责人接力

作为项目负责人，我希望进入项目详情后能看到版本线、主 PRD / 并行 PRD、需求物料补齐情况、implement / qa / release 状态，以及当前推荐 skill。

### US-003: Runtime 只作为实现阶段下钻信息

作为运行态治理者，我希望 `single / team / ralph` 只在运行态中心展示，不抢占生命周期主轴。

### US-004: Team 模式必须可见代理规模与角色状态

作为项目负责人，我希望当某个项目进入 `team` 模式时，能直接看见当前 agent 数、角色、状态和关联 artifact/session 引用，而不是只看到一个模糊“运行中”。

### US-005: Ralph 模式必须可见闭环控制字段

作为项目负责人，我希望当某个项目进入 `ralph` 模式时，能看到 `round_count`、`failure_streak`、`next_action`、`blocker`，以便判断是否仍在有效推进。

### US-006: Git / Worktree 必须成为正式治理对象

作为项目负责人，我希望看板明确表达当前 repo root、branch、dirty、worktree path、预期分支规则和规范状态，而不是只把这些信息埋在本地状态文件里。

### US-007: Host Session 只能展示有限引用

作为人类操作者，我希望 `Codex / Claude` session 只以 metadata / transcript ref / linked run 形式出现，不把宿主完整交互系统平铺到 Beacon 看板。

### US-008: SQLite / PocketBase 失效时项目仍可继续

作为 Beacon 使用者，我希望当 `Beacon Runtime Ledger` 或 PocketBase 不可用时，项目仍可依赖 `docs/beacon` 与 `.beacon` 继续推进，看板只显示 degraded / rebuild 信息，不误判项目本身丢失。

### US-009: `omc / omx` 不进入 Beacon 看板边界

作为产品负责人，我希望 `omc / omx` 与其他 Beacon 外兼容运行时不进入正式投影或默认展示，保证 Beacon 的产品边界不被冲垮。

### US-010: 子 skill 必须按生命周期推荐

作为操作者，我希望看板给出“当前建议下一步”和“当前建议 skill”，例如需求阶段推荐 `beacon-prd / beacon-user-story / beacon-test-case`，实现阶段推荐 `beacon-implement / beacon-qa / beacon-release`，阻断时推荐 `beacon-doctor`。

## Acceptance Criteria

- AC-001 首页生命周期优先：总览层默认只展示项目、版本、feature、生命周期阶段、总进度、交付状态、blocker、下一步；runtime 仅可压缩显示为 badge。
- AC-002 CEO 视图极简：首页不得默认暴露 tmux pane、worker transcript、raw debug event、宿主交互洪流。
- AC-003 项目详情可接力：详情页必须展示版本线、主 PRD / 并行 PRD、需求物料补齐情况、implement / qa / release 状态、推荐 skill / 下一步。
- AC-004 需求物料显式状态：系统必须对 `prd / user-story / test-case` 至少表达 `missing / draft / ready / frozen`。
- AC-005 Runtime 下钻分层：`single / team / ralph` 只在运行态详情层展开，且不作为生命周期主导航。
- AC-006 Team 运行态透明：当 runtime 为 `team` 时，必须可见 agent 数、role、status、role artifact 引用与 session 引用。
- AC-007 Ralph 闭环可观测：当 runtime 为 `ralph` 时，必须可见 `round_count / failure_streak / next_action / current_blocker`。
- AC-008 Git / worktree 治理可见：每个版本迭代 / feature 必须可见 repo root、branch、commit、dirty、worktree path、expected branch rule、spec status。
- AC-009 Session 边界受控：看板可以展示 `Codex / Claude` session metadata 与 transcript ref，但不得把宿主完整 session 系统并入 Beacon 真相层。
- AC-010 Projection / truth 边界明确：页面与文案必须明确 `docs/beacon + .beacon` 是 truth，`Beacon Runtime Ledger + PocketBase` 是 projection / control plane。
- AC-011 降级与重建成立：当 SQLite / PocketBase 缺失时，看板必须显示 degraded / rebuild 信息，并允许从本地 truth 重建最小可用状态。
- AC-012 Beacon 外运行时排除：`omc / omx` 与其他 Beacon 外兼容运行时不进入正式投影和默认看板展示。
- AC-013 生命周期推荐 skill：看板必须基于当前阶段给出推荐 skill，而不是暴露一组无上下文的平铺 skill 列表。
- AC-014 Prototype 参考包一致：原型参考包中的 `portfolio-overview / project-detail / runtime-center / recovery-diagnostics` 四页和关键状态必须与上述 AC 对齐，不得漂移。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 8 |
| Status | ready-for-planning |
| Version | v1.3.4 |
| Feature Slug | beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane |
| Runtime Truth | docs/beacon + .beacon |
| Projection Layer | Beacon Runtime Ledger + Beacon 管理看板 |

