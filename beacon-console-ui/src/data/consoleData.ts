import type { PageTrace } from '../types/common';
import type {
  PortfolioSummary,
  Project,
  RuntimeModeDetail,
} from '../types/project';

const sharedFreezeLinks = [
  {
    label: 'v1.3.5 wireframe summary',
    path:
      'docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/wireframe-summary.md',
    note: '上游 freeze 的页面职责与导航骨架。',
  },
  {
    label: 'v1.3.5 navigation map',
    path:
      'docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/navigation-map.md',
    note: '确认主链路与只读文档流的连接方式。',
  },
];

const makeRuntimeDetails = (details: RuntimeModeDetail[]): RuntimeModeDetail[] => details;

const projects: Project[] = [
  {
    id: 'beacon',
    name: 'beacon',
    type: 'workspace',
    kind: 'internal-runtime',
    rootPath: '/Users/apple/Developer/Personal/products/beacon',
    owner: 'apple',
    currentVersion: 'v1.3.6',
    lifecycle: 'implement',
    healthStatus: 'degraded',
    debugState: 'warn',
    gitStatus: {
      branch: 'beacon/v1.3.5',
      expectedBranch: 'beacon/v1.3.6',
      dirty: true,
      ahead: 2,
      behind: 0,
    },
    currentFeature: 'beacon-v1.3.6-visual-management-console-and-material-viewer',
    progress: 78,
    blocker: 'UI 仍缺 5 页与 implementation/QA evidence，release gate 未闭环。',
    currentDelivery: '管理端 7 页与物料查看器的产品面收口。',
    latestDelivery: [
      '恢复了 `beacon implement` 公共子命令与 legacy CLI 路由。',
      '定义了 4 个真实项目的组合态、runtime 摘要与只读物料流。',
      '对齐 v1.3.5 wireframe freeze 与 v1.3.6 page spec 的回链关系。',
    ],
    nextStep: '补齐前端实现证据，冻结 revision，再跑 QA 解除 blocked。',
    recommendedSkill: 'beacon-implement',
    interventionReason: 'release-ready 收尾被 revision draft 和 QA blocked 拦住。',
    versionLine: ['v1.3.3', 'v1.3.4', 'v1.3.5', 'v1.3.6'],
    mainTracks: [
      {
        slug: 'beacon-v1.3.6-visual-management-console-and-material-viewer',
        title: '可视化管理端与物料查看器',
        track: 'main',
        stage: 'implement',
        status: 'ready',
        summary: '消费 v1.3.5 的 wireframe freeze，形成 Beacon 正式管理面。',
        sourcePath:
          'docs/beacon/v1.3.6/prd/beacon-v1-3-6-visual-management-console-and-material-viewer.md',
      },
      {
        slug: 'beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor',
        title: '宿主原生 LLM 编排与全命令 runtime',
        track: 'main',
        stage: 'release',
        status: 'frozen',
        summary: 'runtime truth 已收敛到 v1.3.6 并通过 release gate。',
        sourcePath:
          'docs/beacon/v1.3.6/prd/beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor.md',
      },
    ],
    parallelTracks: [
      {
        slug: 'openai-eval-skills-research',
        title: 'OpenAI eval skills 接入调研',
        track: 'parallel',
        stage: 'prd',
        status: 'draft',
        summary: '调研文献已拉取，等待编译成 Beacon 接入方案。',
        sourcePath: 'docs/beacon/v1.3.6/research/',
      },
    ],
    requirementClosure: {
      prd: 'ready',
      userStory: 'ready',
      testCase: 'ready',
      prototype: 'frozen',
      implement: 'ready',
      qa: 'draft',
      release: 'draft',
    },
    runtimeSummary: {
      activeMode: 'team',
      activeRuns: 2,
      summary: '公共 implement 已恢复，但 team execution 仍等待 revision freeze 后继续。',
      linkedRun: 'run-20260421T161500Z-console-closure',
    },
    runtimeDetails: makeRuntimeDetails([
      {
        mode: 'single',
        status: 'idle',
        stage: 'implement',
        progress: 0,
        summary: '单人 lane 暂停，等待前端 build 与 docs 冻结完成。',
        linkedRun: 'single-console-standby',
        startedAt: '2026-04-21 10:30',
        artifactRefs: ['src/', 'docs/beacon/v1.3.6/.machine/execution/'],
        timeline: ['10:30 进入待命', '等待 implement evidence 收口'],
      },
      {
        mode: 'team',
        status: 'running',
        stage: 'implement',
        progress: 78,
        summary: 'Codex/Claude 协同完成命令修复与 UI 收尾。',
        linkedRun: 'run-20260421T161500Z-console-closure',
        startedAt: '2026-04-21 16:15',
        artifactRefs: [
          '.beacon/implement/',
          'beacon-console-ui/dist',
          'docs/beacon/v1.3.6/.machine/execution/technical-implementation-beacon-v1.3.6-visual-management-console-and-material-viewer.json',
        ],
        timeline: [
          '16:15 恢复 implement 入口',
          '16:42 进入 UI 闭环与 evidence 补齐',
          '待执行 revision freeze -> QA rerun',
        ],
        teamAgents: [
          {
            name: 'Codex main',
            role: 'implement-owner',
            status: 'running',
            linkedRun: 'run-20260421T161500Z-console-closure',
            artifactRefs: ['beacon/commands/implement/__init__.py', 'beacon-console-ui/'],
            session: {
              host: 'Codex',
              sessionRef: 'codex-session-visual-console',
              updatedAt: '2026-04-21 17:18',
              transcriptRef: '.beacon/runtime/session/codex-session-visual-console.ref',
            },
          },
          {
            name: 'Claude frontend lane',
            role: 'ui-bootstrap',
            status: 'completed',
            linkedRun: 'claude-ui-bootstrap',
            artifactRefs: ['beacon-console-ui/README.md', 'beacon-console-ui/IMPLEMENTATION.md'],
            session: {
              host: 'Claude',
              sessionRef: 'claude-session-ui-bootstrap',
              updatedAt: '2026-04-21 14:08',
              transcriptRef: '.beacon/runtime/session/claude-session-ui-bootstrap.ref',
            },
          },
        ],
      },
      {
        mode: 'ralph',
        status: 'waiting',
        stage: 'qa',
        progress: 35,
        summary: 'QA loop 已创建 scenario map，但被 implementation/evidence 缺口阻塞。',
        linkedRun: 'ralph-qa-visual-console',
        startedAt: '2026-04-20 18:08',
        artifactRefs: [
          '.beacon/qa/features/beacon-v1.3.6-visual-management-console-and-material-viewer/plan.json',
        ],
        timeline: ['初次 QA 编译完成', '检测到 implementation_done=false', '等待 rerun'],
        ralphLoop: {
          roundCount: 2,
          failureStreak: 1,
          nextAction: '生成 implementation evidence 后重新触发 qa run。',
          blocker: 'plan.json 仍是 blocked，缺少 implementation_run_id。',
          recentResult: 'scenario map 已存在，但 scorecard/status 尚未生成。',
        },
      },
    ]),
    recovery: {
      status: 'doctor-suggested',
      truthSources: ['docs/beacon/v1.3.6/', '.beacon/', 'AGENTS.md'],
      issues: [
        {
          severity: 'critical',
          title: 'revision 仍为 draft',
          detail:
            'docs/beacon/v1.3.6/.machine/execution/beacon-v1.3.6-visual-management-console-and-material-viewer.revision.json 仍未 freeze。',
          recommendation: '先执行 `beacon freeze`，再进入 implement / qa rerun。',
        },
        {
          severity: 'warning',
          title: 'QA plan blocked',
          detail:
            '.beacon/qa/features/beacon-v1.3.6-visual-management-console-and-material-viewer/plan.json 还未生成 implementation_run_id。',
          recommendation: '补 `.beacon/implement` 证据后 rerun QA。',
        },
        {
          severity: 'warning',
          title: '工作树与目标分支不一致',
          detail: '当前在 beacon/v1.3.5 上推进 v1.3.6 feature，release gate 会持续报警。',
          recommendation: '在不破坏脏工作树的前提下完成 promotion 收尾。',
        },
      ],
      steps: [
        '执行 `beacon freeze beacon-v1.3.6-visual-management-console-and-material-viewer --project-root . --version v1.3.6`。',
        '运行 `beacon implement plan ...` 与 `beacon implement status ...` 生成实现证据。',
        '完成 `beacon qa run beacon-v1.3.6-visual-management-console-and-material-viewer --project-root . --version v1.3.6 --json`。',
      ],
      riskNotes: [
        'docs/beacon 与 .beacon 才是正式真相，PocketBase/SQLite 只是读模型。',
        '不要把 host session transcript 直接当成 release 证据。',
      ],
    },
    materials: [
      {
        id: 'beacon-v136-summary',
        title: 'v1.3.6 Summary',
        version: 'v1.3.6',
        type: 'summary',
        feature: 'runtime-line',
        path: 'docs/beacon/v1.3.6/SUMMARY.md',
        summary: '当前 Beacon runtime 与 docs line 的总览。',
        createdAt: '2026-04-20',
        updatedAt: '2026-04-21',
        relatedIds: ['beacon-v136-prd-console', 'beacon-v136-release-note'],
        content: `# Beacon v1.3.6 Summary

- 当前 runtime/package version: \`1.3.6\`
- docs truth: \`docs/beacon/v1.3.6/\`
- release-ready 主线：宿主原生 LLM 编排与全命令 runtime
- 并行探索：可视化管理端与物料查看器

## 当前目标

1. 管理端 7 页与物料查看器形成正式产品面。
2. implement / qa / release evidence 可以回到同一 truth line。
3. README / skills / docs / release gate 一次性收敛到可发布状态。`,
      },
      {
        id: 'beacon-v136-prd-console',
        title: 'PRD · 可视化管理端与项目物料查看器',
        version: 'v1.3.6',
        type: 'prd',
        feature: 'beacon-v1.3.6-visual-management-console-and-material-viewer',
        path:
          'docs/beacon/v1.3.6/prd/beacon-v1-3-6-visual-management-console-and-material-viewer.md',
        summary: '定义首页、总览、详情、运行中心、恢复诊断、物料流的产品边界。',
        createdAt: '2026-04-20',
        updatedAt: '2026-04-21',
        relatedIds: ['beacon-v136-story-console', 'beacon-v136-qa-console'],
        content: `# PRD：Beacon v1.3.6 可视化管理端与项目物料查看器

## 主要目标

1. Beacon UI 展示项
2. Beacon UI 数据视图
3. Beacon UI 交互结构
4. 项目物料 Markdown 只读查看

## 功能边界

- 生命周期优先于机器噪音
- 页面实现必须回链 v1.3.5 wireframe freeze
- Markdown 只读查看正式化，不允许在线编辑`,
      },
      {
        id: 'beacon-v136-story-console',
        title: 'User Story · 可视化管理端与项目物料查看器',
        version: 'v1.3.6',
        type: 'user-story',
        feature: 'beacon-v1.3.6-visual-management-console-and-material-viewer',
        path:
          'docs/beacon/v1.3.6/user-story/beacon-v1.3.6-visual-management-console-and-material-viewer.md',
        summary: '定义 CEO / owner / 运行治理者视角的 11 条 story slice。',
        createdAt: '2026-04-20',
        updatedAt: '2026-04-21',
        relatedIds: ['beacon-v136-prd-console', 'beacon-v136-qa-console'],
        content: `# User Story

## 关键 story slice

- 首页先回答经营判断
- 项目详情成为接力页
- Runtime 中心只在需要时下钻
- 物料查看器正式化但保持只读
- 恢复诊断解释 degraded / rebuild / doctor`,
      },
      {
        id: 'beacon-v136-qa-console',
        title: 'QA Test Cases · 可视化管理端与项目物料查看器',
        version: 'v1.3.6',
        type: 'test-case',
        feature: 'beacon-v1.3.6-visual-management-console-and-material-viewer',
        path:
          'docs/beacon/v1.3.6/qa/test-cases/beacon-v1.3.6-visual-management-console-and-material-viewer.md',
        summary: '13 条测试场景覆盖 AC-001 到 AC-017。',
        createdAt: '2026-04-20',
        updatedAt: '2026-04-21',
        relatedIds: ['beacon-v136-prd-console', 'beacon-v136-impl-archive'],
        content: `# Test Cases

## 覆盖重点

- 首页默认不暴露 runtime 洪流
- 管理总览可稳定扫描四个真实项目
- 项目详情可表达 requirement closure
- Runtime 中心展示 Team / Ralph 的有限 metadata
- 文档流按 version -> type -> feature 组织`,
      },
      {
        id: 'beacon-v136-impl-archive',
        title: 'Technical Implementation Archive',
        version: 'v1.3.6',
        type: 'execution',
        feature: 'beacon-v1.3.6-visual-management-console-and-material-viewer',
        path:
          'docs/beacon/v1.3.6/.machine/execution/technical-implementation-beacon-v1.3.6-visual-management-console-and-material-viewer.json',
        summary: '实现证据归档，供 implement / qa / release 共享读取。',
        createdAt: '2026-04-20',
        updatedAt: '2026-04-21',
        relatedIds: ['beacon-v136-qa-console'],
        content: `# Technical Implementation Archive

- 前端入口：\`beacon-console-ui/\`
- 当前目标：build clean、7 页闭环、实现证据补齐
- 依赖页面 spec、wireframe、story-scenario-map 与 QA matrix`,
      },
      {
        id: 'beacon-v136-release-note',
        title: 'Release Note · v1.3.6',
        version: 'v1.3.6',
        type: 'release',
        feature: 'runtime-line',
        path: 'docs/beacon/v1.3.6/release/v1.3.6.md',
        summary: '记录 v1.3.6 runtime promotion 与 release gate。',
        createdAt: '2026-04-20',
        updatedAt: '2026-04-21',
        relatedIds: ['beacon-v136-summary'],
        content: `# Release Note · v1.3.6

- runtime truth 收敛到 host-native line
- CLI 公共入口收口到最小 7+3 surface
- release gate 仍在等待 visual console feature 的 implement / QA evidence 完整闭环`,
      },
    ],
  },
  {
    id: 'slow-uni-bmtop',
    name: 'slow_uni_bmtop',
    type: 'single-repo',
    kind: 'product',
    rootPath: '/Users/apple/Developer/Personal/products/slow_uni_bmtop',
    owner: 'apple',
    currentVersion: 'v0.9.2',
    lifecycle: 'qa',
    healthStatus: 'healthy',
    debugState: 'ok',
    gitStatus: {
      branch: 'release/v0.9.2',
      dirty: false,
      ahead: 0,
      behind: 0,
    },
    currentFeature: 'real-project-validation-and-release-closure',
    progress: 92,
    blocker: '等待最后的验收记录归档。',
    currentDelivery: '真实项目执行验证与 release docs 收口。',
    latestDelivery: [
      '完成真实项目执行与 requirement material 对齐。',
      '补齐 change docs、implementation evidence、QA evidence。',
      '进入 release-ready 检查与版本真相核实。',
    ],
    nextStep: '完成最终验收记录并发布 v0.9.2。',
    recommendedSkill: 'beacon-release',
    interventionReason: '需要 owner 对 release 结论做最终签收。',
    versionLine: ['v0.9.0', 'v0.9.1', 'v0.9.2'],
    mainTracks: [
      {
        slug: 'real-project-validation',
        title: '真实项目执行验证',
        track: 'main',
        stage: 'qa',
        status: 'ready',
        summary: '验证 Beacon 在真实项目上的 implement / qa / release 收口。',
        sourcePath: 'docs/beacon/v0.9.2/',
      },
    ],
    parallelTracks: [],
    requirementClosure: {
      prd: 'frozen',
      userStory: 'frozen',
      testCase: 'frozen',
      prototype: 'ready',
      implement: 'frozen',
      qa: 'ready',
      release: 'draft',
    },
    runtimeSummary: {
      activeMode: 'single',
      activeRuns: 1,
      summary: '真实项目验证已完成，当前仅保留 release sign-off lane。',
      linkedRun: 'slow-uni-release-proof',
    },
    runtimeDetails: makeRuntimeDetails([
      {
        mode: 'single',
        status: 'running',
        stage: 'qa',
        progress: 92,
        summary: '单人验证 lane 正在整理 release-ready 输出。',
        linkedRun: 'slow-uni-release-proof',
        startedAt: '2026-04-21 09:20',
        artifactRefs: ['docs/beacon/v0.9.2/release/', '.beacon/qa/'],
        timeline: ['09:20 启动最终验证', '14:30 补齐 evidence', '等待 owner sign-off'],
      },
      {
        mode: 'team',
        status: 'idle',
        stage: 'qa',
        progress: 0,
        summary: 'team lane 已结束，不再新增 agent。',
        linkedRun: 'team-idle',
        startedAt: '2026-04-21 08:00',
        artifactRefs: [],
        timeline: ['team lane 已封板'],
      },
      {
        mode: 'ralph',
        status: 'idle',
        stage: 'release',
        progress: 0,
        summary: '无需 Ralph 闭环。',
        linkedRun: 'ralph-idle',
        startedAt: '2026-04-21 08:00',
        artifactRefs: [],
        timeline: ['未启用'],
        ralphLoop: {
          roundCount: 0,
          failureStreak: 0,
          nextAction: 'none',
          blocker: 'none',
          recentResult: '未启用',
        },
      },
    ]),
    recovery: {
      status: 'healthy-warning',
      truthSources: ['docs/beacon/v0.9.2/', '.beacon/'],
      issues: [
        {
          severity: 'info',
          title: '待归档 release sign-off',
          detail: '技术与 QA 证据已经齐备，只差最后的发布结论落档。',
          recommendation: '运行 release gate 并归档结果。',
        },
      ],
      steps: ['核对 release checklist。', '补签最终结论。', '发布版本。'],
      riskNotes: ['不要在 sign-off 前修改已冻结 requirement。'],
    },
    materials: [],
  },
  {
    id: 'rolo',
    name: 'rolo',
    type: 'multi-repo',
    kind: 'ops-workbench',
    rootPath: '/Users/apple/Developer/Personal/products/rolo',
    owner: 'apple',
    currentVersion: 'v2.1.0',
    lifecycle: 'release',
    healthStatus: 'healthy',
    debugState: 'ok',
    gitStatus: {
      branch: 'release/v2.1.0',
      dirty: false,
      ahead: 0,
      behind: 0,
    },
    currentFeature: 'governance-board-hardening',
    progress: 100,
    blocker: '无。',
    currentDelivery: '组合治理看板已通过 release gate。',
    latestDelivery: ['项目治理看板、SLA 视图与回放审计已交付。'],
    nextStep: '观测 canary 并记录后评估。',
    recommendedSkill: 'beacon-status',
    interventionReason: '仅需周期性巡检。',
    versionLine: ['v2.0.0', 'v2.0.5', 'v2.1.0'],
    mainTracks: [
      {
        slug: 'governance-board-hardening',
        title: '治理看板强化',
        track: 'main',
        stage: 'release',
        status: 'frozen',
        summary: 'release 已通过。',
        sourcePath: 'docs/beacon/v2.1.0/',
      },
    ],
    parallelTracks: [],
    requirementClosure: {
      prd: 'frozen',
      userStory: 'frozen',
      testCase: 'frozen',
      prototype: 'frozen',
      implement: 'frozen',
      qa: 'frozen',
      release: 'frozen',
    },
    runtimeSummary: {
      activeMode: 'single',
      activeRuns: 0,
      summary: '当前无活跃运行，仅保留 read-model 心跳。',
      linkedRun: 'rolo-heartbeat',
    },
    runtimeDetails: makeRuntimeDetails([
      {
        mode: 'single',
        status: 'completed',
        stage: 'release',
        progress: 100,
        summary: '最后一次 release run 已完成。',
        linkedRun: 'rolo-heartbeat',
        startedAt: '2026-04-20 20:00',
        completedAt: '2026-04-20 20:25',
        artifactRefs: ['docs/beacon/v2.1.0/release/'],
        timeline: ['20:00 发布', '20:25 gate passed'],
      },
      {
        mode: 'team',
        status: 'completed',
        stage: 'release',
        progress: 100,
        summary: 'team lane 已归档。',
        linkedRun: 'rolo-team-closeout',
        startedAt: '2026-04-20 18:00',
        completedAt: '2026-04-20 19:45',
        artifactRefs: ['execution/team-closeout.md'],
        timeline: ['18:00 编排', '19:45 完成'],
      },
      {
        mode: 'ralph',
        status: 'completed',
        stage: 'qa',
        progress: 100,
        summary: 'Ralph 完成回归。',
        linkedRun: 'rolo-ralph-regression',
        startedAt: '2026-04-19 11:10',
        completedAt: '2026-04-19 12:05',
        artifactRefs: ['qa/scorecard.json'],
        timeline: ['11:10 启动', '12:05 通过'],
        ralphLoop: {
          roundCount: 4,
          failureStreak: 0,
          nextAction: 'monitor',
          blocker: 'none',
          recentResult: '所有 regression scenario 均通过。',
        },
      },
    ]),
    recovery: {
      status: 'healthy-warning',
      truthSources: ['docs/beacon/v2.1.0/', '.beacon/'],
      issues: [],
      steps: ['继续观测 health pulse。'],
      riskNotes: ['无需把 canary 日志提升到默认首页。'],
    },
    materials: [],
  },
  {
    id: 'shopxo-canada',
    name: 'shopxo_canada',
    type: 'single-repo',
    kind: 'client-delivery',
    rootPath: '/Users/apple/Developer/Personal/products/shopxo_canada',
    owner: 'apple',
    currentVersion: 'v1.7.4',
    lifecycle: 'qa',
    healthStatus: 'blocked',
    debugState: 'investigating',
    gitStatus: {
      branch: 'feature/v1.7.4-checkout',
      dirty: true,
      ahead: 1,
      behind: 0,
    },
    currentFeature: 'checkout-fallback-hardening',
    progress: 68,
    blocker: '回归环境的支付回调不稳定，Ralph 持续重试。',
    currentDelivery: 'checkout 回退逻辑与验收补强。',
    latestDelivery: ['支付链路补丁已完成，等待 QA 回归通过。'],
    nextStep: '先稳定回归环境，再让 Ralph 完成闭环。',
    recommendedSkill: 'beacon-qa',
    interventionReason: 'blocked 项目，需要 owner 决定是否切换 fallback 策略。',
    versionLine: ['v1.7.2', 'v1.7.3', 'v1.7.4'],
    mainTracks: [
      {
        slug: 'checkout-fallback-hardening',
        title: '结账回退链路强化',
        track: 'main',
        stage: 'qa',
        status: 'ready',
        summary: '实现完成，正等待回归环境恢复。',
        sourcePath: 'docs/beacon/v1.7.4/',
      },
    ],
    parallelTracks: [
      {
        slug: 'docs-refresh',
        title: '交付文档补录',
        track: 'parallel',
        stage: 'user-story',
        status: 'draft',
        summary: '交接文档仍有缺口。',
        sourcePath: 'docs/beacon/v1.7.4/change/',
      },
    ],
    requirementClosure: {
      prd: 'frozen',
      userStory: 'ready',
      testCase: 'ready',
      prototype: 'ready',
      implement: 'frozen',
      qa: 'draft',
      release: 'missing',
    },
    runtimeSummary: {
      activeMode: 'ralph',
      activeRuns: 1,
      summary: 'Ralph 正在循环验证 fallback 回调稳定性。',
      linkedRun: 'shopxo-ralph-checkout',
    },
    runtimeDetails: makeRuntimeDetails([
      {
        mode: 'single',
        status: 'completed',
        stage: 'implement',
        progress: 100,
        summary: '实现已完成并提交预发布包。',
        linkedRun: 'shopxo-single-impl',
        startedAt: '2026-04-20 09:00',
        completedAt: '2026-04-20 15:40',
        artifactRefs: ['build/checkout-fallback.tgz'],
        timeline: ['09:00 开始实现', '15:40 完成'],
      },
      {
        mode: 'team',
        status: 'completed',
        stage: 'qa',
        progress: 100,
        summary: 'team lane 补完 QA checklist。',
        linkedRun: 'shopxo-team-qa',
        startedAt: '2026-04-20 16:00',
        completedAt: '2026-04-20 18:00',
        artifactRefs: ['qa/checklist.md'],
        timeline: ['16:00 生成 QA checklist', '18:00 完成'],
      },
      {
        mode: 'ralph',
        status: 'running',
        stage: 'qa',
        progress: 68,
        summary: 'Ralph 继续验证支付回调稳定性。',
        linkedRun: 'shopxo-ralph-checkout',
        startedAt: '2026-04-21 08:15',
        artifactRefs: ['qa/replay/checkout-fallback.json'],
        timeline: ['08:15 启动闭环', '10:50 命中一次支付超时', '继续重试'],
        ralphLoop: {
          roundCount: 5,
          failureStreak: 2,
          nextAction: '复核回调 mock 与 sandbox 网络抖动。',
          blocker: '支付回调偶发超时，导致 release confidence 降低。',
          recentResult: '最近一轮 fallback 成功，但主回调仍不稳定。',
        },
      },
    ]),
    recovery: {
      status: 'rebuild-suggested',
      truthSources: ['docs/beacon/v1.7.4/', '.beacon/'],
      issues: [
        {
          severity: 'warning',
          title: '回归环境数据陈旧',
          detail: 'QA sandbox 的支付回调配置与最新 fallback 策略不一致。',
          recommendation: '先 rebuild 投影再重跑 Ralph。',
        },
      ],
      steps: ['同步 sandbox 配置。', '重建 QA projection。', '重新执行 Ralph。'],
      riskNotes: ['不要把外部支付系统 trace 直接纳入 Beacon 真相层。'],
    },
    materials: [],
  },
];

