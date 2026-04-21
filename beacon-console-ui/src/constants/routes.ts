export const ROUTES = {
  HOME: '/',
  MANAGEMENT: '/management',
  PROJECT_DETAIL: '/project/:id',
  RUNTIME_CENTER: '/project/:id/runtime',
  RECOVERY_DIAGNOSTICS: '/project/:id/recovery',
  MATERIAL_VIEWER: '/project/:id/materials',
  MATERIAL_DOCUMENT_DETAIL: '/project/:id/materials/:materialId',
} as const;

export const buildProjectDetailRoute = (id: string) => `/project/${id}`;
export const buildRuntimeCenterRoute = (id: string) => `/project/${id}/runtime`;
export const buildRecoveryDiagnosticsRoute = (id: string) => `/project/${id}/recovery`;
export const buildMaterialViewerRoute = (id: string) => `/project/${id}/materials`;
export const buildMaterialDocumentDetailRoute = (projectId: string, materialId: string) =>
  `/project/${projectId}/materials/${materialId}`;
