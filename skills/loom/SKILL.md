---
name: loom
description: "Loom — Beacon 进化品牌（v2 产品线）。入口 $loom-goal；与生产 beacon 双装。"
metadata:
  version: "v2.0.0"
  brand: Loom
---

# Loom

**Loom 就是 Beacon 的升级品牌线**，不是 loom-v2 旁支。

| | 生产 Beacon | 进化 Loom |
|--|-------------|-----------|
| CLI | `beacon` | **`loom`** |
| skill | `$beacon-goal` | **`$loom-goal`** |

双装并行；安装 Loom **禁止**覆盖 `beacon`。

## Runtime backend (locked)

| Surface | Binary | Tech |
|---------|--------|------|
| Production | `beacon` | **Python** CLI |
| Evolution / Loom | `loom` **or** `beacon-v2` | **Rust** (`packages/beacon-rs`) |

Install:

```bash
bash scripts/install-loom-cli.sh      # Rust only; does not touch production beacon
bash scripts/install-loom-skills.sh   # skills/loom only
```

- Python `loom-py` is debug facade only — must not own PATH name `loom`.
- W4 前禁止默认 `BEACON_V2=1` / 用 loom 替换 beacon。
