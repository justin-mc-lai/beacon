# Research: Beacon completeness and maturity matrix

**Date**: 2026-04-08  
**Intent**: turn the current repository analysis into a reusable maturity matrix for Beacon's product surfaces, skill design quality, architecture boundaries, and delivery readiness.

**Assessment basis**:

- current root README positioning
- `skills/beacon/SKILL.md` package surface
- `v1.1.12` architecture / boundaries / release docs
- command-layer structure in `beacon/cli_factory.py` and `beacon/command_catalog.py`
- command implementation depth in `beacon/commands/*`
- current test surface in `tests/`

---

## 1. Executive summary

Beacon 当前不是一个“概念上完整、实现上空心”的系统。

相反，它已经是一个相当成熟的 evidence-first workflow kernel，尤其在：

- `PRD → user-story → QA`
- implementation handoff
- review / gate / release evidence
- project-aware verification boundaries

这四条线上，完整度都较高。

真正的问题不在“缺功能”，而在：

1. 某些核心模块已经过度集中，维护复杂度高
2. skill/product packaging 仍有少量标准化缺口
3. learning plane 和自迭代能力的产品化成熟度还低于主链

一句话：

> Beacon 的核心主链已经成熟，但其“资产化、自迭代、低复杂度维护”这三件事还没有达到同样成熟度。

---

## 2. First-principles anchor

Beacon 的完整度评估不能脱离它的根锚点：

```text
PRD
→ user-story
→ QA
→ implementation evidence
→ review / gate / release
```

因此：

- 任何设计、记忆、prototype、learning-plane、project-skill、profile-routing 能力
- 都必须被看作这条主链的支撑层
- 而不是与主链并列争夺产品中心

这也是这份矩阵的唯一评估基准。

---

## 3. Surface inventory

当前 Beacon 在代码层面已具备：

- `beacon/commands/`：约 **50** 个命令文件
- `tests/`：约 **130** 个测试文件
- `tests/` 中测试定义：约 **622** 个
- `docs/beacon/v1.1.12/`：约 **69** 个当前 release-line 文件

当前高复杂度命令文件：

- `beacon/commands/workflow.py`：约 **3597** 行
- `beacon/commands/gate.py`：约 **3499** 行
- `beacon/commands/implement.py`：约 **1467** 行
- `beacon/commands/review.py`：约 **848** 行
- `beacon/commands/qa.py`：约 **728** 行

这说明 Beacon 已经不是轻工具，而是重治理系统。

---

## 4. Maturity matrix

评分标准：

- `9-10`：成熟、成体系、可作为当前产品核心
- `7-8`：强能力，基本可用，但仍有结构性改进空间
- `5-6`：方向正确，已具雏形，但产品化不足
- `<5`：仍处于概念或局部实验阶段

## 4.1 Product-definition surfaces

| Surface | Score | Why |
|--------|------:|-----|
| Product positioning | 8.5 | README 与 release docs 已清楚表达 Beacon 是 evidence-first workflow kernel |
| Core lifecycle definition | 9.0 | `think → user-story → prd → test-case → implementation → verify → gate → release` 已稳定 |
| Boundary articulation | 9.0 | `architecture-blueprint.md` 与 `boundaries.md` 已明确 Layer 1-4 及硬边界 |
| Docs version truth | 8.5 | `v1.1.12` 已明确 docs/runtime/version truth；但多版本切换心智成本仍偏高 |

## 4.2 Skill / operator surfaces

| Surface | Score | Why |
|--------|------:|-----|
| `skills/beacon/` packaging | 8.0 | 结构完整、角色清晰、可直接作为标准 operator surface 使用 |
| Command discoverability | 8.5 | `cli_factory.py` + `command_catalog.py` 分层清楚，core/support/labs/bridge 边界明确 |
| Navigation/help experience | 7.5 | `help/status` 已强，但仍依赖底层 memory/writeback 一致性 |
| Skill standard completeness | 6.5 | 已有明确模板和 sync rules，但仍存在引用缺口，如缺失的 skill standard 文档路径 |

