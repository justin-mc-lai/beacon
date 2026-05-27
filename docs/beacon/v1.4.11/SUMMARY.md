# Beacon v1.4.11 总览

## 状态

- Version line: `v1.4.11`
- Current status: `release_check_passed_with_ceo_challenge_warning`
- 初始调研主题：Markdown-first 投影权威清理与旧版兼容退场。
- Carry-forward 调研主题：承接 v1.4.10 中已形成 feature 候选但未纳入当前 aggregate package，或仍停留在 research/backlog 的方向。
- 减负重构主题：保留 Beacon 全功能能力，将固定流程下沉为工具 / gate / schema / test，并将 legacy / fallback / compat 历史包袱显式登记和逐步退场。
- Design/prototype 重构主题：旧版 prototype 能力已在 v1.4.11 中重建为 Beacon design 能力，产品 / 设计真相、accepted UI/UX writeback、设计子 skill、上游开源设计能力 admission 一并纳入当前版本。
- 当前版本聚合范围：9 个 frozen requirement package 均已完成 implementation / QA acceptance，版本 change 聚合材料已对齐到 9 个 feature，release check 已通过；当前尚未执行 release 发布或 post-release install。

## 调研输入

- `docs/beacon/v1.4.11/research/authority-vocabulary-and-baseline-inventory-contract.md`
- `docs/beacon/v1.4.11/research/friction-cd1809c3220a-ui-ux-design-truth-writeback-incident.md`
- `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- `docs/beacon/v1.4.11/research/v1410-feature-carry-forward-intake.md`
- `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`
- `docs/beacon/v1.4.11/research/memory-intent-historical-migration-boundary-contract.md`
- `docs/beacon/v1.4.11/research/test-directory-marker-relayering-contract.md`
- `docs/beacon/v1.4.11/research/beacon-design-human-subskills-closure-contract.md`

## Frozen Feature Packages

```text
authority-vocabulary-and-baseline-inventory-contract
compatibility-registry-and-command-catalog-contract
qa-prd-legacy-mirror-retirement-contract
implement-package-legacy-loader-retirement-contract
beacon-design-product-prototype-rebuild-contract
browser-fallback-deterministic-command-contract
memory-intent-historical-migration-boundary-contract
test-directory-marker-relayering-contract
beacon-design-human-subskills-closure-contract
```

## 版本聚合证据

- Version change markdown: `docs/beacon/v1.4.11/change/v1.4.11.md`
- Version change machine payload: `docs/beacon/v1.4.11/.machine/change/v1.4.11.json`
- Feature count: `9`
- QA acceptance briefs:
  - `docs/beacon/v1.4.11/execution/qa-acceptance-brief-authority-vocabulary-and-baseline-inventory-contract.md`
  - `docs/beacon/v1.4.11/execution/qa-acceptance-brief-compatibility-registry-and-command-catalog-contract.md`
  - `docs/beacon/v1.4.11/execution/qa-acceptance-brief-qa-prd-legacy-mirror-retirement-contract.md`
  - `docs/beacon/v1.4.11/execution/qa-acceptance-brief-implement-package-legacy-loader-retirement-contract.md`
  - `docs/beacon/v1.4.11/execution/qa-acceptance-brief-beacon-design-product-prototype-rebuild-contract.md`
  - `docs/beacon/v1.4.11/execution/qa-acceptance-brief-browser-fallback-deterministic-command-contract.md`
  - `docs/beacon/v1.4.11/execution/qa-acceptance-brief-memory-intent-historical-migration-boundary-contract.md`
  - `docs/beacon/v1.4.11/execution/qa-acceptance-brief-test-directory-marker-relayering-contract.md`
  - `docs/beacon/v1.4.11/execution/qa-acceptance-brief-beacon-design-human-subskills-closure-contract.md`

## 冻结边界

- Markdown requirement package 仍是需求真相。
- `.machine`、`.beacon/state`、runtime ledger、QA matrices、acceptance contracts、release scorecards 仍是 projection / evidence / read model。
- 任何把 machine artifacts 称为 source of truth 的源码文案或运行输出都必须修正。
- legacy / compat / fallback path 必须被清点、版本有界，并且要么退场，要么以 fail-closed 方式显式 admission。
- 固定流程不应长期依赖 Skill 反复解释执行；应下沉为 deterministic tools、gate registry、schema 和回归测试。
- accepted UI/UX facts 未写回 `PRODUCT.md` / `DESIGN.md` / PRD / user-story / test-cases 时，implement / QA / release 应 fail closed，而不是按旧 frozen truth 回滚已验收前端事实。

## v1.4.11 减负重构闭环

当前版本完成的顺序切片：

1. `authority-vocabulary-and-baseline-inventory-contract`：统一 authority vocabulary，建立 legacy burden baseline inventory。
2. `compatibility-registry-and-command-catalog-contract`：登记 compatibility registry，显式分层 command catalog。
3. `qa-prd-legacy-mirror-retirement-contract`：默认 current-only，legacy mirror 转为显式 compat policy / warning。
4. `implement-package-legacy-loader-retirement-contract`：移除 implement 内部动态 legacy loader。
5. `beacon-design-product-prototype-rebuild-contract`：把旧 prototype 重建为 Beacon design 能力，纳入 product/design truth 和设计子 skill。
6. `browser-fallback-deterministic-command-contract`：把 browser fallback 重命名为 deterministic command evidence，分离 browser-agent success 与 project-command success。
7. `memory-intent-historical-migration-boundary-contract`：限定 memory / intent historical migration 边界，legacy 输出只作为 compat / migration evidence。
8. `test-directory-marker-relayering-contract`：重分层测试 marker，避免 legacy / historical / deprecated tests 继续冒充 current closure。
9. `beacon-design-human-subskills-closure-contract`：补齐 `beacon-design-*` 人类面子 skill，让 design 能力不再只靠单一总入口和 AI 临场理解分流。

## 下一步

已完成 release check：

```bash
rtk python3 -m beacon.main release check v1.4.11 --project . --json
```

当前 release check 结果为 `status=pass`、`release_ready=true`，但仍有 `ceo challenge coverage current` warning。不得把本状态表述为已经发布；正式发布和 post-release local install 需要单独人工确认。
