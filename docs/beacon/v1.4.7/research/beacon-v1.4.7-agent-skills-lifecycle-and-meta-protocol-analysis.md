# Beacon v1.4.7 Research: Agent Skills, Gstack, Lifecycle Comparison, and Meta-Protocol Direction

> Date: 2026-05-14
> Scope: Beacon `v1.4.6` current runtime release line vs `addyosmani/agent-skills` and `garrytan/gstack`
> Status: Research only
> Source refs:
> - `docs/brainstorms/2026-05-13-beacon-brainstorm-beacon-v1.4.6-evolution-brainstorm-absorb-addyosmani-agent-skills-engineering-ph.md`
> - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/addyosmani-agent-skills/README.md`
> - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/addyosmani-agent-skills/docs/skill-anatomy.md`
> - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/addyosmani-agent-skills/skills/using-agent-skills/SKILL.md`
> - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/addyosmani-agent-skills/skills/spec-driven-development/SKILL.md`
> - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/addyosmani-agent-skills/skills/incremental-implementation/SKILL.md`
> - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/addyosmani-agent-skills/skills/code-review-and-quality/SKILL.md`
> - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack/README.md`
> - `/Users/apple/Developer/Personal/oss-sync/index/analysis/garrytan-gstack.md`
> - `/Users/apple/Developer/Personal/oss-sync/index/learning/garrytan-gstack.zh-CN.md`
> - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack/docs/skills.md`
> - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack/docs/ADDING_A_HOST.md`
> - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack/docs/OPENCLAW.md`
> - `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack/docs/REMOTE_BROWSER_ACCESS.md`
> - `skills/beacon/SKILL.md`
> - `skills/beacon/using-beacon/SKILL.md`
> - `skills/beacon/beacon-prd/SKILL.md`
> - `skills/beacon/beacon-implement/SKILL.md`
> - `skills/beacon/beacon-qa/SKILL.md`
> - `skills/beacon/beacon-release/SKILL.md`
> - `skills/beacon/beacon-toolkit-automation/SKILL.md`
> - `beacon/commands/automation.py`
> - `docs/beacon/global-boundaries.md`
> - `docs/beacon/v1.4.6/SUMMARY.md`
> - `docs/beacon/v1.4.6/prd/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
> - `docs/beacon/v1.4.6/execution/automation-jobs-runbook.md`
> - `beacon/utils/automation_feedback.py`
> - `beacon/utils/automation_queue.py`
> - `beacon/utils/qa_feature.py`

---

## 1. Research Goal

This note evaluates how Beacon should evolve after `v1.4.6` by comparing its current lifecycle and skill system against two influential open-source references:

- `addyosmani/agent-skills`
- `garrytan/gstack`

The question is not whether Beacon should copy that repository.

The real questions are:

> Which parts of these open-source systems strengthen Beacon's engineering surface without breaking Beacon's core identity as an evidence-first, truth-governed, release-gated workflow kernel?

---

## 2. Current High-Level Judgment

Current alignment between Beacon `v1.4.6` and the external references is best described as:

- structurally aligned on **skill anatomy**
- philosophically adjacent on **anti-rationalization** and **workflow discipline**
- intentionally different on **truth, gate, and release governance**
- still incomplete on **horizontal engineering skill breadth**
- still underdeveloped on **role-packaged engineering acceleration** compared with `gstack`

Practical judgment:

> Beacon `v1.4.6` has already absorbed the most valuable structural ideas from `agent-skills`, but it has not yet absorbed enough horizontal engineering skills or role-packaged acceleration patterns to feel like a complete engineering operating system.

### 2.1 Converged Brainstorm Verdict

This research can be reduced to one practical framing:

```text
agent-skills = engineering skill library
gstack       = specialist software factory
Beacon       = truth/evidence/governance kernel
```

Each system is solving a different primary problem:

- `agent-skills` optimizes for broad engineering skill coverage and simple phase-based discovery
- `gstack` optimizes for operator-perceived power, specialist packaging, and shipping velocity
- Beacon optimizes for requirement truth, anti-drift execution, audited QA, and release closure

The correct `v1.4.7` question is therefore not:

> How can Beacon become more like those systems?

It is:

> How can Beacon absorb their strongest engineering advantages while preserving Beacon's kernel identity?

### 2.2 Capability Trait Matrix

| Dimension | `agent-skills` | `gstack` | Beacon `v1.4.6` |
|---|---|---|---|
| Primary identity | Engineering skill library | Specialist software factory | Governed workflow kernel |
| Public shape | phase-oriented skill set | large specialist command surface | compact main chain + support surfaces |
| Requirement truth | light | light-medium | strong |
| Execution discipline | medium | strong | strong |
| QA/release governance | medium | medium | strongest |
| Human discoverability | high | very high | medium |
| Role packaging | low-medium | very high | medium |
| Host portability story | high | very high | medium-high |
| Anti-drift / canonical truth | low | low-medium | very high |
| Auditable memory / learning | low | medium | high |

### 2.3 Lifecycle Delta in One View

```text
agent-skills
define → plan → build → verify → review → ship

