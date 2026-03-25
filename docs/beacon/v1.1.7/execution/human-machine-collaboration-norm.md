# Beacon 人机协作规范（v1.1.7）

## 核心原则

### 1. 人类主读 Markdown
人类默认阅读：
- SUMMARY
- release
- execution index / boundaries
- qa markdown
- user-story / prd / architecture markdown

### 2. 机器主读 `.machine`
机器默认读取：
- execution machine JSON
- QA machine matrix JSON

### 3. runtime 状态不等于正式交付
`.beacon/` 仅为 runtime internal surface。

### 4. 渐进式披露
- 人类默认先看主入口；
- 机器和 LLM 可以读取相同信息，但应先读主入口，再按需展开 `.machine` 与 `.beacon memory`。

## 推荐人类主入口
- `SUMMARY.md`
- `release/<version>.md`
- `execution/index.md`
- `qa/test-cases/index.md`
