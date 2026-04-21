import type {
  DebugState,
  LifecycleStage,
  MaterialType,
  ProjectKind,
  RequirementStatus,
  RuntimeMode,
} from '../types/project';

export const getProjectKindLabel = (kind: ProjectKind): string => {
  const labels: Record<ProjectKind, string> = {
    'internal-runtime': '内部运行时',
    product: '产品',
    'client-delivery': '客户项目',
    'ops-workbench': '运维工作台',
  };
  return labels[kind];
};

export const getLifecycleLabel = (stage: LifecycleStage): string => {
  const labels: Record<LifecycleStage, string> = {
    prd: 'PRD',
    'user-story': 'User Story',
    'test-case': 'Test Case',
    prototype: 'Prototype',
    implement: 'Implement',
    qa: 'QA',
    release: 'Release',
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
    ok: 'OK',
    warn: 'Warn',
    investigating: 'Investigating',
  };
  return labels[state];
};

export const getRuntimeModeLabel = (mode: RuntimeMode): string => {
  const labels: Record<RuntimeMode, string> = {
    single: 'Single',
    team: 'Team',
    ralph: 'Ralph',
  };
  return labels[mode];
};

export const getMaterialTypeLabel = (type: MaterialType): string => {
  const labels: Record<MaterialType, string> = {
    summary: 'Summary',
    prd: 'PRD',
    'user-story': 'User Story',
    'test-case': 'Test Case',
    prototype: 'Prototype',
    execution: 'Execution',
    release: 'Release',
  };
  return labels[type];
};
