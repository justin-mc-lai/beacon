# 测试用例：Beacon v1.3.3 核心瘦身与外部 skill 降级

**Feature**: `beacon-v1.3.3-core-slimming-and-external-skill-demotion`  
**Version**: `v1.3.3`  
**Date**: `2026-04-15`  
**Status**: `planning line`

## 测试目标

这组测试用例验证：

1. Beacon 默认主面是否已回到 `6+3`
2. external skill / runner / orchestration 是否被降级为 compatibility
3. `qa` 是否停止隐式自动执行 external orchestration
4. docs / help / tests / discovery 是否一致收口
5. `beacon-prd-bootstrap` 是否在一键闭环同时满足默认安全防线

## 测试用例

## TC-001：默认主叙事必须保持 `6+3`

- Given：普通用户查看 Beacon 默认文档与帮助面
- When：阅读 README、help、host-visible skill 文案
- Then：默认主路径必须是 `prd -> user-story -> test-case -> implement -> qa -> release`
- And：辅助面必须是 `help / status / doctor`
- Covers：`AC-001`

## TC-002：external runners 必须降级为 compatibility

- Given：维护者检查 runner narrative 与 adapter docs
- When：查看 runner 列表、README、help、skill narrative
- Then：`omx / omc / gstack` 必须被标记为 compatibility
- Covers：`AC-002`

## TC-003：默认实现面必须宿主原生优先

- Given：用户未显式选择 external runner
- When：进入 `implement single/team/ralph`
- Then：默认执行面必须保持 host-native 优先
- Covers：`AC-003`

## TC-004：`qa` 默认不得隐式自动执行 external orchestration

- Given：项目存在 profile 与 external orchestration 配置
- When：用户以默认模式执行 `qa`
- Then：系统不得自动执行 external orchestration
- And：若需要 compatibility plane，必须要求显式开启
- Covers：`AC-004`

## TC-005：`ralph-bridge` 必须退出正式主叙事

- Given：检查命令文案、README、release/summary 叙事
- When：评估 `ralph-bridge` 的位置
- Then：它不得再作为未来主线能力出现
- Covers：`AC-005`

## TC-006：文档主面必须只教学 `6+3`

- Given：阅读 README、help、skills/beacon 文案
- When：查找默认 onboarding 路径
- Then：不得把 `skill / profile / orchestrate` 当普通用户必经主路径
- Covers：`AC-006`

## TC-007：测试必须分成 core 与 compatibility

- Given：检查测试目录与断言责任
- When：定位 `gstack / omx / omc` 相关测试
- Then：这些断言必须归入 compatibility，而不是 core
- Covers：`AC-007`

## TC-008：discover/registry 输出必须分层

- Given：执行 skill detect / registry / discovery
- When：查看输出
- Then：必须能清楚区分 builtin core 与 external compatibility
- Covers：`AC-008`

## TC-009：project contract 必须与 external orchestration 解耦

- Given：真实项目存在 required evidence / required cases / contract drift
- When：不启用 external orchestration
- Then：contract evaluation 仍然可运行
- Covers：`AC-009`

## TC-010：新用户默认路径不得先接触 compatibility plane

- Given：首次接入 Beacon 的轻量项目
- When：按默认 onboarding 路径使用 Beacon
- Then：不应先被引导到 `skill bind / profile create / orchestrate run`
- Covers：`AC-010`

## TC-011：`beacon-prd-bootstrap` 必须默认安全并可回滚

- Given：项目中存在 `beacon-prd-bootstrap` optional skill
- When：执行 `beacon-prd-bootstrap run "<feature>" --desc "<需求描述>" --version v1.3.3`（未显式 apply）
- Then：系统必须执行 `doctor verify-context --strict` 并仅输出 dry-run 计划，不落盘文档
- And：执行 `--apply` 但目标文档已存在时，默认 `--no-overwrite` 必须阻断并返回单一恢复命令
- And：写入阶段必须使用原子写入，异常中断后不得出现半成品文档
- And：运行后必须有 `.beacon/state/prd-bootstrap/<run-id>.json` 与回滚清单
- And：运行期间必须持有 `.beacon/state/locks/prd-bootstrap.lock`
- Covers：`AC-011`

## 建议执行节奏

### Round 1

- 验证默认文档/帮助面是否回到 `6+3`
- 验证 external plane 是否已标记 compatibility

### Round 2

- 验证 `qa` 默认是否停止隐式 external orchestration
- 验证 runner 默认面是否仍是 host-native

### Round 3

- 验证测试分层与 discovery/registry 分层
- 验证 contract plane 与 external orchestration 是否完成解耦

### Round 4

- 验证 `beacon-prd-bootstrap` 在默认参数下仅 dry-run
- 验证 apply 覆盖阻断、原子写入、锁和回滚清单是否完整
