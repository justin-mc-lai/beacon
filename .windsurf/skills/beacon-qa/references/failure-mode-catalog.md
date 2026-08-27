# Failure Mode Catalog（失败模式目录）

> v1.6.13 D3 产物，v1.6.16 P4 扩充到 20+ 条。QA/release 前对抗式审查的固定输入：从本目录抽取 3-5 个翻车点逐条验证。
> 本目录输出为**批判式意见**（findings/evidence），**不自动判 pass**——最终 verdict 由人/既有 gate 决定（user decides）。
> 每条含 source_ref（真实失败来源，v1.6.13-16 实测记录）。

## FM-001 猜代码不读代码（guessing_without_reading）

- 症状：agent 未读目标源码/接口，直接凭常识写实现或改逻辑。
- 判定规则：实现引用"大约意思差不多"；diff 涉及未读过的模块却无源码引用证据。
- rubric：通过 = 有源码/接口读取证据（文件路径 + 关键行）；拦截 = 无读取证据直接改。
- 对应 skill 用例：pln-source（source-anchored）作为审查前强制加载。
- source_ref：v1.6.13 实现调研；方法论 M1 验证>生成。

## FM-002 宣称完成但无产出（docs_only_closure）

- 症状：只写文档/说明，没有可运行的实现、零断言、零证据文件。
- 判定规则：任务勾选 `[x]` 但 `evidence=` 文件不存在；实现零 assert/零测试。
- rubric：通过 = 有 evidence 文件 + 可运行断言；拦截 = 仅有文字描述。
- 对应 skill 用例：beacon-qa `eval-qa`（docs-only completion 直接 blocked）。
- source_ref：v1.6.13 D3 设计；v1.6.14 多次被 QA evidence gate 拦截。

## FM-003 软断言/软测试冒充 exec（soft_test_only）

- 症状：TC 验证列只写 `integration` / `目录存在` / `fixture` / `可选`，无 Command+Assertion；`print(0)` 冒充 exec。
- 判定规则：tests.md 出现软验证列（`integration$|目录存在|^fixture$|^可选$`）；exec TC 无真实断言。
- rubric：通过 = 每 TC 有 Command+Assertion 且 ≥1 exec-layer；拦截 = 软占位 TC。
- 对应 skill 用例：beacon-truth `gen-truth` Round 4（coverage 软占位扫描）。
- source_ref：v1.6.13 假覆盖暴露（soft_test_only 冒充 exec）。

## FM-004 漏读关联改动（missed_sibling_change）

- 症状：只改了命名路径上的一处，没改调用方/兄弟实现（grep 所有 caller 前动手）。
- 判定规则：改动涉及共享函数/常量，却未 grep 全部 caller；跨 surface 不同步。
- rubric：通过 = 改动前有 caller grep 记录；拦截 = 仅改单点。
- 对应 skill 用例：beacon-implement 决策前必须搜索（code-reuse thinking guide）。
- source_ref：v1.6.15 共享函数改动未同步 caller（方法论 M 层）。

## FM-005 越权裁决（overreach_verdict）

- 症状：evaluator 改写 truth、review agent 自动判 pass、生成器自证完成。
- 判定规则：QA 输出改写 frozen truth；review 结论替代人类 gate。
- rubric：通过 = 只产 findings/route recommendation；拦截 = 擅自改 truth 或判 release。
- 对应 skill 用例：beacon-qa / beacon-release（harness 边界 fail-closed）。
- source_ref：harness 边界 HARD GATE（v1.6.10+ 1+6 合并后全版本）。

## FM-006 FSM 终态未声明（unterminated_fsm_state）

- 症状：FSM 表里有状态只作为终点（无出边）但未在 `**终态：**` 声明，校验器报 state_undefined。
- 判定规则：truth_fsm validate 报 `state_undefined ... not a declared terminal`；终态列表遗漏。
- rubric：通过 = 每个无出边状态在终态声明中；拦截 = 漏声明直接 freeze。
- 对应 skill 用例：beacon-truth gen-truth（FSM 校验）。
- source_ref：v1.6.14/15/16 多次 freeze 被 truth_fsm_invalid 拦截（gated/cataloged/reported 等）。

