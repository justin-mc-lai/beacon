---
name: loom-goal
description: >
  Loom 公共 goal 入口（与 beacon-goal 同义 1+6）。后端优先 Rust CLI loom/beacon-v2。
  无版本默认与 hotfix 主线规则同 beacon-goal。
metadata:
  public_surface: true
  public_id: "goal"
  brand: loom
  version: "v2.0.0"
  dual_install_with: beacon-goal
---

# loom-goal

与 **`$beacon-goal`** 同一交付哲学；品牌 Loom / v2。

```bash
# 文档与合同线
beacon goal run "<目标>" -p . -v auto
# 或安装后的 loom CLI 能力面（Rust）
```

## 两场景（同 beacon）

1. **正常**：admit leaf worktree  
2. **生产热修**：`--mode hotfix` + `hotfix/*` 分支登记，不进 feature 开发轨  

## HARD

- 不 auto-release；不自证 complete  
- 无版本：planning 优先否则 patch+1；热修钉发布线  
- 细节：`skills/beacon/references/{version-default,hotfix-prod-incident,git-worktree-execution-flow}.md`
