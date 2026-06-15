# Beacon v1.6.1 Summary

v1.6.1 extends v1.6.0 with **version-level ocean/lake program harness plan** capability: decompose sea-scope utterances (e.g. full OSS parity) into a **book-shaped program truth** (catalog, outline, feature lakes), boil each lake via existing Truth Freeze Intent Loop, and close the loop on **beacon change** with plan review and governed refreeze.

Lifecycle language unchanged:

```text
plan -> truth -> generate -> evaluate -> release
```

Package-authoritative truth:

```text
truth-map resolver -> features/<slug>/{truth,tests,tasks,evidence}.md
```

Program support artifacts (planner advisory until promoted):

```text
docs/beacon/<version>/programs/<program-slug>/
```

Primary v1.6.1 features:

- `beacon-harness-program-plan-v161` — program plan loop, **dual-mode skill triad** (`beacon-pln-program` + auto/interactive), `beacon plan start` CLI, feature graph, program freeze gate, change-intent closure, TIG-aligned governance (**frozen R2**)
- `beacon-agent-eval-v161` — **Agent Eval full parity（R2：全 skill live）**：统一 `beacon eval` 分数面、**37 条 live skill matrix**、composite 0–100 scorecard（`runtime_evidence_only`，不替代 formal QA/release）（**frozen R2**）

Upstream frozen dependencies (v1.6.0):

- `beacon-skill-harness-taxonomy-v160`
- `beacon-pln-review-intent-parity-state-machine-v160`
- `beacon-pln-review-compound-parity-v160`
- `beacon-truth-integrity-gates-v160`
- `beacon-loop-goal-closed-loop-orchestrator`
