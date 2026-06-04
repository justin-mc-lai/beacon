# Test Cases: beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane

## Overview

**Feature**: beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane  
**Test Type**: ALL  
**Version**: v1.3.4  
**Status**: Draft  
**Focus**: lifecycle-first board, multi-project runtime projection, real-project board acceptance, deterministic multi-write, debug tri-state, degradation and rebuild

---

## Scenario Test Set

### TC-001 (AC-001): 首页默认按生命周期展示

- Given：至少两个 Beacon 项目存在不同生命周期阶段
- When：打开 `Beacon 管理看板` 首页
- Then：默认可见项目、版本、feature、生命周期阶段、总进度、交付状态、blocker、下一步，runtime 仅为压缩 badge

### TC-002 (AC-002): CEO 视图不暴露机器洪流

- Given：首页处于 CEO 汇总视图
- When：检查首屏字段与卡片内容
- Then：不得默认出现 tmux pane、worker transcript、raw debug event、宿主会话洪流

### TC-003 (AC-003): 项目详情可支撑项目负责人接力

- Given：选中某个项目卡片进入详情页
- When：查看详情页结构
- Then：必须能看到版本线、主 PRD / 并行 PRD、需求物料补齐情况、implement / qa / release 状态、推荐 skill 与下一步

### TC-004 (AC-004): 需求物料状态显式

- Given：一个 feature 的 `prd / user-story / test-case` 状态分别处于不同阶段
- When：查看项目详情中的 requirement materials 面板
- Then：每类物料都能表达 `missing / draft / ready / frozen`

### TC-005 (AC-005): Runtime 仅在下钻层展开

- Given：首页与项目详情页都可访问 runtime 信息
- When：比较首页、详情页、运行态中心
- Then：首页和详情页只显示摘要，`single / team / ralph` 详细字段只在运行态中心出现

### TC-006 (AC-006): Team 模式显示 agent 数与角色状态

- Given：某个 feature 处于 `team` 模式
- When：查看运行态中心
- Then：可见 agent 数、worker role、status、artifact refs、session refs

### TC-007 (AC-007): Ralph 模式显示闭环控制字段

- Given：某个 feature 处于 `ralph` 模式
- When：查看运行态中心
- Then：可见 `round_count / failure_streak / next_action / current_blocker`

### TC-007A (AC-007A): 不同 implement lane 仍绑定同一份 requirement closure

- Given：同一 feature 分别通过 `single / team / ralph` 三种 implement lane 推进
- When：检查其 delivery summary、review-spec 与 gate 输入
- Then：三者都绑定同一份 PRD / user-story / test-case，且都使用同一套 promised-vs-shipped compare 与 downgrade rule

### TC-008 (AC-008): Git / Worktree 治理信息完整

- Given：某个项目包含单仓或多仓 workspace 绑定
- When：查看 git / worktree 治理卡片
- Then：repo root、branch、commit、dirty、worktree path、expected branch rule、spec status 全部可见

### TC-009 (AC-009): Host Session 只展示有限元数据

- Given：项目有 Beacon-observed `Codex / Claude` session
- When：查看 session / artifact refs 面板
- Then：仅展示 host runtime、session/thread id、linked run、transcript ref、status、started/ended，不展示宿主完整会话系统

### TC-010 (AC-010): Projection / truth 边界文案正确

- Given：查看首页、详情、诊断页
- When：检查关键信息说明和空态文案
- Then：必须明确 `docs/beacon + .beacon` 是 truth，SQLite / PocketBase 是 projection / control plane

### TC-011 (AC-011): SQLite / PocketBase 缺失时降级不阻断

- Given：SQLite 或 PocketBase 不可用
- When：打开看板并查看项目详情
- Then：系统显示 degraded / rebuild 提示，但不把“全局投影缺失”误判成“项目状态丢失”

### TC-012 (AC-011): 从本地 truth 重建最小状态

- Given：全局投影层为空或损坏，但 `docs/beacon` 与 `.beacon` 存在
- When：执行 rebuild / sync
- Then：至少可恢复 project registry、git scopes、feature lifecycle 摘要、health snapshot

### TC-013 (AC-012): `omc / omx` 不进入默认看板

- Given：同机存在 `omc / omx` 运行时痕迹
- When：打开首页、项目详情、运行态中心
- Then：这些对象不进入 Beacon 正式总览，不显示为 runtime mode 或项目项

### TC-014 (AC-013): 看板按生命周期推荐 skill

- Given：不同项目分别处于需求缺口、implement 中、qa 中、阻断状态
- When：查看看板推荐动作
- Then：分别推荐 `beacon-prd / beacon-user-story / beacon-test-case`、`beacon-implement`、`beacon-qa`、`beacon-doctor`

### TC-015 (AC-014): Prototype 参考包与需求一致

- Given：已生成并冻结的 prototype 参考包
- When：检查 `portfolio-overview / project-detail / runtime-center / recovery-diagnostics` 页面与关键状态
- Then：页面结构、状态命名、边界约束与主 AC 一致，不得出现首页暴露 runtime 洪流、遗漏项目详情面板或把 `omc / omx` 带入默认导航

### TC-016 (AC-015): 四个真实项目都能成功并板

- Given：机器上存在 `rolo / slow_uni_bmtop / shopxo_canada / beacon` 四个真实项目
- When：执行项目发现、投影和看板刷新
- Then：四个项目都必须被注册并显示在 `Beacon 管理看板`

### TC-017 (AC-016): `rolo` 以 workspace 语义显示正确

