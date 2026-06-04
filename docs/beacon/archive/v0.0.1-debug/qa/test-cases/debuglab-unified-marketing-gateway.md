# Test Cases: debuglab-unified-marketing-gateway

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | happy-path scenario | unit | 用户可以完成「debuglab-unified-marketing-gateway」主流程，满足：统一 Rolo Debug Lab 调试入口：仅 marketing_sys 保留 UAT 调试入口；其他 rolo 子服务禁止修改 service.yaml 引入新的公网 debug/gateway 路由，不新增 order-svr 等服务的独立 debuglab 网关配置。通过 marketing 后端内网调试能力统一代理数据库只读查询、服务日志查询、受控命令执行与跨子服务 HTTP 调试；非 marketing 子服务仅允许极简单文件实现受控 debug 能力接入，不改变现有业务网关路由。开发车道固定为本地 debug/debuglab 分支，仅允许本地分支合并到 uat/testing，绝对禁止回灌 feature/master/main/prod 正式开发分支。请生成独立 v0.0.1-debug requirement line，并与现有 v1.3.3 业务需求彻底隔离。 |
| TC-002 | AC-002 | validation scenario | unit | 输入校验规则明确，非法输入会返回可读错误。 |
| TC-003 | AC-003 | error-handling scenario | unit | 依赖失败时系统可恢复并提供下一步指引。 |
| TC-004 | AC-004 | observability scenario | unit | 关键步骤具备可追踪日志与最小化诊断信息。 |
| TC-005 | AC-005 | security scenario | unit | 仅授权用户可执行敏感操作，越权请求被拒绝。 |

## Execution Notes

- version: `v0.0.1-debug`
- 每个 AC 至少对应一个 TC，且必须可执行可验证。