gstack
think → plan → build → review → test → ship → reflect

Beacon
prd → user-story → test-case → implement → qa → release
```

Interpretation:

- `agent-skills` is a broad engineering phase map
- `gstack` is a role-heavy operator sprint map
- Beacon is a truth-to-release closure map

Beacon should preserve its own map.
It should only add better translation layers and stronger support capabilities around it.

### 2.4 Root-Preservation Rule

For `v1.4.7`, Beacon should preserve these non-negotiables:

1. the main chain remains compact
2. support surfaces do not become lifecycle stages
3. truth stays canonical and versioned
4. QA and release stay evidence-backed and fail-closed
5. learning stays advisory, replayable, and auditable
6. skills default to philosophy + minimum tools + necessary facts, not rigid scripts

Any evolution idea that weakens one of these should be rejected even if it improves discoverability or short-term ergonomics.

### 2.5 Enhancement Rule

Under those constraints, Beacon should strengthen itself in four ways:

1. **be easier to enter**
   - stronger meta-protocol
   - clearer host routing
   - better lifecycle translation for outside users
2. **feel more complete**
   - more horizontal engineering support skills
   - more visible specialist overlays
3. **be easier to read**
   - lightweight references
   - clearer route explainability
   - more human-readable learning projections
4. **stay hard at the core**
   - no truth/gate dilution
   - no support-surface overreach
   - no expansion of the public main chain

---

## 3. Lifecycle Comparison

### 3.1 `agent-skills` lifecycle model

`agent-skills` presents a broad engineering lifecycle:

```text
define
→ plan
→ build
→ verify
→ review
→ ship
```

It is strong at:

- broad engineering discoverability
- cross-cutting engineering guidance
- direct skill invocation by development phase
- simple host adoption

### 3.2 `gstack` lifecycle model

`gstack` presents itself less as a compact skill library and more as a full software-factory command surface:

```text
think
→ plan
→ build
→ review
→ test
→ ship
→ reflect
```

But the more important framing is not phase naming.

It is a specialist-role system:

- office-hours
- CEO review
- eng review
- design review
- devex review
- review
- QA
- security
- release
- retro
- browser and session tools

It is strong at:

- role-packaged specialist entrypoints
- command-driven orchestration
- fast multi-host installation
- practical browser/session tooling
- making one operator feel like they have a virtual team

### 3.3 Beacon lifecycle model

Beacon's public main chain remains:

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

With `prototype` as a conditional insertion layer and `brainstorm / deep / ceo-review / design-review / help / status / doctor / archive` as support surfaces.

Beacon is strong at:

- requirement truth closure
- evidence-backed implementation and QA handoff
- audited release gating
- anti-drift delivery governance

### 3.4 Net comparison

`agent-skills` is better as a **general engineering phase model**.

`gstack` is better as a **high-energy specialist-role operating kit**.

Beacon is better as a **truth/evidence/governance closure model**.

That difference is real and should remain real.

Beacon should not erase it by becoming either:

- a generic phase-only workflow pack
- or a command-bloated specialist catalog

---

## 4. Where Beacon Already Aligns Well

### 4.1 Skill anatomy

Beacon `v1.4.6` has already converged toward a strong common skill skeleton:

- `Overview`
- `When to Use`
- `Common Rationalizations`
- `Red Flags`
- `Verification`
- `Inputs Contract`
- `Decision Protocol`
- `Anti-Inertia Notes`
- `Learning Notes`
- `Backstop CLI`
- `Examples`

This is a stronger and more governance-aware adaptation of the `agent-skills` anatomy pattern.

### 4.2 Anti-rationalization discipline

`agent-skills` is unusually strong at encoding agent excuses and rebuttals.

Beacon `v1.4.6` has already adopted this pattern into key public skills.

This is one of the most successful absorptions from external skill ecosystems.

### 4.3 Stage routing discipline

`agent-skills` uses `using-agent-skills` to route by development phase.

Beacon uses:

- `beacon` as human-facing wrapper
- `using-beacon` as router
- concrete surface skills for truth, execution, QA, and release

This is directionally correct and already host-usable.

### 4.4 Host-surface projection engineering

Beacon is ahead of `agent-skills` in one important dimension:

- multi-host projection into `.agents`, `.cursor`, `.trae`, `.windsurf`
- version-surface governance
- package/runtime/docs alignment

`agent-skills` is more portable as a repo.
Beacon is more governed as a runtime line.

### 4.5 Support-surface discipline vs `gstack`

Compared with `gstack`, Beacon is much more disciplined about one important thing:

- not every useful capability becomes a public lifecycle step
- support surfaces stay explicitly non-truth and non-gate by default
- route-back semantics are clearer

This makes Beacon slower to feel powerful, but safer against lifecycle sprawl.

---

## 5. Where Beacon Is Stronger Than `agent-skills`

These are not gaps. They are Beacon's differentiators and should remain intact.

### 5.1 Requirement truth closure

Beacon's:

```text
prd
→ user-story
→ test-case
→ acceptance
```

closure model is much stricter than the external pack's phase framing.

### 5.2 Gate and release governance

Beacon has:

- layered QA proof
- release blockers
- version truth
- promotion mechanics
- evidence manifests
- machine-readable state and transaction projections

`agent-skills` does not attempt this level of audited delivery closure.

### 5.3 Anti-drift delivery model

Beacon's canonical truth, projection, transaction consistency, and release proof chain are part of its product identity.

These are not optional add-ons.

### 5.4 Support-surface constitution

Beacon has become much clearer that support surfaces are:

- not truth sources
- not gate sources
- not new lifecycle stages

That boundary discipline is stronger than most open workflow skill packs.

---

## 6. Where Beacon Still Lags

### 6.1 Meta-skill clarity

`using-agent-skills` feels like a real meta-skill.

Beacon has both:

- `skills/beacon/SKILL.md`
- `skills/beacon/using-beacon/SKILL.md`

but the split is still not fully sharpened.

Current state:

- `beacon` is part wrapper, part routing constitution, part version anchor
- `using-beacon` is a router, but not yet a full host-first operating protocol

Needed direction:

- `beacon` should become the compact meta-protocol
- `using-beacon` should become the host-native route constitution

### 6.2 Horizontal engineering skill breadth

`agent-skills` covers many common engineering support functions that Beacon still lacks as first-class, reusable support skills.

Most notable missing families:

- context engineering
- source-driven development
- doubt-driven review
- security review
- performance review
- documentation/ADR discipline
- debug/recovery as a reusable cross-project support surface

### 6.3 Lightweight reference layer

Beacon's machine surface is strong.
Its thin human-friendly reference layer is still underbuilt.

`agent-skills` benefits from short checklists and reference docs that can be loaded on demand.

Beacon needs the equivalent without inflating the main skill files or turning references into duplicated truth.

### 6.4 Cross-project engineering portability

Beacon is very strong for:

- requirement freeze
- anti-drift delivery
- high-assurance QA/release closure

It is still less complete as a generic engineering operating kit for projects that need:

- architecture reviews
- official-doc-grounded implementation
- security/performance/documentation guidance
- context packaging guidance

without necessarily entering Beacon's full truth chain.

### 6.5 Role-packaged acceleration compared with `gstack`

`gstack` feels powerful because it packages expertise into memorable public roles and slash commands:

- CEO
- eng manager
- designer
- DX lead
- reviewer
- QA lead
- CSO
- release engineer

Beacon has parts of this in support surfaces such as:

- `beacon-ceo-review`
- `beacon-design-review`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`
- `beacon-real-project-validation`

