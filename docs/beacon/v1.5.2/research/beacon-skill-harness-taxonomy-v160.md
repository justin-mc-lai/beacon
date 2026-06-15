# Beacon Skill Harness Taxonomy v1.6.0 Brainstorm

- feature: `beacon-skill-harness-taxonomy-v160`
- status: `brainstorm_only`
- authority: `support_advisory`
- target_version: `v1.6.0`
- source_version_context: `v1.5.2`
- generated_at: `2026-06-08`

## Boundary

This document is a `beacon-brainstorm` output. It is not formal requirement truth, not a gate verdict, and not permission to rename skill packages directly.

If accepted, route this into `beacon-change` / v1.6.0 feature package truth before implementation.

## Source Anchors

- v1.5.2 truth-source cutover: `truth-map resolver -> features/<slug>/{truth,tests,tasks,evidence}.md`.
- Legacy `prd/`, `user-story/`, and `qa/test-cases/` are no longer canonical truth surfaces. They are rebuild/absorb/archive artifacts only.
- Global boundaries still require a narrow human mainline and keep support surfaces out of lifecycle stage authority.
- Current skill surface is mixed by historical names: brainstorm/deep/friction/design/review/truth/implement/qa/release/toolkit.
- gstack/Y Combinator skill lesson: the valuable layer is shared philosophy compiled into every skill, plus hard gates and source-generated docs.
- Harness lesson: Harness = Agent minus Model. Split one large agent into planner, generator, evaluator responsibilities.

## Problem

Beacon skill names currently mix four concerns:

- research / brainstorm / analysis / review;
- requirement truth definition and change;
- implementation and repair;
- QA, release, and gate verification;
- toolkit / doctor / archive / memory support.

This creates route ambiguity for humans and LLMs. A rough prompt like "help me analyze this feature" can drift into requirement truth, implementation, or QA language without a stable role boundary.

v1.6.0 should make the harness role explicit in the skill name and contract.

## v1.6.0 Lifecycle Model

v1.6.0 should stop describing the normal lifecycle as `prd -> user-story -> test-case`.

The package-authoritative lifecycle should be:

```text
intake / research support
-> truth package definition
-> implementation planning
-> implementation generation
-> evaluation / QA
-> release decision
```

Canonical truth remains:

```text
truth-map resolver
-> features/<slug>/truth.md
-> features/<slug>/tests.md
-> features/<slug>/tasks.md
-> features/<slug>/evidence.md
```

Legacy command names may still exist in v1.5.2 code, but v1.6.0 skill language should treat them as compatibility concepts to remove, not as primary stage names.

## Harness Taxonomy

### `planner`

Planner surfaces turn a rough human prompt into a bounded plan, route, or truth update proposal.

Allowed:

- classify lake vs ocean;
- read truth/source/evidence;
- split scope;
- identify acceptance gaps;
- route to truth/change/implement/qa/release;
- produce research or planning artifacts.

Forbidden:

- write implementation;
- claim QA pass;
- give release verdict;
- silently mutate frozen truth.

### `generator`

Generator surfaces produce or modify delivery artifacts under a stable plan.

Allowed:

- write or update package truth when the surface is a truth generator;
- write implementation when the surface is an implementation generator;
- materialize automation/tooling artifacts under explicit contracts.

Forbidden:

- define its own gate verdict;
- claim completion from task progress;
- use placeholder/docs-only/fake output as delivery closure;
- override frozen truth without change routing.

### `evaluator`

Evaluator surfaces judge evidence and decide whether the next route is repair, truth change, QA continuation, release, or blocked.

Allowed:

- verify acceptance proof;
- detect drift, placeholder evidence, fake runners, missing coverage;
- produce reason codes and repair routes;
- block release.

Forbidden:

- rewrite requirement truth directly;
- replace implementation;
- pass release readiness from a single proxy signal.

### `governor`

Governor surfaces maintain Beacon's environment, archive, version, memory, hooks, automation, and diagnostic scaffolding.

Allowed:

- repair context;
- sync/generated projections;
- archive historical truth;
- manage queues and hooks;
- expose board/status.

Forbidden:

- become a human mainline stage;
- define requirement truth;
- give QA/release verdict unless explicitly a gate surface.

## Proposed v1.6.0 Skill Name Scheme

Format:

```text
beacon-<harness>-<function>
```

Accepted harness prefixes:

- `beacon-planner-*`
- `beacon-generator-*`
- `beacon-evaluator-*`
- `beacon-governor-*`

