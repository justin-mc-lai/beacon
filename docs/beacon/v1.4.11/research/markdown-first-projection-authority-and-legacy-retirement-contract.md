# 调研：Markdown-first 投影权威与旧版兼容退场契约

**Feature**: `markdown-first-projection-authority-and-legacy-retirement-contract`  
**Version**: `v1.4.11`  
**Status**: `research-input`  
**Date**: `2026-05-26`  
**Surface**: `beacon-brainstorm` + `beacon-source-driven`  

## 1. 背景

Beacon `main` 目前的方向已经是 Markdown-first truth。需求真相应主要落在版本化的人类面材料中：

```text
docs/beacon/<version>/prd/
docs/beacon/<version>/user-story/
docs/beacon/<version>/qa/test-cases/
docs/beacon/<version>/change/
docs/beacon/<version>/research/
```

但对 `main` 做 source-driven review 后发现，源码里仍保留了一些旧版语义和兼容兜底代码，会让 `.machine` 看起来像是与 Markdown 并列，甚至更高优先级的 truth source。

本调研要回答两个问题：

1. 既然已经 Markdown-first，为什么还存在“文档 / 机器投影对齐”？
2. 当前源码是否已经积累大量 legacy / fallback / compat 旧补丁，导致 Beacon 源码冗余和心智漂移？

## 2. Source Anchors

本轮 review 锚定 `main`：

```text
445eed5c Document Beacon release hook orchestration
```

关键源码锚点：

- `docs/beacon/global-boundaries.md`
- `beacon/artifact-language-policy.json`
- `beacon/utils/artifact_language.py`
- `beacon/utils/markdown_first_freeze.py`
- `beacon/utils/material_sync.py`
- `beacon/commands/gate.py`
- `beacon/commands/qa.py`
- `beacon/commands/implement/__init__.py`
- `beacon/commands/prototype.py`
- `beacon/utils/skill_admission.py`
- `beacon/cli_factory.py`
- `beacon/command_catalog.py`

## 3. Brainstorm 收敛

### 3.1 核心区分

问题不是 `.machine` 存在。

真正的问题是 Beacon 当前仍混用了三类概念：

1. 需求真相。
2. 确定性投影 / read model。
3. 旧版兼容 fallback。

Markdown-first 的含义是：需求真相由人类面 Markdown 材料编写、评审和冻结。它不意味着机器材料消失。

`.machine` 在以下角色中仍然合理：

- 从 Markdown truth 单向生成的确定性投影。
- QA matrix / story-scenario map / AC closure read model。
- acceptance 或 release evidence。
- runtime board 输入。
- transaction 与 drift-checking 材料。

`.machine` 不应再被描述成 requirement truth。

### 3.2 为什么仍需要 projection alignment

投影对齐仍然需要存在，因为 Beacon gate 需要确定性结构：

- release 和 QA 需要机器可校验的 AC 与 evidence refs。
- runtime status 需要稳定 read model。
- acceptance transaction contract 需要 hash、sequence id、evidence path。
- support surface 需要索引和投影，但不能改写正式 truth。

因此，“对齐”应该被重新定义为：

```text
Markdown truth -> deterministic projection integrity -> gate evidence
```

不应该再被表达为：

```text
human docs <-> machine truth sync
```

### 3.3 Source-backed 冲突

`beacon/artifact-language-policy.json` 仍然写着：

```text
machine artifacts remain source of truth
source_of_truth: machine-readable artifact
```

`beacon/utils/artifact_language.py` 也内置了同样的默认策略。

这与 Markdown-first 方向冲突，应视为术语和权威模型 bug。

### 3.4 Source-backed 冗余风险

对 `main` 粗扫后，兼容相关命中数量较高：

```text
legacy  ~= 558 matches
fallback ~= 548 matches
compat ~= 490 matches
```

这些数量不代表每一处都应该删除，但足以说明：Beacon 当前不是只有少量兼容 shim，而是已经有一层较宽的历史兼容面。

## 4. 调研发现

### 4.1 保留 projection integrity gate

应保留以下 gate / release 检查：

- runtime projection transaction contract。
- acceptance projection transaction contract。
- QA matrix 可用性。
- AC closure 与 evidence refs。
- release scorecard evidence completeness。

只要投影来源是 Markdown truth，这些检查就不是双写真相，而是 projection / evidence integrity 检查。

### 4.2 修正 authority 语义

需要替换源码、文档、status/report/help 输出中暗示 machine truth 的表述：

- `machine artifacts remain source of truth`
- `source_of_truth: machine-readable artifact`
- `source_of_truth.machine_root`

建议使用以下词汇：

- `truth_root`: `docs/beacon/<version>`
- `projection_root`: `docs/beacon/<version>/.machine`
- `runtime_evidence_root`: `.beacon`
- `projection_integrity`: pass / warn / blocked
- `evidence_integrity`: pass / warn / blocked

### 4.3 重命名 material sync 心智

`doctor sync-materials` 当前语义是从 human docs 同步 machine user-story 和 QA artifacts。

这个行为本身可以保留，但人类面表述应改为：

```text
rebuild machine projections from Markdown truth
```

命令名可以先为兼容保留，但 help 输出、doctor 输出和文档应避免让用户误解为双向同步或机器面也是真相。

### 4.4 legacy CLI surface 需要 registry

当前热点：

- `beacon/commands/implement/__init__.py` 动态加载 `beacon/commands/implement.py` 作为 `_implement_legacy_cli`。
- `beacon/commands/qa.py` 仍从 canonical QA status fallback 到 legacy auto-test status。
- `beacon/commands/prototype.py` 保留 legacy wireframe compatibility。
- `beacon/utils/skill_admission.py` 对 command-skill / `omx` / `omc` 允许 `legacy_inline`。
- `beacon/cli_factory.py` 和 `beacon/command_catalog.py` 仍保留 compat / deprecated aliases。

