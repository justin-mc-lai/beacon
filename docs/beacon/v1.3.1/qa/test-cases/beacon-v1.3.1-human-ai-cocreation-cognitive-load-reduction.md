# 测试用例：Beacon v1.3.1 人机共创心智包袱减重

**Feature**: `beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction`  
**Version**: `v1.3.1`  
**Date**: `2026-04-12`  
**Status**: `accepted supplement line`

## TC-001：人类主闭环必须收敛为六段

- Given：人类阅读 Beacon 主帮助或主文档
- When：查找推荐主命令
- Then：核心主线必须收敛到 `prd -> user-story -> test-case -> implement -> qa -> release`

## TC-002：`brainstorm` 必须嵌入 `prd -> user-story`

- Given：用户进入需求探索
- When：执行 `prd` / `user-story` 链路
- Then：产物必须体现 brainstorm 带来的业务发散与收敛结果

## TC-003：`implement` 对人类保持单入口

- Given：用户要进入实现闭环
- When：查看人类主文档或帮助面
- Then：主入口应是 `implement`，而不是强迫用户理解内部 team lane

## TC-004：`qa` 对人类保持单入口

- Given：用户要进入验收闭环
- When：查看人类主文档或帮助面
- Then：主入口应是 `qa`，而不是强迫用户直接管理 `qa-team` 细节

## TC-005：QA 每一轮都必须带来新的价值

- Given：连续两轮 QA
- When：比较新旧 QA 输出
- Then：新一轮必须至少新增发现、覆盖、边界澄清或 repair handoff

## TC-006：learning / auto research 必须围绕冻结用户故事

- Given：QA 内部使用 learning / auto research
- When：检查其输入与输出
- Then：必须围绕冻结用户故事提升 coverage，不得偏离需求包

## TC-007：旧项目物料必须支持按版本同步

- Given：项目运行较新的 Beacon runtime，但文档包较旧
- When：执行版本指定的物料同步
- Then：`.machine/user-story` 与 `.machine/qa` 必须可被一键更新对齐

## TC-008：极简 CLI 不能丢失闭环能力

- Given：Beacon 探索极简命令行
- When：检查人类主闭环
- Then：仍必须完整覆盖 `prd/user-story/test-case/implement/qa/release`

## TC-009：人类交付与机器协作必须分层

- Given：Beacon 内部继续使用 team / learning / auto research
- When：检查正式交付面
- Then：人类只需对正式文档交付负责，机器协作细节不应成为人类主负担

## TC-010：需求不清不得冻结

- Given：`prd` / `user-story` 中仍存在遗漏点、不清晰点、问号点、未澄清点或需求不明点
- When：尝试 freeze
- Then：Beacon 必须阻塞，不得让需求包进入冻结

## TC-011：需求审核必须显式产出未决项清单

- Given：用户处于 `brainstorm -> prd -> user-story` 探索阶段
- When：检查需求审核输出
- Then：必须存在可收口的未决项/疑问项清单，而不是把问题隐含留在正文里

## TC-012：每个版本的技术评审必须给出确定性实现面

- Given：某版本准备进入 `implement`
- When：检查技术评审产物
- Then：必须明确 git 分支、worktree、隔离环境与实现服务目录

## TC-013：monorepo / multi-service 项目必须明确具体服务

- Given：项目为 monorepo 或多服务，例如 `rolo`
- When：检查版本级技术评审
- Then：必须明确具体需要改动的服务、只读参考服务与服务边界

## TC-014：技术评审未完成不得进入正式实现

- Given：版本级技术评审尚未明确 deterministic implementation contract
- When：进入 `implement`
- Then：Beacon 必须阻塞或明确返回“技术评审未完成”

## TC-015：同一版本必须允许多个并行 feature package

- Given：同一个版本下创建多个 feature 的 `prd / user-story / test-case`
- When：检查对应文档根
- Then：这些 feature package 必须共存，且不应互相覆盖

## TC-016：每个并行 feature package 必须保持自己的一对一文档链

- Given：同一个版本下存在多个 feature package
- When：检查某个 feature 的 `prd / user-story / test-case`
- Then：它们必须通过相同 `feature slug` 串起，不得跨 feature 混链

## TC-017：release 前必须存在独立 change 文档和版本演进图

- Given：某个版本准备进入 release
- When：检查版本交付物
- Then：必须存在独立 `change` 文档，并且能看到新增 / 删除 / 修复和版本路线演进图