## 4.3 Mainline workflow surfaces

| Surface | Score | Why |
|--------|------:|-----|
| `think` | 8.5 | 已成为正式 requirement stage，且与后续 materials 对齐 |
| `user-story` | 9.0 | 已是主链核心，支持 machine state、revision、acceptance mapping |
| `prd` | 9.0 | 与 story/test-case 的 linkage 已较强 |
| `test-case` | 8.5 | 已支持 AC matrix、scenario map、QA9 matrix，产物体系完整 |
| `workflow` orchestration | 8.0 | 编排很强，但复杂度明显过高 |

## 4.4 Delivery evidence surfaces

| Surface | Score | Why |
|--------|------:|-----|
| `implement plan / compile-plan` | 8.5 | requirement-to-implementation closure 已正式化，且有 machine truth |
| `implement` runner integration | 7.5 | 已有 native / adapter / branch preflight / archives，但不同项目依赖 runner 质量 |
| `review` | 8.0 | spec / quality / design / accept 已有正式产物与 contract |
| `gate` | 8.5 | 证据、coverage、drift、memory closure 等均已纳入；但逻辑集中度很高 |
| `release` | 7.5 | 作为 post-gate action 定义明确，但使用复杂度较高 |

## 4.5 Project-aware surfaces

| Surface | Score | Why |
|--------|------:|-----|
| `profile` | 7.5 | 方向正确，能够把项目执行面外置 |
| `skill bind` / orchestration | 7.0 | 结构上成立，但生态化和模板化不足 |
| `verify run` | 7.5 | project-aware 路由逻辑已较完整，适合多服务项目 |
| takeover gate | 8.0 | 从“文档建议”提升到 runtime gate，是成熟信号 |

## 4.6 Advanced / future-facing surfaces

| Surface | Score | Why |
|--------|------:|-----|
| prototype / design governance | 7.5 | 文档和 contract 先进，但仍属于主链支撑层，不是最稳定根面 |
| learning plane | 6.5 | typed surface 和 forbidden surface 设计很好，但产品感知还弱 |
| self-iteration support | 5.5 | 理论与文档输入逐渐齐备，但还没有收敛成真正的生产级 eval plane |
| long-term memory / knowledge plane | 5.5 | 已有 memory/recall 机制，但尚未完全形成围绕 `PRD/story/QA` 的结构化知识层 |

---

## 5. Functional completeness by area

## 5.1 Most complete

以下是 Beacon 当前最成熟、最接近“产品内核”的功能面：

1. `PRD → user-story → QA` 主链
2. requirement materials + `.machine` 双层输出
3. implementation-plan handoff
4. review / gate / release governance

这些能力已经满足三个条件：

- 文档定义清楚
- 代码命令存在
- 测试回归充分

## 5.2 Strong but maintenance-heavy

以下能力很强，但已经出现维护复杂度过高的信号：

1. `workflow`
2. `gate`
3. `implement`

风险不是做不到，而是：

- 逻辑叠加
- 状态来源多
- 使用者与维护者理解成本都偏高

## 5.3 Correct direction, not yet fully productized

以下能力方向正确，但完整度低于主链：

1. learning plane
2. self-iteration
3. memory / compiled knowledge layer
4. skill-ecosystem assetization

这些现在更像：

- advanced governance layer
- future-facing differentiator

而不是“已经像 PRD/story/QA 一样稳固”。

---

## 6. Architecture duty analysis

Beacon 在文档上明确将职责拆为四层：

1. Requirement kernel
2. Delivery evidence kernel
3. Project execution adapters
4. Learning plane

这是当前 Beacon 架构最成熟的部分。

### 6.1 Requirement kernel

成熟度：**very high**

优点：

- 是全系统最清晰的根锚点
- 文档、代码、测试一致度最高
- 已具备 machine-readable truth

判断：