but the overall system still feels more like a governed kernel than an operator-visible virtual team.

That is acceptable, but it means Beacon currently loses on:

- first-session emotional clarity
- operator-perceived capability breadth
- direct discoverability of specialized engineering help

---

## 7. What Beacon Should Not Copy

Beacon must keep its own philosophy line.

It should not mechanically copy `agent-skills` in the following areas.

### 7.1 Do not turn support skills into new stages

Beacon's global boundary is already correct:

> support surfaces can strengthen judgment, but they must not expand the main chain

### 7.2 Do not regress into full operation scripts by default

Beacon's adopted skill philosophy is:

```text
strategy philosophy
→ minimum complete tools
→ necessary facts
```

This must remain the default.

Only strong gate and fail-closed surfaces should carry stronger procedural constraints.

### 7.3 Do not import external skill packs as runtime prerequisites

`agent-skills` is useful as a reference source, not as Beacon's default dependency plane.

The same is true for `gstack`:

- useful as a methodology and surface-design reference
- not suitable as Beacon's default runtime dependency model

### 7.4 Do not let learning become truth or gate

Beacon's memory and learning system must stay:

- replayable
- auditable
- advisory

not truth-defining.

### 7.5 Do not copy `gstack` command sprawl directly

`gstack` derives power from a large public command catalog.

