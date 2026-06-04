# PRD：Beacon v1.3.3 核心瘦身与外部 skill 降级

**Feature**: `beacon-v1.3.3-core-slimming-and-external-skill-demotion`  
**Version**: `v1.3.3`  
**Date**: `2026-04-16`  
**Status**: `current release snapshot`

## 1. 问题

Beacon 主链已经收口到 `6+3`，但核心面仍残留兼容层耦合与历史叙事：

1. `implement` 默认已走宿主原生执行面，但 builtin adapter 仍内置：
   - `omx`
   - `omc`
   - `gstack`
2. `qa` 在 profile gate 未通过时仍会隐式触发 project orchestration，而不是先返回明确阻断与迁移建议。
3. `skill / profile / orchestrate` 虽趋于高级面，但默认文案、测试与 discovery 仍存在“核心能力化”惯性。
4. `ralph-bridge` 仍作为命令面名词存在，和“Ralph 内化闭环控制器”的方向冲突。
5. Team/Ralph HUD 已有基础，但还缺稳定的“人类摘要 + 机器全量”字段约定。

当前风险集中在：

- 新用户默认路径仍会感知 compatibility 复杂度
- 兼容迁移责任分散在 `qa/implement/help`，没有统一治理入口

## 2. 目标

`v1.3.3` 在不破坏已验收主链能力前提下，收敛为：

```text
Core
  = 6+3 human minimal surface
  + host-native implement/qa execution
  + contract/evidence/gate kernel

Compatibility
  = user-custom external skill adapters
  + profile/orchestration legacy support
  + deprecated bridge surfaces
```

### 2.1 核心目标

1. **宿主原生优先**
   - 默认执行面仅面向 `Codex native` / `Claude native`
   - 主落地口径优先 Codex 原生能力，Claude 保持同构语义
2. **核心轻量**
   - 人类主面只保留 `prd -> user-story -> test-case -> implement -> qa -> release` + `help/status/doctor`
   - 不新增人类公开一级主命令
3. **外部适配降级**
   - 保留用户自定义外挂 skill 适配器能力
   - 但 Beacon core 不再内置 `omx/omc/gstack` 为默认 builtin runner
4. **迁移统一治理**
   - 兼容迁移统一由 `beacon doctor` 子命令执行
   - `implement/qa` 不承担隐式迁移职责
5. **HUD 轻量增强**
   - 增强 `ralph HUD` 与 `team HUD` 的闭环观测字段
   - 不引入 TUI/dashboard 新平台依赖

### 2.2 非目标

本线不做：

- 删除所有历史兼容代码（compatibility plane 可保留）
- 删除真实项目所需 contract/evidence gate 能力
- 把 Beacon 改成单一宿主
- 删除 `team` / `qa-team` / `ralph` 机器面能力
- 将迁移逻辑复制到多个命令入口重复维护

## 3. 用户故事

| As a | I want to | So that |
|------|-----------|---------|
| Beacon 人类操作者 | 只记住 `6+3` 主面 | 不被 compatibility 细节淹没 |
| Beacon 维护者 | 把兼容迁移统一收敛到 `doctor` | 降低长期维护与回归风险 |
| 真实项目操作者 | `qa` 先给阻断和下一步，不隐式跑外部命令 | 行为可预期且可审计 |
| 高级项目用户 | 在显式 compatibility mode 下接入外挂 skill | 保留扩展能力但不污染 core |

## 4. 功能需求

### FR-001 默认 runner 必须保持宿主原生优先

`implement` 默认执行路径必须保持：

- `single` -> native single
- `team` -> host-native bounded team runtime
- `ralph` -> host-native loop controller

不得把 external runner 恢复为默认主路径。

### FR-002 external adapter 必须退出 core builtin 集合

以下能力必须退出 core builtin runner 叙事：

- `omx`
- `omc`
- `gstack`

要求：

- 通过 compatibility 机制可选接入
- 不再作为 `implement` 默认 builtin adapters
- README/help/onboarding 不再作为主推荐路径

### FR-003 兼容迁移必须由 doctor 子命令统一执行

新增 doctor 迁移入口（命名可调整，但必须在 doctor 下）：

- `beacon doctor migrate-compat --project-root <root> --version <v> --dry-run|--apply`

最小流程必须包含：

1. 兼容状态扫描（adapter/profile/orchestration/docs/tests）
2. 迁移计划生成（含风险、影响、回滚点）
3. 迁移执行（显式 apply）
4. 迁移后验证（core/compat contract）
5. 迁移报告落盘

