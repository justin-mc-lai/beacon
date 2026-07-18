# Loom + Beacon 并列 30 秒用法

## Loom（v2 进化轨）

```text
$loom-goal
目标：交付 domain-bearing 能力并验收
版本：v2.0.0
```

```bash
loom goal run "..." --project . --version v2.0.0
```

## Beacon（生产轨，不被覆盖）

```text
$beacon-goal
目标：...
版本：v1.6.7
```

```bash
beacon goal run "..." --project . --version v1.6.7
```

## 双装验收

| 检查 | 期望 |
|------|------|
| `which beacon` / `which loom` | 两个不同二进制名 |
| 安装 loom | **不得**改写 beacon launcher |
| 状态根 | `.beacon` vs `.loom`（品牌隔离） |
| release | 两轨皆人工确认 |

**不要**宣称 loom 默认替代 beacon（W4 前）。
