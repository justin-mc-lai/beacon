---
name: beacon-goal
description: >
  【唯一公共入口】一句话目标 → plan/truth/implement/qa/release 直到 done。
  无版本默认规划线或 patch+1；生产事故用 hotfix 主线短分支。Triggers: 目标, goal, 交付, 热修, 生产事故, longrun.
metadata:
  public_surface: true
  public_id: "goal"
  progressive_map: skills/beacon/references/public-surface-progressive-map.v1.json
  version: "v1.6.9"
  entry: public_primary
  role: product_goal_facade
  longrun: true
---

# beacon-goal

**一句话目标 → 验收。** 不要先调 `$beacon-loop-goal`。

## 默认（无版本）

```bash
beacon goal run "<目标>" -p . -v auto
```

`auto` → **planning 线优先**，否则 `current_runtime` 的 **patch +1**（不 silent major/minor）。

## 两场景

| 场景 | 怎么做 |
|------|--------|
| **正常交付** | admit feature worktree → leaf 实现 → merge main → 人工 release |
| **生产热修** | `--mode hotfix`；baseline=**当前发布线**；分支=`hotfix/<baseline>-<slug>`（**不进** feature 开发轨） |

```bash
# 热修（可不写 --from-version，默认当前发布线）
beacon goal run "生产：…" --mode hotfix -p . \
  --forward-port main --rollback-notes "revert <sha>"
beacon goal hotfix-plan "生产：…" -p . --json   # 含 hotfix_branch 登记
beacon release check <baseline> --profile hotfix -p .
```

## HARD

1. **不自证 complete / 不 auto-release**
2. **正常交付禁止裸 main 写业务**；热修必须 **先建 `hotfix/*` 分支**（pre-commit 拦 main）
3. 细节与 longrun/admit/自愈 → **CLI + references**，用户不必记 gov skill 名

## 渐进

内部加载 plan/truth/design/implement/qa/release；map：`public-surface-progressive-map.v1.json`。

## 参考（按需）

- `references/git-worktree-execution-flow.md`
- `references/hotfix-prod-incident.md`
- `references/version-default.md`
- `references/goal-full-ops.md`（完整 ops 备查）
- 示例：`examples/goal-one-shot-30s.md` · `examples/hotfix-30s.md`
