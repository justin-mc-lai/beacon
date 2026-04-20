# Test Cases: beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor

## Overview

**Feature**: `beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor`  
**Version**: `v1.3.5`  
**Status**: `frozen-pending-implementation`  
**AC Matrix JSON**: `docs/beacon/v1.3.5/.machine/qa/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.ac-test-matrix.json`  
**QA9 Matrix JSON**: `docs/beacon/v1.3.5/.machine/qa/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.qa9-matrix.json`  
**Story Scenario Map JSON**: `docs/beacon/v1.3.5/.machine/qa/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.story-scenario-map.json`

## Scenario Test Set

### TC-001 (AC-001): Prototype 唯一正式模式为 wireframe

- Given：用户执行 `prototype plan/create/status/review/freeze`
- When：检查命令输出与产物 manifest
- Then：系统必须统一以 `wireframe` 作为唯一正式模式，并显式记录 `prototype_mode: "wireframe"`

### TC-002 (AC-002): HTML 高保真原型从 Beacon 正式边界移除

- Given：查看 `v1.3.5` 文档、命令叙事与输出要求
- When：搜索 prototype 模式与交付描述
- Then：不得再出现 HTML 高保真原型作为正式要求、兼容模式或默认输出

### TC-003 (AC-003): `prototype create` 输出完整 wireframe 标准包

- Given：某个 feature 已进入 prototype 阶段
- When：执行 `prototype create`
- Then：输出中至少包含 `wireframe-summary.md`、`wireframe-manifest.json`、`navigation-map.md`、`navigation-map.json`、`pages/*.md`、`freeze.json`、`prototype-review.json`

### TC-004 (AC-004): `wireframe-summary.md` 可以冻结页面汇总

- Given：wireframe 包已生成
- When：打开 `wireframe-summary.md`
- Then：必须可见页面 ID、页面名称、平台、优先级、页面职责、关联 PRD / user-story

### TC-005 (AC-005): `navigation-map` 可以冻结路由与跳转

- Given：wireframe 包已生成
- When：查看 `navigation-map.md/json`
- Then：必须能表达页面入口、跳转关系、返回路径、关键状态切换和禁止跳转

### TC-006 (AC-006): `pages/*.md` 可以支撑实现接力

- Given：wireframe 包已生成
- When：打开任一单页草图
- Then：必须包含页面职责、布局块、关键模块、用户动作、状态说明和相关物料链接

### TC-007 (AC-007): wireframe 与 requirement truth 对齐成立

- Given：feature 已有 `prd / user-story / test-case`
- When：检查 wireframe 包引用关系
- Then：wireframe 能映射到对应 PRD、用户故事和验收点，并作为正式 requirement artifact

### TC-008 (AC-008): review / freeze / status 能阻断不完整 wireframe 包

- Given：wireframe 包缺失关键文件或映射关系不完整
- When：执行 `prototype status`、`prototype review` 或 `prototype freeze`
- Then：系统必须给出阻断、降级或不完整状态，而不是误判为可冻结

### TC-009 (AC-009): Prototype 不再承担视觉终稿职责

- Given：某个项目仅进入 prototype 阶段
- When：检查该阶段产物与说明
- Then：产物语义应被限定为需求冻结用 wireframe，而不是高保真视觉稿、最终页面或前端实现

### TC-010 (AC-010): Wireframe 输出中文可读且便于审核

- Given：人类需要审核 prototype 产物
- When：阅读 `wireframe-summary.md` 与 `pages/*.md`
- Then：输出必须优先服务中文需求沟通与实现接力，而不是只有机器可读 JSON

### TC-011 (AC-011): 人类主链显式包含 prototype

- Given：查看 `docs/beacon/global-boundaries.md`、`skills/beacon/SKILL.md` 与 `docs/beacon/v1.3.5/*`
- When：核对人类阶段叙事
- Then：必须一致表达 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`

### TC-012 (AC-012): Host-visible skill 统一为 `beacon-prototype`

- Given：查看 `skills/beacon/` 对外 skill 包
- When：核对公共原型入口
- Then：必须存在 `skills/beacon/beacon-prototype/SKILL.md`，且对外原型阶段以 `beacon-prototype` 作为唯一稳定路由

### TC-013 (AC-013): `wireframe.py` 直接移除且不保留兼容壳层

- Given：检查 Beacon CLI 命令注册、命令目录与技能说明
- When：搜索 `wireframe.py`、`beacon wireframe`、`wireframe` 平行命令入口
- Then：仓库内不得保留 `beacon/commands/wireframe.py`、CLI 注册入口或兼容迁移壳层；旧入口必须被正式摘除

### TC-014 (AC-014): 文档与 skill 对 `prototype` 语义完全一致

- Given：查看 `docs/beacon/v1.3.5/*`、`docs/beacon/global-boundaries.md` 与 `skills/beacon/*.md`
- When：核对 `prototype` 的定义
- Then：都必须明确 `prototype = requirement-driven wireframe freeze orchestrator`，且不再把它解释为 HTML 高保真原型生成器

## Suggested Commands

- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main prototype status beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor --project /Users/apple/Developer/Personal/products/beacon --version v1.3.5 --json`
- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main prototype review beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor --project /Users/apple/Developer/Personal/products/beacon --version v1.3.5 --json`
- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main user-story list --project /Users/apple/Developer/Personal/products/beacon --version v1.3.5`
- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main test-case list --project /Users/apple/Developer/Personal/products/beacon --version v1.3.5`

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
| TC-012 | Pending | from AC-012 |
| TC-013 | Pending | from AC-013 |
| TC-014 | Pending | from AC-014 |
