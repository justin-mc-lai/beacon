# Beacon OSS Parity Matrix Draft

**Version**: v1.6.0
**Status**: research / support_advisory
**Authority**: runtime_evidence_only=false, requirement_truth=false
**Sources**: oss-sync canonical mirrors + Beacon v1.5.2/v1.6.0 contracts

---

## Canonical Mirror Roots (oss-sync)

| Project | Path | Analysis | Learning |
|---------|------|----------|----------|
| OpenSpec | `automation/autoresearch/openspec` | complete | `fission-ai-openspec.zh-CN.md` |
| Spec Kit | `pm/pm/spec-kit` | pending | `github-spec-kit.zh-CN.md` |
| gstack | `agents/agent-skills/gstack` | complete | `garrytan-gstack.zh-CN.md` |
| compound-engineering-plugin | `agents/agent-skills/compound-engineering-plugin` | complete | `everyinc-compound-engineering-plugin.zh-CN.md` |

Inventory resolver: `beacon/utils/oss_sync_inventory.py` → `build_source_capability_inventory()`.

---

## Capability Parity Matrix

| Dimension | OpenSpec | Spec Kit | gstack | Compound | Beacon v1.5.2 | Beacon v1.6.0 |
|-----------|----------|----------|--------|----------|---------------|---------------|
| Truth carrier | `openspec/specs` + `changes/` | `specs/00X-*.md` | skill + CLI ops | plugin skills | `features/<slug>/*.md` | + harness taxonomy |
| State machine audit | directory-as-state (strong) | phase gate (medium) | ops loop (weak) | review loop (medium) | event+log+gate | + planner state model |
| Delta merge | `/opsx:sync` | phase advance | N/A | plan/deepen | refreeze chain | same |
| Cross-IDE | 25+ slash tools | Copilot-first | multi-host | Claude/Cursor plugin | 5 hosts | pln/gen/eval/gov |
| Light onboarding | `/opsx:new` | constitution 3-file | README run | plugin install | prd bootstrap | gov-router |
| Multi-reviewer | verify report | N/A | devex-review | persona catalog | support surfaces | internal reviewer lanes |
| Finding synthesis | CRITICAL/WARNING | N/A | N/A | synthesis+autofix | QA scorecard | compound-parity artifact |
| PR/diff scope | change scope | N/A | worktree | PR scope | git-alignment | diff_scope (degraded) |
| Dev ops closure | N/A | N/A | deploy/canary/ship | release automation | implement runner | gstack dry-run |
| Release gate | soft archive | hard phase | ship evidence | testing-addressed | scorecard (strong) | same |
| Auto source inventory | N/A | N/A | N/A | N/A | none | **oss_sync_inventory** |

---

## Beacon Advantages

- Single feature-package truth via truth-map resolver
- Evidence-first QA + release scorecard + gate chain
- Version lineage + archive governance
- Self-bootstrap via iteration-governance + real-project-validation

## Beacon Gaps (deferral ledger)

| Gap | Status | Route |
|-----|--------|-------|
| OpenSpec directory state machine | deferred | research / v1.7+ |
| Spec Kit lightweight onboarding | deferred | `beacon-gen-truth-init` enhancement |
| gstack ship/canary parity | deferred | `beacon-gen-implement` + gstack runner |
| Compound PR API integration | deferred | out of v1.6.0 scope per truth.md |
| Spec Kit oss-sync analysis | pending | `manage_oss_sync.py analyze github/spec-kit` |

---

## Skill Eval Reference Prompt

> 参考 Compound、OpenSpec、Spec Kit、gstack，完整复刻同等能力，不要 MVP，并保持 Beacon 真相唯一交付。

Benchmark: skill-eval-kit TC-005, TC-026..TC-033.
