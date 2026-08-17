---
slug: beacon-host-subagent-lifecycle-keyword-v168
version: v1.6.8
---

# Evidence

| Kind | Ref |
|------|-----|
| pln-review | `docs/beacon/archive/v1.6.8/research/beacon-host-subagent-lifecycle-keyword-pln-review.md` |
| goal run | `pgr-ecefc5081a72` |
| UD lock | UD-SA-001..004 accepted 2026-07-20 |
| module | `beacon/utils/host_subagent_gate.py` |
| pack | `beacon/utils/host_subagent_pack.py` |
| doctor | `install-subagent-pack`, `verify-subagent-runtime --require-agents` |
| tests | `python3 -m pytest tests/test_v168_host_subagent_keyword.py -q` → **17 passed** |
| examples | `skills/beacon/examples/subagent-*-30s.md` |
| vendored codex | `.codex/agents/*.toml` (minimal 6) |
| vendored claude | `.claude/agents/*.md` (minimal 6) |
| v2 mirror | `docs/beacon/v2.0.0/features/loom-host-subagent-lifecycle-keyword-v200/` |

## Authority

- Test pass is **feature contract evidence**, not formal release GO.
- Subagent gate results are enhancement audit only; complete GoalRun still needs verifier + human release.