Beacon should not adopt that pattern wholesale.

Reasons:

- it would overload the human surface
- it would weaken the 6-stage main chain boundary
- it would push support capabilities toward becoming de facto public stages
- it would blur which surfaces are truth, execution, verification, or gate

Beacon should learn from `gstack`'s packaging energy, not from its total public surface area.

---

## 8. Recommended v1.4.7 Direction

### 8.1 Theme

Recommended `v1.4.7` theme:

> meta-protocol hardening + horizontal engineering support skills + lightweight references

This keeps Beacon's main chain stable while making the overall system more complete and more reusable outside pure requirement-freeze scenarios.

### 8.2 Stream A: converge `beacon` into a true meta-protocol

`skills/beacon/SKILL.md` should be reduced to the irreducible operating constitution:

- how to classify the current decision surface
- which principles always hold
- when to route back
- when support surfaces remain advisory only

It should stop feeling like a broad wrapper page and start feeling like a compact protocol.

### 8.3 Stream B: strengthen `using-beacon` into host-native route constitution

`using-beacon` should become the explicit host-side route selector:

- truth vs execution vs verification vs gate vs support
- route reasoning
- support-surface fallback handling
- explicit return-to-`change` behavior when support outputs alter accepted scope

Suggested division of responsibility:

- `beacon` = meta-protocol
- `using-beacon` = route constitution

### 8.4 Stream C: add horizontal support skill family

High-value candidates:

- `beacon-context-engineering`
- `beacon-source-driven`
- `beacon-doubt-review`
- `beacon-security-review`
- `beacon-performance-review`
- `beacon-documentation-adr`
- `beacon-debug-recovery`

All of these should remain support skills, not public lifecycle stages.

Their job is to:

- challenge
- verify
- explain
- strengthen

not to author canonical truth or release verdicts by themselves.

These skills are the correct place to absorb the most reusable parts of both external references:

- `agent-skills` contributes reusable engineering disciplines
- `gstack` contributes stronger operator-facing packaging and role clarity

### 8.5 Stream D: add lightweight reference pages

Suggested thin references:

- `requirement-closure-checklist.md`
- `research-closure-checklist.md`
- `business-flow-checklist.md`
- `state-machine-checklist.md`
- `freeze-readiness-checklist.md`
- `qa-layer-checklist.md`
- `release-blocker-taxonomy.md`
- `support-surface-routing-cheatsheet.md`

Rules:

- reference pages are not canonical truth
- they are loaded on demand
- they improve human readability and reuse
- they must not duplicate versioned requirement sources

### 8.6 Stream E: add lifecycle mapping, not lifecycle expansion

Beacon should explicitly document a mapping from external engineering phase models into its own model.

For example:

```text
idea/spec/plan
→ brainstorm/prd/user-story/test-case

build
→ implement

verify/review
→ qa + support review skills

ship
→ release
```

This helps absorb external skill ecosystems without changing Beacon's main chain.

### 8.7 Stream F: borrow `gstack`'s specialist energy without copying its surface count

What to borrow:

- clear specialist framing
- memorable operator intent
- strong "who is helping me now?" packaging
- host installation portability
- browser/session support as explicit capability layers

What not to borrow:

- unchecked command multiplication
- treating every specialist as a public first-class main workflow entry
- mixing product ideation, coding, QA, deployment, and retros into one equally weighted flat catalog

Beacon should expose fewer public names, but each one should feel more intentional.

That suggests a pattern like:

- keep public surfaces compact
- let a few support skills own internal specialist modes
- use light references and role overlays instead of multiplying top-level commands

---

## 9. `gstack`-Specific Borrowing Map

### 9.1 What `gstack` is uniquely good at

`gstack` is not just a skill repo.

It is a practical operator environment for solo or small-team high-throughput building:

- many named specialist roles
- strong quick-start ergonomics
- explicit install flow for many hosts
- browser/session tooling
- review/QA/release as tangible operator rituals
- visible "software factory" framing

