---
title: Beacon Skill Usage Rules
impact: HIGH
impactDescription: Keeps Beacon skill packaging aligned with the current human-facing wrapper model while preserving CLI compatibility and version-line discipline.
tags: beacon, skill, workflow, cli, packaging
---

# Beacon Skill Usage Rules

## Rule 1: `skills/beacon/SKILL.md` is the primary packaged wrapper

Beacon's canonical packaged skill entry is:

- `skills/beacon/SKILL.md`

That file is the primary human-facing wrapper for Beacon inside the packaged skill layout.

It should:

- define Beacon's stable identity
- define the default human-facing surface
- route users into the correct child skill
- preserve a small set of stable boundaries

It should not try to be the full runtime manual, release note, or operator runbook.

## Rule 2: Root `SKILL.md` is compatibility material, not product authority

Beacon may still keep a root-level `SKILL.md` for compatibility with older readers, tests, or mirrored installs.

If it exists:

- it is a compatibility mirror or auxiliary entry
- it must not redefine the product contract independently
- it should stay aligned with `skills/beacon/SKILL.md`

Product authority for the packaged skill surface now belongs to:

- `skills/beacon/SKILL.md`

## Rule 3: Main wrapper and child skills do not need a legacy fixed outline

Beacon no longer requires every top-level skill document to share one historical section template.

What must stay consistent is not a rigid outline, but a stable decision shape:

- identity or purpose
- boundary
- minimum entry surface
- routing logic when relevant
- examples
- cold-start anchors when the surface is likely to be misread

The main wrapper may be broader than child skills, but it should still follow this lighter packaging philosophy.

## Rule 4: CLI-first remains the default operator contract

Prefer the installed CLI in any project directory:

- `beacon ...`

Repo-local wrappers may exist for vendored skill packs, but they are compatibility details rather than the default human contract.

Bridge commands, wrapper exports, and host injection details may exist, but they should live in implementation/runtime references rather than in the primary packaged wrapper.

## Rule 5: Delivery truth remains under `docs/beacon/<version>/`

Skill packaging does not change Beacon's truth model:

- `docs/beacon/<version>/` remains versioned delivery truth
- `.beacon/` remains runtime state, evidence, or derived machine material unless a specific surface says otherwise

Skill docs may summarize where truth lives, but they must not redefine it.

## Rule 6: Distinguish default public line from active development lines

Beacon may be actively developing a newer version line before promoting it to the default public/runtime line.

That means:

- a newer line such as `v1.4.5` may have active PRD, user-story, execution, or QA materials
- the primary packaged skill may still point to an older default line such as `v1.4.3`
- skill text must not silently collapse these two states into one

When describing versions, be explicit about whether you mean:

- current packaged/public default line
- current active development line
- project-pinned local line

If those diverge, the wrapper should acknowledge the distinction instead of pretending there is only one active version fact.

## Rule 7: Runtime internals should be pushed down

The main packaged wrapper should not carry:

- detailed runtime evolution history
- long command matrices
- release proof checklists
- HUD/debug procedures
- metadata/branch governance operator walkthroughs
- full QA runbooks

Those belong in one of these places instead:

- versioned docs under `docs/beacon/<version>/`
- focused examples
- child skills
- runtime/reference documents

## Rule 8: QA and release claims must stay evidence-first

Skill text must not encourage:

- claiming progress without evidence truth
- treating unclassified full-suite output as a release pass
- treating unclassified full-suite output as a release blocker
- letting skill text override machine evidence from `doctor`, `qa`, or `release`

When Beacon itself evolves, test interpretation and release claims should stay tied to machine-readable evidence and explicit contract lanes.

## Rule 9: Examples should teach routing, not replace judgment

Examples inside skill docs should primarily help with:

- identifying the correct surface
- distinguishing similar surfaces
- clarifying common misroutes

Examples should not regrow into long procedural scripts unless the file is explicitly an example or runbook document.
