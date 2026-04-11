# 测试用例：Beacon v1.3.0 简化版 Codex 原生子代理

**Feature**: `beacon-v1.3.0-simplified-codex-native-subagents`  
**Version**: `v1.3.0`  
**Date**: `2026-04-10`  
**Status**: `planning line`

## TC-001：规划类 prompt 必须进入 `version`，不能误入 QA

- Given：输入包含 `下一版本`、`演进`、`subagent`
- When：调用 `beacon ask` 或 `beacon prompt optimize`
- Then：路由结果应优先命中 `version`

## TC-002：阶段级 subagent_mode 必须显式开启

- Given：某个阶段命令未启用 `subagent_mode`
- When：命令执行
- Then：必须保持单阶段单面路径，不得隐式进入子代理

## TC-003：非法阶段角色必须阻塞

- Given：某阶段收到未注册角色
- When：Beacon 尝试进入委托
- Then：必须在正式 writeback 前阻塞

## TC-004：没有 evidence 不得正式回写

- Given：阶段已进入子代理委托
- When：worker 输出缺失或格式不合法
- Then：Beacon 必须标记 blocked，而不是继续回写正式材料

## TC-005：`implement run` 需要保留现有 runner

- Given：已有 `native-single` 与 `native-team`
- When：`v1.3.0` 落地新的子代理能力
- Then：现有 runner 仍必须保持兼容

## TC-006：`implement run` 必须先证明第一条 Codex-native 多代理路径

- Given：`implement run --runner codex-subagents`
- When：执行完成
- Then：Beacon 必须先写 plan/evidence，再进入 canonical writeback

## TC-007：QA 子代理阻塞时必须生成 repair handoff

- Given：`qa` 子代理验证出 critical blocker
- When：Beacon 汇总 evidence
- Then：正式 QA 输出必须包含 blocker summary 与 repair handoff

## TC-008：现有版本字段必须保持精准语义

- Given：Beacon 解析 project version context
- When：`help` / `status` / `doctor` / `init` / `version` 消费 version truth
- Then：`package_version`、`runtime_version`、`docs_default_line`、`current_runtime_release_line`、`planning_lines`、`partial_runtime_supplement_lines` 必须保持稳定且互不重叠

## TC-009：文档目标解析与运行目标解析必须显式分离

- Given：某个命令以 `auto/latest` 请求 docs
- When：Beacon 解析目标
- Then：必须走 docs-target 语义，不得静默复用 runtime-target 语义

## TC-010：下一版本 prompt 必须优先命中 planning-line 语义

- Given：输入明确表达下一版本规划
- When：`beacon ask` 或 `beacon prompt optimize` 生成推荐命令
- Then：目标版本应优先是 canonical planning line，而不是 current runtime release line

## TC-011：未来版本字段漂移必须可审查

- Given：Beacon 源码新增版本状态字段或新的 resolver 分支
- When：未同步更新 canonical contract
- Then：review / gate / tests 必须把它视为 semantic drift，而不是默认接受

## TC-012：人类主读材料必须默认中文

- Given：`v1.3.0` 的 `PRD`、`用户故事`、`测试用例`
- When：生成或维护人类主读材料
- Then：默认语言应为中文

## TC-013：机器工件允许默认英文

- Given：`.machine`、runtime state、JSON contract
- When：写入机器工件
- Then：可以继续保持英文键名与稳定结构

## TC-014：中文镜像与英文 contract 必须保持同步

- Given：`beacon/version-semantics.json` 与 `docs/beacon/v1.3.0/execution/version-semantics-contract.md`
- When：任一侧发生变化
- Then：统一渲染或测试必须确保两侧同步，否则测试失败

## TC-015：未来 contract artifact 必须复用四件套规范

- Given：新增任意 contract 类 artifact
- When：进入正式版本线
- Then：必须同时存在 source JSON、中文镜像 Markdown、render 函数与 drift test

## TC-016：`implement plan` 必须优先输出 team-mode 方案

- Given：用户进入 `implement plan`
- When：Beacon 生成执行方案
- Then：应优先给出 team-mode 的显性稳定触发方式与角色拆解

## TC-017：`implement run` 必须优先使用 codex-subagents

- Given：用户进入 `implement run`
- When：Beacon 解析默认执行路径
- Then：应优先落到 `codex-subagents` / team-mode 路径

## TC-018：`qa` 必须提供显性 team-mode 触发

- Given：用户进入 `qa`
- When：Beacon 生成执行建议或运行路径
- Then：必须提供 team-mode 的显性稳定触发方式

## TC-019：implement 与 qa 必须上下文隔离

- Given：同一 feature 先执行 implement，再执行 qa
- When：QA 开始运行
- Then：QA 只能消费正式工件、evidence refs、handoff 摘要，不得直接继承 implement 私有上下文
