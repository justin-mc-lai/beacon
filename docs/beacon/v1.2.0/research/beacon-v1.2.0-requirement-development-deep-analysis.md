# Research: Beacon v1.2.0 requirement development deep analysis

**Date**: 2026-04-08  
**Version target**: `v1.2.0`  
**Intent**: synthesize the current `.research` deep analyses and the accumulated `docs/beacon/research` studies into one clear requirement-development direction for Beacon `v1.2.0`.

**Primary inputs**:

- `.research/beacon-architecture-deep-analysis-2026-04-08.md`
- `.research/beacon-command-simplification-evolution-plan-2026-04-08.md`
- `.research/beacon-project-skill-workflow-deep-analysis-2026-04-08.md`
- `docs/beacon/research/*.md`

---

## 1. Executive conclusion

The current `v1.2.0` materials correctly identify important problems:

1. command complexity
2. project-skill workflow friction
3. prototype / requirement anchoring

But taken together with the broader research set, they still need one stronger product-level constraint:

> `v1.2.0` must be defined around the `PRD → user-story → QA` anchor chain, not around a loose collection of UX, skill, and prototype improvements.

This changes the framing of `v1.2.0`:

- **not**: "command simplification + project skill workflow + prototype anchoring"
- **but**: "make the `PRD/story/QA` chain easier to operate, easier to adapt per-project, and harder to drift"

That distinction matters because Beacon's strongest product truth is not its CLI breadth, not its learning plane, and not its prototype layer.
Its strongest product truth is:

```text
PRD
→ user-story
→ QA
→ implementation evidence
→ review / gate / release
```

Everything in `v1.2.0` should strengthen this chain.

---

## 2. What the current research already proves

## 2.1 From architecture deep analysis

The architecture analysis establishes:

- Beacon `v1.1.12` is already production-grade in the mainline requirement/evidence kernel
- the four-layer split is real:
  1. Requirement kernel
  2. Delivery evidence kernel
  3. Project execution adapters
  4. Learning plane
- the strongest capabilities are already concentrated around:
  - requirement materials
  - implementation handoff
  - QA / review / gate

This means `v1.2.0` should **not** behave like a greenfield reinvention.
It should behave like a selective hardening and simplification line.

## 2.2 From command simplification evolution plan

The command simplification plan correctly diagnoses:

- too many top-level commands
- mental overhead for new users
- overlapping support/labs/bridge surfaces

But command simplification is only strategically valuable if it improves:

- discoverability of the mainline
- `PRD/story/QA` operator fluency
- stage-aware next-step reliability

If simplification is treated as a separate UX beautification effort, it will drift.

## 2.3 From project-skill workflow deep analysis

The project-skill analysis correctly sees that Beacon needs:

- better project-specific skill composition
- stronger adapter templates
- better project onboarding and binding

But this also must stay subordinate to the mainline:

- project skills are not the product center
- they are a means to protect project-local verification and delivery truth

This is a very important product-boundary rule for `v1.2.0`.

---

## 3. What the broader research set adds

The documents under `docs/beacon/research/` sharpen the requirement direction significantly.

## 3.1 `LLM Wiki` study

This study adds a critical point:

- Beacon should not only produce stage outputs
- it should eventually support a compiled knowledge layer

But that knowledge layer is not free-form.
It should help the mainline:

```text
PRD
→ story
→ QA
→ evidence
```

not replace it.

## 3.2 `awesome-design-md` + `autoagent` study

This study adds two critical ideas:

- package important capability into standard asset bundles
- keep self-iteration bounded to tiny policy surfaces

This means `v1.2.0` should likely produce more stable bundles and fewer ad hoc operator decisions.

## 3.3 `mempalace` study

This study adds an important caution:

- do not summarize away reasoning too early
- keep important raw context where it matters

For `v1.2.0`, this means:

- PRD tradeoffs
- story decomposition logic
- QA/gate blockage reasoning

should stay easier to trace.

## 3.4 completeness matrix + remediation roadmap

These two documents provide the strongest constraint:

- the mainline is already strong
- advanced layers are less mature
- `v1.2.0` should therefore prioritize:
  1. mainline hardening
  2. complexity reduction
  3. assetization
  4. bounded evolution

This sequencing should override any temptation to expand horizontally.

---

## 4. Reframing `v1.2.0`

## 4.1 Correct product statement

The current `v1.2.0` direction should be reframed as:

> Beacon `v1.2.0` is the line that makes the `PRD → user-story → QA` chain easier to operate, easier to adapt per-project, and harder to drift.

That one sentence should govern every requirement.

## 4.2 Incorrect product statements

These should be actively avoided:

- "the command simplification release"
- "the project skill release"
- "the prototype anchoring release"
- "the UX cleanup release"

Those can be workstreams, but not the product center.

---

## 5. The right `v1.2.0` structure

`v1.2.0` should be structured as one mainline objective with three subordinate workstreams.

## Main objective

### Mainline objective

Harden and simplify the `PRD → user-story → QA → evidence → closure` chain.

## Workstream A

### A. Command-surface simplification for mainline fluency

Goal:

- reduce external command complexity
- improve operator discoverability
- keep the mainline obvious

Allowed outcomes:

- command grouping
- command hiding
- routing improvements
- better `help` / `status`

Not the goal:

- expanding command count
- building a new command taxonomy detached from the mainline

## Workstream B

### B. Project-skill workflow hardening

Goal:

- make project-local skill workflows easier to discover, bind, and verify

Allowed outcomes:

- skill discoverability
- adapter/profile starter templates
- project-aware binding improvements

Not the goal:

- moving project execution into Beacon core

