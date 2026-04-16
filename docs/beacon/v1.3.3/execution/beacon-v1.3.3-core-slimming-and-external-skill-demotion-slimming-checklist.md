# Beacon v1.3.3 瘦身改造清单

**Feature**: `beacon-v1.3.3-core-slimming-and-external-skill-demotion`  
**Version**: `v1.3.3`  
**Type**: `execution checklist`

## 目标

把 Beacon 收敛成：

- core: `6+3 + host-native internal lanes`
- compatibility: external skill / runner / orchestration

## 分阶段

### Phase 1: 叙事收口

- 更新 README 主路径，删除默认 `skill/profile/orchestrate` 教学。
- 更新 help/status 文案，把 external plane 标成 compatibility。
- 更新 host skill 文案，继续强调 `beacon-prd` 到 `beacon-release` 的最小面。

### Phase 2: 主路径去隐式依赖

- 改 `qa`，默认不自动执行 project orchestration。
- 增加显式开关或显式 profile mode，只有在用户选择时才跑 external orchestration。
- 保持阻断信息清晰，给出推荐下一步。

### Phase 3: 执行面分层

- 把 external adapters 从 core runner narrative 中拆出。
- 调整 `skill detect/list/registry` 输出，区分：
  - builtin native
  - optional compatibility
- 给 `ralph-bridge` 标记 deprecated 或迁到 compatibility。

### Phase 4: 测试收口

- 拆分 core tests 和 compatibility tests。
- 把 `gstack/omx/omc` 相关断言迁到 compatibility tests。
- 保留最小 smoke coverage，确保 legacy path 仍可选工作。

### Phase 5: contract 解耦

- 保留 project contract / evidence gate。
- 把 contract evaluation 与 external orchestration execution 解耦。
- 确保真实项目仍能在不启用 external plane 时运行 core QA/implement。

## 文件清单

### 优先改

- `README.md`
- `beacon/commands/qa.py`
- `beacon/utils/project_skills.py`
- `beacon/commands/skill.py`
- `beacon/commands/ralph_bridge.py`
- `beacon/utils/help_support.py`

### 需要一起更新

- `beacon/command_catalog.py`
- `beacon/cli_factory.py`
- `skills/beacon/SKILL.md`
- `skills/beacon/using-beacon/SKILL.md`
- `tests/test_v114_implement_command.py`
- `tests/test_v114_skill_command.py`

## 判定标准

- 新用户不看 compatibility 文档也能完整使用 Beacon。
- `qa run` 在默认模式下不会隐式执行外部 command。
- `implement list-runners` 不再把 external adapter 表述成正式核心能力。
- 文档、help、tests 对 core/compatibility 的分层一致。
