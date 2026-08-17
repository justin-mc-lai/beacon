# Domain-FSM Truth Checklist (P2)

Non-canonical support reference for the **truth** harness and plan→truth transition.

Use when freezing requirement material that includes lifecycle, domain events, or multi-state flows. Complements `beacon-truth` / `loom-truth` progressive skills.

## When domain_fsm is required

Treat domain FSM as **required** when any of:

- payment / auth / permission / security language appears
- multi-status workflows (order, ticket, approval, subscription)
- user said 状态机 / FSM / parity of source states
- `done_when` includes `domain_fsm` (goal default)

## Empty-castle forbid

- [ ] Every promised behavior is anchored to a source, interface, or explicit UD — no invented APIs
- [ ] States have enter/exit/illegal transitions listed or deliberately out of scope
- [ ] “Happy path only” is **not** enough when high_risk plan_artifact is true
- [ ] plan_artifact `deep_want` + options inform freeze; plan does **not** write frozen truth itself

## Legal / illegal walks

- [ ] At least one legal walk from initial → terminal success
- [ ] At least one illegal or rejection walk (deny, timeout, cancel, refund as applicable)
- [ ] Visibility rules: who can see which state (role/tenant)
- [ ] Idempotency / replay for events that can fire twice

## Completeness before freeze

- [ ] AC table is testable (not slogans)
- [ ] Non-goals prevent scope creep into implement
- [ ] Soft plan→truth hint reviewed (`plan_to_truth_hint` on goal run) — soft, not hard-stop
- [ ] After freeze, route is implement or qa — not open brainstorming as “still exploring”

## Related

- `skills/beacon/references/state-machine-checklist.md`
- `skills/beacon/references/freeze-readiness-checklist.md`
- `skills/beacon/references/requirement-closure-checklist.md`
- Runtime: `beacon.utils.plan_artifact.plan_to_truth_gate` (soft)
