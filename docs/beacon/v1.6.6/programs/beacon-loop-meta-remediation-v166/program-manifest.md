---
program_slug: beacon-loop-meta-remediation-v166
version: v1.6.6
plan_mode: interactive
plan_mode_reason: prior_pln_review_ud_confirmed; no source_url; product_intent_from_conversation
scope_mode: full_parity
lake_or_ocean: 海
program_phase: P3
p4_ack: true
delegated_sub_skill: beacon-pln-program-interactive
upstream_program: beacon-oss-borrow-hardening-v165
upstream_version: v1.6.5
user_decisions:
  UD-TRACE-001: v1.6.6_jsonl_first_spine_pointer_v2_projection_rebuild
  UD-REMED-001: runtime_overlay_only_no_auto_canonical_skill
  UD-REMED-002: tests_md_subset_plus_stop_when_maker_ne_checker
  UD-PROGRAM-001: v1.6.6_new_program_after_v1.6.5_release
---

# Program Manifest — Loop Meta-Remediation v1.6.6

## User Intent (one line)

v1.6.6 交付 **结构化 Agent 全链路 trace → 停滞检测 Meta-Agent → 沙盒自动 remediation（overlay 改写 + eval + 回滚）**，消灭「请再试一次」式空转 loop。

## Utterance (stable paraphrase)

1. 给所有 Agent 加结构化日志：决策、失败、重试、输出全部结构化存储，禁止仅靠 print。
2. 第二个 Agent（governor/planner）只读 trace：检测重复犯错、重复劳动、平台期。
3. 检测到停滞后自动产出 remediation patch（prompt/skill/workflow/eval 标准），在 governed worktree 沙盒测试；改坏自动回滚；不说「请再试一次」。

## Scope Mode

`full_parity` — 三步合起来是海；拆成 3 个湖 feature，禁止单包空壳 closure。

## Non-Negotiable Boundaries (user-confirmed)

| UD | Decision |
|----|----------|
| UD-TRACE-001 | Step 1 先落 **v1.6.6 JSONL + spine 指针**；v2 `lifecycle_events` 迁移时 `projection rebuild` |
| UD-REMED-001 | **禁止**自动改 canonical `skills/beacon/*` 或 `features/*/truth.md`；仅 `.beacon/runtime-overlays/` |
| UD-REMED-002 | 沙盒 eval = 当前 feature `tests.md` **子集** + **stop_when maker≠checker**（对齐 v2 AC-106 语义） |
| UD-PROGRAM-001 | **独立 v1.6.6 program**；不阻塞 v1.6.5 release 闭环 |

## Harness Boundary

- Planner program artifacts only — not package truth.
- Meta-Agent = **governor** lane；remediation overlay ≠ truth change.
- Canonical skill/truth promote → `beacon-gen-change` + user ack.

## Source Refs (behavioral, not OSS clone)

- `docs/beacon/v1.6.5/` loop pattern registry, failure catalog, token budget, workspace pool (upstream)
- `docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md` AC-106/107/108 (semantic alignment, not v2 delivery)
- `beacon/utils/workflow_memory.py` lifecycle events (partial trace today)
- Prior `beacon-pln-review` artifact: loop-meta-remediation planning review (2026-07-10)

## Route Recommendation (post-P4)

After `p4_ack: true` → topological `beacon-gen-truth` per lake:

1. `beacon-agent-structured-trace-v166`
2. `beacon-loop-stagnation-detector-v166`
3. `beacon-harness-remediation-sandbox-v166`
