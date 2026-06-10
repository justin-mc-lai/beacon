# 证据：Beacon Planner Review Runtime Multi-Agent v1.6.0

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| planner-analysis | support_advisory | 当前用户确认的“多视角已实现但真实多代理 runtime 缺失”分析 | accepted-for-change | truth.define |
| feature-package | requirement_truth | docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md | authoritative | truth.define |
| package-tests | test_truth | docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/tests.md | authoritative | truth.coverage |
| prior-feature | support_advisory | docs/beacon/v1.6.0/features/beacon-pln-review-intent-parity-state-machine-v160/truth.md | indexed | source-study |
| prior-implementation | support_advisory | docs/beacon/v1.6.0/execution/implementation-summary-beacon-pln-review-intent-parity-state-machine-v160.md | indexed | source-study |
| reviewer-catalog | support_advisory | skills/beacon/beacon-pln-review/references/reviewer-catalog.md | indexed | source-study |
| skill-eval-kit | support_advisory | beacon/utils/skill_eval_kit.py | pending-implementation | generate |

## 决策记录

- 已接受：当前能力不能只停留在 reviewer catalog，多代理必须有 runtime evidence。
- 已接受：本 feature 不是 MVP，scope mode 是 `full_parity`。
- 已接受：没有 subagent runtime 时必须显式 fallback，不能假装并行多代理。
- 已接受：planner 多代理 evidence 仍是 support/runtime evidence，不是 truth、QA verdict 或 release verdict。

## 待实现证据

由 `beacon-gen-implement` 追加：

- changed files；
- runtime artifact builder；
- skill reference 更新；
- benchmark artifacts；
- pytest output；
- package verify / truth-map verify output；
- implementation evidence import marker。
