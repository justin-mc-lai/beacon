# 证据：Beacon Agent Eval v1.6.1

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| planner-research | support_advisory | docs/beacon/v1.6.1/research/beacon-agent-eval-v161.md | promoted | truth.define |
| planner-review | support_advisory | .beacon/state/planner-review/beacon-agent-eval-v161/pln-review-20260615t090341z.json | indexed | research |
| feature-package | requirement_truth | docs/beacon/v1.6.1/features/beacon-agent-eval-v161/truth.md | frozen R2 | implement |
| package-tests | test_truth | docs/beacon/v1.6.1/features/beacon-agent-eval-v161/tests.md | authoritative | truth.coverage |
| change-intent | support_advisory | user utterance：坚持全 skill live | accepted | beacon-gen-change |
| upstream-harness-taxonomy | requirement_truth | docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md | frozen | dependency |
| upstream-program-plan | requirement_truth | docs/beacon/v1.6.1/features/beacon-harness-program-plan-v161/truth.md | frozen R2 | dependency |
| upstream-tig | requirement_truth | docs/beacon/v1.6.0/features/beacon-truth-integrity-gates-v160/truth.md | frozen | dependency |

## 决策记录

- R1：scope A full parity Agent Eval；统一分数面 + catalog + 分层 runner；分数 runtime evidence only。
- **R2 change（用户确认 2026-06-15）**：**坚持全 skill live** — PB-AE-001 从 post-freeze 拉回 P0；matrix 权威源 = `v160_skill_package_projection()`（36）+ `beacon-eval-agent`（37 条 live case）。
- Research promoted：`user_decision=promoted`，`promotion_ref` 指向 feature package truth。

## Gate 证据

### R1 truth freeze（2026-06-15）

| gate | status | artifact |
|------|--------|----------|
| TIG block | pass | 0 findings |
| verify-closure | pass | closure_allowed=true |
| freeze R1 | frozen | `sha256:13809725dedfba88bbf9c6e31fc3d27614e364c8924d9c3bdd6f8f2f179ebd2c` |

### R2 change refreeze（2026-06-15）

| gate | command | status | artifact |
|------|---------|--------|----------|
| reopen | `beacon change … --reopen-now` | R1→R2 | revision_state |
| TIG | `beacon doctor verify-truth-integrity … --mode block` | pass (0 findings) | truth_integrity_gate |
| truth-map | `beacon truth-map rebuild-machine …` | rebuilt | `.machine/requirement/*.truth-map.json` |
| freeze R2 | `beacon freeze … --version v1.6.1` | frozen | `sha256:72b97d62c01867b78abe0bbdd3ca59acaf23d831afe76f294ceb286a837e482e` |

注：`beacon change --refreeze-chain` 因 `legacy_cutover_required` blocked；R2 经 `beacon freeze` + TIG pass 完成 closure（与 R1 同路径）。

## Context traceability

- 对话 + planner review → scope A → AC-AE-001..033
- R2：pln-review P1-01 用户拍板全 skill live

## Boundary

`evidence.md` 为索引/read model。Agent Eval scorecard 不得承载 final QA verdict 或 release readiness authority。
