---
slug: beacon-qa-chrome-extension-e2e-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.4/features/beacon-qa-chrome-extension-e2e-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：QA Chrome Extension E2E v1.6.4

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-CX-001 | contract | `python3 -m pytest tests/test_v164_qa_chrome_extension_e2e.py::test_runner_registered -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `BROWSER_RUNNER_REGISTRY` 含 `playwright-extension`；`default_browser_runner_command('playwright-extension')` 返回非空字符串且含可执行入口 |
| AC-002 | TC-CX-002 | integration | `python3 -m pytest tests/test_v164_qa_chrome_extension_e2e.py::test_load_extension_passthrough -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runner 启动参数含 `--load-extension=<path>`；构造损坏扩展包时 block 且 reason_code 含 `extension_load_failed` |
| AC-003 | TC-CX-003 | integration | `python3 -m pytest tests/test_v164_qa_chrome_extension_e2e.py::test_headless_new_mode -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runner 默认 headless 用 `--headless=new`；旧 headless 不被选用于扩展模式 |
| AC-004 | TC-CX-004 | integration | `python3 -m pytest tests/test_v164_qa_chrome_extension_e2e.py::test_extension_id_fixed -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 给定 manifest `key` field，runner 解析出固定 extension ID；两次启动 ID 一致 |
| AC-005 | TC-CX-005 | integration | `python3 -m pytest tests/test_v164_qa_chrome_extension_e2e.py::test_extension_page_navigation -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runner 导航到 `chrome-extension://<id>/index.html` 并断言页面含预期 DOM 元素 |
| AC-006 | TC-CX-006 | integration | `python3 -m pytest tests/test_v164_qa_chrome_extension_e2e.py::test_popup_test -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | popup 测试通过 `action.openPopup()` 或 `popup.html?tab=<id>` 注入；断言 popup DOM 可访问 |
| AC-007 | TC-CX-007 | integration | `python3 -m pytest tests/test_v164_qa_chrome_extension_e2e.py::test_service_worker_target -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runner 检测到 service worker target（type==='service_worker'）；能 evaluate SW 上下文（如 `chrome.storage.local`）；SW 终止后能重新等待 |
| AC-008 | TC-CX-008 | contract | `python3 -m pytest tests/test_v164_qa_chrome_extension_e2e.py::test_fail_closed_no_false_pass -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 扩展加载失败 / ID 不匹配 / SW 未就绪三种场景 → QA `blocked=True`，reason_code 明确；evidence 不被记为 pass（`NON_ACCEPTANCE_EVIDENCE_KINDS` 拒绝） |
| AC-009 | TC-CX-009 | contract | `python3 -m pytest tests/test_v164_qa_chrome_extension_e2e.py::test_evidence_axes_extension -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `BROWSER_EVIDENCE_AXES` 含 `extension_page` / `service_worker` / `popup`；qa_acceptance 接受扩展 evidence 并校验形状 |

## 验证说明

- TC 文件 `tests/test_v164_qa_chrome_extension_e2e.py` 由 implement 阶段创建；实现前 tasks 允许标注 `BLOCKED:implement`。
- TC-001/008/009 为 contract 层（import + 断言 registry/evidence 形状，无需真实 Chrome）。
- TC-002..007 为 integration 层，需真实 Chrome + 最小扩展包 fixture（`tests/fixtures/chrome-ext/`）；用 `tmp_path` 构造扩展包，monkeypatch Chrome 路径。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..009 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
