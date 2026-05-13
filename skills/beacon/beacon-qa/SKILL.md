---
name: beacon-qa
description: Use when the user wants to verify a Beacon feature, inspect new findings, improve coverage, or assess whether a feature is ready for release through Beacon's current v1.4.3 runtime surface.
---

# Beacon QA

This skill routes verification work through Beacon's `qa` surface.

The public command stays on the **`v1.4.3`** runtime line; docs and contracts live under `docs/beacon/v1.4.3/` unless your project pins another version.
Compatibility wrappers may preserve older runtime aliases, but QA truth and verdict interpretation should follow the `v1.4.3` docs line.

`Beacon Acceptance Kit v1` is the shared QA verdict base. QA should read and project:

- `skill-contract`
- `scenario-suite`
- `trace-scorecard`
- `real-project-proof`

Use the layered verdicts as the release-facing truth, not a single score.

## Use for

- feature verification
- new findings and repair handoff review
- coverage improvement
- release confidence and QA iteration
- shared acceptance proof chain validation

## Operator rule

Prefer:

- `beacon qa ...`
- optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh qa ...`

Keep `qa-team`, learning, and auto research hidden behind the public `qa` surface unless the user explicitly asks for internals.

## Inputs Contract

- `project-root`
- `version`
- `feature`
- implementation evidence
- frozen `prd / user-story / test-case`
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

## Learning Notes

- Reuse prior QA findings as hint for scenario prioritization.
- Learning can highlight likely failure modes, but it cannot convert blocked evidence into pass.
- Stale learning should bias toward re-verification, not trust.

## Backstop CLI

- `beacon qa ...`
- `beacon implement ...` for repair handoff
- `beacon release ...` only after layered evidence is sufficient

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
