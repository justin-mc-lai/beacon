---
slug: beacon-qa-chrome-extension-e2e-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.4/features/beacon-qa-chrome-extension-e2e-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：QA Chrome Extension E2E v1.6.4

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/v1.6.4/features/beacon-qa-chrome-extension-e2e-v164/truth.md |
| tests.md | test_truth | docs/beacon/v1.6.4/features/beacon-qa-chrome-extension-e2e-v164/tests.md |
| tasks.md | requirement_truth | docs/beacon/v1.6.4/features/beacon-qa-chrome-extension-e2e-v164/tasks.md |

## Truth 阶段证据（已发生）

| Round | 产物 | 结果 |
|-------|------|------|
| R1 truth.define + acceptance | truth.md | draft |
| R1 truth.coverage | tests.md | draft |

## Source refs

- Chrome 官方 e2e 文档：https://developer.chrome.com/docs/extensions/how-to/test/end-to-end-testing
- program feature-graph：docs/beacon/v1.6.4/programs/beacon-qa-capability-hardening-v164/feature-graph.md (Phase 1 source parity inventory)

## Diagnostic evidence（QA capability gap baseline）

- `BROWSER_RUNNER_REGISTRY` 无 extension runner；`default_browser_runner_command('playwright')` 返回空
- `grep -rnE "loadExtension|--load-extension|extension_id|chrome-extension://|action.openPopup|service_worker.*target" beacon/` → 零命中
- `BROWSER_EVIDENCE_AXES` = (function/ui/ux/compatibility/session/state_data)，无 extension 维度

## Implementation/QA evidence

由下游 `beacon-gen-implement` / `beacon-eval-qa` 阶段填充（truth 阶段不留 placeholder）。
