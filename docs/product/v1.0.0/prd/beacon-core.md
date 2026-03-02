# PRD: Beacon v1.0.0 - AI 驱动的产品交付工具

**状态**: Draft
**来源**: think_vnext
**版本**: v1.0.0
**日期**: 2026-02-28

---

## 1. 背景与目标

### 1.1 背景

Beacon 从 product-toolkit 升级而来，是面向 AI 时代的智能产品工作流工具。在当前 AI 浪潮下，产品与研发协作面临新的挑战：

- 需求迭代速度加快，范围漂移风险增加
- AI 辅助开发需要更明确的交付标准
- 跨团队协作需要可追溯的证据链

### 1.2 目标

**核心目标**：把「需求想法」稳定地转成「可交付证据」

**成功指标**：
- 需求文档完整率 ≥ 95%
- 范围偏离检出率 ≥ 90%
- 交付终态判定准确率 ≥ 95%
- 证据链完整率 100%

---

## 2. 用户与价值

### 2.1 目标用户

| 用户角色 | 核心需求 |
|----------|----------|
| 产品经理 | 快速产出标准需求文档，清晰定义范围 |
| 研发工程师 | 明确验收标准，减少返工 |
| 项目经理 | 实时掌握交付状态，证据可追溯 |
| AI 开发者 | 结构化输入，标准化输出，接入 AI 流程 |

### 2.2 用户价值

1. **效率提升** — 一键生成 US/PRD/TC 产物链，减少手工切换
2. **范围保障** — AI 驱动的越界检测与预警，避免范围漂移
3. **交付确定性** — 明确的终态判定（Pass/Blocked/Cancelled）
4. **证据可信** — 完整证据链，支持审计与复盘

---

## 3. 范围定义

### 3.1 In Scope

| 功能模块 | 描述 |
|----------|------|
| 需求工作流 | think → user-story → prd → test-case 主路径 |
| 范围守护 | Scope Guard 越界检测与 deviations/confirmations 记录 |
| 交付门控 | Gate Pass/Blocked/Cancelled 终态判定 |
| 证据治理 | raw-command-log.jsonl / evidence-manifest.json / gate-consistency-report.json |
| 版本演进 | version / roadmap / release / evolution-summary |
| CLI 入口 | beacon 命令行工具，统一执行入口 |
| Skill 集成 | /beacon:workflow、/beacon:gate 等技能 |

### 3.2 Out of Scope

- 具体的代码实现与测试执行
- 第三方项目管理工具深度集成
- 多租户/云服务化部署
- 移动端应用

---

## 4. 功能需求

### 4.1 需求工作流

**FR-001**: 主路径自动化

- 支持 `think` → `user-story` → `prd` → `test-case` 串联执行
- 默认自动执行 Gate 收口
- 输出目录结构: `docs/product/v{version}/{prd,user-story,qa/test-cases}/`

**FR-002**: 分步执行

- 支持独立命令: `/beacon:think`、`/beacon:user-story`、`/beacon:prd`、`/beacon:test-case`
- 每步产出符合标准模板

### 4.2 范围守护 Scope Guard

**FR-003**: 越界检测

- 监控需求实现过程中的范围偏离
- 支持 strict/normal 模式
- 越界时强制记录 `deviations` / `confirmations`

**FR-004**: AI 预警（未来扩展）

- LLM 预测越界风险
- v1.0.0 仅支持规则检测

### 4.3 交付门控 Gate

**FR-005**: 终态判定

- 执行结果判定: Pass / Blocked / Cancelled
- 阻断规则:
  - open_question.blocking=true 且未关闭
  - critical/high 冲突未关闭
  - AC→TC 映射缺失
  - boundaries.md 或 terminal.json 关键字段缺失

**FR-006**: 自动收口脚本

- `workflow_gate_autorun.sh` 自动执行
- 输出: gate-consistency-report.json

### 4.4 证据链治理

**FR-007**: 证据三件套

| 证据类型 | 文件 | 描述 |
|----------|------|------|
| 命令日志 | raw-command-log.jsonl | 所有执行的命令记录 |
| 证据清单 | evidence-manifest.json | 产物完整性校验 |
| 门控报告 | gate-consistency-report.json | 终态一致性检查 |

### 4.5 版本演进

**FR-008**: 版本管理命令

| 命令 | 功能 |
|------|------|
| `/beacon:version` | 创建/管理版本 |
| `/beacon:roadmap` | 路线图规划 |
| `/beacon:release` | 发布变更生成 |
| `/beacon:evolution-summary` | 版本演进总结 |

---

## 5. 非功能需求

### 5.1 性能要求

- 单次 workflow 执行 ≤ 60 秒（不含 AI 调用）
- CLI 响应时间 ≤ 2 秒

### 5.2 可用性

- 错误信息友好，定位快速
- 支持 `--help` 和 `--verbose`

### 5.3 安全

- 无敏感数据存储
- 本地文件操作，无网络强制依赖

---

## 6. 发布与回滚

### 6.1 发布策略

- GitHub Release 规范化
- 版本号语义化 (SemVer)
- 变更日志自动生成

### 6.2 回滚策略

- 支持旧版本配置文件回滚
- 文档产物不涉及运行时回滚

---

## 7. 风险与未决问题

### 7.1 已知风险

| 风险 | 级别 | 缓解措施 |
|------|------|----------|
| AI 驱动的范围预测准确率不足 | Medium | v1.0.0 仅用规则，逐步引入 AI |
| Skill 命令兼容性 | Low | 与 product-toolkit 保持接口兼容 |

### 7.2 待决问题

| 问题 | 状态 | Owner |
|------|------|-------|
| CLI 技术栈选型（Shell vs Python） | Open | TBD |
| Skill 命名空间冲突 | Open | TBD |

---

## 8. 交付判定

### 8.1 Blocked 条件

- open_question.blocking=true 且未关闭
- critical/high 冲突未关闭
- AC→TC 映射缺失
- boundaries.md 或 terminal.json 关键字段缺失
- 架构关键产物缺失

### 8.2 Warn 条件

- medium/low 冲突未关闭（保留风险记录）
- 非关键字段缺失

### 8.3 验收标准

| 验收项 | 标准 |
|--------|------|
| 主流程可执行 | `/beacon:workflow` 完整执行无报错 |
| 产物完整 | US/PRD/TC 三类文档均生成 |
| 证据可查 | 证据三件套均可生成 |
| 门控可用 | Gate 判定结果准确 |

---

## 附录：目录结构

```
beacon/
├── docs/product/v1.0.0/
│   ├── prd/beacon-core.md
│   ├── user-story/
│   ├── qa/test-cases/
│   ├── execution/
│   │   ├── boundaries.md
│   │   └── terminal.json
│   └── architecture/
├── skills/
│   ├── workflow/SKILL.md
│   ├── gate/SKILL.md
│   └── ...
├── scripts/
│   └── workflow_gate_autorun.sh
└── beacon (CLI 入口)
```