The most reusable lessons for Beacon are not its exact commands.

They are its packaging choices.

### 9.2 Best borrowing candidates for Beacon

1. **Host portability as a first-class concern**
   - `gstack` treats multi-host installation and agent support as core product surface.
   - Beacon already projects into multiple hosts, but the story is more infrastructural than operator-readable.
   - Borrowing direction: make Beacon's host model easier to explain and easier to discover from `using-beacon`.

2. **Specialist framing for support skills**
   - `gstack` makes each command feel like a specific specialist.
   - Borrowing direction: support skills such as `ceo-review`, `design-review`, future `security-review`, `performance-review`, and `doubt-review` should feel like crisp specialist overlays, not generic helper prompts.

3. **Session/browser/tool reality**
   - `gstack` invests heavily in practical browser access, cookies, session continuity, and remote-host support.
   - Borrowing direction: Beacon should continue strengthening browser/session admission and operator-facing explanation inside `qa`, `doctor`, and future support references, without turning browser tooling into a new lifecycle.

4. **Operator-visible workflow confidence**
   - `gstack` excels at making the user feel that the system has a complete bench of helpers.
   - Borrowing direction: Beacon should raise perceived completeness through support skill family + references, not through lifecycle expansion.

5. **Retrospective and learning surfaces**
   - `gstack` includes `learn` and `retro` as explicit improvement loops.
   - Beacon already has governed learning, but it is more infrastructure-heavy than operator-facing.
   - Borrowing direction: keep Beacon learning auditable, but improve human readability of what Beacon learned and how it affects route suggestions.

### 9.3 Things Beacon should explicitly avoid copying from `gstack`

- giant flat public command lists
- operator dependence on remembering dozens of command names
- weak distinction between advisory surfaces and authoritative surfaces
- treating specialist roles as equivalent to truth or release stages

### 9.4 Net takeaway from `gstack`

Concise verdict:

> `gstack` demonstrates how much perceived power comes from role-packaged specialist surfaces, host portability, and practical operator tooling. Beacon should borrow that packaging discipline, but retain its smaller public chain, stronger truth boundaries, and explicit truth/gate separation.

---

## 10. Smallest Useful v1.4.7 Slice

The smallest version of this evolution that is still worth shipping:

1. Rewrite `skills/beacon/SKILL.md` as a clearer meta-protocol
2. Tighten `skills/beacon/using-beacon/SKILL.md` as route constitution
3. Add 3 support skills first:
   - `beacon-context-engineering`
   - `beacon-source-driven`
   - `beacon-doubt-review`
4. Add 6 lightweight reference pages
5. Wire key main skills to those references:
   - `beacon-prd`
   - `beacon-implement`
   - `beacon-qa`
   - `beacon-release`
   - `using-beacon`

This would materially improve Beacon's engineering completeness without expanding the lifecycle or weakening truth governance.

---

## 11. Automation Closure-Loop Audit

This section narrows the automation discussion to one question only:

> How much of Beacon's automation direction is already implemented, what runtime contract is still missing, and what is the smallest next slice worth building?

The target framing remains:

> Beacon automation should stay a host-scheduled support plane and evolve from a QA feedback helper into a truth-preserving closure-state routing loop.

### 11.1 Already Implemented Automation Contract

Beacon already has a real public automation toolkit surface.
This is not hypothetical anymore.

#### 11.1.1 Public CLI contract

The following commands already exist on the public surface:

```text
beacon automation capabilities
beacon automation init
beacon automation validate-queue
beacon automation summarize-qa
beacon automation update-queue
beacon automation build-summary
```

Current meaning:

- `capabilities`
  - reports the supported host-scheduled automation capability plane
- `init`
  - generates project-local automation scaffold assets
- `validate-queue`
  - validates the canonical automation queue contract
- `summarize-qa`
  - writes the canonical QA feedback ledger used by automation jobs
- `update-queue`
  - applies frozen queue update rules after QA feedback
- `build-summary`
  - emits the shared automation summary payload used by notifications and operator summaries

#### 11.1.2 Canonical artifact contract

The following automation artifacts are already frozen enough to count as implemented contract:

- queue
  - `automation/beacon-automation-queue.json`
- feedback ledger
  - `.beacon/automation/qa-feedback-ledger.json`
- shared run summaries
  - `.beacon/automation-runs/<layer>/qa-summary-*.json`
- job wrappers
  - `automation/jobs/`
