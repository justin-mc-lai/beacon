# Boundaries: Beacon v1.0.0

**版本**: v1.0.0
**日期**: 2026-02-28

---

## In Scope

### 功能范围

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 需求工作流 | think → user-story → prd → test-case 主路径 | Must |
| 范围守护 | Scope Guard 越界检测与记录 | Must |
| 交付门控 | Gate Pass/Blocked/Cancelled 终态判定 | Must |
| 证据治理 | raw-command-log/evidence-manifest/gate-report | Must |
| 版本演进 | version/roadmap/release/evolution-summary | Should |
| CLI 入口 | beacon 命令行工具 | Must |
| Skill 集成 | /beacon:* 技能调用 | Must |

### 交付产物

- PRD 文档: `docs/product/v1.0.0/prd/beacon-core.md`
- 用户故事: `docs/product/v1.0.0/user-story/beacon-core.md`
- 测试用例: `docs/product/v1.0.0/qa/test-cases/beacon-core.md`
- 证据三件套
- Gate 终态报告

---

## Out of Scope

| 功能 | 原因 |
|------|------|
| 具体代码实现 | 定位为产品工作流工具，非开发框架 |
| 第三方集成 | v1.0.0 聚焦核心能力 |
| 云服务化 | 本地工具，暂无SaaS计划 |
| 移动端 | 非核心场景 |

---

## Done Criteria

| 条件 | 验证方式 |
|------|----------|
| 主流程可执行 | `/beacon:workflow` 无报错 |
| 产物完整 | US/PRD/TC 三类文档齐全 |
| 证据可查 | 证据三件套可生成 |
| 门控可用 | Gate 判定准确 |
| 版本管理可用 | version/roadmap 命令正常 |

---

## Blocked Criteria

| 条件 | 状态 |
|------|------|
| open_question.blocking=true 未关闭 | Blocked |
| critical/high 冲突未解决 | Blocked |
| AC→TC 映射缺失 | Blocked |
| boundaries.md 关键字段缺失 | Blocked |
| 架构关键产物缺失 | Blocked |

---

## Dependencies

- PTK v3.7.0 成熟能力作为基础
- Claude Code / Codex 环境
- Shell 脚本执行环境
