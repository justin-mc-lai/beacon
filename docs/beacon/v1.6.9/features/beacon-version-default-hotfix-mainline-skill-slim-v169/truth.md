---
slug: beacon-version-default-hotfix-mainline-skill-slim-v169
version: v1.6.9
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO UD全接受: version-default + hotfix-mainline + skill-slim"
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
ux_required: false
design_deferral: "CLI/runtime + host skill slim; no product UI"
---

## 人话

无版本默认规划线/patch+1；生产热修钉发布线并登记 hotfix/*；goal skill 压到 ≤80 行。

## UD（全接受）

| ID | Value |
|----|-------|
| UD-SK-001 | Public goal skill L0 ≤80 行 |
| UD-SK-002 | 自愈不暴露 gov skill 名 |
| UD-HF-001 | 生产事故=hotfix；从生产基线拉 hotfix/*，不进 feature 开发轨 |
| UD-HF-002 | 主线热修=基线 main/release；Git 必须登记 hotfix 分支 |
| UD-HF-003 | 无版本热修 baseline=current_runtime_release_line |
| UD-HF-004 | forward_port+rollback_notes+human release 仍要 |
| UD-VER-001 | 无版本 normal=planning 优先否则 patch+1 |
| UD-VER-002 | 热修不 bump |
| UD-VER-003 | 禁止 silent major/minor bump |
| UD-ENF-HF | hotfix/* 可业务提交；裸 main 仍禁 |

## AC

| ID | Description |
|----|-------------|
| AC-VD-001 | default_target_version: planning>runtime 时取最小更高 planning |
| AC-VD-002 | 无更高 planning 时 bump_patch(runtime) |
| AC-VD-003 | goal create/auto 使用 default_target_version |
| AC-HF-001 | hotfix 无 --from-version 时默认 baseline=current_runtime_release_line |
| AC-HF-002 | hotfix_plan 含 hotfix_branch 登记名与 not_feature_worktree |
| AC-HF-003 | forward_port 默认 main（仍可改）；缺 rollback 则 release_ready false |
| AC-SS-001 | skills/beacon/beacon-goal/SKILL.md 行数 ≤80 |
| AC-SS-002 | 细节在 references/goal-*.md |
| AC-SS-003 | loom-goal 同步瘦身或指针 |

## Non-goals

- 自动执行 production rollback
- 裸 main 无分支热修
