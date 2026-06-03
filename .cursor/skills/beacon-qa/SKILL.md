---
name: beacon-qa
description: Use when the user wants to verify a Beacon feature, inspect new findings, improve coverage, or assess whether a feature is ready for release through Beacon's current v1.5.2 package-authoritative runtime surface.
---

# Beacon QA

## Overview

This skill routes verification work through Beacon's `qa` surface.

QA reads frozen requirement truth and implementation evidence, then evaluates layered acceptance proof instead of relying on one proxy score.
The active human-facing contract is aligned to the current `v1.5.2` package-authoritative docs line.
Compatibility reference: v1.4.7 docs line `docs/beacon/v1.4.7/`.
For v1.5.2 features, QA judgment must bind to resolver-selected `features/<slug>/{truth,tests,tasks,evidence}.md`. Legacy truth files may be rebuilt, absorbed, or archived, but they are not the normal QA authority.

## When to Use

- feature verification
- new findings and repair handoff review
- coverage improvement
- release confidence and QA iteration
- shared acceptance proof chain validation

## Boundary

- `qa` is the only public verification entry, but it does not rewrite frozen truth
- passing one proof layer does not imply release readiness
- browser/live-environment blockers must be recorded, not masked

## Workflow / Decision Loop

- continue in `qa` when implementation evidence exists and acceptance truth is frozen
- route back to `implement` for execution gaps
- route to `change` for truth drift
- route to `test-case` when coverage truth is insufficient
- route to `beacon-qa-evo-deep` when deep QA support analysis is needed for state machines, business flows, scenario combinations, permission boundaries, data consistency, cross-surface closure, or repeated QA round memory
- evaluate layered verdicts before handing off to `release`

## Common Rationalizations

- “有一层绿了，应该就算过。” -> 不允许；QA 是分层 verdict
- “环境挡住了，就当产品失败。” -> 不允许；需显式记录 runner/admission blocker
- “发现 acceptance 不对，直接在 QA 里改掉。” -> 不允许；truth drift 要回 `change`

## Red Flags

- implementation evidence 不足，却已经想做 release-ready 结论
- coverage truth 缺口被误当成 execution failure
- protected live surface 的 runner admission 不成立，却被记成产品 bug

## Verification

- layered QA proof 明确覆盖 `skill-contract / scenario-suite / trace-scorecard / real-project-proof`
- route explainability、learning visibility、guardrail behavior 在厚 human-facing decision surface 上可验证
- blocked/skip 情况带有明确 reason code 和 runner/evidence 说明

## Evidence Produced

- layered QA verdicts
- scenario results and findings
- release-facing proof status and repair route

## State Updated

- QA status and session state
- acceptance proof/read model projections

## Gate Impact

- can block `release`
- can route back to `implement`, `test-case`, or `change` depending on the failure family

## Inputs Contract

- `project-root`
- `version`
- `feature`
- implementation evidence
- frozen `features/<slug>/truth.md` and `features/<slug>/tests.md`
- conditionally triggered `prototype` handoff when applicable
- acceptance kit proof layers and gate context

## Decision Protocol

- Continue in `qa` when implementation evidence exists and acceptance truth is frozen.
- Route back to `implement` for execution gaps, to `change` for truth drift, or to `test-case` when coverage truth is insufficient.
- Treat `skill-contract`, `scenario-suite`, `trace-scorecard`, and `real-project-proof` as layered verdicts, not one proxy score.
- Verify route explainability, learning use visibility, and guardrail behavior when the feature claims a thicker human-facing decision surface.

## Anti-Inertia Notes

- `qa` is the only public verification entry, but it is not allowed to rewrite frozen truth silently.
- Passing one layer does not imply release readiness.
- Browser or live-environment blockers must be recorded explicitly, not masked as product failure.
- `qa` cannot rewrite frozen truth or override gate truth by itself.
- `beacon-qa-evo-deep` can produce routeable findings and release supplement input, but it cannot replace `beacon qa run` or produce QA/release verdicts.

## Learning Notes

- Reuse prior QA findings as hint for scenario prioritization.
- Learning can highlight likely failure modes, but it cannot convert blocked evidence into pass.
- Stale learning should bias toward re-verification, not trust.

## Backstop CLI

