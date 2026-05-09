---
name: beacon-qa
description: Use when the user wants to verify a Beacon feature, inspect new findings, improve coverage, or assess whether a feature is ready for release through Beacon's current v1.4.0 runtime surface.
---

# Beacon QA

This skill routes verification work through Beacon's `qa` surface.

The public command stays on the **`v1.4.0`** runtime line; docs and contracts live under `docs/beacon/v1.4.0/` unless your project pins another version.
Compatibility wrappers may preserve older runtime aliases, but QA truth and verdict interpretation should follow the `v1.4.0` docs line.

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

### Runner priority (prefer higher rows first)

When verifying a protected live surface in an environment where **multiple runners** may exist, prefer this order until one is **actually available and wired** on the host:

1. **`web-access`** — best fit for **reusing an existing local Chrome profile / logged-in session** when that integration is installed and healthy.
2. **`agent-browser`** (or equivalent **attached real browser** runner) — same family: **reuse real browser session** with agent-driven steps.
3. **`playwright-cli` with attach / CDP** — deterministic selectors + **connected browser** (session carried by the attached target).
4. **Bare `playwright test` / default Playwright runner** — acceptable for **anonymous** or **token-unlocked** staging; **last choice** for protected live URLs.

If **`browser-use`** (or similar) is only a **thin / placeholder adapter** in the current Beacon wiring, do **not** treat it as first-tier until it is proven end-to-end on the host.

### Default behavior: avoid idle failure loops

- **Do not** keep **bare Playwright** as the silent default for protected live URLs when an **attached-session** path exists or can be configured.
- If **no** attached / CDP / `storage_state` / cookie bridge is available for this run, **stop early** with an explicit outcome:
  - **`skip`** or **`blocked`**, not a timeout masked as **fail**.
  - Record a **short reason** (for example: `vercel_sso_redirect_no_session_bridge`).
- Prefer fixing **QA admission / runner selection** at the **`beacon qa` skill + runtime entry** so individual project specs do not each reimplement SSO detection and retries.

### Operator checklist (before long browser QA)

1. Confirm **URL class**: staging with public access vs **protected live**.
2. Confirm **session bridge**: attached Chrome, exported `storage_state`, or CI secret path — not “my laptop browser works” unless automation shares that session.
3. If protected and **no bridge**, **skip with reason** rather than running to timeout.

### Evidence expectation

When skipping or switching runners for protection, leave **machine-readable** notes (runner attempted, redirect observed, skip reason) so release-facing verdicts stay **evidence-first**, not ambiguous flakes.
