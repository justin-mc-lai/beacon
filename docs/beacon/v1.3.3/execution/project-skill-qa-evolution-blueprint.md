# Beacon v1.3.3 Project Skill / QA Evolution Blueprint

## Goal

`v1.3.3` 的目标是把 Beacon 收回到轻量核心，同时保留外部能力的兼容平面：

```text
human minimal surface
→ host-native implement / qa
→ compatibility plane (external skills/adapters, explicit opt-in)
```

本蓝图用于约束 project-skill 暴露与 QA 演进，避免“兼容能力反向污染主叙事”。

## 1. Human surface boundary

`v1.3.3` 主面继续固定为：

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`
- `help`
- `status`
- `doctor`

兼容能力 (`skill/profile/orchestrate`、external adapters、legacy bridge) 必须保持非默认、显式启用。

## 2. Project skill boundary

Host-visible skills 对外只需承接最小主面：

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`

可选能力：

- `beacon-prd-bootstrap` 作为 human skill（非一级命令）
- 默认 `dry-run + no-overwrite + strict context verify + atomic write + rollback/lock`

## 3. QA evolution boundary

`qa` 仍为正式第二执行面，但必须遵循：

- 默认不隐式触发 external orchestration
- 默认先返回 Beacon 内部 closure judgment
- 仅显式 compatibility mode 才进入外部链路
- QA 结果必须写回 scorecard / AC closure / repair handoff

## 4. HUD minimal contract

v1.3.3 的 HUD 采用极简约束：

- 目标 1~3 行
- 核心字段：版本、feature、当前 stage、阻塞原因/下一步
- 兼容 Codex / Claude 输入区下方展示，不暴露内部调度细节

## 5. Evidence and governance contract

- 冻结 requirement package 后再进入 implement/qa
- quality review 与 acceptance writeback 必须闭环
- release gate 判断依赖：
  - formal version package closure
  - feature-aware QA evidence/scorecard
  - required evidence / contract drift 策略

## 6. Freeze criteria

本蓝图完成条件：

1. 人类仍可只依赖最小主链完成交付。
2. external plane 仅以 compatibility 语义出现。
3. QA 默认路径不再隐式外部编排。
4. HUD 在 Codex/Claude 均可稳定展示且保持极简。
5. release/governance 可基于版本包材料给出一致判断。

