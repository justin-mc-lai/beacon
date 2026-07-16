# Machine JSON Convergence Source Map v1.5.1

- feature: `beacon-truth-map-center-and-package-cutover`
- status: `support-analysis`
- source skills: `beacon-brainstorm`, `beacon-source-driven`
- code map: `.understand-anything/graph-build-report.json`
- code map stats: `filesScanned=19995`, `nodes=25813`, `edges=27426`, `importEdges=1636`

## Conclusion

v1.5.1 needs an explicit machine JSON convergence lane.

The target is not “delete JSON”. The target is:

```text
Markdown truth selected by resolver -> generated machine JSON -> gate/runtime consumers
```

Machine JSON must be regenerated, hash-bound, and role-labeled. It must not become a second truth source.

## JSON Roles

| Role | Keep JSON? | Authority? | Examples |
|---|---:|---:|---|
| requirement-derived state | yes | no | `.machine/requirement/*.json`, `.machine/user-story/*.json`, `.machine/qa/*.json` |
| transaction evidence | yes | no | `.machine/change/*.json`, `.machine/execution/*transaction*.json` |
| gate input | yes | no | QA matrices, test contract index, requirement clarity report |
| runtime/process record | yes | no | `.beacon/auto-test-status.json`, `.beacon/qa/status.json`, `.jsonl` logs |
| JSON truth twin | no | no | Markdown-equivalent duplicate truth documents |

## Required Rebuild Entry

Add resolver-owned rebuild:

```bash
beacon truth-map rebuild-machine "<feature>" --project . --version v1.5.1 --json
beacon truth-map verify "<feature>" --project . --version v1.5.1 --strict --json
```

Expected generated classes:

- `.machine/requirement/<slug>.freeze-state.json`
- `.machine/requirement/feature-package-validation.json`
- `.machine/user-story/<slug>.json`
- `.machine/qa/<slug>.ac-test-matrix.json`
- `.machine/qa/<slug>.qa9-matrix.json`
- `.machine/qa/<slug>.story-scenario-map.json`
- `.machine/testing/test-contract-index.json`
- `.machine/execution/requirement-clarity-<slug>.json`

## Source-Anchored Change Points

| File | Change |
|---|---|
| `beacon/utils/truth_map.py` | New resolver, machine rebuild plan, source hash verification. |
| `beacon/cli_factory.py` | Register `truth-map` command group. |
| `beacon/commands/feature_package.py` | Route validation through resolver for v1.5.1+. |
| `beacon/utils/feature_package.py` | Add resolver/source hashes and machine JSON role labels; keep v1.5.0 behavior. |
| `beacon/utils/markdown_first_freeze.py` | Resolve truth paths via resolver and stop naming verification output as truth projection. |
| `beacon/utils/material_sync.py` | Rebuild machine user-story and QA artifacts from resolver-selected Markdown. |
| `beacon/commands/test_case.py` | Generate QA matrices from resolver/package test rows for v1.5.1+. |
| `beacon/utils/test_contract_governance.py` | Rebuild and verify index freshness against resolver hashes. |
| `beacon/utils/requirement_clarity.py` | Build diagnostic JSON from resolver-selected truth surfaces. |
| `beacon/utils/change_refreeze.py` | Add resolver machine rebuild before refreeze verification. |
| `beacon/utils/material_audit.py` | Fail closed on stale or non-resolver `.machine` JSON. |
| `beacon/utils/release_scorecard.py` | Consume machine JSON only after resolver freshness checks. |
| `beacon/utils/qa_feature.py` | Classify `.beacon/qa/*.json` as runtime/compatibility state, not truth. |

## Change-Refreeze Recommendation

This support analysis should be promoted into formal v1.5.1 truth via `beacon-change-refreeze` before implementation.

Minimum AC additions:

- resolver-owned machine JSON rebuild;
- generated JSON role labels;
- source hash freshness checks;
- stale `.machine` fail-closed verification;
- runtime/process JSON exempt from Markdown twin requirements.