- Given：`/Users/apple/Developer/Company/rolo` 含 root `.beacon`、多 child repo 与最新 debug runtime friction
- When：查看首页卡片与详情页
- Then：必须展示为 `multi_repo_workspace`，debug 状态为 `runtime_feed_only`，且不能退化为单服务单仓判定

### TC-018 (AC-016): `slow_uni_bmtop` 以单仓 + materialized_issue 显示正确

- Given：`/Users/apple/Developer/Personal/products/slow_uni_bmtop` 存在 `debug/index.json` 与 `debug/issues/beacon-core--runtime_feedback.json`
- When：查看首页卡片与详情页
- Then：必须展示为 `single_repo`，debug 状态为 `materialized_issue`

### TC-019 (AC-016): `shopxo_canada` 无 debug feed 但仍保留项目态

- Given：`/Users/apple/Developer/Personal/products/shopxo_canada` 存在 `.beacon` 运行态与 team/handoff 证据，但无 `debug/index.json`
- When：查看首页卡片与详情页
- Then：必须展示 `no_debug_feed`，但仍显示项目推进、runtime 摘要与下一步

### TC-020 (AC-016, AC-022): `beacon` 源码项目自并板正确

- Given：`/Users/apple/Developer/Personal/products/beacon` 本身处于 `v1.3.4` 主线
- When：查看首页卡片与详情页
- Then：必须按普通受管项目显示 `v1.3.4` 自迭代状态，不依赖特殊硬编码旁路

### TC-021 (AC-017): CEO 首页一眼分辨四项目差异

- Given：四项目同时出现在首页
- When：从 CEO 视图进行巡检
- Then：必须一眼分辨 workspace 项目、单仓项目、无 debug feed 项目和 Beacon 自演进项目，不得出现四张同质卡片

### TC-022 (AC-018): 详情页解释性成立

- Given：进入四个真实项目中的任一详情页
- When：查看 project_kind、lifecycle、debug state、recommended next step 说明
- Then：页面必须能解释这些字段为何成立，以及主要来源来自哪类 truth

### TC-023 (AC-019): Deterministic projection envelope 重复执行一致

- Given：固定同一份 `docs/beacon + .beacon + git/worktree` snapshot
- When：重复执行 projection 两次以上
- Then：生成的 `projection envelope`、`source_hash`、`projection_seq` 一致，SQLite / PocketBase 看到的输入版本一致

### TC-024 (AC-020): Branch / Worktree 冲突只能进入 partial / conflicted

- Given：用户显式 branch、git worktree 实证与 heuristic 推断存在冲突
- When：执行 preflight 与投影写入
- Then：系统必须 `reject / partial / conflicted`，并提供 doctor 提示，不得静默覆盖

### TC-025 (AC-021): Debug 三态被正式建模

- Given：真实项目分别对应 `materialized_issue / runtime_feed_only / no_debug_feed`
- When：查看看板、详情页与诊断页
- Then：三态必须有稳定命名、展示与治理语义，不得混淆成“有 issue / 无 issue”二元状态

### TC-026 (AC-023): 断库后可重建四项目最小并板状态

- Given：SQLite / PocketBase 缺失，但四项目的 `docs/beacon`、`.beacon` 与 git/worktree 仍存在
- When：执行重建
- Then：至少恢复 project registry、project_kind、lifecycle 摘要、debug 三态、推荐下一步

### TC-027 (AC-024): 真实项目验收留痕

- Given：完成一次四项目并板验收
- When：检查验证输出
- Then：必须存在机器可读或文档化验收记录，可回溯项目路径、时间、结果与阻塞项

---

## Suggested Commands

- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main prototype status beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane --project /Users/apple/Developer/Personal/products/beacon --version v1.3.4 --json`
- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main prototype review beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane --project /Users/apple/Developer/Personal/products/beacon --version v1.3.4 --json`
- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main prototype directory beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane --project /Users/apple/Developer/Personal/products/beacon --version v1.3.4 --json`
- `python3 -m beacon.main status --project /Users/apple/Developer/Company/rolo --json`
- `python3 -m beacon.main status --project /Users/apple/Developer/Personal/products/slow_uni_bmtop --json`
- `python3 -m beacon.main status --project /Users/apple/Developer/Personal/products/shopxo_canada --json`
- `python3 -m beacon.main status --project /Users/apple/Developer/Personal/products/beacon --json`

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 |
| TC-004 | Pending | from AC-004 |
| TC-005 | Pending | from AC-005 |
| TC-006 | Pending | from AC-006 |
| TC-007 | Pending | from AC-007 |
| TC-008 | Pending | from AC-008 |
| TC-009 | Pending | from AC-009 |
| TC-010 | Pending | from AC-010 |
| TC-011 | Pending | from AC-011 |
| TC-012 | Pending | from AC-011 |
| TC-013 | Pending | from AC-012 |
| TC-014 | Pending | from AC-013 |
| TC-015 | Pending | from AC-014 |
| TC-016 | Pending | from AC-015 |
| TC-017 | Pending | from AC-016 |
| TC-018 | Pending | from AC-016 |
| TC-019 | Pending | from AC-016 |
| TC-020 | Pending | from AC-016, AC-022 |
| TC-021 | Pending | from AC-017 |
| TC-022 | Pending | from AC-018 |
| TC-023 | Pending | from AC-019 |
| TC-024 | Pending | from AC-020 |
| TC-025 | Pending | from AC-021 |
| TC-026 | Pending | from AC-023 |
| TC-027 | Pending | from AC-024 |
