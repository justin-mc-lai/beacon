# Test Cases: beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane

## Overview

**Feature**: beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane  
**Test Type**: ALL  
**Version**: v1.3.4  
**Status**: Draft  
**Focus**: lifecycle-first board, multi-project runtime projection, PocketBase control plane, runtime drilldown, degradation and rebuild

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

---

## Suggested Commands

- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main prototype status beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane --project /Users/apple/Developer/Personal/products/beacon --version v1.3.4 --json`
- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main prototype review beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane --project /Users/apple/Developer/Personal/products/beacon --version v1.3.4 --json`
- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main prototype directory beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane --project /Users/apple/Developer/Personal/products/beacon --version v1.3.4 --json`

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

