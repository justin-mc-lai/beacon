# Beacon v1.4.2 Project Skill QA Evolution Blueprint

## Status

- version: `v1.4.2`
- status: `freeze-ready`
- feature: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`

## Purpose

This blueprint defines how Beacon skill delivery should guide QA and test evolution for Beacon self-iteration without turning full-suite drift into ambiguous release status, and without letting protected live browser verification silently degrade into fake evidence or auth-noise failures.

## Skill Guidance Contract

Beacon skills must instruct agents to:

1. identify the target feature and docs version;
2. read `docs/beacon/global-boundaries.md` first;
3. read the frozen PRD, user-story, and test-case package;
4. inspect or request the Test Contract Index;
5. classify tests by lane before interpreting failures;
6. classify browser-capable targets as anonymous, session-backed, or protected-live before selecting a runner;
7. prefer `web-access -> attached agent-browser -> playwright attach/CDP -> bare Playwright` for protected surfaces when those paths are actually available;
8. run release-facing and current-runtime contract checks before release claims;
9. route blockers through existing support surfaces such as `doctor`, `qa`, `release`, and `help`.

## QA Lane Order

Skill guidance must preserve this QA sequence:

```text
user story / AC order
-> scenario divergence
-> current-round execution
-> evidence pack
-> coverage_current / coverage_gap
-> continue_decision
-> severe blocker stop_for_repair
-> repair handoff
-> beacon help resume
-> next QA round with test-case backfill
-> release guidance
```

## Lane Vocabulary

- `feature_release_facing`
- `current_runtime_contract`
- `generated_surface_sync`
- `compatibility_contract`
- `legacy_snapshot`
- `browser_runtime_admission`

## Agent Anti-Patterns

Agents must not:

- claim release readiness from unclassified full-suite output;
- treat transcript-only placeholder runner artifacts as browser QA closure;
- keep retrying protected live URLs with clean-context Playwright when no session bridge exists;
- treat planning-line docs as runtime release promotion;
- rewrite frozen truth from skill text;
- treat legacy snapshots as current release blockers by default;
- skip `beacon help` when a severe blocker requires resume guidance.

## Skill Surface Updates in Implementation Scope

The implementation should update:

- root `SKILL.md` delivery guidance;
- `skills/beacon/SKILL.md` command and QA guidance;
- `skills/beacon/references/usage-rules.md` with contract-lane test evolution rules;
- `skills/beacon-iteration-governance/SKILL.md` and workflow reference;
- managed context guidance when appropriate.
