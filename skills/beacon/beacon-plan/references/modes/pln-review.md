# Mode: pln-review

> Archived from `beacon-pln-review` during 1+6 merge. This is progressive disclosure content for `beacon-plan`.

# Beacon Planner Review

Use this skill to run a planner-only review before truth/change/refreeze/implementation. It consolidates the old founder, doubt, security, performance, context, simplify, ADR, design, and deep review surfaces into internal reviewers.

> 共享守则（preamble / HARD GATE / GIT_ADMISSION）见 `skills/beacon/references/shared-preamble.md`
## GIT_ADMISSION (mandatory — Tier A/B when version+feature known)

Before ANY repo write or implement/qa/release route:
1. `beacon workspace admit --project-root . --version <v> --feature <slug> --json`
2. If status != pass → STOP; show reason_codes; do NOT edit files
3. Set cwd to worktree_path from payload
4. Do NOT git checkout elsewhere to "fix" branch
5. When admission is soft-skipped (`require_workspace_admission=false`), still verify `current_branch == resolved target_branch` before repo writes (R5 UD-024)
6. (implement only) Before writing implementation, merge `truth_canonical` into the development branch so implementation bases on canonical frozen truth

## When to Use

- 用户要求多角度 review、多代理审查、CEO/founder/doubt/security/performance/design/context/ADR/simplify/deep 类挑战。
- 用户引用成熟 OSS/source 项目、要求完整复刻、同等能力、做全、parity 或不要 MVP。
- plan 到 truth 前需要检查用户真实意图是否被缩小、误译、弱化或无授权延期。
- feature 涉及 lifecycle、workflow、状态、队列、loop、resume、stop、rollback、recovery、权限、跨 harness 或多 agent。
- 需要合成 reviewer findings，给出下一跳 route，但不能直接改 truth 或实现。

## Workflow

1. 读取用户原话、resolver-selected truth/source/evidence refs 和相关 research。
2. 选择 reviewer：always-on reviewers 必跑；conditional reviewers 按触发条件加载。
3. **Runtime evidence（v1.6 实现线 `beacon-pln-review-runtime-multi-agent-v160`）**：在需要可审计多代理审查时，先运行 deterministic runtime builder，再基于 artifact 做 human-facing synthesis：
   ```bash
   beacon planner-review run <feature> --project-root . --version <version> --prompt "<utterance>" --json
   ```
   - artifact 写入 `.beacon/state/planner-review/<feature>/<review_id>.json`；
   - 无 subagent runtime 时必须为 `single_process_multi_reviewer` + `fallback_reason`；
   - 禁止声称 parallel subagent execution。
4. 输出结构化 findings，保留 severity、confidence、authority、evidence refs 和 user decision 字段。
5. 合成一个 route recommendation；P0/P1 不得静默进入 implement、QA 或 release。

## Output Contract

Review artifact must include:

- `intent_snapshot`
- `scope_mode`
- `source_capability_inventory` when source/parity is in scope
- `parity_matrix` when source/parity is in scope
- `deferral_ledger` for any MVP, cut, delay, partial coverage, or unimplemented capability
- `state_model` when the state-machine reviewer triggers
- `findings`
- `recommended_route`


## Underspecified / block still emit (mandatory)

If the user asks for multi-angle review / full parity / 完整复刻 but source OSS, target repo, feature, or version is missing:

1. **Do not** only ask clarifying questions and stop.
2. Still emit the full output contract with explicit placeholders and blockers:
   - `mode_id: pln-review`
   - `intent_snapshot` (from user utterance; mark unknown fields)
   - `scope_mode: full_parity` when user said 做全/同等能力/不要 MVP (never silently downgrade to MVP)
   - `parity_matrix` / `deferral_ledger` (may be empty tables + note "blocked: missing source")
   - `findings` with at least one **P0** finding: missing source/target/scope
   - `recommended_route` / `recommended_next_harness`: usually `stop` or `plan` until user supplies refs
3. List the exact questions needed next, **after** the structured artifact.
4. Never route silently to implement/QA/release while P0 blockers remain.

## References

Read only the reference files needed for the current request:

- `references/pln-review/reviewer-catalog.md` for reviewer selection and internal reviewer roles.
- `references/pln-review/finding-schema.md` for finding shape, severity, and route rules.
- `references/pln-review/intent-parity-artifacts.md` for intent snapshot, scope mode, parity matrix, and deferral ledger.
- `references/pln-review/state-machine-review.md` for finite state machine triggers, outputs, and truth/tests landing.
- `references/pln-review/multi-agent-runtime.md` for planner-only multi-reviewer runtime evidence, lane outputs, synthesis, and fallback transparency.
- `references/pln-review/compound-parity-review.md` for Compound-style reviewer catalog, source parity delivery, finding synthesis, autofix routing, diff scope, release ops, and QA evidence hygiene.
- `references/pln-review/skill-package-standard.md` for skill-creator anatomy and eval/benchmark package constraints.

## Route Rules

- User intent or source parity changed: route `beacon-gen-truth` or `beacon-gen-change`.
- Frozen truth needs refreeze after accepted support advisory: route `beacon-gen-refreeze`.
- Implementation is ready but not started: route `beacon-gen-implement`.
- Evidence sufficiency needs judgment: route `beacon-eval-qa`.
- Release readiness needs judgment: route `beacon-eval-release`.
- Friction is useful but not accepted for truth/change: route `beacon-pln-friction` or `defer/queue`.
