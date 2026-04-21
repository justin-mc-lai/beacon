export type ProjectType = 'single-repo' | 'multi-repo' | 'workspace';

export type ProjectKind =
  | 'internal-runtime'
  | 'product'
  | 'client-delivery'
  | 'ops-workbench';

export type HealthStatus = 'healthy' | 'degraded' | 'blocked' | 'error';

export type DebugState = 'ok' | 'warn' | 'investigating';

export type LifecycleStage =
  | 'prd'
  | 'user-story'
  | 'test-case'
  | 'prototype'
  | 'implement'
  | 'qa'
  | 'release';

export type RequirementStatus = 'missing' | 'draft' | 'ready' | 'frozen';

export type RuntimeMode = 'single' | 'team' | 'ralph';

export type MaterialType =
  | 'summary'
  | 'prd'
  | 'user-story'
  | 'test-case'
  | 'prototype'
  | 'execution'
  | 'release';

export interface GitStatus {
  branch: string;
  dirty: boolean;
  ahead: number;
  behind: number;
  expectedBranch?: string;
}

export interface FeatureTrack {
  slug: string;
  title: string;
  track: 'main' | 'parallel';
  stage: LifecycleStage;
  status: RequirementStatus | 'active';
  summary: string;
  sourcePath: string;
}

export interface RequirementClosure {
  prd: RequirementStatus;
  userStory: RequirementStatus;
  testCase: RequirementStatus;
  prototype: RequirementStatus;
  implement: RequirementStatus;
  qa: RequirementStatus;
  release: RequirementStatus;
}

export interface RuntimeSummary {
  activeMode: RuntimeMode;
  activeRuns: number;
  summary: string;
  linkedRun: string;
}

export interface SessionMetadata {
  host: 'Codex' | 'Claude';
  sessionRef: string;
  updatedAt: string;
  transcriptRef: string;
}

export interface TeamAgent {
  name: string;
  role: string;
  status: string;
  linkedRun: string;
  artifactRefs: string[];
  session: SessionMetadata;
}

export interface RalphLoop {
  roundCount: number;
  failureStreak: number;
  nextAction: string;
  blocker: string;
  recentResult: string;
}

export interface RuntimeModeDetail {
  mode: RuntimeMode;
  status: string;
  stage: LifecycleStage;
  progress: number;
  summary: string;
  linkedRun: string;
  startedAt: string;
  completedAt?: string;
  artifactRefs: string[];
  hostSession?: SessionMetadata;
  timeline: string[];
  teamAgents?: TeamAgent[];
  ralphLoop?: RalphLoop;
}

export interface RecoveryIssue {
  severity: 'critical' | 'warning' | 'info';
  title: string;
  detail: string;
  recommendation: string;
}

export interface RecoveryState {
  status: 'healthy-warning' | 'degraded' | 'rebuild-suggested' | 'doctor-suggested';
  truthSources: string[];
  issues: RecoveryIssue[];
  steps: string[];
  riskNotes: string[];
}

export interface MaterialDocument {
  id: string;
  title: string;
  version: string;
  type: MaterialType;
  feature: string;
  path: string;
  summary: string;
  content: string;
  relatedIds: string[];
  createdAt: string;
  updatedAt: string;
}

export interface Project {
  id: string;
  name: string;
  type: ProjectType;
  kind: ProjectKind;
  rootPath: string;
  owner: string;
  currentVersion: string;
  lifecycle: LifecycleStage;
  healthStatus: HealthStatus;
  debugState: DebugState;
  gitStatus: GitStatus;
  currentFeature: string;
  progress: number;
  blocker: string;
  currentDelivery: string;
  latestDelivery: string[];
  nextStep: string;
  recommendedSkill: string;
  interventionReason: string;
  versionLine: string[];
  mainTracks: FeatureTrack[];
  parallelTracks: FeatureTrack[];
  requirementClosure: RequirementClosure;
  runtimeSummary: RuntimeSummary;
  runtimeDetails: RuntimeModeDetail[];
  recovery: RecoveryState;
  materials: MaterialDocument[];
}

export interface PortfolioSummary {
  totalProjects: number;
  blockedProjects: number;
  activeRuntimeCount: number;
  interventionCount: number;
  deliveredToday: number;
}
