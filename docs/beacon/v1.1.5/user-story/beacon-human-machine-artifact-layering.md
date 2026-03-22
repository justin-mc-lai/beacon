# User Story: Beacon 人机协作分层与 `.machine` 机器面迁移（v1.1.5）

**Feature**: beacon-human-machine-artifact-layering  
**Version**: v1.1.5

**As a** Beacon 使用者 / 维护者  
**I want** 正式把人类主阅读面、机器读取面和 runtime 内部面分层定义清楚  
**So that** 人类不会再被大量 JSON 工件压垮，而机器仍能稳定读取结构化输入完成 doctor / gate / verify / report。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Machine Surface | 机器正式读取面迁移到 `docs/beacon/<version>/.machine/` |
| AC-002 | Human Surface | 人类主阅读面只保留 Markdown 主入口与正式阅读文档 |
| AC-003 | Runtime Surface | `.beacon/` 明确仅作为 runtime internal surface |
| AC-004 | No Compatibility | v1.1.5 不以兼容旧结构为目标，不做长期双写方案 |
| AC-005 | Doctor Authority | `doctor` 负责把旧包修到 v1.1.5 新规范 |
| AC-006 | Memory 4-Layer | memory 正式拆成 store / lifecycle / feedback / consumption-projection |
| AC-007 | LLM Reading Contract | 机器和 LLM 读取 `.machine` + 人类需求文档 + `.beacon memory`，但对人类采用渐进式披露 |
| AC-008 | Human Entry | `SUMMARY.md` / `release/<version>.md` / `execution/index.md` / `qa/test-cases/index.md` 成为人类主入口 |
| AC-009 | QA Layering | `*.ac-test-matrix.json` / `*.qa9-matrix.json` 属于机器工件，不作为 primary reading path |
| AC-010 | Execution Layering | `config.json` / `source.json` / `git-alignment.json` / `change-impact.json` / `delivery-manifest.json` / `terminal.json` 属于机器工件 |
| AC-011 | Doctor Repair Scope | doctor 修复必须覆盖路径、索引、引用，不只移动文件 |
| AC-012 | Gate Safety | v1.1.5 新规范下 doctor/gate/report/status 仍然能读取 memory 与 machine artifacts |
| AC-013 | Human Relief | 默认文档入口不再把 JSON 当做人类主阅读产物 |
| AC-014 | First Principles | 规范以“谁需要读什么”出发，而不是以旧目录结构出发 |
| AC-015 | Delivery Kernel | Beacon 仍保持 delivery kernel 定位，不进入 runtime orchestration 方向 |

## Notes
- 不是删除 machine artifacts；
- 而是把 machine artifacts 从人类主阅读路径降级为机器校验输入；
- 不是让人类看不到机器工件；
- 而是让人类默认不需要先看机器工件。