产物要求：

- `.beacon/state/compat-migration/<run-id>.json`
- `docs/beacon/<version>/execution/compat-migration-<run-id>.md`

### FR-004 `qa` 默认不得隐式自动触发 external orchestration

`qa` 在 profile gate 未通过时：

- 默认不得自动执行 `run_profile_orchestration`
- 必须返回明确 `reason_code` 与 `recommended_command`
- 推荐命令优先指向 `beacon doctor migrate-compat ...`

只有在显式 compatibility mode（或等价显式开关）下，才允许执行 external orchestration。

### FR-005 `skill/profile/orchestrate` 必须退出默认主叙事

以下命令/能力不再作为普通用户默认路径：

- `skill`
- `profile`
- `orchestrate`

要求：

- 保留为 optional/advanced/compatibility
- 不得进入主 onboarding

### FR-006 `ralph-bridge` 必须退出正式产品叙事

`ralph-bridge` 必须收敛为 compatibility 历史面：

1. 保留命令但明确标记 deprecated compatibility
2. 或由 Beacon 内部 `ralph` 控制面替代并停止主叙事命名

无论采用哪种方式，不得继续作为未来主线能力。

### FR-007 文档主面必须只教 `6+3`

README、help、host-visible skills、usage docs 默认教学路径只教：

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`
- `help`
- `status`
- `doctor`

external compatibility 只允许进入：

- compatibility 文档
- migration 文档
- 特种项目扩展文档

### FR-008 测试合同必须按 core/compat 分层

测试必须重构为：

- core tests：只覆盖主链与宿主原生执行面
- compatibility tests：覆盖 legacy/external adapters 与外部编排

不得在 core tests 中隐含 external runner 是核心组成。

### FR-009 discover/registry 输出必须分层展示

如果保留 `skill detect`、`skill registry`、project skill discovery：

- builtin native 能力单独一层
- external compatibility 能力单独一层
- 输出文案明确：
  - builtin = Beacon core
  - external = optional compatibility

### FR-010 project contract 能力必须与 external execution 解耦

以下能力继续保留：

- required evidence
- required cases
- contract drift
- profile-bound verification policy

要求：

- contract evaluation 与 external command execution 分离
- 未启用 compatibility mode 时，contract 仍可独立评估与阻断

### FR-011 Ralph HUD 与 Team HUD 轻量增强

在不新增公开一级命令前提下，增强 HUD 机器可观测字段，并遵守极简场景契约：

- 场景契约（S1-S6）：
  - S1：主链空闲（1 行）
  - S2：Single 执行（2 行）
  - S3：Team 执行（2 行）
  - S4：Ralph 执行（2 行）
  - S5：Warn（3 行）
  - S6：Trip/Blocked（3 行）
- 行数约束：
  - 默认最多 2 行
  - 仅阻断/告警时允许第 3 行
- 字段约束：
  - 人类面只展示阶段、执行进度、阻断原因、下一步命令
  - 全量细节继续在 JSON/artifacts

- Ralph HUD 最小字段：
  - `phase`
  - `round_count`
  - `stop_state`
  - `next_action`
  - `current_blocker`
  - `last_round_ref`
  - `gate_release_status`
  - `failure_streak`
  - `no_delta_streak`
- Team HUD 最小字段：
  - `team_state`
  - `terminal_status`
  - `review_gates`
  - `fix_loops`
  - `roles[*].latest_event`
  - `roles[*].artifacts`

人类面保持摘要；全量细节通过 `--json` 与 artifacts 查看。

### FR-012 兼容层必须默认不干扰新用户

首次接入项目默认体验必须保持：

`prd -> user-story -> test-case -> implement -> qa -> release`

并且不应先引导：

- `skill bind`
- `profile create`
- `orchestrate run`
- external adapter registry 心智

### FR-013 必须新增并行 HUD PRD 作为实现输入

`v1.3.3` 必须在同版本包内提供并行 PRD，专门约束 HUD 的极简场景设计与实现切片：

- 目标：`minimal-hud` 只做状态压缩，不做新产品面
- 约束：不新增主命令，不引入 TUI/dashboard 依赖
- 实现切片：渲染器、状态聚合、命令挂接、字段补齐、场景测试
- 文档路径：`docs/beacon/archive/v1.3.3/prd/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.md`

### FR-014 必须新增并行 Memory/Friction Evolution Toolkit PRD

`v1.3.3` 必须在同版本包内提供并行 PRD，约束“记忆进化 + 摩擦错误演进”Toolkit：

- 定位：可选 analysis toolkit，与主链 `6+3` 并行，不替代主链
- 并行：与 `beacon-toolkit-lighthouse` 并行运行，静态结构图与动态摩擦候选在报告层汇合
- 复用：优先复用 `remember/recall/workflow_memory/debug_feedback/learning_loop`
- 约束：不得新增第二套 memory plane，不得把 toolkit 升级为公开主命令面
- 文档路径：`docs/beacon/archive/v1.3.3/prd/beacon-v1.3.3-memory-friction-evolution-toolkit.md`

### FR-015 必须新增 `beacon-prd-bootstrap` 人类 skill（可选）

`v1.3.3` 必须新增一个可选人类 skill：`beacon-prd-bootstrap`，用于一键编排 requirement 三件套：

- 目标：在不新增公开一级命令前提下，一键生成 `prd + user-story + test-case`
- 定位：optional skill，不替代主 `6+3`，仅降低 requirement 启动摩擦
- 命令契约（建议）：
  - `beacon-prd-bootstrap run "<feature>" --desc "<需求描述>" --version <v> --dry-run`
  - `beacon-prd-bootstrap run "<feature>" --desc "<需求描述>" --version <v> --apply --no-overwrite`

风险防线（默认必须生效）：

1. 前置门禁：先执行 `beacon doctor verify-context --project-root . --strict`
2. 双阶段执行：默认 `dry-run`，必须显式 `--apply` 才落盘
3. 防覆盖策略：默认 `--no-overwrite`，遇到既有文件阻断并给单一恢复命令
4. 原子写入：临时文件写入后统一替换，失败不留半成品
5. 跨文档一致性：`feature/version` 一致，`AC -> test-case` 映射完整
6. 质量阈值门控：禁止空模板/未完成占位符超阈值产物落盘
7. 可回滚可追踪：落盘 `.beacon/state/prd-bootstrap/<run-id>.json`
8. 并发锁：执行期间持有 `.beacon/state/locks/prd-bootstrap.lock`

### FR-016 Codex 输入框下固定 HUD 必须通过 hook 自动注入

`v1.3.3` 对 HUD 的“极简”要求必须覆盖 Codex 宿主输入面：

1. 目标体验：
   - 在 Codex 会话中，输入框下方稳定看到 Beacon 极简 HUD（1-3 行）
   - HUD 文本必须来自 `minimal_hud` 同一数据契约，禁止双源文案
2. 触发事件（最小）：
   - `UserPromptSubmit`：每次提交用户输入时刷新 HUD
   - 会话刷新事件：至少支持 `SessionStart/SessionResume/SessionRefresh` 中的可配置集合
3. 输出契约：
   - hook 输出必须包含 `hookSpecificOutput.additionalContext`
   - 内容必须是极简 HUD 行（S1-S6 契约），不得塞入大段解释文本
4. 失败退化：
   - hook 失败时不得阻断用户输入提交流程
   - 降级为空 HUD + debug 事件落盘
5. 治理边界：
   - 不自动改写用户全局 `~/.codex` hook 配置
   - 安装/校验流程统一走 `beacon doctor` 子命令

## 5. 瘦身改造清单

### A. 必须收敛

1. README 主路径里的 `skill/profile/orchestrate` 推荐流程
2. `qa` 主路径中的隐式 project orchestration 自动执行
3. `ralph-bridge` 作为正式能力名词的存在感
4. tests 中把 `gstack/omx/omc` 视为 core runner 的断言
5. builtin adapters 中 external runner 的默认内置地位
6. HUD 输出中超出极简场景契约的冗余展示

### B. 应降级为 compatibility

1. `implement_adapters` 中 external builtin adapters
2. `skill registry` 中 external skill 的正式产品化叙事
3. `project_skills.run_profile_orchestration()` 的默认调用地位
4. README 中面向普通用户的 project-aware skill 文案
5. `ralph-bridge` 命令面叙事

### C. 可保留

1. host-native readiness/delegation precheck
2. `team` / `qa-team` 作为隐藏机器面能力
3. project contract / required evidence / required cases
4. external adapter dry-run/detect 能力（仅 compatibility plane）
5. `doctor` 的 compatibility migration 能力作为唯一官方迁移入口

### D. 新增迁移切片（doctor）

1. `doctor migrate-compat --dry-run`：扫描 + 计划，不改写
2. `doctor migrate-compat --apply`：执行迁移并产出报告
3. `doctor` 迁移后验证：校验 core/compat 边界
4. `qa` 阻断推荐命令统一回指 doctor 迁移入口

### E. 新增 HUD 并行 PRD 切片

1. 在 `v1.3.3/prd/` 增加 HUD 并行 PRD
2. 主 PRD 与 HUD 并行 PRD 互相引用，避免单文档过载
3. HUD 场景与实现约束以并行 PRD 为准，主 PRD 保留总要求

### F. 新增 Memory/Friction Evolution Toolkit 并行 PRD 切片

1. 在 `v1.3.3/prd/` 增加 toolkit 并行 PRD
2. 与 `beacon-toolkit-lighthouse` 并行输出 single-file artifacts
3. 候选建议必须包含 `evidence_refs + recommended_command`
4. 记忆写回必须复用 `remember add --upsert`，不得创建新 memory silo

### G. 新增 `beacon-prd-bootstrap` 切片

1. 新增可选人类 skill `beacon-prd-bootstrap`
2. 默认 `dry-run`，显式 `--apply` 才允许写入
3. 默认 `--no-overwrite`，阻断覆盖风险
4. 失败即停并输出单一恢复命令
5. 输出 state artifact 与回滚清单

## 6. 非功能约束

1. 不破坏当前 `implement` 三模式主线
2. 不破坏 `qa` 对冻结材料的正式验收能力
3. 不破坏真实项目需要的 contract drift/evidence gate
4. 收敛动作必须可审计、可测试、可回退
5. 不得在 `v1.3.3` 再引入新的公开 bridge/runtime 命令
6. `doctor` 迁移必须支持 dry-run 与回滚清单
7. HUD 增强不得引入 TUI/dashboard 前置依赖
8. toolkit 增强不得扩张主 `6+3`，仅允许在 `labs/hidden` analysis 面暴露
9. `beacon-prd-bootstrap` 只能作为 optional skill，不得新增公开一级命令
10. `beacon-prd-bootstrap` 必须默认 `dry-run + no-overwrite + context strict verify`

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 真实项目仍依赖旧 profile/orchestration 路径 | 高 | 通过 `doctor migrate-compat` 提供扫描、迁移、验证与回滚点 |
| 收敛过快导致旧测试大面积失效 | 中 | 先拆分 core/compatibility tests，再删旧断言 |
| 文档与代码不同步 | 高 | README/help/tests/skill docs 同步收敛 |
| project contract 和 external execution 耦合未拆干净 | 高 | 先完成 contract/execution 解耦，再默认关闭隐式 external orchestration |
| HUD 字段扩张导致人类面噪音上升 | 中 | 人类面维持摘要，细节仅进 JSON/artifact |
| toolkit 与现有 learning_loop 重叠导致重复建设 | 中 | 先做薄封装，复用 remember/recall/debug_feedback/learning_loop 数据面 |
| `beacon-prd-bootstrap` 误写/覆盖导致 requirement 漂移 | 高 | 强制 `doctor verify-context --strict` + `dry-run/apply` + `no-overwrite` + 原子写入 + 一致性校验 + 锁 |

## 8. 成功标准

1. Beacon core 主叙事只剩 `6+3`
2. 默认 `implement/qa` 不再依赖 external skill orchestration
3. `qa` 不再隐式自动执行 external orchestration，阻断时统一推荐 doctor 迁移命令
4. external adapters 不再作为 core builtin 默认面
5. `ralph-bridge` 不再作为正式主能力出现
6. README/help 不再把 `skill/profile/orchestrate` 当普通用户主路径
7. 测试明确分成 core 与 compatibility 两层
8. `doctor` 完成兼容迁移全链路（scan/plan/apply/verify/report）
9. Ralph HUD 与 Team HUD 在保持轻量前提下提供稳定闭环观测字段
10. HUD 满足 S1-S6 场景与 1-3 行预算约束
11. 并行 HUD PRD 已纳入 `v1.3.3` 正式 requirement 包
12. 并行 toolkit PRD 已纳入 `v1.3.3` 正式 requirement 包
13. toolkit 可基于真实 memory/debug 数据输出 Top-N 摩擦演进候选
14. toolkit 与 lighthouse 可并行运行，且不影响主 `6+3` 路径
15. `beacon-prd-bootstrap` 可一键生成 `prd/user-story/test-case` 且默认不覆盖
16. `beacon-prd-bootstrap` 运行全程可追踪、可回滚、可阻断半成品

---

**Created**: 2026-04-16  
**Version**: v1.3.3  
**Status**: Draft  
**Memory Context**: N/A