- executor / host scaffold
  - `automation/codex/`
  - `automation/launchd/`
  - `automation/README.md`

#### 11.1.3 Queue governance contract

Beacon already implements a narrow queue-governance rule set:

- passed QA candidate can leave the QA queue
- repair-needed candidate can enter implement queue
- queue updates are derived from canonical QA feedback, not per-project shell invention

This means Beacon is already beyond "example scripts".
It already owns a real automation truth layer for:

- queue shape
- feedback ledger shape
- summary shape
- scaffold shape

#### 11.1.4 Human-facing route contract

From the `using-beacon` side, the intended route is already clear enough to state:

- enter `beacon-toolkit-automation` when the operator is maintaining the recurring scheduler toolkit itself
- return to `beacon-qa`, `beacon-implement`, `beacon-change`, or `beacon-release` for authoritative work

Current operator sentence:

> Beacon timed automation is a recurring closure-maintenance shell around the main chain, not a replacement for the main chain.

#### 11.1.5 Current implementation verdict

Implemented today:

- host-scheduled automation toolkit
- project-local scaffold generation
- queue validation
- QA feedback ledger generation
- queue update from QA feedback
- shared automation summary generation
- explicit host-vs-Beacon boundary

Not yet implemented today:

- authoritative closure-state loop runtime
- bounded multi-round repair orchestration
- explicit deep/refreeze/release automation routing kernel

### 11.2 Missing Runtime Contract

The main gap is no longer "Beacon lacks automation commands".

The main gap is:

> Beacon does not yet have the runtime contract that turns those commands into a governed multi-round closure loop.

#### 11.2.1 Missing state model

Beacon still lacks a formal automation runtime model for:

- `closure_state`
  - `active`
  - `blocked`
  - `release_ready`
  - `closed`
  - `human_escalation_required`
- `next_route`
  - `qa`
  - `implement`
  - `support_review`
  - `change_refreeze`
  - `release`
  - `human`
- `terminal_signal`
  - stage-specific exit reason that explains why the loop is moving

Without this split, automation remains a queue helper rather than a closure router.

#### 11.2.2 Missing multi-round inheritance contract

Beacon still lacks a frozen contract for repeated QA/repair rounds:

- no formal `round_number`
- no formal `previous_round_ref`
- no formal active issue register
- no formal inheritance rule for:
  - unresolved stop reasons
  - accepted fixes
  - targeted rerun hints
  - latest implement outcome
  - latest deep verdict
  - truth hash
  - implementation evidence hash

Current result:

- the system can schedule and summarize
- but it cannot yet explain a multi-round closure loop as a first-class runtime object

#### 11.2.3 Missing support-review / deep route contract

The research direction assumes:

- repeated structural failure should route to support review
- `deep` should remain a support executor, not a new stage

That route is still not frozen as runtime contract.

Missing pieces:

- machine-side `support_review` route label
- clear `deep` executor admission inside automation
- `deep_exit_no_truth_delta`
- `deep_route_implement`
- `deep_route_truth_refreeze`
- `deep_repeat_cap_reached`

#### 11.2.4 Missing truth-recompile gate after refreeze

The biggest correctness gap is still:

- if automation finds requirement-meaning delta
- it must not jump from refreeze directly back to implement

Still missing:

- `truth_recompiled_pending`
- explicit regeneration gate for:
  - `user-story`
  - `test-case`
  - `requirement_clarity`
  - `freeze`

Without this, automation can still drift into mixed truth.

#### 11.2.5 Missing scenario discovery contract

The research line requires a split between:

- `closure_supplement`
- `promotion_candidate`

This runtime contract does not yet exist in a formal way.

Still missing:

- `requirement_meaning_delta=true|false`
- non-canonical scenario discovery sink
- explicit promotion route into `change/refreeze`

#### 11.2.6 Missing concurrency contract

This is the most operationally dangerous missing layer.

Still missing:

- feature execution lease
- queue revision
- compare-and-swap write semantics
- single-flight per feature
- stale-writer rejection
- notification dedupe key contract

Until these exist, any serious timed automation rollout can race or fork state under real host schedulers.

#### 11.2.7 Missing promotion contract

Beacon still lacks a frozen runtime predicate for:

- when a feature exits the QA loop automatically
- when it re-enters implement
- when it must escalate to human
- when release can consume the converged closure state

This is the difference between:

- queue-governed support automation

and:

- a real closure-state runtime

### 11.3 Smallest Next Implementation Slice

The next slice should not try to implement the whole research line.

