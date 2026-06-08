# 证据：Beacon Skill Harness Taxonomy v1.6.0

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-brainstorm | support_advisory | docs/beacon/v1.5.2/research/beacon-skill-harness-taxonomy-v160.md | adopted | truth.define |
| version-plan | support_advisory | docs/beacon/v1.6.0/version/beacon-skill-harness-taxonomy-v160.md | indexed | truth.define |
| feature-package | requirement_truth | docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md | authoritative | truth.define |
| package-tests | test_truth | docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/tests.md | authoritative | truth.coverage |
| package-tasks | support_advisory | docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/tasks.md | task-intent-indexed | implement |
| package-evidence | support_advisory | docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/evidence.md | evidence-indexed | qa |
| gstack-ethos-study | support_advisory | /Users/apple/Developer/Personal/personal-brain/sources/web-notes/mp-weixin-qq-com-yc-50-ai/2026-06-08-142327.md | indexed | planner |
| codex-workflow-study | support_advisory | /Users/apple/Developer/Personal/personal-brain/sources/web-notes/baoyu-io-codex-codex/2026-06-08-132909.md | indexed | planner |
| slow-uni-bmtop-friction | support_advisory | /Users/apple/Developer/Personal/products/slow_uni_bmtop/.beacon/analysis/friction-intake-fit-20260608T053823Z.md | indexed | no-fake-delivery |
| default-truth-language-zh | requirement_truth | docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md | adopted | truth.define |
| planner-research-contract | requirement_truth | docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md | adopted | truth.define |
| skill-rename-rewrite-contract | requirement_truth | docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md | adopted | truth.define |
| harness-hard-gate-injection | requirement_truth | docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md | adopted | truth.define |
| skill-creator-eval-harness-research | support_advisory | docs/beacon/v1.6.0/research/skill-creator-eval-harness-research.md | accepted-for-change | change/refreeze |
| skill-eval-benchmark-contract | requirement_truth | docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md | adopted | truth.define |

## 决策记录

- 已接受：v1.6.0 使用 harness-first skill naming。
- 已接受：host-visible v1.6.0 skill aliases 有意 breaking；旧名称从 v1.6.0 skill package 移除。
- 已接受：CLI compatibility 如有需要，属于 runtime migration concern，不能表现为重复 host-visible skill names。
- 已接受：每个 v1.6.0 skill 都携带 generated shared preamble。
- 已接受：planner、generator、evaluator 和 governor hard gates 定义 skill authority。
- 已接受：no fake delivery policy 是 cross-surface closure constraint。
- 已接受：除非用户显式指定其他语言，Beacon 需求真相默认以中文为主语言；英文只保留为稳定术语、路径、命令和协议标识。
- 已接受：`research/` 是 planner artifact surface，authority 为 `support_advisory`；它承载调研和路由建议，但不能自动成为 requirement truth。
- 已接受：research 进入需求真相必须有用户确认和 `promotion_ref`，并通过 governed truth/change/refreeze 路径冻结。
- 已接受：v1.6.0 skill 改名必须按 Rename Matrix 生成新 `beacon-<harness>-<function>` host-visible skill，并移除旧 host-visible aliases。
- 已接受：v1.6.0 不能只依赖 CLI/function routing 治理 harness 边界；每个 host-visible skill 必须在共享 preamble 后注入 harness-specific `HARD GATE`，由 agent-surface verify 扫描并阻断缺失或不匹配的 gate。
- 已接受：skill eval 需要 benchmark 行为证据层，输出 `eval_metadata/`、`grading/`、`benchmark/`、`analysis/`，并把 TC-006 到 TC-011、TC-017 从静态或 replay-only 证明升级为 runtime evidence。

## 边界

`evidence.md` is an index/read model. It must not contain final verdict, gate truth, release readiness, or source-of-truth override fields.
