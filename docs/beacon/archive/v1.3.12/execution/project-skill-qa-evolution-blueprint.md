# Beacon v1.3.12 Project Skill QA Evolution Blueprint

## 目的

明确 `v1.3.12` 中 `prd / user-story / test-case` 与 `help / status / board` 的分工，确保需求深挖、补料、再冻结与可见化闭环一致。

## 核心分工

- Beacon 核心：
  - requirement deepening contract
  - gap digest / supplement task / re-freeze transaction
  - frozen truth read model
- project skill / human surface：
  - PRD / story / test-case 的补料与重冻结
  - help / status / board 的卡点投影
- delivery layer：
  - 只读 completeness
  - 不回写 requirement truth

## QA 关注点

- 补料项是否能从 board 跳回具体 user-story / test-case 入口
- help 是否能解释当前下一跳是 brainstorm、补料还是 change
- status 是否能显示当前卡在哪个子 gate
- delivery 层是否只消费 completeness 而不改写 truth