The right next slice is:

> add the minimum runtime contract that lets automation route repeated QA and implement repair safely, without yet trying to automate deep/refreeze/release end to end.

#### 11.3.1 Scope of the smallest useful slice

Implement only these five things:

1. **Closure-state envelope**
   - add a machine-readable runtime envelope for:
     - `closure_state`
     - `next_route`
     - `terminal_signal`
     - `round_number`
     - `previous_round_ref`
2. **Active issue register**
   - define the inherited per-round payload
   - do not inherit full prior artifacts inline
3. **Authoritative QA exit predicates**
   - at minimum:
     - `qa_exit_ready_for_release`
     - `qa_route_implement_repair`
     - `qa_route_human_escalation`
4. **Implement re-entry contract**
   - at minimum:
     - `implement_exit_to_qa`
     - `implement_route_human_escalation`
5. **Queue safety primitives**
   - add:
     - `queue_revision`
     - feature-level execution lease
     - stale-writer rejection

This slice is intentionally narrow.

It does **not** yet need to automate:

- `deep` routing
- truth recompilation after refreeze
- scenario promotion
- final release orchestration

Those should come only after the first closure-state envelope is stable.

#### 11.3.2 Why this is the right smallest slice

This slice gives Beacon the first real step from:

- QA feedback helper

to:

- bounded repair-loop runtime

without triggering the biggest risks:

- shadow truth
- pseudo-stage expansion
- state explosion
- queue corruption

#### 11.3.3 Suggested user-story payload for the next slice

Minimum next user-story set:

1. As an operator, I want QA to emit an authoritative closure-state envelope so automation can distinguish release-ready, repair-needed, and human-escalation outcomes.
2. As an operator, I want implement repair rounds to inherit only the active issue register so repeated rounds stay convergent and auditable.
3. As an operator, I want queue writes to carry queue revision and feature lease metadata so concurrent schedulers cannot fork the same feature.

#### 11.3.4 Suggested test-case payload for the next slice

Minimum next test set:

1. QA `ready_for_release` writes `closure_state=release_ready` and exits queue
2. QA `stop_for_repair` writes `next_route=implement` and creates Round 1 repair envelope
3. Implement repair writes `implement_exit_to_qa` and preserves inherited active issue register
4. stale queue writer is rejected when queue revision no longer matches
5. second scheduler cannot claim a feature that already has an active execution lease

#### 11.3.5 Net implementation verdict

Current Beacon automation is already good enough to be called:

- a real scheduler toolkit contract

It is not yet good enough to be called:

- a truth-preserving closure-state runtime

So the next version should not market "full self-iterating automation".

It should ship the first bounded runtime kernel:

> closure-state envelope + active issue register + QA/implement loop contract + queue safety primitives

That is the smallest slice that materially moves the architecture forward without breaking Beacon's lightweight boundary model.

### 11.4 CEO Feasibility Verdict

The ambitious end-state remains directionally valid:

> Beacon automation may eventually evolve into a closure-maintenance runtime that can carry bounded multi-round repair work without drifting requirement truth.

But the CEO-level feasibility verdict is stricter than the architecture direction:

> the full Automation Closure-Loop is strategically valid as a research north star, but it is not yet an operationally valid near-term product promise.

This distinction matters.

The current Beacon runtime is strong enough to support:

- host-scheduled automation toolkit
- repeated QA feedback collection
- narrow queue-governance updates
- bounded future evolution toward a repair-loop kernel

The current Beacon runtime is **not** yet strong enough to safely support:

- autonomous end-to-end closure routing across QA, implement, deep, refreeze, and release
- self-directed truth-pressure handling when requirement meaning changes
- unattended convergence claims under real scheduler concurrency
- night-long iterative automation that can continue acting without strong terminal signals and human escalation boundaries

#### 11.4.1 CEO challenge verdict

Recommended verdict:

- direction: `hold as north star`
- near-term implementation scope: `reduce`
- operator promise: do **not** market or frame this as full autonomous closure-loop

Beacon should explicitly say:

- today it has a real automation toolkit
- next it may ship a bounded closure-state kernel
- it does not yet provide a full self-iterating closure runtime

#### 11.4.2 Why the full promise is too early

The proposal becomes dangerous when it assumes the world stays orderly.

By default, a CEO review should assume the opposite:

