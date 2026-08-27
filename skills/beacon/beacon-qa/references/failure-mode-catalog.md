# Failure Mode Catalog（失败模式目录）

> v1.6.13 D3 产物。QA/release 前对抗式审查的固定输入：从本目录抽取 3-5 个翻车点逐条验证。
> 本目录输出为**批判式意见**（findings/evidence），**不自动判 pass**——最终 verdict 由人/既有 gate 决定（user decides）。

## FM-001 猜代码不读代码（guessing_without_reading）

- 症状：agent 未读目标源码/接口，直接凭常识写实现或改逻辑。
- 判定规则：实现引用"大约意思差不多"；diff 涉及未读过的模块却无源码引用证据。
- rubric：通过 = 有源码/接口读取证据（文件路径 + 关键行）；拦截 = 无读取证据直接改。
- 对应 skill 用例：pln-source（source-anchored）作为审查前强制加载。

## FM-002 宣称完成但无产出（docs_only_closure）

- 症状：只写文档/说明，没有可运行的实现、零断言、零证据文件。
- 判定规则：任务勾选 `[x]` 但 `evidence=` 文件不存在；实现零 assert/零测试。
- rubric：通过 = 有 evidence 文件 + 可运行断言；拦截 = 仅有文字描述。
- 对应 skill 用例：beacon-qa `eval-qa`（docs-only completion 直接 blocked）。

## FM-003 软断言/软测试冒充 exec（soft_test_only）

- 症状：TC 验证列只写 `integration` / `目录存在` / `fixture` / `可选`，无 Command+Assertion；`print(0)` 冒充 exec。
- 判定规则：tests.md 出现软验证列（`integration$|目录存在|^fixture$|^可选$`）；exec TC 无真实断言。
- rubric：通过 = 每 TC 有 Command+Assertion 且 ≥1 exec-layer；拦截 = 软占位 TC。
- 对应 skill 用例：beacon-truth `gen-truth` Round 4（coverage 软占位扫描）。

## FM-004 漏读关联改动（missed_sibling_change）

- 症状：只改了命名路径上的一处，没改调用方/兄弟实现（grep 所有 caller 前动手）。
- 判定规则：改动涉及共享函数/常量，却未 grep 全部 caller；跨 surface 不同步。
- rubric：通过 = 改动前有 caller grep 记录；拦截 = 仅改单点。
- 对应 skill 用例：beacon-implement 决策前必须搜索（code-reuse thinking guide）。

## FM-005 越权裁决（overreach_verdict）

- 症状：evaluator 改写 truth、review agent 自动判 pass、生成器自证完成。
- 判定规则：QA 输出改写 frozen truth；review 结论替代人类 gate。
- rubric：通过 = 只产 findings/route recommendation；拦截 = 擅自改 truth 或判 release。
- 对应 skill 用例：beacon-qa / beacon-release（harness 边界 fail-closed）。

## 使用方式

1. QA/release 前对抗式审查：从本目录抽取 3-5 条，逐条按 rubric 验证并留证据。
2. 发现目录外的新失败模式：回填本目录（id 递增，保持 ≥5 条）。
3. 本目录不自动判 pass；verdict 由人/既有 gate 决定。
