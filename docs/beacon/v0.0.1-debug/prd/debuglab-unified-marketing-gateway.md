# PRD: debuglab-unified-marketing-gateway

## 1. Overview

- 目标版本: `v0.0.1-debug`
- 需求描述: 统一 Rolo Debug Lab 调试入口：仅 marketing_sys 保留 UAT 调试入口；其他 rolo 子服务禁止修改 service.yaml 引入新的公网 debug/gateway 路由，不新增 order-svr 等服务的独立 debuglab 网关配置。通过 marketing 后端内网调试能力统一代理数据库只读查询、服务日志查询、受控命令执行与跨子服务 HTTP 调试；非 marketing 子服务仅允许极简单文件实现受控 debug 能力接入，不改变现有业务网关路由。开发车道固定为本地 debug/debuglab 分支，仅允许本地分支合并到 uat/testing，绝对禁止回灌 feature/master/main/prod 正式开发分支。请生成独立 v0.0.1-debug requirement line，并与现有 v1.3.3 业务需求彻底隔离。

## 2. Scope

- In scope: `debuglab-unified-marketing-gateway` 的核心业务流程与必要风控校验。
- Out of scope: 与该需求无关的跨域重构或新增平台能力。

## 3. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | 用户可以完成「debuglab-unified-marketing-gateway」主流程，满足：统一 Rolo Debug Lab 调试入口：仅 marketing_sys 保留 UAT 调试入口；其他 rolo 子服务禁止修改 service.yaml 引入新的公网 debug/gateway 路由，不新增 order-svr 等服务的独立 debuglab 网关配置。通过 marketing 后端内网调试能力统一代理数据库只读查询、服务日志查询、受控命令执行与跨子服务 HTTP 调试；非 marketing 子服务仅允许极简单文件实现受控 debug 能力接入，不改变现有业务网关路由。开发车道固定为本地 debug/debuglab 分支，仅允许本地分支合并到 uat/testing，绝对禁止回灌 feature/master/main/prod 正式开发分支。请生成独立 v0.0.1-debug requirement line，并与现有 v1.3.3 业务需求彻底隔离。 |
| FR-002 | AC-002 | 输入校验规则明确，非法输入会返回可读错误。 |
| FR-003 | AC-003 | 依赖失败时系统可恢复并提供下一步指引。 |
| FR-004 | AC-004 | 关键步骤具备可追踪日志与最小化诊断信息。 |
| FR-005 | AC-005 | 仅授权用户可执行敏感操作，越权请求被拒绝。 |

## 4. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | happy-path | 用户可以完成「debuglab-unified-marketing-gateway」主流程，满足：统一 Rolo Debug Lab 调试入口：仅 marketing_sys 保留 UAT 调试入口；其他 rolo 子服务禁止修改 service.yaml 引入新的公网 debug/gateway 路由，不新增 order-svr 等服务的独立 debuglab 网关配置。通过 marketing 后端内网调试能力统一代理数据库只读查询、服务日志查询、受控命令执行与跨子服务 HTTP 调试；非 marketing 子服务仅允许极简单文件实现受控 debug 能力接入，不改变现有业务网关路由。开发车道固定为本地 debug/debuglab 分支，仅允许本地分支合并到 uat/testing，绝对禁止回灌 feature/master/main/prod 正式开发分支。请生成独立 v0.0.1-debug requirement line，并与现有 v1.3.3 业务需求彻底隔离。 |
| AC-002 | validation | 输入校验规则明确，非法输入会返回可读错误。 |
| AC-003 | error-handling | 依赖失败时系统可恢复并提供下一步指引。 |
| AC-004 | observability | 关键步骤具备可追踪日志与最小化诊断信息。 |
| AC-005 | security | 仅授权用户可执行敏感操作，越权请求被拒绝。 |

## 5. Risks

- 需求理解偏差：通过 AC 与 TC 一一映射降低语义漂移。
- 交付回归风险：通过测试用例覆盖主流程、异常路径与安全边界。

## 6. Release Guard

- 通过 `qa` 验证 AC 关闭状态后方可进入 release 评审。
