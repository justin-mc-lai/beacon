# Loom

**Loom = Beacon 的升级品牌线（产品 v2）**，不是「又一个叫 loom-v2 的旁支」。

| 轨 | 品牌 | CLI | Skills | 定位 |
|----|------|-----|--------|------|
| 生产 | **Beacon** | `beacon` | `$beacon-goal` / `skills/beacon/*` | 现网 v1.6.x |
| 进化 | **Loom** | **`loom`** | `$loom-goal` / `skills/loom/loom-*` | 原 Beacon v2 能力与 Rust kernel |

## 命名原则

- 对用户只说 **Loom**，不说 `loom-v2`、`beacon-v2` 作为产品名。
- 版本号可以是 v2.0.0（发布线），品牌名始终是 Loom。
- 双装并行：安装 Loom **不得**覆盖 `beacon` launcher（W4 前禁止默认接管）。

## 入口

```bash
# 产品目标（公共）
loom goal run "..." --project . --version v2.0.0
# 或 skill
$loom-goal
```

```bash
# Rust kernel 面（同品牌 CLI 名 loom；与 Python facade 分发行物时以 PATH 为准）
loom harness list --json
loom worktree resolve --mode worktree --project-root . --run-id r1 --json
```

## Skill 前缀

- Loom 轨：`loom-*`（`skills/loom/`）
- 内容单源过渡期可仍路由 `skills/beacon/*`（见 `mirror-manifest.json`）
- 生产轨继续 `beacon-*`，互不替换

## 状态根

- 生产：`.beacon/`
- 进化：`.loom/`（如 worktree：`.loom/worktrees/<run_id>`）

## 与仓库路径

过渡期需求文档可仍在 `docs/beacon/v2.0.0/`（历史路径）；**对外品牌与 CLI 一律 Loom**。
