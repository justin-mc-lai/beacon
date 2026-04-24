import type {
  DebugState,
  LifecycleStage,
  MaterialType,
  ProjectKind,
  RecoveryIssue,
  RecoveryState,
  RequirementStatus,
  RuntimeMode,
} from '../types/project';

export const getProjectKindLabel = (kind: ProjectKind): string => {
  const labels: Record<ProjectKind, string> = {
    'internal-runtime': 'Beacon 运行时项目',
    product: '产品项目',
    'client-delivery': '客户交付项目',
    'ops-workbench': '运维工作台项目',
  };
  return labels[kind];
};

export const getLifecycleLabel = (stage: LifecycleStage): string => {
  const labels: Record<LifecycleStage, string> = {
    prd: '需求定义',
    'user-story': '用户故事',
    'test-case': '测试用例',
    prototype: '原型冻结',
    implement: '实施',
    qa: '验证',
    release: '发布',
  };
  return labels[stage];
};

export const getRequirementTone = (
  status: RequirementStatus,
): 'default' | 'processing' | 'warning' | 'success' | 'error' => {
  const tones: Record<
    RequirementStatus,
    'default' | 'processing' | 'warning' | 'success' | 'error'
  > = {
    missing: 'error',
    draft: 'warning',
    ready: 'processing',
    frozen: 'success',
  };
  return tones[status];
};

export const getRequirementLabel = (status: RequirementStatus): string => {
  const labels: Record<RequirementStatus, string> = {
    missing: '缺失',
    draft: '草稿',
    ready: '就绪',
    frozen: '冻结',
  };
  return labels[status];
};

export const getDebugTone = (
  state: DebugState,
): 'default' | 'warning' | 'processing' | 'success' => {
  const tones: Record<DebugState, 'default' | 'warning' | 'processing' | 'success'> = {
    ok: 'success',
    warn: 'warning',
    investigating: 'processing',
  };
  return tones[state];
};

export const getDebugLabel = (state: DebugState): string => {
  const labels: Record<DebugState, string> = {
    ok: '正常',
    warn: '关注中',
    investigating: '排查中',
  };
  return labels[state];
};

export const getRuntimeModeLabel = (mode: RuntimeMode): string => {
  const labels: Record<RuntimeMode, string> = {
    single: '单线执行',
    team: '协同执行',
    ralph: 'Ralph 验证环',
  };
  return labels[mode];
};

export const getRuntimeStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    idle: '待命',
    running: '执行中',
    completed: '已完成',
    waiting: '等待中',
    failed: '失败',
  };
  return labels[status] ?? status;
};

export const getRecoveryStatusLabel = (status: RecoveryState['status']): string => {
  const labels: Record<RecoveryState['status'], string> = {
    'healthy-warning': '受控告警',
    degraded: '降级',
    'rebuild-suggested': '建议重建',
    'doctor-suggested': '建议执行诊断修复',
  };
  return labels[status];
};

export const getRecoveryStatusTone = (
  status: RecoveryState['status'],
): 'blue' | 'gold' | 'green' | 'volcano' => {
  const tones: Record<RecoveryState['status'], 'blue' | 'gold' | 'green' | 'volcano'> = {
    'healthy-warning': 'blue',
    degraded: 'gold',
    'rebuild-suggested': 'volcano',
    'doctor-suggested': 'gold',
  };
  return tones[status];
};

export const getSeverityLabel = (severity: RecoveryIssue['severity']): string => {
  const labels: Record<RecoveryIssue['severity'], string> = {
    critical: '关键',
    warning: '警告',
    info: '提示',
  };
  return labels[severity];
};

export const getSeverityTone = (
  severity: RecoveryIssue['severity'],
): 'red' | 'gold' | 'blue' => {
  const tones: Record<RecoveryIssue['severity'], 'red' | 'gold' | 'blue'> = {
    critical: 'red',
    warning: 'gold',
    info: 'blue',
  };
  return tones[severity];
};

export const getMaterialTypeLabel = (type: MaterialType): string => {
  const labels: Record<MaterialType, string> = {
    summary: '摘要',
    prd: 'PRD',
    'user-story': '用户故事',
    'test-case': '测试用例',
    prototype: '原型',
    execution: '执行材料',
    release: '发布材料',
    architecture: '架构材料',
    research: '调研材料',
    plan: '计划材料',
    report: '报告材料',
    guide: '说明材料',
  };
  return labels[type];
};
