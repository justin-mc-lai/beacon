# PRD：Beacon v1.3.3 极简 HUD 场景与实现

**Feature**: `beacon-v1.3.3-minimal-hud-scenarios-and-implementation`  
**Version**: `v1.3.3`  
**Date**: `2026-04-16`  
**Status**: `planning line`

## 1. 问题

Beacon 已有 `team_hud` 与 Ralph 状态基础，但当前缺少统一、极简、场景化的 HUD 契约：

1. 人类面缺少稳定的“阶段 + 阻断 + 下一步”最小可视化。
2. HUD 信息边界不清晰，容易膨胀为运行细节堆积。
3. `help/status` 未形成统一 HUD 渲染规则，场景一致性不足。

## 2. 目标

在 `v1.3.3` 中新增一个并行 PRD，明确 HUD 的最小范围：

1. **极简展示**
   - 默认 1 行
   - 执行阶段 2 行
   - 告警/阻断 3 行
2. **场景驱动**
   - 固定 S1-S6 六个场景，不做泛化扩张
3. **主链对齐**
   - HUD 只服务 `6+3` 主链，不新增命令面
4. **实现可落地**
   - 给出最小数据契约、代码切片、测试切片

## 3. 用户故事

| As a | I want to | So that |
|------|-----------|---------|
| 人类操作者 | 3 秒内看到“现在在哪 + 下一步” | 减少主链决策成本 |
| 维护者 | HUD 有固定场景和行数预算 | 避免后续功能膨胀 |
| 调试者 | 阻断时看到单一推荐命令 | 快速恢复流程 |

## 4. 场景契约

| 场景 | 触发条件 | 输出 |
|------|---------|------|
| S1 主链空闲 | `stage != implement` 且无阻断 | 1 行 |
| S2 Single 执行 | `stage=implement` 且 `mode=single` | 2 行 |
| S3 Team 执行 | `stage=implement` 且 `mode=team` | 2 行 |
| S4 Ralph 执行 | `stage=implement` 且 `mode=ralph` | 2 行 |
| S5 Warn | `blocker.level=warn` | 3 行 |
| S6 Trip/Blocked | `blocker.level=blocked` 或 `circuit=trip` | 3 行 |

## 5. 功能需求

### FR-001 HUD 必须遵守 1-3 行预算

- 常态最多 2 行
- 告警/阻断才允许第 3 行

### FR-002 HUD 默认只展示最小决策信息

- 当前阶段
- 执行进度（single/team/ralph）
- 阻断原因（短文案）
- 下一步推荐命令（单一）

### FR-003 Ralph HUD 必须可观测闭环状态

最小字段：

- `phase`
- `round_count`
- `stop_state`
- `next_action`
- `current_blocker`
- `last_round_ref`
- `gate_release_status`
- `failure_streak`
- `no_delta_streak`

### FR-004 Team HUD 必须可观测执行摘要

最小字段：

- `team_state`
- `terminal_status`
- `review_gates`
- `fix_loops`
- `roles[*].latest_event`
- `roles[*].artifacts`

### FR-005 命令面不得扩张

- 不新增公开一级命令
- 挂接在 `help/status` 与现有 implement 输出

### FR-006 阻断推荐命令必须统一

compatibility 相关阻断时，推荐命令优先指向：

- `beacon doctor migrate-compat ...`

### FR-007 机器细节必须保留但不挤占人类面

- 人类 HUD 保持摘要
- JSON/artifacts 保持全量

## 6. 最小数据契约

```json
{
  "beacon_version": "v1.3.3",
  "docs_version": "v1.3.3",
  "feature": "feature-name",
  "stage": "prd|user-story|test-case|implement|qa|release",
  "execution": {
    "mode": "single|team|ralph",
    "elapsed": "1m30s",
    "progress": {"done": 0, "total": 0, "round": 0},
    "circuit_status": "ok|warn|trip"
  },
  "blocker": {"level": "none|warn|blocked", "reason": "", "recommended_command": ""},
  "next_action": ""
}
```

## 7. 实现切片

### Slice A：HUD 渲染器

- 新增 `beacon/utils/minimal_hud.py`
- 输出 `build_minimal_hud_lines(payload)`（1-3 行）

### Slice B：状态聚合

- 修改 `beacon/utils/help_support.py`
- 聚合最小 HUD payload

### Slice C：命令挂接

- 修改 `beacon/commands/help.py`
- 修改 `beacon/commands/status.py`
- 人类模式展示 HUD，`--json` 保持兼容

### Slice D：字段补齐

- 修改 `beacon/utils/ralph_runtime.py`
- 修改 `beacon/utils/subagent_runtime.py`
- 只补齐必要字段，不改主路径

## 8. 测试要求

新增：

- `tests/utils/test_minimal_hud.py`

最小用例：

1. S1 1 行
2. S2 2 行（single）
3. S3 2 行（team）
4. S4 2 行（ralph）
5. S5 3 行（warn）
6. S6 3 行（blocked/trip）
7. 行长与字段白名单约束

回归：

- `help/status` 现有 JSON 字段不回归
- Ralph/Team 现有状态读取不回归

## 9. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| HUD 信息膨胀 | 高 | 固定场景 + 行数预算 + 字段白名单 |
| 命令输出兼容性回归 | 中 | JSON 输出只增不删 |
| 阻断命令不一致 | 中 | 统一在 `help_support` 生成推荐命令 |

## 10. 成功标准

1. `help/status` 稳定覆盖 S1-S6 场景
2. HUD 维持 1-3 行预算
3. compatibility 阻断时推荐 doctor 迁移命令
4. 无新增公开一级命令
5. 场景测试与回归测试通过

---

**Created**: 2026-04-16  
**Version**: v1.3.3  
**Status**: Draft  
**Memory Context**: N/A
