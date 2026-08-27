---
slug: beacon-v1614-feature-map
version: v1.6.14
schema: feature-map.v1
status: derived
---

# Feature Map: beacon-v1614-feature-map

> 单向投影：地图引用 truth 的 AC，绝不反向改写 truth（AC-004）。

## 入口（Entry Points）

| AC ID | type | path | how_to_enter |
|-------|------|------|--------------|
|  | file | .agents/skills/beacon-design/SKILL.md |  |
|  | file | .agents/skills/beacon-goal/SKILL.md |  |
|  | file | .agents/skills/beacon-implement/SKILL.md |  |
|  | file | .agents/skills/beacon-plan/SKILL.md |  |
|  | file | .agents/skills/beacon-qa/SKILL.md |  |
|  | file | .agents/skills/beacon-qa/scripts/eval-real-project/run_real_project_board_validation.sh |  |
|  | file | .agents/skills/beacon-release/SKILL.md |  |
|  | file | .agents/skills/beacon-truth/SKILL.md |  |
|  | file | .agents/skills/runtime-skill-admission-smoke/SKILL.md |  |
|  | file | .cursor/skills/beacon-design/SKILL.md |  |
|  | file | .cursor/skills/beacon-implement/SKILL.md |  |
|  | file | .cursor/skills/beacon-plan/SKILL.md |  |
|  | file | .cursor/skills/beacon-qa/SKILL.md |  |
|  | file | .cursor/skills/beacon-qa/scripts/eval-real-project/run_real_project_board_validation.sh |  |
|  | file | .cursor/skills/beacon-release/SKILL.md |  |
|  | file | .cursor/skills/beacon-truth/SKILL.md |  |
|  | file | .trae/skills/beacon-design/SKILL.md |  |
|  | file | .trae/skills/beacon-implement/SKILL.md |  |
|  | file | .trae/skills/beacon-plan/SKILL.md |  |
|  | file | .trae/skills/beacon-qa/SKILL.md |  |

## 验证命令（Verification Commands）

| AC ID | command | assertion | signal |
|-------|---------|-----------|--------|
| AC-001 | `rg -n "feature-map.md" docs/beacon/v1.6.14/features/beacon-v1614-feature-map/truth.md` | 骨架引用存在 + entry/verification 绑定 AC | exit_code_0 |
| AC-002 | `python3 tests/test_v1614_feature_map.py -k reproduce` | exit 0：模糊描述路由到 entry/verification | exit_code_0 |
| AC-003 | `python3 tests/test_v1614_feature_map.py -k self_verify` | exit 0：verification 命令可执行且信号可断言 | exit_code_0 |
| AC-004 | `python3 tests/test_v1614_feature_map.py -k one_way_projection` | exit 0：map 引用 truth 不反向改写；无命令面 | exit_code_0 |
| AC-004 | `rg -n "反向改写\` | 投影越权" docs/beacon/v1.6.14/features/beacon-v1614-feature-map/truth.md` | exit_code_0 |

## 复现路由（Reproduce Routes）

| symptom_hint | steps |
|--------------|-------|
| filled | open .agents/skills/beacon-design/SKILL.md; run feature entrypoint; observe signal |