这是 Beacon 当前最稳的“产品核”。

### 6.2 Delivery evidence kernel

成熟度：**high**

优点：

- implementation summary / technical archive / review / gate 已成链
- 强证据意识明显

风险：

- 复杂度越来越集中在少数大型命令文件中

判断：

这是 Beacon 与普通模板工具最主要的差异化来源之一。

### 6.3 Project execution adapters

成熟度：**medium-high**

优点：

- 没有把项目私有执行面吞到 core
- profile/skill/orchestrate/verify 已有接口

风险：

- 生态和模板还不足以让项目适配变成“低摩擦默认项”

判断：

边界方向是对的，但“项目化落地模板”仍欠缺。

### 6.4 Learning plane

成熟度：**medium**

优点：

- typed surface / forbidden surface / budget thinking 都很先进

风险：

- 容易在产品叙事上跑得比真实落地更快
- 若不围绕 `PRD/story/QA` 收束，容易漂向通用自迭代系统

判断：

必须继续围绕主链锚定，而不能单独成为新产品中心。

---

## 7. Skill-agent standard design analysis

从“skill agent 标准设计”角度，Beacon 已经具备很强的产品化意识：

### Strengths

1. `skills/beacon/SKILL.md` 不是随意 prompt，而是结构化 operator contract
2. skill docs 明确了主文档/补充文档角色
3. skill docs 定义了固定 section template
4. lifecycle navigation rules 明确，不让 agent 猜下一步

### Weaknesses

1. 部分文档引用链不闭合
2. skill 层对外资产化仍弱于内核能力本身
3. 部分高级 surfaces 仍更像“内部专家话语”而不是“对外标准产品包”

### Assessment

Beacon 的 skill 标准设计已经明显优于很多 agent 项目，但还没有做到“每个核心能力面都有相应 asset pack + example pack + benchmark pack”。

---

## 8. Main risks

当前 Beacon 最重要的三个风险不是缺功能，而是：

### Risk 1: command concentration risk

`workflow.py` 和 `gate.py` 体量过大，后续继续增长会影响：

- 可维护性
- 可解释性
- 重构安全性

### Risk 2: capability sprawl risk

如果继续扩 prototype / learning / memory / project-skill，而不回到 `PRD/story/QA` 主链锚点，Beacon 会慢慢变成“什么都能讲一点的系统”。

### Risk 3: packaging lag risk

内核能力比外部资产面成熟得快：

- 内部 architecture 比外部 examples 清楚
- 内部 contracts 比外部 bundles 清楚

这会让 Beacon 的“真实完成度”高于用户感知完成度。

---

## 9. Recommendations

如果只做三件事，最值的是：

### 1. Keep the root anchor explicit

持续在所有研究、记忆、learning-plane、自迭代设计中反复写清：

```text
PRD
→ story
→ QA
→ evidence
→ closure
```

### 2. Convert the mainline into bundles

把最成熟的主链能力资产化：

- PRD/story/QA baseline bundle
- implementation-plan bundle
- review/gate scorecard bundle

### 3. Split evaluation from orchestration

learning plane 与自迭代不要直接碰全系统。

应只允许围绕：

- PRD-to-story fidelity
- story coverage
- AC coverage
- false-complete rate

这些主链指标做受控优化。

---

## 10. Final assessment

Beacon 当前完整度可以概括为：

> 作为 `PRD → story → QA → evidence → gate` 的工作流内核，Beacon 已经很成熟；  
> 作为“可复制资产系统”和“受控自迭代系统”，Beacon 仍处于正在成型阶段。

因此最合理的结论不是“Beacon 还不完整”，而是：

- **核心链路完整度高**
- **外围资产化完整度中高**
- **自迭代与长期知识层完整度中等**

如果未来持续围绕 `PRD/story/QA` 锚点推进，而不是继续横向扩表面能力，Beacon 有机会从一个强 workflow kernel，进一步变成一个真正成熟的 product governance system。

