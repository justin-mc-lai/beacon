# v2 Skill 是否已是 loom-* 调用方式？— 审计结论

**日期**：2026-07-18  
**合同**：`loom-brand-surface` UD-LOOM-007 / AC-LOOM-BR-004

## 结论（短）

| 问题 | 答案 |
|------|------|
| v2 **所有** skill 是否都叫 `loom-*`？ | **否** |
| 是否符合冻结合同？ | **是（Phase-1 设计）** |
| 公共入口是否 loom？ | **是**：`$loom-goal` / `loom goal` |
| 子 skill 是否 loom 镜像？ | **否**：Phase-1 **共享** `skills/beacon/*` |

## 现状盘点

### Loom 轨（已存在）

| 路径 | 角色 |
|------|------|
| `skills/loom/SKILL.md` | host 路由 |
| `skills/loom/loom-goal/SKILL.md` | **唯一公共入口** |
| `skills/loom/examples/goal-one-shot-30s.md` | 30s 用法 |
| `loom` Python package + `loom` CLI | 双装 CLI |

### 缺失（相对命名矩阵，非 Phase-1 必须）

| 期望名 | 状态 |
|--------|------|
| `$loom-loop-goal` | **未实现 skill 目录**（truth 写 support only；Phase-1 可路由到 `$beacon-loop-goal`） |
| `loom-gen-*` / `loom-eval-*` / `loom-pln-*` | **未 fork** — UD-LOOM-007 Phase-1 明确共享 `skills/beacon/*` |
| `loom-gov-*` | **不应**成为 v2 一等 public skill（AC-125 denylist） |

### Beacon 轨（生产，完整 33+ skill 树）

仍全部在 `skills/beacon/*`：`beacon-goal`, `beacon-loop-goal`, `beacon-gen-*`, `beacon-eval-*`, `beacon-pln-*`, `beacon-gov-*` …

## 合同对齐

- **UD-LOOM-007**：Sub-skills Phase-1 **共享** `skills/beacon/*` 内容路由；Phase-2 **可选** `loom-*` 镜像  
- **UD-LOOM-003/006**：公共入口唯一 = `$loom-goal`；loop = support  
- **AC-125 / six harness**：v2 一等能力是 loop/truth/design/implement/qa-evidence/release，**不是** 33 个 loom 镜像 skill  
- **禁止**：第三公共入口与 `loom-goal` 并列主编排（I-LOOM-BR-002）

## 调用方式（正确 Phase-1）

```text
用户 / host
  └─ $loom-goal  或  loom goal run ...
        └─ 渐进加载 skills/beacon/*（plan/truth/implement/qa/release）
        └─ 不要求 $loom-gen-implement 等存在
```

```text
错误期望（当前合同不要求）
  $loom-gen-truth / $loom-eval-qa / ... 全量 loom-* 镜像
```

## Phase-2（可选，需单独 change）

1. 增加 `skills/loom/loom-loop-goal`（support-only，转发 beacon-loop-goal）  
2. 可选镜像高流量子 skill 为 `loom-*` 别名（内容仍单源）  
3. **不要**把 gov/doctor/router 升为 loom 公共 skill  

## 机器可读检查

见 `tests/test_v200_loom_skill_surface.py`。
