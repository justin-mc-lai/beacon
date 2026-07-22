---
slug: truth-humanizer-runtime-v1610
version: v1.6.10
status: frozen
revision_id: R2
language: zh
domain_required: false
ux_required: false
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
program_ref: docs/beacon/v1.6.10/programs/beacon-truth-authority-humanizer-v1610/program-manifest.md
previous_revision: R1
change_reason: "R2: align as Humanizing Engine in two-engines map; no path change; reinforce require_on_truth_write + doctor optional"
---

# Requirement Truth: Humanizer Runtime Config (v1.6.10 R2)

## 人话

写或改需求真相的人话时，按语言加载 oss-sync 里整份 Humanizer 规则来润色。默认中文用 Humanizer-zh；英文用 blader/humanizer。配置在全局和项目文件里合并。润色不许改 AC 编号、状态名和非法转移表。这是「两引擎」里的表达引擎，不替代真相权威。

- 能做：默认 zh；项目改 en；resolve 全文 SKILL
- 不能做：蒸馏摘要冒充权威；润色改机器字段
- 怎样算完：路径存在；config 契约齐；truth 写入流程要求挂载 profile

## User Intent

作为 **Humanizing Engine**，为 truth 人话/叙述提供双语全文润色运行时配置。

## User Intent Snapshot

```yaml
engine: humanizer
default_language: zh
profiles:
  zh: oss-sync/core-skills/Humanizer-zh/SKILL.md
  en: oss-sync/core-skills/humanizer/SKILL.md
```

## User Decisions

| ID | Value |
|----|-------|
| UD-HUM-001 | default_language = zh |
| UD-HUM-002 | zh = Humanizer-zh fulltext oss-sync |
| UD-HUM-003 | en = blader/humanizer fulltext oss-sync |
| UD-HUM-004 | 蒸馏 prose = 速查非权威 |
| UD-HUM-005 | preserve_machine_fields = true |
| UD-HUM-006 | global ⊕ project config merge |
| UD-HUM-007 | require_on_truth_write = true（写 L0/叙述） |

## Config contract

```yaml
humanizer:
  default_language: zh
  require_on_truth_write: true
  preserve_machine_fields: true
  profiles:
    zh:
      skill_path: <oss-sync>/core-skills/Humanizer-zh/SKILL.md
      l0_heading: "## 人话"
    en:
      skill_path: <oss-sync>/core-skills/humanizer/SKILL.md
      l0_heading: "## Plain language"
```

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-HUM-001 | schema 含 default_language 与 profiles.zh/en |
| AC-HUM-002 | 默认 zh 路径指向 Humanizer-zh SKILL（文件存在） |
| AC-HUM-003 | en 路径指向 blader/humanizer SKILL（文件存在） |
| AC-HUM-004 | 润色范围排除 AC/FSM/路径/命令/ID |
| AC-HUM-005 | 蒸馏文标注速查非权威 |
| AC-HUM-006 | merge 顺序 global⊕project |
| AC-HUM-007 | bilingual 分段选 profile |
| AC-HUM-008 | missing path + require_on_truth_write → fail reason_code |
| AC-HUM-009 | gen-truth 合同要求挂载 active profile 全文 |
| AC-HUM-010 | truth_human_readable 机器检查可并行 |
| AC-HUM-011 | 在演进图中标注为两引擎之 Humanizing Engine（本 SUMMARY/本包） |

## Non-goals

- 第八公共 harness  
- 改上游 Humanizer 仓库内容  

## Relation to Truth Review Gate (v1.6.10 R3)

Humanizer 仅在 **Check A/B/C pass 之后、freeze 之前** 执行（见 `truth-core-authority-v1610` AC-TRG-006）。本包不负责审查逻辑，只提供 profile 全文路径。

## Freeze readiness R2

- [x] 契约与路径
- [ ] implement resolve
