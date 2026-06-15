# Beacon v1 架构缺陷全面审查

## 核心结论
10 大缺陷共享同一根因：**架构层级强制力的缺失**。代码约定（comments/docstrings/conventions）可被绕过，只有类型系统和显式状态机转换表才能做到"CLI 强制执行"。

## v2 硬约束（5 项）
1. 主流程无显式状态机 → Rust enum 编译期穷举匹配
2. 阶段定义分散 4+ 模块 → 单一 canonical source
5. 同步阻塞 + busy-wait → tokio async
6. 状态不完备 → 9 种 StageStatus (含 Crashed/TimedOut/Interrupted/Repairing)
8. beacon-loop/beacon-run 重叠 → 统一编排器

## 可渐进修复（5 项）
3. 巨型文件 → 先拆分再重写
4. eager import → Python lazy import
7. 779 run 目录 → cleanup 命令
9. 版本不一致 → single source 脚本
10. token 估算 → tiktoken 替换

## 产出文档
- `docs/analysis/beacon-v1-architecture-defects-audit.md` — 五重审视全面审查
- `docs/plans/beacon-v2-redesign.md` — 详细架构计划

## 代码图关键事实
Understand-Anything 分析：31,948 节点 / 33,955 边 / 6,706 函数。高耦合热点：main.py(187 1-hop)、runtime.py(133)、versioning.py(113)、story_state.py(85)。