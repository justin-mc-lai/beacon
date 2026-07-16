# 证据：Beacon Planner Review Runtime Multi-Agent v1.6.0

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| feature-package | requirement_truth | docs/beacon/archive/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md | **frozen R1** | truth.define |
| package-tests | test_truth | docs/beacon/archive/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/tests.md | authoritative | truth.coverage |
| runtime-builder | support_advisory | beacon/utils/planner_review_runtime.py | **implemented** | generate |
| planner-cli | support_advisory | beacon/commands/planner_review.py | **implemented** | generate |
| loop-delegate | support_advisory | packages/beacon-loop/src/delivery/review.ts | **implemented** | generate |
| skill-surface | support_advisory | skills/beacon/beacon-pln-review/SKILL.md | **implemented** | generate |
| skill-eval-kit | support_advisory | beacon/utils/skill_eval_kit.py (TC-021–025) | **implemented** | evaluate |
| prior-feature | support_advisory | docs/beacon/archive/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md | indexed | source-study |

## 决策记录

- 已接受：多代理必须有 runtime evidence，不能只用 reviewer catalog。
- 已接受：scope mode 为 `full_parity`；无 subagent 时必须显式 fallback。
- 已接受：runtime evidence 非 truth、非 QA verdict、非 release verdict。

## Implementation Evidence

| 项 | 值 |
|----|-----|
| changed files | `beacon/utils/planner_review_runtime.py`, `beacon/commands/planner_review.py`, `packages/beacon-loop/src/delivery/review.ts`, `skills/beacon/beacon-pln-review/**`, `beacon/utils/skill_eval_kit.py`, `tests/test_v160_pln_review_multi_agent.py` |
| pytest | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py` → 12 passed |
| benchmark | `beacon skill eval-kit benchmark --version v1.6.0 --json` → TC-021–025 covered |
| summary | docs/beacon/archive/v1.6.0/execution/implementation-summary-beacon-pln-review-runtime-multi-agent-v160.md |
| QA | formal QA accepted（见 `.beacon/qa/features/beacon-pln-review-runtime-multi-agent-v160/`） |

## QA / Release Verdict

Formal QA：**accepted**（support/runtime feature；非 release-blocking v1.6 promotion 项以外自洽）。