这些 surface 不应盲删。应先进入一个版本化 compatibility registry，明确：

- 为什么存在。
- 哪些版本允许。
- 默认是否启用。
- 是否需要显式 override。
- 退场路线是什么。

### 4.5 v1.4.11+ 对隐藏 fallback 应 fail-closed

对于 `v1.4.11+`，隐藏兼容兜底应默认 fail-closed，除非用户显式 admission。

示例：

- `legacy_inline` skill admission 应要求显式 override，并写入清晰兼容 evidence。
- QA status 应优先 canonical status，legacy status 只能作为历史 evidence，不应作为 pass authority。
- prototype legacy source 应作为迁移输入可见，而不是默认 gate-ready source。
- compat command alias 应隐藏或标记 deprecated，除非 operator 显式进入 advanced compatibility。

## 5. 旧版兼容与冗余代码系统清单

本节按 source-driven 结果把 legacy / compat / fallback 分为三类：

1. **应保留但要改名 / 限界**：仍有功能价值，但需要明确它不是 truth。
2. **应收敛为 registry / 显式 admission**：不能静默启用，应有版本范围和 override。
3. **应进入退场 / 删除计划**：主要是历史入口、半迁移结构或已被新主链替代的旧代码。

### 5.1 Authority 旧语义：应优先修正

**Source**:

- `beacon/artifact-language-policy.json`
- `beacon/utils/artifact_language.py`
- `beacon/commands/status.py`

**现象**:

- policy 仍写 `machine artifacts remain source of truth`。
- `sync_contract.source_of_truth` 仍是 `machine-readable artifact`。
- status 输出仍有 `source_of_truth.machine_root`。

**判断**: 应优先修正，不应保留。

这不是兼容功能，而是 authority model 的语义 bug。Markdown-first 下应改成：

```text
truth_root: docs/beacon/<version>
projection_root: docs/beacon/<version>/.machine
runtime_evidence_root: .beacon
```

**建议**:

- 直接替换 policy 和 renderer 默认值。
- status/report/help 里不再输出 `source_of_truth.machine_root`，改为 `projection.root` 或 `projection_root`。
- 增加测试阻止 machine-as-truth 文案回归。

### 5.2 `.machine` projection gate：应保留

**Source**:

- `beacon/commands/gate.py`
- `beacon/utils/material_sync.py`
- `beacon/utils/markdown_first_freeze.py`
- `beacon/utils/qa_runtime.py`
- `beacon/utils/release_scorecard.py`

**现象**:

- gate 检查 runtime / acceptance projection transaction contract。
- material sync 从 human docs 生成 `.machine/user-story`、`.machine/qa`。
- QA / release 依赖 machine matrix、AC closure、scorecard evidence。

**判断**: 应保留，但要改心智。

这些是确定性读模型和证据，不是双写真相。删除会削弱 gate、release、QA 的可自动校验能力。

**建议**:

- 保留 gate。
- 将 reason_code / help 文案从 truth alignment 调整为 projection integrity / evidence integrity。
- `sync-materials` 可以保留命令名作为兼容 alias，但人类面文案应改为 “rebuild projections from Markdown truth”。

### 5.3 `doctor sync-materials` 与 context drift override：应收敛

**Source**:

- `beacon/commands/doctor.py`
- `beacon/utils/material_sync.py`
- `beacon/commands/implement.py`
- `beacon/utils/requirement_deepening.py`
- `beacon/utils/prd_bootstrap.py`

**现象**:

- `sync-materials` 的 help 是 “Sync machine requirement materials”。
- `material_sync.py` 在运行 test-case create 时临时设置 `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1`。
- implement / requirement_deepening / bootstrap 多处推荐 `doctor sync-materials`。

**判断**: 功能可保留，语义和安全边界应收敛。

生成 projection 是合理的，但 `sync` 和 context drift override 容易让用户误解为为了机器面对齐可以绕过版本一致性。

**建议**:

