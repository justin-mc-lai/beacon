# Beacon 稳交付调研列表：Loop / 搜索 / 子代理 / 商业 Skill

> 生成日期：2026-07-20  
> 用途：支撑「Beacon 能力变稳 + 接入搜索 + 子代理并行 + 商业分析 skill」  
> 索引根：`/Users/apple/Developer/Personal/oss-sync`

## 1. oss-sync 录入状态

| Repo | Category | Classification | Status | Path |
|------|----------|----------------|--------|------|
| VoltAgent/awesome-claude-code-subagents | agents/agent-skills | canonical | **已在库** analysis=pending | agents/agent-skills/awesome-claude-code-subagents |
| VoltAgent/awesome-codex-subagents | agents/agent-skills | canonical | **已在库** analysis=complete | agents/agent-skills/awesome-codex-subagents |
| nicobailon/pi-subagents | agents/tools | canonical | **本次 import** | agents/tools/pi-subagents |
| linhh29/Skill_MAS | multi-agents | canonical | **本次 import** | multi-agents/Skill_MAS |
| dontbesilent2025/dbskill | agents/agent-skills | canonical | **已在库** analysis=complete | agents/agent-skills/dbskill |

### 建议后续动作

```bash
# 补分析（尤其 claude subagents 仍 pending）
python3 ~/.codex/skills/manage-oss-sync/scripts/manage_oss_sync.py analyze VoltAgent/awesome-claude-code-subagents --json
python3 ~/.codex/skills/manage-oss-sync/scripts/manage_oss_sync.py analyze nicobailon/pi-subagents --json
python3 ~/.codex/skills/manage-oss-sync/scripts/manage_oss_sync.py analyze linhh29/Skill_MAS --json
python3 ~/.codex/skills/manage-oss-sync/scripts/manage_oss_sync.py learn VoltAgent/awesome-codex-subagents --json
```

## 2. 对 Beacon / Loom 的使用映射

| 来源 | 对 Beacon | 对 Loom | 可直接用？ |
|------|-----------|---------|------------|
| awesome-codex-subagents | Codex host 角色库：search-specialist / multi-agent-coordinator / reviewer | 同构 | **角色提示可抄**；不得绕过 truth/gate |
| awesome-claude-code-subagents | Claude host 角色库；与 Codex 镜像 | 进化轨实验 | 同上 |
| pi-subagents | 运行时模型：scout→researcher→planner→worker→reviewer→oracle + 并行 + 后台 | Loom 可先试 | **模式蒸馏**；runtime 是 Pi 扩展，不是 Beacon 内核 |
| Skill_MAS | skill 进化 / 对比反思 | Loom eval 旁路 | **研究旁路**；禁止自动 rewrite 生产 skill |
| dbskill | 商业分析 skill 包模板 | 可选侧翼 | **模式+可选内容**；CC BY-NC 商用需授权 |

## 3. 稳交付优先吸收（P0→P2）

### P0（直接提升交付稳定性）

1. **Codex search-specialist / docs-researcher 角色** → 接到 `beacon-pln-source` / goal 前置 research stage（host subagent，不进内核 cron）
2. **pi-subagents 角色分工**：scout / researcher / worker / reviewer / oracle  
   → 映射 Beacon harness：pln / gen / eval / gov；并行 reviewer 可挂 implement 后
3. **multi-agent-coordinator 任务图** → 强化 `main_star_satellite_pool` 的「关键路径 vs 侧翼」规则
4. **durable longrun 默认策略**：新项目 `goal.longrun_default`（skill 已写 v1.6.8 方向）+ host bridge 必配

### P1（并行与搜索接入）

5. goal 意图识别：`搜索/竞品/资料` → 强制 researcher 子代理（host）再 truth  
6. 并行 reviewer 三切片：correctness / tests / simplicity（来自 pi-subagents 工作流）  
7. Agent Eval 增加 `subagent_parallel_success_rate` 维度（自定义 KPI，非替换 composite）

### P2（进化与商业侧翼）

8. Skill_MAS 对比反思 → `beacon-gov-learn` 候选补丁（人审入库）  
9. dbskill 路由模式 → 新商业 skill 包（见第 5 节）  
10. awesome business-product 目录（market-researcher 等）作角色提示补充

## 4. 禁止混入内核的能力

- 把 VoltAgent 154/171 角色全部装进 Beacon skill 树  
- 用 subagent 自证 complete / release  
- 把 Skill_MAS 自动 rewrite 生产 `skills/beacon/*`  
- 把 dbskill 全文商用并入 beacon 发行（许可）  
- 把 Pi/Claude/Codex host runtime 绑死进 Beacon 核心

## 5. 商业分析 Skill 建议（新增，与 Beacon 并列）

| 项 | 建议 |
|----|------|
| 包名 | `beacon-biz` 或独立 `dbs-beacon` 侧翼包（**不**进交付主链） |
| 入口 | `$beacon-biz` / `/biz`（单入口路由，学 dbskill） |
| 子 skill 最小集 | diagnosis · benchmark · goal-clarity · content-hook · save/restore |
| 与 goal 关系 | 商业分析产出 **advisory**；若要变产品需求 → 显式 `beacon-gen-change` / program 升级 |
| 数据落盘 | `~/.beacon/biz/` 或项目 `.beacon/biz/`（学 dbskill `~/.dbs`） |
| 许可证 | 自写方法 + 引用开源思想；不直接拷贝 dbskill 正文 |

## 6. 推荐调研阅读顺序

1. `agents/agent-skills/awesome-codex-subagents/categories/10-research-analysis/search-specialist.toml`
2. `.../09-meta-orchestration/multi-agent-coordinator.toml`
3. `agents/tools/pi-subagents/README.md`（builtin agents 表）
4. `multi-agents/Skill_MAS/README.md`（evolution 三阶段）
5. `agents/agent-skills/dbskill/skills/dbs/SKILL.md` + `dbs-goal` + `dbs-save`
