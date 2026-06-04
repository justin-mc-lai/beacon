# Beacon v1.1.3 命令收口清单（保留 / 迁出 / 废弃）

**当前命令总数**: 40  
**目标**: 把 Beacon 命令面收口到 `core + support`，并把 `labs + bridge` 明确迁出默认叙事。

---

## 1. 汇总

| 决策 | 数量 | 说明 |
|------|------|------|
| 保留 | 22 | 保留在 Beacon 默认产品表面（其中部分为 support/internal） |
| 迁出 | 15 | 迁出到 `labs` 或 `bridge` 叙事/包 |
| 废弃 | 3 | 合并或仅保留兼容别名 |

---

## 2. 保留命令

| 子命令 | 当前角色 | 目标层 | 决策 | 理由 |
|-------|----------|--------|------|------|
| `ask` | 自然语言入口 | support | 保留 | 作为单一 NL facade，收敛 `prompt` |
| `auto-test` | 自动化测试证据 | core | 保留 | 主链闭环核心能力 |
| `debug` | 调试/诊断辅助 | support-internal | 保留 | 支撑 router / feedback / runtime 诊断 |
| `doctor` | 环境/物料诊断 | support | 保留 | 维持可诊断性 |
| `evolution-summary` | 版本演进总结 | support | 保留 | 服务版本与复盘，不抢主叙事 |
| `feedback` | 反馈写回闭环 | support | 保留 | 支撑 evidence assimilation |
| `gate` | 门禁与阻断 | core | 保留 | 主链核心 |
| `init` | 项目初始化 | support | 保留 | 负责上下文与目录基座 |
| `prd` | 产品需求文档 | core | 保留 | 主链核心 |
| `prototype` | UI 原型参考实现 | core | 保留 | UI 型需求主链组成部分 |
| `recall` | 记忆检索 | support | 保留 | 支撑闭环追溯 |
| `release` | 放行清单 / 检查 | core | 保留 | 主链核心 |
| `remember` | 记忆写入 | support | 保留 | 支撑闭环追溯 |
| `report` | 运行与验收报告 | support | 保留 | 证据汇总出口 |
| `resume` | 恢复工作流 | support | 保留 | 闭环恢复能力 |
| `status` | 当前进度 / board | support | 保留 | 观测入口 |
| `test-case` | 测试用例 / AC 矩阵 | core | 保留 | 主链核心 |
| `test-progress` | 测试进度回写 | support | 保留 | 支撑 verify/release |
| `think` | 需求澄清/收敛 | core | 保留 | 主链起点 |
| `user-story` | 用户故事与 AC | core | 保留 | 主链核心 |
| `version` | 版本规划与演进 | support | 保留 | 版本治理能力 |
| `workflow` | 主链编排 | core | 保留 | Beacon 的中心骨架 |

---

## 3. 迁出命令（Labs）

| 子命令 | 当前角色 | 目标层 | 决策 | 理由 |
|-------|----------|--------|------|------|
| `analyze` | 竞品分析模板 | labs | 迁出 | 模板型能力，不是闭环内核 |
| `api-design` | API 设计模板 | labs | 迁出 | 模板型能力，适合外置 pack |
| `brainstorm` | 发散模板 | labs | 迁出 | 与 `think` 的收敛主链不同 |
| `data-dictionary` | 数据字典模板 | labs | 迁出 | 文档模板，不应污染 core |
| `design` | Design Thinking 模板 | labs | 迁出 | 研究模板，不是主链闭环能力 |
| `jtbd` | JTBD 模板 | labs | 迁出 | 方法论模板 |
| `kano` | Kano 模板 | labs | 迁出 | 方法论模板 |
| `moscow` | MoSCoW 模板 | labs | 迁出 | 方法论模板 |
| `persona` | Persona 模板 | labs | 迁出 | 模板能力 |
| `roadmap` | Roadmap 模板 | labs | 迁出 | 模板能力 |
| `ui-spec` | UI Spec 模板 | labs | 迁出 | 模板能力，非核心交付内核 |
| `wireframe` | Wireframe 模板 | labs | 迁出 | 模板能力 |

### Labs 迁出原则

- 不否定这些命令的价值；
- 只是不再让它们占用 Beacon core 心智预算；
- 适合迁入独立 skill pack 或 `beacon labs <cmd>` 命名空间。

---

## 4. 迁出命令（Bridge / Experimental）

| 子命令 | 当前角色 | 目标层 | 决策 | 理由 |
|-------|----------|--------|------|------|
| `ralph-bridge` | 与 OMC/OMX/外部 runtime 桥接 | bridge | 迁出 | 桥接型能力，不应成为默认主叙事 |
| `run` | workflow/team/bridge 统一入口 | bridge | 迁出 | 抽象层过高，容易与 core workflow 重叠 |
| `team` | 团队协作执行编排 | bridge | 迁出 | 已逼近 orchestrator 形态，与 Symphony 边界重叠 |

### Bridge 迁出原则

- 保留其存在价值；
- 但从 Beacon core narrative 中降级；
- 更适合独立 `beacon-bridge` / `beacon team-runtime` 方案，或直接交给更专门的 orchestrator。

---

## 5. 废弃 / 合并命令

| 子命令 | 当前角色 | 目标去向 | 决策 | 理由 |
|-------|----------|----------|------|------|
| `prompt` | prompt optimize / catalog | 合并到 `ask` | 废弃 | 与 `ask` 双入口重叠，用户心智浪费 |
| `save` | 会话状态存档 | 合并到 workflow memory / `remember` / `resume` | 废弃 | 在 memory 已存在前提下价值重叠 |
| `work` | `workflow start` 别名 | 保留兼容别名，长期移除 | 废弃 | 无独立语义，仅制造重复命名 |

---

## 6. 兼容策略建议

| 旧命令 | 过渡写法 | 最终方向 |
|--------|----------|----------|
| `beacon prompt optimize ...` | `beacon ask "..." --plan-only` | 合并到 ask |
| `beacon save` | `beacon remember ...` / `beacon resume ...` | 记忆与恢复统一 |
| `beacon work <feature>` | `beacon workflow start <feature>` | 只保留短期 alias |
| `beacon team ...` | `beacon-bridge team ...` / 外部 orchestrator | bridge 化 |
| `beacon run workflow ...` | `beacon workflow start/continue ...` | 语义回收至 workflow |
| `beacon ralph-bridge ...` | `beacon-bridge ralph ...` | bridge 化 |

---

## 7. 目标命令表面

### 7.1 用户默认看到的 Beacon

**主链**

- `think`
- `user-story`
- `prd`
- `prototype`
- `test-case`
- `workflow`
- `auto-test`
- `gate`
- `release`

**治理与观测**

- `status`
- `report`
- `doctor`
- `feedback`
- `remember`
- `recall`
- `resume`
- `version`
- `evolution-summary`
- `init`
- `test-progress`
- `ask`

### 7.2 不再默认主推的命令

- 全部模板型分析命令；
- 全部 bridge / team / runner 型命令；
- 全部重复入口型命令。