## Workstream C

### C. Prototype anchoring as a subordinate contract

Goal:

- ensure prototype outputs remain traceable to PRD/story contracts

Allowed outcomes:

- bidirectional requirement/prototype checks
- UI module contract templates
- stronger prototype-to-story traceability

Not the goal:

- allowing prototype/design governance to become the product center

---

## 6. Requirement priorities for `v1.2.0`

## P0 — must define the anchor contract

`v1.2.0` should explicitly define:

1. PRD-to-story traceability requirements
2. story-to-AC traceability requirements
3. AC-to-test-case traceability requirements
4. scenario-family coverage expectations
5. evidence expectations for closure

Without this, command simplification and project-skill improvements will optimize the wrong thing.

## P1 — simplify the command surface around the anchor

The simplification effort should be judged against one metric:

> Does it make the mainline easier to learn and use correctly?

That means:

- core/mainline commands stay obvious
- advanced surfaces move behind explicit disclosure
- `help` becomes a stage-aware command router

## P1 — make project skills support the anchor

Project skills should be evaluated by:

- do they help a project execute the right verify/delivery path?
- do they protect required evidence and required cases?

Not by:

- how many workflows they can theoretically express

## P2 — bundle the mainline

Before adding more advanced evolution logic, `v1.2.0` should package:

- story-QA baseline bundles
- implementation-plan bundles
- review/gate scorecard bundles

This is the bridge between powerful internals and usable product outputs.

## P3 — use prototype anchoring to reduce drift

Prototype anchoring belongs here, not at the center.

It is valuable because it reduces:

- UI drift from PRD/story
- story drift from implemented UX

but it is still subordinate to the delivery chain.

---

## 7. Deep assessment of the current `v1.2.0` docs

The current `think / user-story / prd / test-case` line for `beacon-v1.2.0-command-simplification-and-project-skill-workflow` is directionally strong but still too wide.

### Strengths

1. it already identifies real operator pain
2. it preserves the Beacon mainline in spirit
3. it respects project adapter boundaries

### Weaknesses

1. it treats three concerns as co-equal
2. it does not explicitly elevate `PRD/story/QA` as the single anchor
3. it risks prototype work gaining equal status with command and skill work
4. it risks turning `v1.2.0` into a broad enhancement release instead of a sharp product line

### Required correction

`v1.2.0` docs should explicitly state:

```text
Mainline anchor:
PRD → story → QA

Workstream support:
- command simplification
- project-skill workflow
- prototype anchoring
```

That single hierarchy change would make the whole line much more coherent.

---

## 8. Imported directives from the April 8 deep analyses

### 8.1 Architecture deep analysis → selective hardening rule

The architecture deep analysis adds an important constraint:

- Beacon `v1.1.12` mainline is already production-grade enough to protect
- `v1.2.0` should therefore harden and clarify that mainline, not re-architect Beacon from scratch
- explicit agent orchestration, large-module decomposition, and full testing-visibility upgrades remain follow-on work, not the product center of this line

### 8.2 Command simplification plan → operator contract

The command simplification research sharpens `v1.2.0` in three ways:

1. mainline commands remain stable
2. `ask` / `help` become the smart-entry surfaces
3. advanced/labs surfaces should be progressively disclosed instead of competing with the mainline by default

This means `v1.2.0` needs a command-surface blueprint, not only a generic “simplify commands” statement.

### 8.3 Project-skill workflow analysis → bounded discovery rule

The project-skill deep analysis contributes:

- template-library direction
- memory-aware recommendation inputs
- preview-first `skill discover` semantics
- stronger forward/reverse prototype-anchor expectations

It also suggests a broader `beacon discover` idea, but the correct v1.2.0 requirement decision is to keep that generic codebase-analysis direction **outside** the frozen core scope for this line.

### 8.4 Closure implication

After importing the three deep analyses, the requirement package should explicitly contain:

- research convergence docs
- command-surface simplification blueprint
- project-skill execution blueprint
- source-architecture surface
- machine-freeze baseline for the current feature line

---

## 9. Recommended `v1.2.0` deliverables

The strongest `v1.2.0` package should include:

### 9.1 Required analysis/contract docs

1. `PRD-story-QA anchor contract`
2. `story-QA baseline bundle contract`
3. `coverage scorecard contract`
4. architecture-readiness research convergence
5. command-surface simplification blueprint
6. project-skill workflow deep-analysis convergence

### 9.2 Main implementation documents

1. command simplification blueprint
2. project-skill discovery/binding blueprint
3. prototype anchor contract
4. source-architecture surface

### 9.3 Optional follow-up docs

1. command migration guide
2. project-skill starter pack guide
3. story-QA baseline examples

---

## 10. What should be cut or deferred

To keep `v1.2.0` sharp, the following should be cut or explicitly deferred:

1. any memory-plane expansion not directly serving `PRD/story/QA`
2. any learning-plane evolution that is not benchmarked against story/QA outcomes
3. any new top-level commands that do not simplify the mainline
4. any project-skill abstraction that starts pulling execution logic into Beacon core
5. any prototype/design expansion that is not directly traceability-oriented
6. generic codebase-wide `beacon discover` as a core frozen deliverable
7. agent-platform rewrites or large module decomposition as freeze prerequisites

---

## 11. Final recommendation

The best way to understand `v1.2.0` is this:

> It should be the release that re-centers Beacon around `PRD → user-story → QA`, then reshapes the command surface, project-skill workflow, and prototype validation so that this chain becomes easier to operate and harder to drift.

If that framing is held, `v1.2.0` can become a strong line.
If not, it risks becoming a broad but blurry enhancement bundle.
