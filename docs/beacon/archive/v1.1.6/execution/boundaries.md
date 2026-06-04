# Boundaries (v1.1.6)

## 本版要解决什么

v1.1.6 只聚焦以下结构性能力：

1. 原生 implement runner
2. revision 生命周期闭环
3. story item writeback
4. 任意阶段 reopen / rewrite
5. native-team 多角色实现模式
6. navigator/help/doctor/scoring 导航层

## 本版不解决什么

1. 不复制 DeerFlow 的 frontend workspace / channels / K8s provisioner
2. 不复制 GSD 2 的完整 runtime / UI / parallel orchestration
3. 不引入 OpenSpec 级的跨工具技能分发复杂度
4. 不改变 release 是 post-gate action 的语义
5. 不把 Beacon 演进成全栈 agent 平台
6. 不把 help/doctor 做成静态命令清单，而忽略阶段感知与评分输出

## 核心边界

### Beacon 应负责
- 生命周期对象模型
- revision / story / item / run 的状态机
- native implement 执行内核
- writeback
- status / review / workflow 的闭环协同
- help / doctor / skill prompt 的阶段感知导航

### Beacon 不应负责
- 具体外部 runtime 的平台抽象扩张
- 长期兼容“implementation 只是 adapter shell”的旧模型
- 需求变化时直接覆盖旧 revision 历史

