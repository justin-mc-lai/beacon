# Workspace Clean Manifest

`workspace-clean-manifest` defines how `beacon doctor verify-clean-workspace` classifies lifecycle artifacts before a stage may exit.

| artifact_role | Examples | Allowed action |
|---------------|----------|----------------|
| `canonical_truth` | `docs/beacon/<version>/features/<feature>/{truth,tests,tasks,evidence}.md` | commit |
| `formal_evidence` | `.beacon/evidence/implement/**`, `.beacon/evidence/test-results/**`, `.beacon/transactions/**`, `.beacon/{auto-test-status,coverage-summary,evidence-manifest,evidence-signature-chain,gate-report,release-gate-report}.json`, `.beacon/qa/status.json` | commit or promote |
| `machine_projection` | `docs/beacon/<version>/.machine/**`, `docs/beacon/<version>/execution/**` | commit or regenerate |
| `host_projection` | `.agents/**`, `.codex/**`, `.cursor/**`, `.trae/**`, `.windsurf/**` | local-only ignore/skip policy or deterministic surface-sync commit |
| `runtime_private` | `.beacon/traces/**`, `.beacon/state/**`, `.beacon/memory/**`, `.beacon/raw-command-log.jsonl` | ignore, quarantine, or promote redacted digest |
| `forbidden` | secrets, `.env*`, private keys | remove and rotate |

Formal evidence must be tracked, branch-carried, and hash-valid. Runtime-private data, including raw trace JSONL, cannot satisfy QA or release verdicts unless a redacted digest is promoted as formal evidence.
