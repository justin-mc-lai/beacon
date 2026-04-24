# Test Cases: beacon-v1.3.6-internal-semantic-layer-and-default-taste-skill-bridge

## Overview

**Feature**: `beacon-v1.3.6-internal-semantic-layer-and-default-taste-skill-bridge`  
**Version**: `v1.3.6`  
**Status**: `frozen-pending-implementation`  
**Brainstorm Source**: `docs/brainstorms/2026-04-22-beacon-official-product-language-contract-for-prototype-and-implement-brainstorm.md`

## Scenario Test Set

### TC-001 (AC-001): `semantic layer` 被定义为 Beacon 内建能力

- Given：Beacon 已进入 requirement compile 与 `prototype / implement` 生命周期设计
- When：检查并行 PRD、user story、execution 分析与实现边界
- Then：`semantic layer` 被定义为 Beacon 内建能力，而不是外部 skill 或前端阶段的临时补丁

### TC-002 (AC-002): `prototype` 存在 semantic preflight 边界

- Given：同一 feature 已有 `prd / user-story / test-case`
- When：检查 `prototype` 的目标语义与设计方案
- Then：在 wireframe freeze 前，必须先存在一层官方语义预生成与消费边界

### TC-003 (AC-003, AC-004): 默认外部设计 bridge skill 被明确冻结

- Given：Beacon 需要桥接外部 design skill
- When：检查并行 PRD / user story / capability boundary 结论
- Then：官方默认 bridge 明确为 `https://github.com/Leonxlnx/taste-skill` 的 `taste-skill`

### TC-004 (AC-005): 外部 design skill 输出必须经过 canonical writeback

- Given：`prototype` 或 `implement` 内部调用外部 design skill
- When：检查产物收口方式
- Then：skill 输出必须先归一化为 Beacon evidence / canonical writeback，不能直接成为 truth source

### TC-005 (AC-006): `qa / release` 把 semantic/design consistency 作为正式 gate

- Given：某 feature 已完成 prototype、implement 与 design augmentation
- When：进入 `qa` 或 `release`
- Then：系统能够检查语义层、原型表达、实现表达与交付叙事是否一致

### TC-006 (AC-007): CLI 顶层 help 主流程对齐当前 `7+3` 全局边界

- Given：运行 `beacon --help`
- When：检查顶层主流程文案
- Then：主链显示为 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`，不再把旧 `think / gate` 叙事混入主线

### TC-007 (AC-008): `project_skills.py` 接受 canonical stage vocabulary

- Given：project skill profile 使用 `prototype / implement / qa / release` stage
- When：执行 registry list、orchestration validation 或 stage filter
- Then：系统按 canonical stage 工作，不要求继续使用 `implementation / verify / review / delivery`

### TC-008 (AC-008): legacy aliases 继续兼容

- Given：历史 profile 仍使用 `implementation / verify / review / delivery`
- When：执行 registry list、orchestration validation 或 stage filter
- Then：系统仍能成功解析并映射到 canonical stage，而不是直接报错

## Suggested Commands

- `python3 -m pytest tests/test_v117_project_skill_orchestration.py -q`
- `python3 -m pytest tests/test_v112_version_truth_profile_boundary_governance.py -q`

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 / AC-004 |
| TC-004 | Pending | from AC-005 |
| TC-005 | Pending | from AC-006 |
| TC-006 | Pending | from AC-007 |
| TC-007 | Pending | from AC-008 |
| TC-008 | Pending | backward compatibility |