Do not introduce aliases in the v1.6.0 skill package. If compatibility is needed for CLI commands, keep it in CLI registry or migration tooling, not in host-visible skill names.

## Proposed Skill Rename Matrix

| Current skill | v1.6.0 skill | Harness | Role |
|---|---|---:|---|
| `beacon-brainstorm` | `beacon-planner-brainstorm` | planner | Rough prompt decomposition and route convergence |
| `beacon-deep` | `beacon-planner-deep-analysis` | planner | Complex state/risk/test-delta analysis |
| `beacon-friction-intake` | `beacon-planner-friction-intake` | planner | Friction capture and queue-only governance |
| `beacon-ceo-review` | `beacon-planner-founder-review` | planner | Founder/business challenge before truth or execution |
| `beacon-design-review` | `beacon-planner-design-review` | planner | UX/design challenge before truth or implementation |
| `beacon-security-review` | `beacon-planner-security-review` | planner | Security challenge and route advice |
| `beacon-performance-review` | `beacon-planner-performance-review` | planner | Performance challenge and route advice |
| `beacon-doubt-review` | `beacon-planner-doubt-review` | planner | Assumption and self-rationalization challenge |
| `beacon-source-driven` | `beacon-planner-source-driven` | planner | Source evidence anchoring before truth/execution |
| `beacon-context-engineering` | `beacon-planner-context-engineering` | planner | Context reshaping and drift reduction |
| `beacon-truth` | `beacon-generator-truth-package` | generator | Package-authoritative truth umbrella |
| `beacon-prd` | remove or absorb into `beacon-generator-truth-package` | generator | Legacy truth drafting concept |
| `beacon-user-story` | remove or absorb into `beacon-generator-truth-package` | generator | Legacy acceptance derivation concept |
| `beacon-test-case` | remove or absorb into `beacon-generator-truth-package` | generator | Legacy coverage derivation concept |
| `beacon-prd-bootstrap` | `beacon-generator-truth-bootstrap` | generator | One-shot package bootstrap |
| `beacon-change` | `beacon-generator-truth-change` | generator | Governed frozen truth change |
| `beacon-change-refreeze` | `beacon-generator-truth-refreeze` | generator | One-shot change/refreeze chain |
| `beacon-prototype` | `beacon-generator-prototype-binding` | generator | Accepted UI/UX result binding |
| `beacon-implement` | `beacon-generator-implementation` | generator | Implementation planning/execution |
| `beacon-design` | `beacon-generator-design-support` | generator | Design support umbrella |
| `beacon-design-bootstrap` | `beacon-generator-design-bootstrap` | generator | Design capability admission |
| `beacon-design-explore` | `beacon-generator-design-explore` | generator | UI direction exploration |
| `beacon-design-system` | `beacon-generator-design-system` | generator | Component system planning |
| `beacon-design-polish` | `beacon-generator-design-polish` | generator | UI polish support |
| `beacon-design-library` | `beacon-governor-design-library` | governor | Reference lookup |
| `beacon-design-extract` | `beacon-governor-design-extract` | governor | Screenshot/reference extraction |
| `beacon-design-simplify` | `beacon-planner-design-simplify` | planner | Simplicity audit |
| `beacon-qa` | `beacon-evaluator-qa` | evaluator | Acceptance verification |
| `beacon-qa-evo-deep` | `beacon-evaluator-qa-deep` | evaluator | Deep QA support findings |
| `beacon-release` | `beacon-evaluator-release` | evaluator | Release readiness |
| `beacon-real-project-validation` | `beacon-evaluator-real-project` | evaluator | Real project release proof |
| `beacon-documentation-adr` | `beacon-planner-documentation-adr` | planner | ADR/documentation clarity support |
| `beacon-doctor` | `beacon-governor-doctor` | governor | Context/environment repair |
| `beacon-debug-recovery` | `beacon-governor-debug-recovery` | governor | Blocker diagnosis and recovery |
| `beacon-status` | `beacon-governor-status` | governor | Board and state visibility |
| `beacon-help` | `beacon-governor-help` | governor | Next-step guidance |
| `beacon-archive` | `beacon-governor-archive` | governor | Historical truth isolation |
| `beacon-learn` | `beacon-governor-learn` | governor | Governed learning recall/audit/prune |
| `beacon-project-hooks` | `beacon-governor-hooks` | governor | Lifecycle hook contracts |
| `beacon-toolkit-automation` | `beacon-governor-automation` | governor | Scheduled automation assets |
| `beacon-toolkit-branch-governance` | `beacon-governor-branch` | governor | Branch/worktree governance |
| `beacon-toolkit-lighthouse` | `beacon-governor-lighthouse` | governor | Fast source/repo analysis |
| `beacon-toolkit-metadata` | `beacon-governor-metadata` | governor | Deterministic metadata tooling |
| `using-beacon` | remove or replace with `beacon-governor-router` | governor | Host-level router |