- `beacon qa ...`
- `beacon qa evo-deep "<feature>" --project . --version <version>` for deep QA support findings
- `beacon implement ...` for repair handoff
- `beacon release ...` only after layered evidence is sufficient

## v1.5.2 Package-Authoritative Read Order

For v1.5.2+ features, read the resolver output before consuming QA inputs:

```bash
beacon truth-map resolve <feature> --project . --version v1.5.2 --json
```

Then read `features/<slug>/{truth,tests,tasks,evidence}.md` from the resolved paths. Markdown package files are the requirement and coverage authority; resolver output and generated `.machine` JSON are generated state, not truth authority.

## v1.5.2 Evidence Index Quick Template

When writing `features/<slug>/evidence.md`, keep evidence as an index with explicit authority labels:

```markdown
# Evidence Index: Example Feature

## Evidence Index

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-deep | support_advisory | docs/beacon/v1.5.2/research/example.md | indexed | change |
| qa | qa_verdict | docs/beacon/v1.5.2/.machine/qa/example.qa9-matrix.json | linked | qa |
```

Do not add final verdict, gate truth, or release readiness fields to `evidence.md`.

## Supporting References

Use these lightweight references when verification needs a faster human-readable closure frame:

- `../references/qa-layer-checklist.md`
- `../references/release-blocker-taxonomy.md`
- `../references/state-machine-checklist.md`
- `../references/support-surface-routing-cheatsheet.md`

These references support layered judgment. They do not replace formal QA evidence.

## Protected live surfaces & browser runner admission

Bare Playwright (clean context) against **live URLs** behind **Vercel Deployment Protection / SSO** often redirects to **“Log in to Vercel”**. That is usually an **environment + auth model** signal, not an automatic product regression. Route browser QA so operators **do not burn time on predictable SSO redirects** and **do not record false failures**.

### When this applies

Treat the target as a **protected surface** when any of the following hold:

- Host matches **Vercel-style** deployment URLs (for example `*.vercel.app`) or project docs state **Deployment Protection** / **SSO**.
- First navigation lands on an **identity / login interstitial** (Vercel login, access gate, or SSO provider) instead of the app shell.
- The scenario requires a **human session** (logged-in dashboard, tenant data) but no **session bridge** is configured for automation.

### Runner admission principle

When verifying a protected live surface, prefer runners that can reuse a real authenticated browser session over clean-context runners.

- Attached-session or connected-browser paths rank above bare Playwright.
- Bare Playwright is acceptable for anonymous or token-unlocked staging, but it is a last choice for protected live URLs.
- Placeholder or thin adapters should not be treated as first-tier admission paths until proven end to end on the host.

### Default behavior: avoid idle failure loops

- **Do not** keep **bare Playwright** as the silent default for protected live URLs when an **attached-session** path exists or can be configured.
- If **no** attached / CDP / `storage_state` / cookie bridge is available for this run, **stop early** with an explicit outcome:
  - **`skip`** or **`blocked`**, not a timeout masked as **fail**.
  - Record a **short reason** (for example: `vercel_sso_redirect_no_session_bridge`).
- Prefer fixing **QA admission / runner selection** at the **`beacon qa` skill + runtime entry** so individual project specs do not each reimplement SSO detection and retries.

### Evidence expectation

When skipping or switching runners for protection, leave **machine-readable** notes (runner attempted, redirect observed, skip reason) so release-facing verdicts stay **evidence-first**, not ambiguous flakes.

## Examples

- 适用例：
  - “实现已经完成，现在要判断 acceptance proof 是否足够进入 release。”
  - “发现新问题了，想知道这是 execution gap、truth drift，还是 coverage gap。”
  - “这个 feature 的 verification 已经有一部分证据，但我不确定 layered verdict 是否真的够。”
- 不适用例：
  - “需求本身要重写，acceptance criteria 已经不成立。” -> 应回 `change` 或 requirement surfaces
  - “我只是想继续 challenge scope，还没到验证阶段。” -> 应优先去 guidance/support surface

## Cold-start anchors

- `qa` 判断的是证据是否足够，不是用来改写 frozen truth。
- 一层通过不代表整体 release-ready。
- 对 protected live surface，要先判断 runner admission 是否成立，再判断产品是否失败。