## FM-007 shell 命令花括号展开失败（brace_expansion_breakage）

- 症状：tests.md 命令用 `rg -n "a\|b"` 花括号/管道转义，QA 执行器（POSIX sh）不展开导致失败。
- 判定规则：命令含 `{a,b}` 花括号或 `\|` 在 rg 里非法；QA 执行器 exit 2。
- rubric：通过 = 命令在 QA 执行器可跑；拦截 = 依赖 shell 特定展开。
- 对应 skill 用例：beacon-qa eval-qa（exec-layer 命令校验）。
- source_ref：v1.6.13 L1/L3/L4 的 TC-ILLEGAL 命令多次修复。

## FM-008 执行路径在目标环境不可用（exec_path_unavailable）

- 症状：命令引用 `.claude/` 等 gitignored 或 worktree 不存在路径，QA 执行器找不到文件。
- 判定规则：命令路径在 canonical surface 不存在；worktree 与 main 路径差异。
- rubric：通过 = 命令路径指向 canonical/可解析路径；拦截 = 依赖本地专属路径。
- 对应 skill 用例：beacon-qa eval-qa。
- source_ref：v1.6.13 的 `.claude/` 路径在 QA 执行器不可用（改为 canonical）。

## FM-009 测试选择器与函数名不匹配（tc_selector_mismatch）

- 症状：tests.md 用 `-k validator` 但测试函数名不含该词，QA 找不到测试 → exit 1。
- 判定规则：`-k` 选择器在测试脚本无匹配；断言被跳过却报通过。
- rubric：通过 = 选择器能匹配到测试；拦截 = 匹配 0 个却 exit 0。
- 对应 skill 用例：beacon-qa exec-layer TC。
- source_ref：v1.6.13/14 多次（`-k validator`/`-k vertex_assert`/`-k illegal_excluded` 无匹配）。

## FM-010 编辑落点错位（edit_target_mismatch）

- 症状：实现改动误写到 main 而非 worktree（editable install 遮蔽），导致 main 被改、worktree 缺。
- 判定规则：worktree 文件与 main 不一致；提交了非预期路径。
- rubric：通过 = 改动在 worktree 且 main 干净；拦截 = main 被实现改动污染。
- 对应 skill 用例：beacon-implement（worktree 隔离）。
- source_ref：v1.6.14 L1 freeze.py 误改到 main；v1.6.15 L1 同问题。

## FM-011 冻结 truth 改后未 refreeze（truth_edit_without_refreeze）

- 症状：修改 frozen truth（tests.md）后直接继续，机器投影/版本哈希过期，QA gate 拦截。
- 判定规则：truth-map verify 报 hash 陈旧；freeze 后文件又改。
- rubric：通过 = 改 truth 后 refreeze + 重新生成机器投影；拦截 = 改后不重冻。
- 对应 skill 用例：beacon-truth gen-change / gen-refreeze。
- source_ref：v1.6.14/15 多次（tests.md 改后需 refreeze 才能过 QA）。

## FM-012 editable install 遮蔽 worktree（editable_install_shadowing）

- 症状：PYTHONPATH 指向 worktree 但 import 解析到 main 的模块（editable 安装优先）。
- 判定规则：`module.__file__` 指向 main 路径；测试改了 worktree 却跑 main 代码。
- rubric：通过 = import 解析到 worktree 模块；拦截 = 静默跑 main 版本。
- 对应 skill 用例：beacon-implement（worktree 测试）。
- source_ref：v1.6.15 L1 测试 import 到 main 的 story_scenarios（DEFAULT_CONTRACT_FAMILIES 找不到）。

## FM-013 版本线未登记（version_line_unregistered）

- 症状：新版本线未登记 version-truth-catalog / project-version-governance，QA 前置链卡住。
- 判定规则：QA/cutover 报 legacy_or_mixed_truth_state；catalog 无该版本条目。
- rubric：通过 = 版本线已登记 + SUMMARY 存在；拦截 = 未登记即跑 QA。
- 对应 skill 用例：beacon-doctor（setup-context / catalog）。
- source_ref：v1.6.13/14/15/16 每次新版本线都需先登记。

