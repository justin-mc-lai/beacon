# 证据：Beacon Planner Review Compound Parity v1.6.0

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| user-request | support_advisory | 当前用户确认“使用 beacon-gen-change 落 beacon-pln-review-compound-parity-v160” | accepted-for-change | truth.define |
| planner-analysis | support_advisory | docs/beacon/archive/v1.6.0/research/beacon-pln-review-compound-parity-v160.md | promoted | truth.define |
| feature-package | requirement_truth | docs/beacon/archive/v1.6.0/features/beacon-pln-review-compound-parity-v160/truth.md | authoritative | truth.define |
| package-tests | test_truth | docs/beacon/archive/v1.6.0/features/beacon-pln-review-compound-parity-v160/tests.md | authoritative | truth.coverage |
| prior-intent-parity | support_advisory | docs/beacon/archive/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md | indexed | source-study |
| prior-runtime-multi-agent | support_advisory | docs/beacon/archive/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md | indexed | source-study |
| compound-reference | support_advisory | /Users/apple/.codex/skills/compound-engineering/ce-code-review/SKILL.md | indexed | source-study |
| beacon-review-skill | support_advisory | skills/beacon/beacon-pln-review/SKILL.md | implemented | generate |
| compound-reference | support_advisory | skills/beacon/beacon-pln-review/references/compound-parity-review.md | implemented | generate |
| planner-runtime | support_advisory | beacon/utils/planner_review_runtime.py | implemented | generate |
| skill-eval-kit | support_advisory | beacon/utils/skill_eval_kit.py | implemented | generate |
| unit-tests | support_advisory | tests/test_v160_pln_review_compound_parity.py | passed | qa |
| benchmark | support_advisory | .beacon/state/skill-eval/benchmarks/skill-benchmark-20260609t125148z | passed | qa |
| skill-package-verify | support_advisory | beacon skill package verify --project-root . --version v1.6.0 --json | passed | qa |

## 决策记录

- 已接受：Beacon QA 类型覆盖不是主要缺口，主要缺口是 planner review 工程闭环。
- 已接受：本 feature 必须保留 Beacon 的 truth/evidence/release 边界，不把 planner review 变成实现或验收入口。
- 已接受：Compound 式 reviewer/finding/synthesis/autofix routing 需要进入 `beacon-pln-review` 的内部 contract。
- 已接受：source parity 防缩水是核心能力，不能把“完整复刻/同等能力/做全”静默降级为 MVP。
- 已接受：QA evidence hygiene、release ops closure、PR/diff/worktree scope 都需要成为 planner review 可发现、可路由的 finding。

## 实现证据

- changed files: `beacon/utils/planner_review_runtime.py`, `beacon/utils/skill_eval_kit.py`, `skills/beacon/beacon-pln-review/SKILL.md`, `skills/beacon/beacon-pln-review/references/compound-parity-review.md`, `.agents/skills/beacon-pln-review/**`, `docs/beacon/archive/v1.6.0/.generated/skills/beacon/beacon-pln-review/**`, `tests/test_v160_pln_review_compound_parity.py`, `tests/test_v160_skill_harness_taxonomy.py`
- pytest: `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py tests/test_v160_pln_review_multi_agent.py tests/test_v160_skill_harness_taxonomy.py` -> pass, 41 passed
- benchmark: `beacon skill eval-kit benchmark --version v1.6.0 --json` -> pass, `.beacon/state/skill-eval/benchmarks/skill-benchmark-20260609t125148z`
- package verify: `beacon skill package verify --project-root . --version v1.6.0 --json` -> pass