## Shared v1.6.0 Skill Preamble

Every v1.6.0 Beacon skill should include a generated shared preamble:

```text
Beacon v1.6.0 shared preamble:

1. Lake/ocean first: boil bounded lakes; split, mark, or defer oceans.
2. Search before building: read resolver-selected truth, source, evidence, and relevant memory before reasoning.
3. User sovereignty: Beacon recommends routes; the user decides whether to accept scope or upgrade queue items into truth/change.
4. No fake delivery: placeholder implementation, docs-only completion, fake runners, zero assertions, or placeholder evidence cannot count as closure.
5. Harness boundary: planner does not implement; generator does not judge its own completion; evaluator does not rewrite truth; governor does not become a main lifecycle stage.
```

This preamble should be generated into skill files, not hand-copied, to avoid drift.

## v1.6.0 Hard Gates

### Planner hard gate

Planner skills may write research/planning artifacts only. They cannot write code, frozen truth, QA verdicts, or release verdicts.

### Generator hard gate

Generator skills may produce truth or implementation artifacts only inside their authority. They cannot claim completion without evaluator evidence.

### Evaluator hard gate

Evaluator skills may pass/block/route based on evidence. They cannot repair implementation or rewrite truth as part of the verdict.

### Governor hard gate

Governor skills may repair tooling/state/projections. They cannot become a human mainline stage or silently promote support artifacts into truth.

## Rough Prompt Routing Contract

A rough user prompt must first be reduced to:

- user outcome;
- current source/truth/evidence refs;
- lake/ocean classification;
- truth gap;
- acceptance/test gap;
- implementation risk;
- verification risk;
- recommended harness route.

Example:

```text
"帮我分析这个功能怎么做"
-> beacon-planner-brainstorm
-> route: truth-package / implementation / qa / deep-analysis / friction-intake
```

## New Human-Facing Lifecycle

The user-facing lifecycle should be:

```text
plan
-> truth
-> generate
-> evaluate
-> release
```

The canonical package files behind `truth` remain:

```text
features/<slug>/truth.md
features/<slug>/tests.md
features/<slug>/tasks.md
features/<slug>/evidence.md
```

`prd`, `user-story`, and `test-case` should not appear as v1.6.0 primary skill categories.

## Migration Strategy

This is a breaking migration.

1. Create v1.6.0 feature package for `beacon-skill-harness-taxonomy-v160`.
2. Accept this brainstorm through `beacon-change` into formal truth.
3. Generate new skill directories with `beacon-<harness>-<function>` names.
4. Remove old host-visible skill directories from the v1.6.0 package.
5. Keep CLI compatibility only where needed for runtime transition, not as skill compatibility.
6. Update `command_catalog.py`, root `SKILL.md`, README, install docs, and skill discovery tests.
7. Add validation that no v1.6.0 skill name starts with deprecated role names such as `beacon-prd`, `beacon-user-story`, `beacon-test-case`, `beacon-brainstorm`, or `beacon-qa` without harness prefix.

## Acceptance Shape For Formal Truth

If promoted, the v1.6.0 truth package should include acceptance criteria:

- AC-001: All host-visible skills use `beacon-<harness>-<function>` names.
- AC-002: Each skill declares one harness role: planner, generator, evaluator, or governor.
- AC-003: Shared preamble is generated into every skill.
- AC-004: Legacy prd/user-story/test-case naming is removed from primary skill taxonomy.
- AC-005: Planner/generator/evaluator/governor hard gates are represented in skill text and tests.
- AC-006: Rough prompt routing produces route recommendation without writing truth or implementation.
- AC-007: No fake delivery policy is visible in generator/evaluator skills and enforced by QA/gate tests.
- AC-008: v1.5.2 feature package authority remains the truth model; generated JSON remains non-authoritative.

## Route Recommendation

Next route:

```bash
beacon change beacon-skill-harness-taxonomy-v160 --project . --version v1.5.2 --reason "accept v1.6.0 harness taxonomy and breaking skill rename proposal"
```

Then define the package truth under:

```text
docs/beacon/v1.5.2/features/beacon-skill-harness-taxonomy-v160/
```

Implementation should not begin until the package truth and tests are accepted.