const pageTraces: Record<string, PageTrace> = {
  home: {
    pageId: 'home',
    pageName: '首页',
    freezeLinks: [
      ...sharedFreezeLinks,
      {
        label: 'v1.3.5 state-flow guardrail',
        path:
          'docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/state-flow-map.md',
        note: '首页不直接下钻恢复诊断，保持生命周期优先。',
      },
    ],
    currentSpecLinks: [
      {
        label: 'v1.3.6 human wireframe',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/human-view/wireframes/01-home.md',
        note: '定义经营总览条、重点介入区、项目推进摘要。',
      },
      {
        label: 'v1.3.6 machine page spec',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/machine-view/page-specs/home.json',
        note: '对应 ready/blocked/intervention-needed 等状态说明。',
      },
    ],
    acceptanceCriteria: ['AC-001', 'AC-002', 'AC-008', 'AC-016', 'AC-017'],
  },
  'management-overview': {
    pageId: 'management-overview',
    pageName: '管理总览',
    freezeLinks: [
      ...sharedFreezeLinks,
      {
        label: 'v1.3.5 management-overview',
        path:
          'docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/pages/management-overview.md',
        note: '多项目密集管理视图的上游冻结页。',
      },
    ],
    currentSpecLinks: [
      {
        label: 'v1.3.6 human wireframe',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/human-view/wireframes/02-management-overview.md',
        note: '项目注册表、筛选条与风险摘要。',
      },
      {
        label: 'v1.3.6 machine page spec',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/machine-view/page-specs/management-overview.json',
        note: 'ready / filtered / empty / error 状态定义。',
      },
    ],
    acceptanceCriteria: ['AC-003', 'AC-013', 'AC-014', 'AC-015', 'AC-017'],
  },
  'project-detail': {
    pageId: 'project-detail',
    pageName: '项目详情',
    freezeLinks: [
      ...sharedFreezeLinks,
      {
        label: 'v1.3.5 implementation map',
        path:
          'docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/implementation-map.json',
        note: '承接首页、总览、runtime、material 的主链路骨架。',
      },
    ],
    currentSpecLinks: [
      {
        label: 'v1.3.6 human wireframe',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/human-view/wireframes/03-project-detail.md',
        note: '定义版本线、PRD 轨道、需求闭环、推荐动作。',
      },
      {
        label: 'v1.3.6 machine page spec',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/machine-view/page-specs/project-detail.json',
        note: '可接力页面的状态与出入口。',
      },
    ],
    acceptanceCriteria: ['AC-004', 'AC-005', 'AC-008', 'AC-015', 'AC-016', 'AC-017'],
  },
  'runtime-center': {
    pageId: 'runtime-center',
    pageName: '运行中心',
    freezeLinks: [
      ...sharedFreezeLinks,
      {
        label: 'v1.3.5 runtime-center',
        path:
          'docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/pages/runtime-center.md',
        note: 'single / team / ralph 下钻只在运行中心展开。',
      },
    ],
    currentSpecLinks: [
      {
        label: 'v1.3.6 human wireframe',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/human-view/wireframes/04-runtime-center.md',
        note: '模式切换、会话引用、artifact 与 blocker。',
      },
      {
        label: 'v1.3.6 machine page spec',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/machine-view/page-specs/runtime-center.json',
        note: 'team / ralph / idle / error 状态定义。',
      },
    ],
    acceptanceCriteria: ['AC-008', 'AC-009', 'AC-010', 'AC-011', 'AC-017'],
  },
  'recovery-diagnostics': {
    pageId: 'recovery-diagnostics',
    pageName: '恢复诊断',
    freezeLinks: [
      ...sharedFreezeLinks,
      {
        label: 'v1.3.5 state-flow fallback',
        path:
          'docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/state-flow-map.md',
        note: '所有 data failure fallback 到 recovery-diagnostics。',
      },
    ],
    currentSpecLinks: [
      {
        label: 'v1.3.6 human wireframe',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/human-view/wireframes/05-recovery-diagnostics.md',
        note: '明确 degraded / rebuild / doctor 的诊断与恢复步骤。',
      },
      {
        label: 'v1.3.6 machine page spec',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/machine-view/page-specs/recovery-diagnostics.json',
        note: 'truth 来源、恢复步骤与风险提示的结构定义。',
      },
    ],
    acceptanceCriteria: ['AC-012', 'AC-015', 'AC-017'],
  },
  'material-viewer': {
    pageId: 'material-viewer',
    pageName: '项目物料查看器',
    freezeLinks: [
      ...sharedFreezeLinks,
      {
        label: 'v1.3.5 material-viewer',
        path:
          'docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/pages/material-viewer.md',
        note: 'version -> type -> feature 的只读浏览骨架。',
      },
    ],
    currentSpecLinks: [
      {
        label: 'v1.3.6 human wireframe',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/human-view/wireframes/06-material-viewer.md',
        note: '左侧导航、文档列表、右侧阅读面板。',
      },
      {
        label: 'v1.3.6 machine page spec',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/machine-view/page-specs/material-viewer.json',
        note: '只读模式、source-missing 与 empty 状态定义。',
      },
    ],
    acceptanceCriteria: ['AC-006', 'AC-007', 'AC-015', 'AC-017'],
  },
  'material-document-detail': {
    pageId: 'material-document-detail',
    pageName: '物料文档详情',
    freezeLinks: [
      ...sharedFreezeLinks,
      {
        label: 'v1.3.5 material-document-detail',
        path:
          'docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/pages/material-document-detail.md',
        note: '冻结阅读态、同类文档切换与来源路径说明。',
      },
    ],
    currentSpecLinks: [
      {
        label: 'v1.3.6 human wireframe',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/human-view/wireframes/07-material-document-detail.md',
        note: '面包屑、正文区、同类文档切换与只读说明。',
      },
      {
        label: 'v1.3.6 machine page spec',
        path:
          'docs/beacon/v1.3.6/prototype/beacon-v1-3-6-visual-management-console-and-material-viewer/machine-view/page-specs/material-document-detail.json',
        note: 'version-switch / sibling-switch / source-missing 状态定义。',
      },
    ],
    acceptanceCriteria: ['AC-006', 'AC-007', 'AC-015', 'AC-017'],
  },
};

export function getPortfolioSummary(): PortfolioSummary {
  return {
    totalProjects: projects.length,
    blockedProjects: projects.filter((project) => project.healthStatus === 'blocked').length,
    activeRuntimeCount: projects.reduce(
      (count, project) => count + project.runtimeSummary.activeRuns,
      0,
    ),
    interventionCount: projects.filter(
      (project) => project.healthStatus !== 'healthy' || project.lifecycle !== 'release',
    ).length,
    deliveredToday: projects.reduce(
      (count, project) => count + Math.min(project.latestDelivery.length, 2),
      0,
    ),
  };
}

export function getProjects(): Project[] {
  return projects;
}

export function getProjectById(projectId?: string): Project | undefined {
  return projects.find((project) => project.id === projectId);
}

export function getPageTrace(pageId: string): PageTrace {
  return pageTraces[pageId];
}
