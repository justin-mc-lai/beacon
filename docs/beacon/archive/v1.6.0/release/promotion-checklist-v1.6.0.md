# v1.6.0 Runtime Promotion Checklist

**Version**: v1.6.0
**Status**: planning_only → promotion candidate
**Role**: release-facing promotion gate for harness-first skill migration

---

## Phase 0 — Docs Convergence (prerequisite)

- [x] Root `SKILL.md` aligned to runtime `v1.5.2`
- [x] `skills/beacon/metadata.json` aligned to skill surface `v1.6.0`
- [x] `tests/test_docs_current_contract.py` uses `docs/beacon/archive/` historical paths
- [x] `skills/beacon-iteration-governance` aligned to `v1.5.2`
- [x] `iteration-governance quick --version v1.5.2` passes (`iter-gov-20260610111437`)
- [ ] `iteration-governance full --version v1.6.0` passes (post-promotion)

## Phase 1 — v1.6.0 Feature Package Closure

| Feature | QA | Evidence |
|---------|-----|----------|
| `beacon-skill-harness-taxonomy-v160` | required | `features/.../evidence.md` |
| `beacon-pln-review-compound-parity-v160` | required | `features/.../evidence.md` |
| `beacon-pln-review-runtime-multi-agent-v160` | required | `features/.../evidence.md` |
| `beacon-pln-review-intent-parity-state-machine-v160` | required | `features/.../evidence.md` |
| `beacon-loop-native-runner-and-automation-retirement` | pending (implement gate) | `features/.../evidence.md` |

- [x] All 5 features: `beacon validate-feature-package <slug> --version v1.6.0 --json` pass
- [ ] All 5 features: `beacon qa run` accepted (4/5 have `qa-acceptance-*.json`; `beacon-loop-native-runner-and-automation-retirement` blocked on implement evidence + technical review)
- [x] Skill eval benchmark TC-026..TC-033 pass (pytest + skill-eval state green)

## Phase 2 — OSS Parity Integration

- [x] `beacon/utils/oss_sync_inventory.py` landed
- [x] `planner_review_runtime` delegates to oss-sync inventory
- [x] `tests/test_oss_sync_inventory.py` pass
- [x] oss-sync learning: `github-spec-kit.zh-CN.md`, `everyinc-compound-engineering-plugin.zh-CN.md`
- [ ] `manage_oss_sync.py analyze github/spec-kit` complete (Spec Kit analysis pending)

## Phase 3 — Release Preflight (before runtime switch)

```bash
beacon doctor verify-materials --project-root . --version v1.6.0 --json
beacon release check v1.6.0 --project . --json
beacon real-project-validation --project-root . --version v1.6.0 --feature "beacon-skill-harness-taxonomy-v160" --json
beacon gate check release --project-root . --version v1.6.0 --json
beacon skill package verify --project-root . --version v1.6.0 --package-root skills/beacon --json
```

- [ ] `release check v1.6.0` no blockers
- [ ] Version aggregate projection includes all QA-accepted features
- [ ] Agent surface verify strict pass (cursor/codex/claude)

## Phase 4 — Runtime Truth Switch (final)

Only after Phase 0–3 green:

1. `beacon/version-truth.json`: `v1.6.0` → `current_runtime_release`; `v1.5.2` → `historical_release`
2. `beacon/__init__.py`: `__toolkit_version__ = "v1.6.0"`
3. `pyproject.toml`: `version = "1.6.0"`
4. `README.md` current release line → v1.6.0
5. Post-release: `beacon-post-release-local-install` hook green

## Hard Gate

> v1.6.0 becomes runtime release only when iteration-governance full is green, all feature packages are QA-accepted, and `release check v1.6.0` passes without repair-only blockers.
