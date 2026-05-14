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
> - `docs/beacon/global-boundaries.md`
> - `docs/beacon/v1.4.6/SUMMARY.md`

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

## 11. Final Research Verdict

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
