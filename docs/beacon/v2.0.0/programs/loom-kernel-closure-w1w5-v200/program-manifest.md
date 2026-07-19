---
program_slug: loom-kernel-closure-w1w5-v200
version: v2.0.0
brand: Loom
status: frozen
revision_id: R1
promotion_ref: planner-review:pln-review-20260719t110159z+user-accept-option2-20260719
parent_feature: beacon-v2-rust-kernel-redesign
---

# Program Manifest — Loom Kernel Closure W1–W5

## 人话

把 Rust/Loom 内核还没关的洞，按 **6 个湖** 一次挂上拓扑：先隔离树真实现，再长跑可停可验，再冻结不烂，再敢 release，再多 git 拓扑，最后双轨评分可比。  
**不**做默认替换生产 `beacon`；**不**做 slug 全量 rename。

## User Intent

用户确认 option 2：change 一次挂上 6 湖 program 拓扑，仍按序 implement。

## Waves

| Wave | Lake | AC |
|------|------|-----|
| W1 | loom-git-worktree-implement-harness | 099, 100 |
| W2 | loom-run-agent-stop-when-external | 105, 106 |
| W3 | loom-tig-truth-integrity-v2 | 101, 103 |
| W4a | loom-cross-track-adversarial-release | 166, 167 |
| W4b | loom-gitscope-topology-gates | 171–173 |
| W5 | loom-skill-score-corpus-v1 | 169 |

## Implement order

W1 → W2 → W3 → (W4a ∥ W4b) → W5

## Non-Goals

- P6 默认切换 / criterion 全套（另波）
- feature slug 全量 beacon-v2-* → loom-* 路径迁移
