---
name: beacon-brainstorm
description: Use when the user wants Beacon's built-in thinking sidecar to continue requirement brainstorming, converge gaps from docs/beacon/<version>, or explore project evolution without rewriting frozen truth or entering implementation.
---

# Beacon Brainstorm

Use this skill as a read-only Beacon thinking sidecar.

It is not a new main lifecycle stage. The default lifecycle remains:

```text
prd -> user-story -> test-case -> prototype -> implement -> qa -> release
```

## Use for

- Continuing requirement brainstorming from `docs/beacon/<version>/`.
- Finding missing questions before editing PRD, user-story, or test-case materials.
- Exploring project evolution ideas before promoting them into a formal Beacon change.
- Returning `brainstorm closed` when the gap is stable and no further supplement is needed.
- Checking implementation prompts against frozen requirement evidence before `beacon-implement`.

## Thinking Protocol

Always apply:

- First principles: reduce the prompt to user outcome, evidence, and closure constraints.
- Socratic questioning: ask what must be true, what could falsify it, and which frozen evidence proves it.
- Occam's razor: remove redundant mechanisms, duplicate docs, and broad speculation.

## Operator rule

Prefer the installed CLI (works in any project directory once `beacon` is on `PATH`; does **not** depend on `skills/beacon/scripts/` being vendored):

```bash
beacon brainstorm run "<prompt>" \
  --project-root . \
  --version auto \
  --mode requirement-convergence \
  --json
```

Runtime note: current CLI line reports **`Beacon CLI v1.4.3`**. Adjust `--version` / docs paths if your project pins a different docs line.

Optional compatibility (Beacon repo or vendored skill pack only):

```bash
bash skills/beacon/scripts/run_beacon.sh brainstorm run "<prompt>" \
  --project-root . \
  --version auto \
  --mode requirement-convergence \
  --json
```

默认规则：

- Beacon 自身 requirement / evolution 头暴默认写入 `docs/brainstorms/`
- 外部项目或外部仓库分析会自动隔离到 `docs/brainstorms/external/`
- 如果需要写到明确目标位置，始终显式传 `--output`

Supported modes:

- `requirement-convergence`
- `project-evolution`
- `implementation-readiness`
- `scope-simplification`

Legacy aliases:

- `frozen-truth-delta` -> `implementation-readiness`
- `evolution-exploration` -> `project-evolution`
- `redundancy-pruning` -> `scope-simplification`

## Boundary

- Do not rewrite `docs/beacon/<version>/prd/`, `user-story/`, `qa/test-cases/`, `prototype/`, or `.machine/`.
- Do not execute implementation.
- If brainstorm changes frozen scope, route to `beacon-change`.
- If brainstorm only confirms frozen scope, route back to `beacon-implement`.

## Human Closure Contract

When the feature is materially complex, brainstorm must help produce a human-readable research closure package before freeze:

- `docs/beacon/<version>/research/<feature-slug>.md`
- architecture explanation
- business flow explanation
- state-machine explanation when states or transitions matter
- decision-priority explanation when conflicting rules must be resolved

Do not treat this as decoration. These materials are upstream inputs to `prd -> user-story -> test-case -> requirement_clarity -> freeze`.

## Examples

- 适用例：
  - “这个 PRD 看起来方向对，但我怀疑还漏了关键问题，先帮我收敛 gap。”
  - “需求不想立刻改 truth，先 challenge 一下假设、范围和证据缺口。”
  - “实现前想确认 frozen requirement 有没有明显洞，但不想直接进入 execution。”
- 不适用例：
  - “我已经确定要改 frozen scope，直接写回正式变更。” -> 应路由到 `beacon-change`
  - “需求已经稳定，现在要开始做实现。” -> 应路由到 `beacon-implement`

## Cold-start anchors

- `brainstorm` 是 read-only convergence surface，不是新 stage。
- 它的主要价值是 challenge framing、收敛 gap、解释 route，不是直接产出 truth。
- 如果结论会改正式承诺面，就必须回 `change`；如果只是确认 scope 稳定，就回主链继续执行。
