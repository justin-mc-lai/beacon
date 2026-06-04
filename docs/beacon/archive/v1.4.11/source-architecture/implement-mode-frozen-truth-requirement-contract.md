# Source Architecture: Implement Mode Frozen Truth Requirement

- version: `v1.4.11`
- feature: `implement-mode-frozen-truth-requirement-contract`

## Affected Sources

### Skill surface (human-facing)
- `skills/beacon/beacon-implement/SKILL.md` — Decision Protocol, Inputs Contract
- `skills/beacon/beacon-implement/references/implement-single.md` — single mode truth binding
- `skills/beacon/beacon-implement/references/implement-team.md` — team mode truth injection
- `skills/beacon/beacon-implement/references/implement-ralph.md` — ralph mode baseline verification
- `.agents/skills/beacon-implement/SKILL.md` — synced copy

### Python guardrail (enforcement)
- `beacon/commands/implement.py` — dev-run preflight, handoff gate
- Gate: technical_review_contract, requirement_clarity (preflight only)

### Truth sources (read by implement)
- `PRODUCT.md` — project-level product truth
- `DESIGN.md` — project-level design truth
- `docs/beacon/<version>/prd/<feature>.md`
- `docs/beacon/<version>/user-story/<feature>.md`
- `docs/beacon/<version>/qa/test-cases/<feature>.md`

## Current Gap

```
Preflight:  ✅ file existence (gate)
Execution:  ❌ AC verification (blank)
Handoff:    ❌ AC coverage matrix (blank)
```

## Proposed Injection Points

### Skill surface (no Python change)
- `beacon-implement/SKILL.md` Decision Protocol: add AC matrix mandate
- `implement-single.md`: add "Self-verify: mark pass/partial/blocked per AC"
- `implement-team.md`: add "Per-worker AC subset injection" + "Aggregated AC matrix"
- `implement-ralph.md`: add "Verify baseline hash before routing next action"

### Python guardrail (optional, for fail-closed)
- `beacon implement dev-run` handoff: scan AC coverage matrix existence
- DESIGN.md token checker: regex-scan changed files for hardcoded hex vs DESIGN.md token