- 新增主推荐文案：`doctor rebuild-projections` 或保留 `sync-materials` 作为 alias。
- 输出中明确 `source=Markdown truth`、`target=machine projection`。
- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT` 的使用应写入 evidence / diagnostics，并限定为 projection rebuild 内部行为。

### 5.4 QA canonical / legacy 双写：应进入退场计划

**Source**:

- `beacon/utils/qa_runtime.py`
- `beacon/commands/qa.py`
- `beacon/commands/report.py`
- `.beacon/auto-test-status.json`

**现象**:

- `write_qa_status` 同时写 `.beacon/qa/status.json` 和 `.beacon/auto-test-status.json`。
- `load_qa_status` 优先 canonical，但 fallback 到 legacy auto-test status。
- `qa status` 文档字符串仍写 “falling back to legacy auto-test status”。
- QA manifest 同时记录 legacy 和 canonical refs。

**判断**: `v1.4.11+` 应从默认双写转为兼容镜像 / 显式历史读取。

`.beacon/auto-test-status.json` 可作为历史兼容 evidence，但不应继续作为 current QA pass authority。

**建议**:

- `v1.4.11+` 默认只写 canonical `.beacon/qa/status.json`。
- legacy mirror 需要显式配置或兼容模式。
- `load_qa_status` 对 legacy fallback 返回 `status=historical_legacy_only` 或 blocked，不直接当 current status。
- report 可以读取 legacy 作为 historical evidence，不作为 release-ready 判断来源。

### 5.5 implement 半迁移 legacy loader：应完成迁移

**Source**:

- `beacon/commands/implement/__init__.py`
- `beacon/commands/implement.py`
- `tests/test_v147_automation_support_review_and_promotion_contract.py`

**现象**:

- `implement` 已拆成 package submodules，但 `__init__.py` 仍动态加载 sibling `beacon/commands/implement.py` 为 `_implement_legacy_cli`。
- 注释明确写着 “12 CLI commands remain in parent implement.py”。
- 测试直接引用 `implement_module._legacy_cli`。

**判断**: 这是明显的半迁移结构，应作为源码精简重点。

它不是对用户有价值的兼容，而是内部迁移未完成，增加 import 复杂度和测试耦合。

**建议**:

- 把 Typer commands 从 `beacon/commands/implement.py` 迁入 package 内 `commands.py` 或 `__init__.py`。
- 删除 `_load_legacy_cli_module` 动态加载。
- 测试从 `_legacy_cli` 改为公共 app / helper。
- 保留用户命令 `beacon implement ...` 不变。

### 5.6 `legacy_inline` skill admission：应 fail-closed

**Source**:

- `beacon/utils/skill_admission.py`

**现象**:

- skill root 未发现时，如果 `adapter_type == command-skill` 或 adapter 是 `omx` / `omc`，会生成 `admission_mode=legacy_inline` 且 `status=pass`。
- validation 标记为 `not_applicable`，compatibility 标记为 supported。

**判断**: 应改为显式 admission，不应静默 pass。

这类兼容对早期 command-skill 可能有用，但在当前 skill contract / hook / project skill 体系下，静默 pass 会绕过 contract。

**建议**:

- `v1.4.11+` 默认 blocked：`skill_contract_missing` 或 `skill_not_discovered`。
- 只有显式 `--allow-legacy-inline` 或 project config admission 才允许。
- legacy inline 必须写入 compatibility evidence，不能显示为普通 pass。

### 5.7 prototype legacy wireframe：应降为迁移输入

**Source**:

- `beacon/commands/prototype.py`
- `beacon/utils/prototype_utils.py`
- `skills/beacon/beacon-prototype/SKILL.md`

**现象**:

- prototype 已外置 UI/UX 生成，当前定位是 design-result adapter。
- 但 status/list 仍读取 legacy single-file prototype source。
- `evaluate_prototype_status` 在 bundle root 不存在时返回 `legacy_source_only`。

**判断**: 历史可读性可以保留，但不应成为 gate-ready 语义。

**建议**:

- 保留 legacy source inspection。
- `legacy_source_only` 应明确是 `migration_input`，不是 current prototype status。
- v1.4.11+ release/gate 不应因为 legacy source present 而认为 prototype closure 可用。
- 技能文档可保留 “v1.4.8 及更早可读”，但强调不可作为 current truth。

### 5.7.1 P0 friction：accepted UI/UX facts 未写回 truth 导致自动化按旧冻结需求回滚

独立记录：

- `docs/beacon/v1.4.11/research/friction-cd1809c3220a-ui-ux-design-truth-writeback-incident.md`

结论摘要：

- `friction:cd1809c3220a` 证明 accepted `ui-ux-dev` UI/UX facts 未写回 Beacon truth 时，`beacon-implement` / `beacon-qa` 会按旧 frozen truth 回滚已验收前端事实。
- 这是 Beacon 源码侧 truth intake / gate 问题，不是 Foghorn v0.0.1 问题。
- Markdown-first 不能等于盲信旧 Markdown；当前 accepted human facts 必须进入 `PRODUCT.md` / `DESIGN.md` / PRD / user-story / test-cases 或 prototype adapt transaction。
- 候选 gate：`accepted_ui_ux_truth_gap_gate`。
- 候选 feature：`accepted-ui-ux-truth-writeback-gate-contract`。

### 5.8 compat / deprecated command surface：应注册化治理

**Source**:

- `beacon/command_catalog.py`
- `beacon/cli_factory.py`
- `beacon/think.py`
- `beacon/commands/think.py`
- `beacon/commands/workflow.py`
- `beacon/commands/auto_test.py`

**现象**:

- `think`、`workflow`、`gate`、`verify`、`auto-test` 被列为 `COMPAT_COMMANDS`。
- `prompt`、`save`、`work` 被列为 `DEPRECATED_COMMANDS`。
- 多个命令仍被 import 和注册为 hidden。
- `beacon/think.py` 保留 `python -m beacon.think` 兼容入口。
- `ThinkSession` 仍读写 legacy progress file。

**判断**: 不能一次性删除，但应进入 compatibility registry。

这些入口可能仍被旧脚本、测试、外部项目使用；但它们不应无限期留在主源码心智中。

**建议**:

- 建立 `beacon/compat_registry.py` 或 JSON registry。
- 每个 compat command 标注：`introduced_for`、`current_visibility`、`allowed_until`、`replacement`、`test_owner`。
- `SUPPORTED_SUBCOMMANDS` 中重复项和 deprecated 项应清理或由 registry 生成。
- `work` alias、`python -m beacon.think` 这类入口应设置退场版本。

### 5.9 browser fallback adapter：应保留但改名为 explicit deterministic runner

**Source**:

- `beacon/adapters/browser_use_runner.py`
- `beacon/adapters/agent_browser_runner.py`
- `beacon/adapters/browser_runner_common.py`

**现象**:

- browser-use / agent-browser 不可用或缺 task 时，可使用 `--fallback-cmd` 执行确定性项目命令。
- adapter 写 runner artifacts，避免假通过。

**判断**: 这类 fallback 可以保留。

它不是旧版兼容补丁，而是外部浏览器 runtime 不稳定时的显式 deterministic execution path。问题只是 “fallback” 这个词容易和旧版兜底混淆。

**建议**:

- 保留能力。
- 文案改为 `deterministic_command` / `explicit_project_command`。
- 只有显式传入 command 时执行。
- evidence 中标注 `execution_mode=deterministic_command`，避免被误读为 browser agent 已真实执行。

### 5.10 测试层历史版本覆盖：应分层，不应全删

**Source**:

- `tests/test_v110_*`
- `tests/test_v114_*`
- `tests/test_v118_*`
- `tests/test_v135_*`
- `tests/test_v139_*`
- `tests/test_compat_cli_flat_commands.py`
- `tests/test_skill_command_alignment.py`

**现象**:

- 大量测试固定旧版本行为和 compat 行为。
- 部分测试仍直接验证 legacy module entrypoint 或 old auto-test status。

**判断**: 测试不能简单删除，但需要分层。

历史测试有价值，但如果它们继续要求 current behavior 保留旧入口，就会阻碍源码精简。

**建议**:

- 分为 `current_contract`、`compat_contract`、`historical_fixture` 三类。
- current tests 不再依赖 legacy fallback。
- compat tests 需要绑定 registry 和退场版本。
- historical tests 只证明旧包可读，不证明当前新包必须继续双写。

## 6. 保留完整大能力的重构优化蓝图

如果 v1.4.11 要进入重构，不应以“删 legacy 代码”为目标，而应以“保留完整能力、收敛权威模型、降低隐式分叉”为目标。

当前 Beacon 的大能力包括：

- Markdown-first requirement truth。
- `.machine` deterministic projection / evidence。
- QA / release gate。
- implement single / team / Ralph。
- project hook / skill admission。
- prototype design-result adapter。
- browser / auto-test / QA9。
- memory / learn / support surface。
- doctor / status / report / board。

这些能力应保留，但需要统一治理层。

### 6.1 建立 Authority Kernel

**问题**:

当前 truth、projection、runtime evidence、legacy mirror 的命名分散在 policy、status、material audit、PRD、QA、release 中。

**优化**:

新增一个集中 authority 模块，例如：

```text
beacon/utils/authority.py
```

职责：

- 定义 `truth_root`、`projection_root`、`runtime_evidence_root`。
- 定义 artifact role：`truth` / `projection` / `evidence` / `compat_mirror` / `historical_fixture`。
- 提供统一 human readout label。
- 禁止新代码直接拼 `source_of_truth.machine_root`。

**保留能力**:

- 不删 `.machine`。
- 不删 gate。
- 只是让所有 surface 使用同一套 authority vocabulary。

### 6.2 建立 Projection Kernel

**问题**:

PRD、user-story、test-case、QA、release、runtime board 都在各自生成 projection，导致 `sync-materials`、mirror、transaction、drift check 概念重复。

**优化**:

新增集中 projection 模块，例如：

```text
beacon/utils/projection_kernel.py
```

职责：

- `rebuild_projection(source_markdown, target_kind)`。
- `verify_projection_integrity(source_hash, projection_hash)`。
- `write_projection_transaction(...)`。
- `classify_projection_drift(...)`。

当前分散实现可以逐步适配：

- `markdown_first_freeze.py` 保留 Markdown parser / hash helper。
- `material_sync.py` 改成 projection rebuild facade。
- `material_audit.py` 调用 projection integrity checker。
- `gate.py` 只消费 projection gate result，不再自己理解旧 mirror 细节。

**保留能力**:

- 保留 `.machine/prd/*.canonical.json`、`.compile.json`。
- 保留 `.machine/qa/*.json`。
- 保留 runtime / acceptance projection gate。
- 但写入路径变成统一投影事务。

### 6.3 建立 Compatibility Registry

**问题**:

compat / legacy / deprecated 现在散落在：

- `command_catalog.py`
- `cli_factory.py`
- `qa_runtime.py`
- `skill_admission.py`
- `prototype_utils.py`
- `memory.py`
- `intent_router.py`
- `tests/*`

没有统一说明哪个兼容还有效、为什么保留、何时退场。

**优化**:

新增 registry，例如：

```text
beacon/compat_registry.py
```

或：

```text
beacon/compatibility/registry.json
```

每条记录包含：

```json
{
  "compat_id": "qa-auto-test-status-legacy-mirror",
  "surface": "qa",
  "status": "allowed_explicit_only",
  "introduced_for": "v1.1.x auto-test compatibility",
  "current_default": "disabled_for_v1.4.11_plus",
  "replacement": ".beacon/qa/status.json",
  "allowed_until": "v1.4.11",
  "requires_operator_override": true,
  "evidence_role": "historical_fixture"
}
```

**保留能力**:

- 保留老项目可读性。
- 保留显式 compat 模式。
- 但禁止隐式 fallback 改变 current truth / gate。

### 6.4 Command Surface 收敛

**问题**:

CLI 注册层同时存在 core、support、labs、bridge、compat、deprecated，但部分 hidden command 仍被 import / registered，且 `SUPPORTED_SUBCOMMANDS` 手写重复。

**优化**:

- `command_catalog.py` 由 registry 生成或至少校验。
- `cli_factory.py` 只注册当前 surface。
- compat / deprecated command 必须通过 registry 判断是否注册。
- `BEACON_LABS` / `BEACON_ADVANCED` 继续保留，但作为显式 capability plane。

建议分层：

```text
core: prd/user-story/test-case/prototype/implement/qa/release
support: help/status/doctor/archive/report/review/deep/hooks
advanced: board/orchestrate/debug/skill/profile
labs: brainstorm/design/jtbd/kano/roadmap/etc.
compat: think/workflow/auto-test/verify/gate/work/prompt/save
```

**保留能力**:

- 旧命令不立即删除。
- 默认 help 和主心智只显示当前面。
- compat 命令必须显式开关或高级模式。

### 6.5 Implement 重构：完成 package 化

**问题**:

`beacon/commands/implement.py` 仍有约 5000 行，`beacon/commands/implement/__init__.py` 动态加载它作为 legacy CLI。这是典型半迁移。

**优化**:

迁移目标：

```text
beacon/commands/implement/
  __init__.py
  commands.py
  single.py
  team.py
  ralph.py
  adapter.py
  git.py
  evidence.py
  preflight.py
```

阶段：

1. 先移动 Typer command 定义到 `commands.py`。
2. `__init__.py` 直接导出 `commands.app`。
3. 删除 `_load_legacy_cli_module`。
4. 测试不再引用 `_legacy_cli`。

**保留能力**:

- `beacon implement run ... --mode single|team|ralph` 不变。
- single / team / Ralph 能力保留。
- 只消除内部 legacy loader。

### 6.6 QA / Auto-test 重构：拆 current QA 与 compat auto-test

**问题**:

`qa_runtime.py` 让 current QA status 和 legacy auto-test mirror 双写。`auto_test.py` 仍是大文件并写 QA status。`qa.py` 也读取同一 runtime。

**优化**:

拆成：

```text
beacon/utils/qa_status.py          # current canonical status
beacon/utils/qa_compat.py          # legacy auto-test status adapter
beacon/commands/qa.py              # public QA surface
beacon/commands/auto_test.py       # compat/labs runner surface
```

策略：

- current QA 只写 `.beacon/qa/status.json`。
- legacy auto-test mirror 由 compat registry 控制。
- `auto-test` 可以继续存在，但其输出进入 compatibility evidence，不直接冒充 current QA verdict。
- `load_qa_status` 增加 `allow_legacy=False` 默认参数。

**保留能力**:

- 保留 browser / QA9 / compatibility matrix。
- 保留 auto-test 老入口的显式运行。
- 不再默认双写或默认 fallback。

### 6.7 PRD / Material Audit 重构：legacy PRD mirror 降级

**问题**:

`prd.py` Markdown-first 下仍写 `.beacon/prd/<slug>.json` 和 `.beacon/transactions/prd-<slug>.json` 作为 legacy mirror。`material_audit.py` 仍把 `legacy_machine_mirror_sync` 纳入 drift category。

**优化**:

- `.machine/prd/*.canonical.json` 作为 projection。
- `.beacon/prd/*.json` 降级为 compat mirror，默认不要求 current pass。
- `material_audit.py` 对 v1.4.11+ 不再把 legacy mirror stale 作为主 package blocker。
- 若需要历史兼容，输出 `compat_mirror_stale`，不叫 `truth_drift`。

**保留能力**:

- 老项目仍可读 `.beacon/prd/*.json`。
- current package closure 不再被旧 mirror 阻塞。

### 6.8 Prototype 重构：adapter 与 legacy inspector 分离

**问题**:

prototype 当前同时承担：

- v1.4.9+ design-result adapter。
- v1.4.8- legacy wireframe status/list。
- sqlite projection / bundle status / review / freeze 历史逻辑。

**优化**:

拆分：

```text
beacon/commands/prototype.py
beacon/utils/prototype_adapter.py
beacon/utils/prototype_legacy_inspector.py
beacon/utils/prototype_projection.py
```

策略：

- current command 主路径只处理 accepted UI/UX result binding。
- legacy inspector 只在 `--include-legacy` 或 compat mode 下展示。
- `legacy_source_only` 改为 `migration_input_present`。

**保留能力**:

- 保留历史 wireframe 可读性。
- current prototype gate 不再被旧 source 语义污染。

### 6.9 Browser / QA runner 重构：fallback 改为 explicit command lane

**问题**:

browser adapter 的 fallback 其实是显式项目命令执行，但叫 fallback，容易和 legacy fallback 混淆。

**优化**:

- CLI alias 保留 `--fallback-cmd`，新增推荐参数 `--deterministic-command` 或 `--project-command`。
- evidence 中 `execution_mode` 从 `fallback` 改为 `deterministic_command`。
- status 从 `fallback-executed` 改为 `deterministic-command-executed`。

**保留能力**:

- 保留外部 browser runtime 不可用时的确定性验证能力。
- 避免假称 browser agent 已执行。

### 6.10 Intent / Memory 重构：历史迁移只读化

**问题**:

`intent_router.py` 有 legacy rule route facade。`memory.py` 自动 migrate legacy memory，并持续写 legacy projection。

**优化**:

- legacy intent route 标记为 compat router。
- current route 使用 boundary-aware router。
- memory legacy projection 默认只在 compat mode 写。
- 首次 migrate 后写 migration transaction，后续不再持续双写 legacy files。

**保留能力**:

- 老 memory 可导入。
- 老 intent API 可显式使用。
- current runtime 不再被历史 projection 写入拖累。

### 6.11 测试重构：建立三层测试目录或 marker

**问题**:

当前测试大量锁定历史行为。如果直接重构，会不知道哪些失败代表 current regression，哪些只是 legacy contract 需要更新。

**优化**:

引入测试分层：

```text
tests/current/
tests/compat/
tests/historical/
```

或 pytest marker：

```text
@pytest.mark.current_contract
@pytest.mark.compat_contract
@pytest.mark.historical_fixture
```

规则：

- current_contract 不允许依赖 legacy fallback。
- compat_contract 必须绑定 registry 记录。
- historical_fixture 只验证旧材料可读，不阻止新版本精简。

**保留能力**:

- 不丢历史回归保护。
- 当前实现可以逐步瘦身。

### 6.12 重构顺序建议

推荐按低风险到高风险推进：

1. **Authority vocabulary**：修正 machine-as-truth 文案和测试。
2. **Compatibility registry**：先登记，不改变行为。
3. **Command catalog validation**：去重和显式分层。
4. **QA legacy mirror policy**：新增 `allow_legacy` 开关，默认 current-only。
5. **PRD legacy mirror policy**：legacy mirror 从 blocker 降级为 compat warning。
6. **Implement package migration**：消除 `_implement_legacy_cli`。
7. **Prototype legacy inspector split**。
8. **Browser fallback rename**。
9. **Memory / intent historical migration 限界**。
10. **测试目录 / marker 重分层**。

### 6.13 不建议做的重构

以下方向不建议：

- 直接删除 `.machine`。
- 直接删除 `auto-test`、`workflow`、`think` 等旧命令。
- 在一个 feature 里同时拆 implement、QA、prototype、memory、intent。
- 为了减少代码行数牺牲 release / QA gate 的可校验性。
- 把 compat registry 做成新的用户主流程。

正确路线是：

```text
先统一 authority
再注册 compat
再分层测试
最后逐个 surface 退场
```

## 7. 大白话：当前 Beacon 功能实现的完整能力边界

本节不用内部术语堆叠，直接说明 Beacon 现在到底管什么、不管什么、哪些东西是门禁、哪些东西只是证据。

### 7.1 Beacon 是什么

Beacon 不是一个单纯的 CLI，也不是一个只生成文档的工具。

它更像一个“需求到交付的管控内核”：

```text
先把需求讲清楚
再把需求冻结
再按冻结需求实现
再拿证据验收
最后判断能不能 release
```

主链应该保持简单：

```text
prd -> user-story -> test-case -> implement -> qa -> release
```

其它能力都应该围绕这条主链服务，而不是把主链撑爆。

### 7.2 Beacon 的真相边界

大白话：

```text
人看的 Markdown 是需求真相。
机器看的 JSON 是投影和证据。
运行时状态是现场记录。
```

对应目录：

```text
docs/beacon/<version>/prd/              # 需求说明
docs/beacon/<version>/user-story/       # 用户故事 / AC
docs/beacon/<version>/qa/test-cases/    # 测试用例
docs/beacon/<version>/change/           # 变更冻结
docs/beacon/<version>/research/         # 只读调研
docs/beacon/<version>/.machine/         # 机器投影 / gate evidence
.beacon/                                # 运行态记录 / 状态 / 证据
```

要点：

- `.machine` 不是要删除。
- `.machine` 也不是需求真相。
- `.machine` 是为了让 gate、QA、release 能稳定检查。

### 7.3 Beacon 的文档能力边界

Beacon 管这些：

- PRD 是否存在、是否与 feature 对应。
- User Story 是否有清晰 AC。
- Test Case 是否覆盖 AC。
- Research 是否只是调研，不越权变 truth。
- Change / refreeze 是否把需求变更说清楚。
- 版本目录是否完整。

Beacon 不应该做这些：

- 让 brainstorm / deep / source-driven 直接改正式需求。
- 让 `.machine` 反向改 Markdown。
- 让 release 根据“感觉差不多”放行。

### 7.4 Beacon 的实现能力边界

Beacon implement 不是“随便让 agent 写代码”。

它应该做：

- 读取 frozen requirement。
- 确认当前分支 / 版本 / 工作区没错。
- 选择 single / team / Ralph 模式。
- 产出实现计划、任务进度、交付证据。
- 把变更与 AC / test / evidence 绑定。

三种 implement mode：

```text
single: 小改动，单通道实现。
team: 复杂实现，多角色分工。
ralph: 多轮闭环控制，连接 implement / review / QA / release next action。
```

边界：

- implement 不改 frozen truth。
- Ralph 不替代 QA。
- team 不替代 release。
- 外部 skill / hook 不应该直接给 pass。

### 7.5 Beacon 的 QA 能力边界

Beacon QA 应该回答：

```text
这个功能有没有按照 AC 被真实验证？
证据是不是足够？
失败是不是被记录？
哪些地方必须返修？
```

QA 应覆盖：

- unit。
- interface。
- contract。
- integration。
- smoke。
- functional。
- regression。
- exception。
- compatibility。
- browser E2E。

QA 不应该只是：

- 跑了一个命令。
- 写了一个 passed。
- 有一个空报告。
- browser 测试其实没打开真实浏览器。

QA 的机器材料可以保留，但角色是 evidence / scorecard / read model。

### 7.6 Beacon 的 release 能力边界

Release 不是“最后生成一份 checklist”。

Release 应该判断：

- 需求包是否闭环。
- QA 是否闭环。
- AC 是否有证据。
- release scorecard 是否支持放行。
- gate 是否还有 blocker。
- 当前版本、分支、项目元信息是否对齐。
- hook 或部署动作是否只是 supplement，而不是正式 QA verdict。

Release 可以说：

```text
pass / blocked / stop_for_repair
```

但 release 不应该：

- 修需求。
- 替 QA 补证据。
- 因为 hook 成功就认为发布成功。
- 忽略 gate blocker。

### 7.7 核心 Gate 门禁边界

Gate 是 Beacon 最核心的“别带病继续”机制。

大白话：

```text
Gate 不是为了制造流程。
Gate 是为了防止需求、实现、证据、版本、分支不一致时继续往后走。
```

当前源码里的主要 gate 类型包括：

#### 需求包门禁

Source:

- `beacon/utils/material_audit.py`
- `build_requirement_package_gate`

检查：

- PRD 是否存在。
- User Story 是否存在。
- Test Case 是否存在。
- revision / baseline hash 是否一致。
- Markdown-first freeze truth 是否可校验。
- `.machine` projection 是否能从 Markdown truth 对上。

这个门禁决定：

```text
需求包不完整，就不能 implement / qa / release。
```

#### 需求澄清门禁

Source:

- `beacon/utils/requirement_clarity.py`

检查：

- 是否还有 open question。
- AC 是否足够明确。
- 人类面 closure 是否完成。
- support review 是否只是建议，还是需要回 change。

这个门禁决定：

```text
需求没讲清楚，就不要开工。
```

#### AC / Test 映射门禁

Source:

- `beacon/commands/gate.py`
- `beacon/utils/qa_precision.py`

检查：

- AC 是否有 test case。
- test case 是否有执行证据。
- evidence refs 是否有效。
- AC closure 是否 accepted。

这个门禁决定：

```text
验收标准没被验证，就不能说功能闭环。
```

#### Evidence chain 门禁

Source:

- `beacon/commands/gate.py`
- `beacon/utils/v115_delivery.py`

检查：

- raw command log 是否存在。
- evidence manifest 是否存在。
- sha256 manifest 是否完整。
- gate report 状态和 blocker 是否一致。

这个门禁决定：

```text
没有可复现证据，就不能 release。
```

#### Projection transaction 门禁

Source:

- `runtime_projection_transaction_contract`
- `acceptance_projection_transaction_contract`

检查：

- runtime projection transaction 是否完整。
- acceptance projection 是否完整。
- transaction id、source hash、projection seq 是否可追溯。

这个门禁决定：

```text
机器投影坏了，不代表需求坏了，但 gate 不能盲放。
```

#### Scope guard 门禁

Source:

- `check_scope_guard`

检查：

- 实现是否越过本 feature 范围。
- 是否需要确认 scope expansion。
- 是否存在未确认的变更。

这个门禁决定：

```text
不能借一个 feature 偷偷做另一个 feature。
```

#### Prototype / UI 门禁

Source:

- `check_prototype_contract`
- `beacon/commands/prototype.py`

检查：

- 需要 prototype 的版本是否有 prototype。
- prototype 是否 frozen。
- design review 是否通过。
- UI copy / page state / visible contract 是否完整。

这个门禁决定：

```text
涉及 UI/UX 的功能不能只靠口头说明。
```

#### QA9 / Browser / Compatibility 门禁

Source:

- `check_qa9_contract`
- `beacon/commands/auto_test.py`
- `beacon/commands/qa.py`

检查：

- QA 层级是否齐全。
- compatibility matrix 是否完整。
- browser evidence 是否是真实证据。
- protected surface 是否有 session / runner admission。

这个门禁决定：

```text
前端、H5、小程序、后台页面不能用假 browser evidence 放行。
```

#### Memory / Workflow closure 门禁

Source:

- `workflow_memory_transaction_contract`
- `check_memory_closure`
- `check_release_memory_profile`

检查：

- 生命周期事件是否闭环。
- workflow run 是否可追踪。
- repair / feedback 是否同步。
- release decision 是否绑定版本。

这个门禁决定：

```text
长任务不能丢轮次记忆，也不能丢闭环记录。
```

### 7.8 Git 治理门禁边界

Git 门禁不是附属功能，它是实现前和发布前的重要安全线。

Source:

- `beacon/utils/git_alignment.py`
- `beacon/utils/project_metadata.py`
- `beacon/utils/material_audit.py`

Beacon 当前会检查：

- 当前 repo 是否存在。
- 当前分支是否是目标版本分支。
- 是否 detached HEAD。
- tag / branch 是否满足版本引用。
- worktree 是否 dirty。
- 是否允许 dirty worktree 切分支。
- monorepo / multi-service 是否每个 service 都在正确 branch。
- per-service worktree 是否与元信息一致。

典型 blocker：

```text
git_repo_missing
git_detached_head
git_branch_target_mismatch
git_branch_prefix_mismatch
git_version_ref_not_satisfied
implement_branch_switch_dirty_worktree
explicit_version_canonical_worktree_mismatch
explicit_version_per_service_map_missing
```

大白话：

```text
代码不在正确分支，不能开工。
工作区脏且要切分支，不能硬切。
多服务项目没说清楚哪个服务在哪个分支，不能直接实现。
```

### 7.9 项目 / 版本元信息治理边界

项目元信息不是装饰，它决定 Beacon 如何理解项目。

Source:

- `beacon/utils/project_metadata.py`
- `metadata_machine_path`
- `metadata_human_path`
- `verify_project_metadata`
- `resolve_project_metadata_view`

Beacon 项目元信息管理：

- project root。
- topology kind：single_repo / monorepo。
- default execution service。
- service bindings。
- version scoped metadata。
- participating services。
- per-service canonical branch。
- branch governance template。
- previous / next version branch。
- worktree path。

大白话：

```text
Beacon 要知道这是单仓、单服务，还是 monorepo 多服务。
Beacon 要知道这个版本应该动哪些服务。
Beacon 要知道每个服务对应哪个分支和 worktree。
```

如果这些信息缺失，implement / gate / release 都可能误判。

### 7.10 Version 治理边界

Version 不是一个字符串参数。

Beacon 需要同时处理：

- docs version。
- runtime version。
- context managed version。
- release version。
- git branch version。
- project metadata version contract。

Source:

- `beacon/utils/versioning.py`
- `beacon/commands/status.py`
- `beacon/commands/doctor.py`
- `beacon/utils/version_surface.py`

大白话：

```text
你说 v1.4.11，文档、运行时、AGENTS/CLAUDE context、git branch、release checklist 都要对得上。
```

典型问题：

- docs 是 v1.4.11，但 runtime context 还写 v1.4.8。
- 当前分支不是 `beacon/v1.4.11`。
- release checklist 指向旧版本。
- context drift 被静默允许。

这些都不应被忽略。

### 7.11 Doctor / Status / Help 的边界

Doctor 不是主流程。

Status / Help 也不是 gate verdict。

它们的职责是：

- 发现当前阻塞。
- 解释为什么阻塞。
- 给下一条命令。
- 修 context / materials / metadata / install 状态。

它们不应该：

- 改 frozen truth。
- 直接给 release pass。
- 让 support surface 变主流程。

### 7.12 Hook / Project Skill 的边界

Project hook 是项目级能力，不是版本级 truth。

Source:

- `beacon/utils/project_hooks.py`
- `docs/beacon/hooks/<hook-id>.md`

Hook 可以做：

- release 后本地安装 CLI / agent skill。
- implement 后部署到 UAT。
- QA blocked 后进入项目 debuglab。

Hook 不应该做：

- 自动修改 PRD。
- 自动给 QA pass。
- 自动给 release pass。
- 隐藏执行高副作用命令。

大白话：

```text
hook 是项目动作编排，不是 Beacon 生命周期新阶段。
```

### 7.13 Support Skill 的边界

Support skill 包括：

- brainstorm。
- source-driven。
- deep。
- ceo-review。
- security-review。
- performance-review。
- documentation-adr。
- learn。
- qa-evo-deep。

它们能做：

- 分析。
- 挑战。
- 深挖风险。
- 提供 route 建议。
- 写 research / deep / learning 材料。

它们不能做：

- 改正式 truth。
- 替代 QA。
- 替代 release。
- 直接改变 gate verdict。

### 7.14 当前最需要补齐的门禁治理点

基于本轮 source-driven 分析，v1.4.11 应补齐这些全方位点：

1. **Gate Registry**  
   把当前 gate 分散逻辑统一列出：gate id、stage、blocking level、reason codes、repair command。

2. **Authority-aware Gate Output**  
   gate 输出不再说 machine truth，而是说 truth / projection / evidence 的哪一层坏了。

3. **Git Governance Gate**  
   把 branch、worktree、per-service map、dirty worktree、version ref 纳入清晰门禁。

4. **Project Metadata Gate**  
   topology、service bindings、version contract、branch governance 缺失时要明确 blocked / warn。

5. **Version Context Gate**  
   docs/runtime/context/release/git version 不一致时要明确是否允许 drift。

6. **Requirement Package Gate**  
   PRD / user-story / test-case / change / revision / baseline hash 缺失时禁止继续。

7. **QA Evidence Gate**  
   AC 没证据、browser evidence 为空、compat matrix 缺失时 fail closed。

8. **Release Scorecard Gate**  
   release 不只看 checklist，还要看 scorecard、QA、AC closure、memory、projection。

9. **Compat Gate**  
   legacy / fallback / compat path 被使用时必须显式 admission，并写 evidence。

10. **Hook Side-effect Gate**  
   hook 只能 manual confirmed / dry-run / evidence-bound，不能 hidden auto-run。

### 7.15 一句话边界

Beacon 应该保留完整能力，但每个能力必须有清楚身份：

```text
Markdown 负责真相。
Projection 负责机器可校验。
Evidence 负责证明发生过。
Gate 负责阻断带病继续。
Git / Metadata / Version 负责确认你在正确项目、正确版本、正确分支上做事。
Support skill 负责分析，不负责放行。
Hook 负责项目动作，不负责验收结论。
Release 负责最终判断，不负责补材料。
```

## 8. 建议 v1.4.11 候选 Feature

推荐候选：

```text
markdown-first-projection-authority-and-legacy-retirement-contract
```

### 8.1 目标

让 Beacon 的 authority model 明确到不可误读：

```text
Markdown package is truth.
.machine is projection/evidence.
.beacon is runtime state/evidence.
legacy fallback is explicit, version-bounded, and auditable.
```

中文表达：

```text
Markdown 需求包是真相。
.machine 是投影 / 证据。
.beacon 是运行态状态 / 证据。
legacy fallback 必须显式、版本有界、可审计。
```

### 8.2 In scope

- 修正 policy 文件、status/report/help 输出和文档中的 authority 词汇。
- 增加测试，防止 machine-as-truth 表述回归。
- 将 `sync-materials` 文案和输出改为 projection rebuild 心智。
- 为 legacy / fallback / compat surface 增加 compatibility registry。
- 为 `v1.4.11+` 引入隐藏 legacy fallback fail-closed 策略。
- 保留 `.machine` projection gates。
- 补充 authority kernel / projection kernel / compat registry 的最小实现边界。
- 建立 current / compat / historical 测试分层策略。
- 补充 gate registry、git governance gate、project metadata gate、version context gate 的统一边界。
- 将 gate 输出改为 truth / projection / evidence / git / metadata / version 分层诊断。

### 8.3 Out of scope

- 删除 `.machine`。
- 删除 release / QA projection gates。
- 重写所有历史版本文档。
- 一次性删除全部 legacy 代码。
- 修改已发布 v1.4.10 的 frozen acceptance。
- 一次性重写 implement、QA、prototype、memory、intent 全部大文件。
- 将 compatibility registry 暴露成新的用户主流程。
- 将 gate registry 变成新的主流程 stage。
- 让 hook 或 support skill 直接改变 gate verdict。

## 9. 候选验收草案

正式 AC 后续应通过 `change-refreeze` 创建。当前候选验收建议：

- AC-001: 当前 policy 或生成 guidance 不再把 machine artifacts 称为 requirement source of truth。
- AC-002: status/report/help 输出能区分 truth root、projection root、runtime evidence root。
- AC-003: Projection gates 保持启用，但命名为 projection/evidence integrity checks。
- AC-004: legacy / compat / fallback surfaces 进入 registry，包含 owner、reason、allowed version range、default behavior、retirement route。
- AC-005: `v1.4.11+` 隐藏 fallback path 在无显式 operator override 时 fail closed。
- AC-006: 回归测试阻止重新引入 machine-as-truth 文案。
- AC-007: implement 不再通过 `_implement_legacy_cli` 动态加载 sibling CLI。
- AC-008: QA current status 不再默认双写 legacy auto-test status；legacy 只作为显式兼容 evidence。
- AC-009: browser deterministic command path 被命名为 explicit project command，而不是旧版 fallback pass。
- AC-010: compatibility registry 覆盖 compat / deprecated / legacy mirror / legacy fallback surface。
- AC-011: current contract tests 不依赖 legacy fallback；compat tests 必须绑定 registry。
- AC-012: PRD legacy mirror stale 不再作为 v1.4.11+ current package blocker。
- AC-013: gate registry 覆盖 requirement package、requirement clarity、AC/test、evidence chain、projection transaction、git alignment、project metadata、version context、QA evidence、release scorecard、hook side-effect。
- AC-014: git governance gate 能区分 branch mismatch、dirty worktree、detached HEAD、per-service map missing、worktree mismatch。
- AC-015: project metadata gate 能验证 topology、default service、service bindings、version contract、branch governance。
- AC-016: version context gate 能报告 docs/runtime/context/git/release version drift，并给出 repair route。

## 10. 路由建议

下一步正式路由：

```bash
beacon change-refreeze "markdown-first-projection-authority-and-legacy-retirement-contract" --project . --version v1.4.11
```

本调研不是 frozen truth。它需要后续进入 `change-refreeze`，再进入 PRD、user-story、test-case、implementation、QA、release。
