---
name: loom-goal
description: "【Loom 公共入口】一句话目标 → 计划/需求/实现/验收。与 $beacon-goal 双装并行，不覆盖 beacon。"
metadata:
  public_surface: true
  public_id: "goal"
  progressive_map: skills/beacon/references/public-surface-progressive-map.v1.json
  version: "v2.0.0"
  entry: public_primary
  brand: Loom
  dual_install_with: beacon-goal
---

# Loom Goal — Loom 轨唯一公共交付入口

## 与 Beacon 的关系

| | Beacon (生产) | Loom (进化/验收) |
|--|---------------|------------------|
| skill | `$beacon-goal` | **`$loom-goal`** |
| CLI | `beacon goal` | **`loom goal`** |
| 默认替换 | — | **禁止** Day-1 覆盖 beacon |

两轨可同机安装。W4 前禁止默认 `BEACON_V2=1` 或 alias beacon→loom。

## 30 秒

```text
$loom-goal
目标：...
版本：v2.0.0
```

```bash
loom goal run "<目标>" --project . --version v2.0.0
```

## 规则

- complete 需 verifier；release 人工门
- loop 仅 support（`$loom-loop-goal` 若存在）
- Phase-1 可共享 `skills/beacon/*` 实现路由

详见 `skills/loom/examples/goal-one-shot-30s.md`。

## Git worktree

See `skills/beacon/references/git-worktree-execution-flow.md` (shared; do not fork).


## InjectBundle steering (v2.0.0 R3)

Each turn injects **InjectBundle**: steering (Codex distill templates under `docs/beacon/v2.0.0/fixtures/steering/`) → **resume-pack digest** → next_action (not full chat/jsonl). Completion audit only prepares **awaiting_verifier**; never self-certify complete.

## Host subagent keyword (parity v1.6.8 / UD-SA-004)

Same gate as Beacon (`beacon.utils.host_subagent_gate`). Default off; satellite parallel independent of host agents.

## Backend

`$loom-goal` 对应 **Rust CLI**（不是 Python `loom-py`）：

```bash
bash scripts/install-loom-cli.sh
export PATH="$HOME/.local/bin:$PATH"
loom --help          # Rust
beacon --version     # Python production
```