- QA signals will sometimes be partial, stale, or locally green while requirement closure is still false
- repeated implement rounds will sometimes improve evidence while also increasing hidden drift risk
- `deep` may discover either implementation defects or requirement-meaning pressure, and those are not the same class of event
- host schedulers will eventually race, duplicate, resume late, or replay stale work
- automation that appears elegant in principle may create expensive morning-after triage burden

In other words:

> the current story works mainly when reality remains cooperative; that is not a sufficient basis for Beacon to promise full closure-loop autonomy.

#### 11.4.3 Main explosion risks

The major risks are not cosmetic.
They strike Beacon's core boundary model.

1. `truth_freeze_destabilization`
   - if automation keeps discovering scenario gaps or requirement pressure, it will naturally tend to keep pushing for "better truth"
   - without a strict refreeze and truth-recompile barrier, support automation can silently bend frozen truth
2. `stage_boundary_sprawl`
   - if automation owns cross-stage routing from QA through implement, deep, refreeze, and release, it stops being a support plane and starts becoming a shadow lifecycle
3. `false_closure_signal`
   - local QA pass, local rerun success, or "no new issue found" is not the same as requirement closure or release readiness
4. `operator_cost_underpricing`
   - the hidden cost sits in stale state cleanup, duplicate notifications, replay reasoning, escalation recovery, and explaining why the loop moved
5. `buried_landmine`
   - the worst failure mode is not visible red failure
   - it is a system that looks converged after many night rounds while actually preserving mixed truth or stale assumptions
6. `too_smooth_path`
   - the proposal assumes that defects, scenario discovery, and requirement deltas can be separated cleanly enough for unattended routing
   - that separation is still not strong enough in the current runtime

#### 11.4.4 Hard preconditions before attempting the full loop

Beacon should not attempt the full end-state until all of the following are first-class runtime contract, not research prose:

1. authoritative closure-state envelope
   - `closure_state`
   - `next_route`
   - `terminal_signal`
   - `round_number`
   - `previous_round_ref`
2. queue and scheduler safety
   - `queue_revision`
   - feature execution lease
   - compare-and-swap semantics
   - stale-writer rejection
   - single-flight per feature
3. truth-pressure separation
   - explicit split between implementation defect, closure supplement, and requirement-meaning delta
   - fail-closed route to `change/refreeze` when requirement meaning is under pressure
4. truth recompile barrier
   - `truth_recompiled_pending`
   - explicit regenerated downstream package before any resumed implementation
5. stage terminal signals
   - QA, implement, support review, and release all need explicit stop conditions rather than "keep going until nothing obvious remains"
6. bounded human escalation model
   - the runtime must know when to stop optimizing and hand the problem back to a human operator

#### 11.4.5 CEO operating stance for v1.4.7

The correct product stance for `v1.4.7` is:

- keep the full Automation Closure-Loop as research direction
- do not freeze it as an implementation promise
- implement only the bounded kernel that improves repair-loop safety without granting automation truth-moving authority

That means the allowed implementation line remains:

> closure-state envelope + active issue register + QA/implement bounded loop + queue safety primitives

And the explicitly disallowed near-term line remains:

- automatic `deep` routing as an always-on continuation engine
- automatic truth refreeze or requirement promotion
- automatic scenario promotion into canonical requirement materials
- automatic release orchestration based on accumulated local pass signals

#### 11.4.6 Final CEO conclusion

The full Automation Closure-Loop is feasible only under a much stronger runtime contract than Beacon currently has.

So the right executive conclusion is:

> pursue the vision, but refuse the premature promise.

Beacon may automate repeated repair work.
It must not yet automate ownership of evolving truth.

---

## 13. Final Research Verdict

Beacon should not try to become `agent-skills`.

Beacon should also not try to become `gstack`.

Beacon should remain:

- evidence-first
- truth-governed
- anti-drift
- release-auditable

But Beacon should evolve by absorbing the missing strengths from `agent-skills`:

- better meta-skill clarity
- broader horizontal engineering support skills
- lightweight reusable references
- cleaner lifecycle mapping for host operators

And it should evolve by absorbing selective strengths from `gstack`:

- stronger specialist packaging for support skills
- clearer multi-host/operator story
- more visible browser/session/tooling capability surfaces
- more legible human-facing learning and retrospection overlays

Concise verdict:

> `agent-skills` behaves like a high-quality engineering skills library. `gstack` behaves like a high-energy specialist software factory. Beacon `v1.4.6` behaves like a governed workflow kernel. `v1.4.7` should preserve Beacon's kernel identity while filling the horizontal engineering skill gaps and support-surface packaging gaps that make those external systems feel more complete.
