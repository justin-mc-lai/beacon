# 证据：Beacon Planner Review Intent Parity State Machine v1.6.0

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| planner-research | support_advisory | docs/beacon/v1.6.0/research/beacon-pln-review-intent-parity-state-machine-v160.md | accepted-for-change | truth.define |
| feature-package | requirement_truth | docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md | authoritative | truth.define |
| package-tests | test_truth | docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/tests.md | authoritative | truth.coverage |
| package-tasks | support_advisory | docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/tasks.md | task-intent-indexed | generate |
| package-evidence | support_advisory | docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/evidence.md | evidence-indexed | evaluate |
| compound-skill-pattern | support_advisory | /Users/apple/.codex/skills/compound-engineering/ce-code-review/SKILL.md | indexed | source-study |
| compound-reviewer-catalog | support_advisory | /Users/apple/.codex/skills/compound-engineering/ce-code-review/references/persona-catalog.md | indexed | source-study |
| qi-dev-skill-creator | support_advisory | /Users/apple/Developer/Personal/products/justin-mc-lai-skills/skills/qi-dev/references/personal-skill-creator-spec.md | indexed | source-study |
| state-machine-checklist | support_advisory | skills/beacon/references/state-machine-checklist.md | indexed | source-study |
| diagram-truth-runtime | support_advisory | beacon/utils/diagram_truth.py | indexed | source-study |
| requirement-clarity-runtime | support_advisory | beacon/utils/requirement_clarity.py | indexed | source-study |

## 决策记录

- 已接受：方案 2 是目标方向，即新增 `beacon-pln-review` 并把过细 planner 能力降级为内部 reviewer catalog。
- 已接受：`beacon-pln-review` 必须保护用户意图，不允许把“完整复刻/同等能力/做全”静默降为 MVP。
- 已接受：source parity 必须通过 inventory + matrix 表达，不能只靠总结性文字。
- 已接受：有限状态机审查是硬性标准，不是可选 checklist；状态机 reviewer 必须能从整体状态机审视 plan/truth readiness。
- 已接受：状态机审查必须在 package truth 和 coverage truth 中有落点。
- 已接受：Beacon skill package 必须吸收 qi-dev/OpenAI/Anthropic skill-creator 标准，但不能破坏 Beacon truth/evidence/gate 边界。

## 待实现证据

`beacon-gen-implement` 已追加以下实现证据：

- changed files：`beacon/utils/agent_surface.py`、`beacon/utils/skill_eval_kit.py`、`skills/beacon/SKILL.md`、`skills/beacon/beacon-pln-review/`、`skills/beacon/beacon-gov-router/SKILL.md`、`skills/beacon/beacon-eval-qa/SKILL.md`、`skills/beacon/metadata.json`、`docs/beacon/v1.6.0/.generated/skills/beacon/`、`tests/test_v160_skill_harness_taxonomy.py`。
- skill projection diffs：`.generated/skills/beacon` 新增 `beacon-pln-review`，并移除 `beacon-pln-deep`、`beacon-pln-founder`、`beacon-pln-design`、`beacon-pln-security`、`beacon-pln-performance`、`beacon-pln-doubt`、`beacon-pln-context`、`beacon-pln-simplify`、`beacon-pln-adr`。
- reviewer reference files：`skills/beacon/beacon-pln-review/references/reviewer-catalog.md`、`finding-schema.md`、`intent-parity-artifacts.md`、`state-machine-review.md`、`skill-package-standard.md`。
- eval/benchmark artifacts：`.beacon/state/skill-eval/benchmarks/skill-benchmark-20260609t084012z/{eval_metadata,grading,benchmark,analysis}`。
- focused test command output：`pytest -q tests/test_v160_skill_harness_taxonomy.py` -> 16 passed。
- implementation summary：`docs/beacon/v1.6.0/execution/implementation-summary-beacon-pln-review-intent-parity-state-machine-v160.md`。
- implementation evidence import marker：`.beacon/state/implementation-beacon-pln-review-intent-parity-state-machine-v160.json`。

## 边界

`evidence.md` 是证据索引，不是 final verdict。它不得包含 QA pass、release readiness 或 implementation completion。
