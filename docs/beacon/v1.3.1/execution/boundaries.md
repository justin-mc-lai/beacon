# Workflow Boundaries (v1.3.1)

- feature: Beacon v1.3.1 human-AI cocreation cognitive load reduction
- workflow_status: accepted supplement line / human surface simplification
- guardrail: reduce human-visible command burden without weakening formal delivery, freeze, QA, or release truth

---

## Mainline boundary

`v1.3.1` defines a stricter human-facing mainline than previous lines:

```text
PRD
→ user-story
→ test-case
→ implement
→ QA
→ release
```

This is the **human primary chain**.

Everything else is subordinate.

Additional rule:

> the chain runs per feature package, even when multiple feature packages coexist inside the same version line.

## Human vs machine boundary

### Human primary commands

Human operators should only be expected to hold these commands in long-term working memory:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

These six commands form the canonical human delivery loop.

### Human auxiliary commands

These commands remain allowed, but should only surface when the user is blocked, lost, or maintaining package integrity:

- `help`
- `status`
- `doctor`

They are **support surfaces**, not the primary loop.

### Host-visible public skills

The host-visible skill layer must mirror the same human boundary:

- umbrella:
  - `using-beacon`
- primary:
  - `beacon-prd`
  - `beacon-user-story`
  - `beacon-test-case`
  - `beacon-implement`
  - `beacon-qa`
  - `beacon-release`
- support:
  - `beacon-help`
  - `beacon-status`
  - `beacon-doctor`

Rule:

> if a host-visible skill does not fit this 6+3 human boundary, it should not be public.

### Hidden / machine-first commands

These commands or lanes may continue to exist, but should not become the normal human operating burden:

- `brainstorm` as a standalone long-term surface
- `team`
- `implement-team`
- `qa-team`
- learning / auto research orchestration
- low-level runtime/debug/repair lanes

Rule:

> machine collaboration may stay rich, but human cognition must stay narrow.

## Feature-package boundary

`v1.3.1` makes the following boundary explicit:

- one version line may contain multiple feature packages
- one feature package owns exactly one primary `prd`
- that `prd` maps to its own `user-story`
- that `user-story` maps to its own `test-case`

The binding key is the shared `feature slug`.

Allowed:

- multiple `prd/*.md` files under the same version
- multiple `user-story/*.md` files under the same version
- multiple `qa/test-cases/*.md` files under the same version
- parallel implementation/QA per feature package

Forbidden:

- assuming one version must collapse into one PRD
- mixing one feature's PRD with another feature's story/test package
- releasing a version without knowing which feature packages actually landed

## Brainstorm boundary

`brainstorm` must remain a valid Beacon capability, but it should no longer behave like a separate human stage that competes with the primary chain.

Allowed:

- embed `brainstorm` into `prd -> user-story`
- use it to surface open questions, business ambiguity, and missing assumptions
- collapse its output into formal PRD / user-story materials

Forbidden:

- leaving brainstorm as an endlessly separate pre-work lane
- requiring humans to maintain a second long-lived "brainstorm state" outside the formal package
- freezing PRD / user-story while brainstorm-level ambiguity remains unresolved

## Freeze boundary

`v1.3.1` introduces a hard requirement:

If the requirement package still contains:

- missing points
- unclear points
- question-mark points
- unclarified points
- requirement ambiguity

then `prd` / `user-story` must not freeze.

Formal interpretation:

```text
ambiguity present
→ freeze blocked
```

Before freeze, Beacon must be able to point to a concrete unresolved-items set such as:

- open questions
- missing decisions
- ambiguous requirements
- scope gaps

## Technical review boundary

Each version must complete a technical review before formal implementation begins.

This technical review is not optional commentary. It is a deterministic implementation contract.

At minimum it must declare:

- target git branch
- branch prefix / base branch
- worktree usage
- worktree root
- environment isolation strategy
- service directories in scope
- service ownership boundary

If the project is monorepo / multi-service, the review must additionally declare:

- gateway / BFF / downstream service relationships
- which services are writable
- which services are read-only references
- which repos or service directories participate in branch/worktree enforcement

## Implement boundary

For humans:

- `implement` is the only primary implementation command

For Beacon runtime:

- internal team mode remains allowed
- internal role decomposition remains allowed
- internal learning or research support remains allowed

But formal implementation must not start until:

1. freeze gate is satisfied
2. technical review contract is present
3. branch/worktree/service scope is deterministic

## QA boundary

For humans:

- `qa` is the only primary QA command

For Beacon runtime:

- `qa-team` remains allowed
- verifier / repair-handoff-writer remain allowed
- learning / auto research remain allowed

But every QA round must satisfy:

- new finding, or
- new coverage, or
- new boundary clarity, or
- new repair handoff

QA that does not improve one of these should not be treated as meaningful progress.

## Material sync boundary

When Beacon runtime upgrades but a real project still points at older docs materials:

- the operator must be able to sync by explicit docs version
- the operator should not manually rebuild `.machine/user-story` and `.machine/qa`

Required operator surface:

```bash
beacon doctor sync-materials --project-root <root> --version <docs-version> --all-features
```

## Change-document boundary

`implementation-summary` and `technical-implementation` are not enough on their own.

`v1.3.1` requires an independent change surface so the delivery truth is readable without diff archaeology.

Required outputs:

- feature-level `change/<feature-slug>.md`
- version-level `change/<version>.md`

Required classification:

- added
- removed
- fixed
- retained / unchanged where necessary for context

Rule:

> release truth should reference explicit change documents, not implicit memory of implementation archives.

## CLI simplification boundary

Extreme simplification does not mean deleting necessary control surfaces.

Allowed:

- reducing the default human-visible command set
- hiding machine-only lanes behind `implement` / `qa`
- using `help/status/doctor` only when needed

Forbidden:

- deleting freeze/doctor integrity logic
- removing technical review obligations
- making recovery impossible
- claiming "simple" while silently dropping formal delivery rigor
