# Test Cases: beacon-v1.3.6-visual-management-console-and-material-viewer

## Overview

**Feature**: `beacon-v1.3.6-visual-management-console-and-material-viewer`  
**Version**: `v1.3.6`  
**Status**: `ready-for-implementation`  
**Upstream Freeze**: `docs/beacon/v1.3.5/prd/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor.md`

## Scenario Test Set

### TC-001 (AC-001, AC-002): 首页默认先回答经营判断

- Given：Beacon 管理端已发现多个受管项目
- When：打开首页首屏
- Then：首屏先展示项目数、阻塞数、活跃运行态数、重点介入区、项目清单、当前交付与下一步，不默认展示 runtime 洪流

### TC-002 (AC-002): CEO 视图不暴露机器内部噪音

- Given：首页处于 CEO / 经营总览视图
- When：检查首屏字段与默认卡片内容
- Then：不得默认出现 tmux pane、raw event、完整 transcript、宿主交互洪流

### TC-003 (AC-003): 总览页可以密集扫描多项目状态

- Given：至少存在 `rolo / slow_uni_bmtop / shopxo_canada / beacon` 四个项目
- When：进入管理总览页
- Then：必须可稳定扫描项目名、项目类型、版本、主 feature、阶段、总进度、健康态、debug 态、下一步与推荐 skill

### TC-004 (AC-004, AC-005): 项目详情页可接力并表达需求闭环

- Given：从总览页进入任一项目详情
- When：查看详情页主体结构
- Then：必须看到版本线、主 PRD、并行 PRD、需求物料状态、当前阶段、最近交付摘要与推荐动作，且 `prd / user-story / test-case` 状态明确

### TC-005 (AC-006, AC-007): Markdown 物料查看器只读且按版本组织

- Given：项目已有 `docs/beacon/<version>/` 物料
- When：在管理端打开文档查看器
- Then：可以按 `version -> document type -> feature` 浏览并查看 Markdown 内容，但不能在线编辑，且保留来源路径

### TC-006 (AC-008): Runtime 只在运行中心下钻

- Given：首页、项目详情页与运行中心页都可访问
- When：比较三层信息密度
- Then：首页和项目详情只展示 runtime 摘要，`single / team / ralph` 详细字段只在运行中心展开

### TC-007 (AC-009, AC-010, AC-011): Team / Ralph 与 Session 元数据展示受控

- Given：某项目分别处于 `team` 或 `ralph` 运行态，并带有关联 host session
- When：查看运行中心
- Then：`team` 显示 agent 数、role、status、linked run、artifact ref、session metadata；`ralph` 显示 `round_count / failure_streak / next_action / blocker / recent_result`；宿主完整会话系统不被并入

### TC-008 (AC-012): 恢复诊断页能解释 degraded / rebuild

- Given：SQLite 或 PocketBase 不可用，但本地 `docs/beacon` 与 `.beacon` 仍在
- When：查看恢复诊断页
- Then：页面必须明确 truth 仍来自 `docs/beacon` 与 `.beacon`，并展示 degraded / rebuild / doctor 提示

### TC-009 (AC-013): Beacon 外系统不进入默认管理边界

- Given：机器上存在 `omc / omx` 等 Beacon 外系统痕迹
- When：打开管理端总览、详情与运行中心
- Then：这些对象不进入默认项目注册表、默认 runtime 视图与默认导航

### TC-010 (AC-014): 四个真实项目都能被正确解释

- Given：`rolo / slow_uni_bmtop / shopxo_canada / beacon` 四个真实项目都进入同一管理看板
- When：查看首页、详情和推荐动作
- Then：必须都能解释其 `project_kind / lifecycle / debug state / next step`

### TC-011 (AC-015): 正式页面能回链 `v1.3.5` wireframe freeze

- Given：某个正式页面已进入实现验收
- When：检查其需求来源
- Then：该页面必须能回链到 `v1.3.5` 对应的 wireframe artifact，而不是回退到 HTML 高保真原型

### TC-012 (AC-016): 屏蔽机器细节后仍能支持人类决策

- Given：管理端以生命周期优先展示
- When：只阅读首页与项目详情的默认层
- Then：人类仍能判断项目当前阶段、交付内容、blocker、下一步与是否需要介入

### TC-013 (AC-017): `v1.3.4` 看板主轴在 `v1.3.6` 中被保留并扩展

- Given：`v1.3.6` 草图原型基于 `v1.3.4` Beacon 管理看板整理
- When：检查首页、管理总览、项目详情、运行中心、恢复诊断、物料查看器与文档详情之间的导航关系
- Then：必须保留 `home -> management-overview -> project-detail -> runtime-center / recovery-diagnostics` 主链路，并把 `project-detail -> material-viewer -> material-document-detail` 只读文档流正确接入

## Suggested Commands

- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main user-story list --project /Users/apple/Developer/Personal/products/beacon --version v1.3.6`
- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main test-case list --project /Users/apple/Developer/Personal/products/beacon --version v1.3.6`

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001, AC-002 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 |
| TC-004 | Pending | from AC-004, AC-005 |
| TC-005 | Pending | from AC-006, AC-007 |
| TC-006 | Pending | from AC-008 |
| TC-007 | Pending | from AC-009, AC-010, AC-011 |
| TC-008 | Pending | from AC-012 |
| TC-009 | Pending | from AC-013 |
| TC-010 | Pending | from AC-014 |
| TC-011 | Pending | from AC-015 |
| TC-012 | Pending | from AC-016 |
| TC-013 | Pending | from AC-017 |
