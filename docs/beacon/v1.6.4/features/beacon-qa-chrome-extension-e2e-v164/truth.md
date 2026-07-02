---
slug: beacon-qa-chrome-extension-e2e-v164
version: v1.6.4
status: frozen
revision_id: R1
language: zh
change_reason: R1 — beacon qa browser_e2e 层支持 Chrome 扩展 e2e 验收（--load-extension / extension ID / popup / service worker / fail-closed）
source_revision_id: null
canonical_refs:
  prd: docs/beacon/v1.6.4/features/beacon-qa-chrome-extension-e2e-v164/truth.md
  user_story: docs/beacon/v1.6.4/features/beacon-qa-chrome-extension-e2e-v164/truth.md
  test_case: docs/beacon/v1.6.4/features/beacon-qa-chrome-extension-e2e-v164/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：QA Chrome Extension E2E v1.6.4

## 概述

beacon qa 的 `browser_e2e` 层当前是通用 Web 页面 e2e（playwright/browser-use 跑普通 URL），无法验收 Chrome 扩展。Chrome 扩展 e2e 需加载扩展包、固定 extension ID、访问 `chrome-extension://` 页面、测试 popup、检测 service worker——这些是结构性缺口（零代码）。

本 feature 在 `BROWSER_RUNNER_REGISTRY` 新增 `playwright-extension` runner，adapter 透传 `--load-extension` / `--headless=new`，扩展 evidence axes，使 beacon qa 能对 Chrome 扩展做端到端验收。

## User Intent（一行）

beacon qa 的 browser_e2e 层能加载 Chrome 扩展包并验收扩展页面/popup/service worker，fail-closed 不记 false pass。

## User Intent Snapshot

- user_prompt: "beacon qa 具备 Chrome 扩展 e2e 验收能力"
- lake_or_ocean: 湖（海级程序已拆，本 feature 单点结构性 gap，scope 清晰）
- scope_mode: brownfield_takeover（既有 browser_e2e 层，做扩展能力扩展）
- silent_scope_change_allowed: false
- program_ref: docs/beacon/v1.6.4/programs/beacon-qa-capability-hardening-v164/feature-graph.md (Phase 1)

## User Decisions（locked）

- UD-001 runner 命名：新增 `playwright-extension` runner（不污染现有 `playwright`，UD-2 from program ack）
- UD-002 fail-closed 原则：扩展加载失败 / ID 不匹配 / SW 未就绪 → block，不记 false pass（preamble §4 不假交付）

## Problem Statement

1. `BROWSER_RUNNER_REGISTRY` 无扩展专用 runner；`default_browser_runner_command('playwright')` 返回空字符串。
2. adapter（agent_browser_runner / browser_use_runner）无 `--load-extension` 透传，无法加载扩展包。
3. 无 extension ID 管理（固定 ID 是扩展 e2e 前置，Chrome 官方要求）。
4. 无 `chrome-extension://` 页面导航、popup 测试、service worker target 检测。
5. `BROWSER_EVIDENCE_AXES` 无扩展维度（extension_page / service_worker / popup）。

## Non-Goals

- 不实现非 Chrome 扩展的浏览器扩展（Firefox/Edge 等，仅 Chrome MV3）。
- 不重构现有 `playwright` / `browser-use` runner 行为（新增 `playwright-extension`，UD-001）。
- 不做置信度链传递（Phase 2 范围）。
- 不做 defect 路由（Phase 4 范围）。
- 不做单元测试框架本身的扩展（仅 e2e 验收能力）。

## 受影响代码面

- `beacon/utils/qa_acceptance.py`：`BROWSER_RUNNER_REGISTRY` 加 `playwright-extension`；`BROWSER_EVIDENCE_AXES` 加 `extension_page` / `service_worker` / `popup`。
- `beacon/utils/browser_task_compiler.py`：`default_browser_runner_command` 增 `playwright-extension` 默认命令。
- `beacon/adapters/`：新增或扩展 extension runner adapter（`--load-extension` / `--headless=new` / extension ID / popup / SW target）。
- `tests/test_v164_qa_chrome_extension_e2e.py`：TC-CX-001..009。

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | runner-registered | `BROWSER_RUNNER_REGISTRY` 含 `playwright-extension`；`default_browser_runner_command('playwright-extension')` 返回非空可执行命令（**Must**） |
| AC-002 | load-extension | runner adapter 透传 `--load-extension=<path>` 到 Chrome 启动参数；扩展包加载失败时 block（reason_code `extension_load_failed`）（**Must**） |
| AC-003 | headless-new | runner 使用 `--headless=new`（旧 headless 不支持扩展）；默认 headless 模式下扩展可加载（**Must**） |
| AC-004 | extension-id-fixed | 支持固定 extension ID（manifest `key` field 或 computed key）；测试可解析并复用该 ID（**Must**） |
| AC-005 | extension-page-nav | runner 能导航到 `chrome-extension://<id>/<page>.html` 并断言页面内容（**Must**） |
| AC-006 | popup-test | popup 测试支持：`action.openPopup()` 或 tab-ID URL 注入（`popup.html?tab=<id>`）；能断言 popup DOM（**Must**） |
| AC-007 | service-worker-target | runner 能检测 service worker target（`waitForTarget(type==='service_worker')`）；能 evaluate SW 上下文（如 `chrome.storage`）；支持 SW 终止测试（**Must**） |
| AC-008 | fail-closed | 扩展加载失败 / ID 不匹配 / SW 未就绪 → QA block，reason_code 明确，不记 false pass（`NON_ACCEPTANCE_EVIDENCE_KINDS` 拒绝 dry_run / 非验收 evidence）（**Must**，UD-002） |
| AC-009 | evidence-axes-extension | `BROWSER_EVIDENCE_AXES` 含 `extension_page` / `service_worker` / `popup`；qa_acceptance 校验扩展 evidence 形状（**Must**） |

## Deferral Ledger

| ID | 项 | user_decision |
|---|---|---|
| UD-001 | runner 命名 playwright-extension（新增） | accepted（program P4 ack UD-2） |
| UD-002 | fail-closed 不记 false pass | accepted（preamble §4） |
| UD-003 | Firefox/Edge 扩展支持 | accepted（延后，本 feature 仅 Chrome MV3） |

## State Machine

```
[无扩展 runner] --AC-001--> [playwright-extension runner 注册]
[runner 注册] --AC-002/003--> [扩展加载 + headless=new]
[扩展加载] --AC-004--> [extension ID 固定]
[ID 固定] --AC-005/006/007--> [页面/popup/SW 可测]
[可测] --AC-008--> [fail-closed block 不假交付]
[fail-closed] --AC-009--> [evidence axes 扩展维度]
```

## Closed Questions

是否扩展现有 playwright runner：否（UD-001，新增 playwright-extension 不污染现有）。是否支持非 Chrome 扩展：否（UD-003，延后）。

## Downstream Routes（post-freeze）

- `beacon-gen-implement`：实现 AC-001..009（runner + adapter + evidence axes）。
- `beacon-eval-qa`：用真实 Chrome 扩展验证 e2e 验收 + fail-closed。
- Phase 2（confidence-chain）依赖本 feature 的 browser_e2e 扩展能力。
