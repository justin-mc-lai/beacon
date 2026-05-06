# Beacon v1.3.12 人类面一页操作手册

> 适用：PRD / Story / Test / 状态查看 / 实现衔接  
> 目标：按最短路径跑通 `prd -> brainstorm -> user-story/test-case -> status/board -> implement`

## 先记住 4 条

1. `prd` 先定真相锚点。  
2. `brainstorm` 只做只读收敛，不改 frozen truth。  
3. `user-story / test-case` 负责补料、再冻结、再验收。  
4. `status / board` 用来看卡点和跳回具体补料项。

## 标准路径

```bash
# 1. 先看 PRD
beacon prd create "My Feature" --project . --version v1.3.12

# 2. 发现缺口后做只读收敛
beacon brainstorm run "补齐 PRD 缺口" \
  --project-root . \
  --version auto \
  --feature "My Feature" \
  --mode requirement-convergence \
  --json

# 3. 进入补料
beacon user-story create "My Feature" --project . --version v1.3.12 --json
beacon test-case create "My Feature" --project . --version v1.3.12 --json

# 4. 看补料和重冻结状态
beacon status --board --project-root . --version v1.3.12 --feature "My Feature"

# 5. 需要时直接进入实现
beacon implement plan "My Feature" --project . --version v1.3.9 --json
```

## 什么时候走哪条路

| 场景 | 用什么 |
|---|---|
| PRD 还缺角色、状态机、边界、异常、风险 | `beacon-prd` 或 `beacon-brainstorm` |
| 只是在读真相上继续深挖，不改 scope | `beacon-brainstorm` |
| 缺用户故事或 AC | `beacon-user-story` |
| 缺覆盖、场景或 QA 族群 | `beacon-test-case` |
| 需要看卡在哪个补料项 | `beacon-status --board` |
| 想直接跳回补料入口 | `beacon status --board` 里的 jump link |
| frozen feature 要改真相 | `beacon-change` |
| 准备实现 | `beacon-implement` |

## 稳定态判断

- `brainstorm` 输出 `brainstorm closed` 时，表示当前缺口已稳定，不要继续把它当成主路径。
- 如果 `status / board` 还显示补料项，优先回 `user-story / test-case` 补齐。
- 如果补料会改变 frozen truth，先走 `change`，不要直接改文档。

## 最小闭环

```text
PRD
-> brainstorm
-> user-story / test-case
-> re-freeze
-> status / board
-> implement
```