## FM-014 类型覆盖假全绿（type_coverage_false_green）

- 症状：只测 happy path 却报 coverage_rate=1.0（数量覆盖冒充类型覆盖）。
- 判定规则：required 5 类但 covered 只有 primary；scenario_family 全默认 primary。
- rubric：通过 = 类型覆盖（negative/boundary 等）真实达标；拦截 = 数量全绿但类型缺口。
- 对应 skill 用例：beacon-qa（v1.6.15 类型加权 coverage_rate）。
- source_ref：v1.6.14 三个 lake 实测（required 5 类/covered primary 仍 1.0）。

## FM-015 live runner 未准入（live_runner_not_admitted）

- 症状：eval live 层全部 blocked（live_skill_pass=0），因 admission 配置缺失。
- 判定规则：is_live_runner_admitted=False；admission 文件不存在。
- rubric：通过 = admission 已配置（admitted=true, host 有值）；拦截 = 缺失导致全 blocked。
- 对应 skill 用例：beacon-eval-agent（live 层）。
- source_ref：v1.6.16 P1 根因（agent-eval-runner-admission.json 缺失）。

## FM-016 release 工件陈旧（release_artifact_stale）

- 症状：release-gate-report / coverage-summary 等工件版本落后（v1.6.12 残留），release check 失败。
- 判定规则：release check 报 gate report version mismatch / coverage 陈旧。
- rubric：通过 = 工件与目标版本一致 + 重新生成；拦截 = 沿用旧版本工件。
- 对应 skill 用例：beacon-eval-release / beacon-doctor。
- source_ref：v1.6.13/14/15 每次 release 前旧工件导致门禁失败。

## FM-017 版本晋升不完整（version_promotion_incomplete）

- 症状：只改 version-truth.json 未改 __init__/pyproject/surfaces，runtime_docs_release_drift。
- 判定规则：release 报 runtime_docs_release_drift；resolve_runtime_version 用旧包版本。
- rubric：通过 = 包版本 + version-truth + surfaces 全部晋升；拦截 = 部分晋升。
- 对应 skill 用例：beacon-eval-release / sync-version-surfaces。
- source_ref：v1.6.13/14/15 版本晋升时需同步多处。

## FM-018 测试间共享状态污染（test_state_pollution）

- 症状：一个测试写入临时文件（如 scorecard）影响后续测试判定。
- 判定规则：测试顺序改变结果；共享路径被多个测试读写。
- rubric：通过 = 测试独立/清理自身副作用；拦截 = 依赖执行顺序。
- 对应 skill 用例：beacon-qa exec-layer 测试编写。
- source_ref：v1.6.16 P3 测试（临时 scorecard 影响 pending/match 判定）。

## FM-019 admission/cutover 凭证过期（workspace_credential_stale）

- 症状：worktree 提交后 HEAD 变化，admit 报 dirty_head/merge_main_conflict，QA 被拦。
- 判定规则：admit 返回 merge_main_conflict；凭证记录旧 HEAD。
- rubric：通过 = 提交后重新 admit + 刷新凭证；拦截 = 旧凭证直接跑 QA。
- 对应 skill 用例：beacon-implement（workspace admit）。
- source_ref：v1.6.14/15/16 每次 worktree 提交后需重新 admit。

## FM-020 合并冲突用错侧（merge_conflict_wrong_side）

- 症状：机器投影/运行时文件冲突时选了错误侧，导致数据丢失或版本回退。
- 判定规则：冲突解决后文件与权威版不一致；feature 分支实现被覆盖。
- rubric：通过 = 冲突解决保留权威内容（main 版）；拦截 = 用错侧丢内容。
- 对应 skill 用例：beacon-implement（git merge 冲突）。
- source_ref：v1.6.14/15 多次（.beacon/qa/status.json、feature-package-validation.json）。

## 使用方式

1. QA/release 前对抗式审查：从本目录抽取 3-5 条，逐条按 rubric 验证并留证据。
2. 发现目录外的新失败模式：回填本目录（id 递增，保持 ≥20 条）。
3. 本目录不自动判 pass；verdict 由人/既有 gate 决定。
