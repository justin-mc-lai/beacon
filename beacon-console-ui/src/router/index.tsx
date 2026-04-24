import { Suspense, lazy, type ReactNode } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import { Layout } from '../components/Layout';
import { Loading } from '../components/Loading';
import {
  ROUTES,
  buildMaterialDocumentDetailRoute,
  buildMaterialViewerRoute,
  buildProjectDetailRoute,
  buildRecoveryDiagnosticsRoute,
  buildRuntimeCenterRoute,
} from '../constants/routes';

const HomePage = lazy(async () => {
  const module = await import('../pages/HomePage');
  return { default: module.HomePage };
});
const ManagementOverviewPage = lazy(async () => {
  const module = await import('../pages/ManagementOverviewPage');
  return { default: module.ManagementOverviewPage };
});
const ProjectDetailPage = lazy(async () => {
  const module = await import('../pages/ProjectDetailPage');
  return { default: module.ProjectDetailPage };
});
const RuntimeCenterPage = lazy(async () => {
  const module = await import('../pages/RuntimeCenterPage');
  return { default: module.RuntimeCenterPage };
});
const RecoveryDiagnosticsPage = lazy(async () => {
  const module = await import('../pages/RecoveryDiagnosticsPage');
  return { default: module.RecoveryDiagnosticsPage };
});
const MaterialViewerPage = lazy(async () => {
  const module = await import('../pages/MaterialViewerPage');
  return { default: module.MaterialViewerPage };
});
const MaterialDocumentDetailPage = lazy(async () => {
  const module = await import('../pages/MaterialDocumentDetailPage');
  return { default: module.MaterialDocumentDetailPage };
});

function withSuspense(node: ReactNode) {
  return <Suspense fallback={<Loading tip="页面加载中..." />}>{node}</Suspense>;
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        path: ROUTES.HOME,
        element: withSuspense(<HomePage />),
      },
      {
        path: ROUTES.MANAGEMENT,
        element: withSuspense(<ManagementOverviewPage />),
      },
      {
        path: buildProjectDetailRoute(':id'),
        element: withSuspense(<ProjectDetailPage />),
      },
      {
        path: buildRuntimeCenterRoute(':id'),
        element: withSuspense(<RuntimeCenterPage />),
      },
      {
        path: buildRecoveryDiagnosticsRoute(':id'),
        element: withSuspense(<RecoveryDiagnosticsPage />),
      },
      {
        path: buildMaterialViewerRoute(':id'),
        element: withSuspense(<MaterialViewerPage />),
      },
      {
        path: buildMaterialDocumentDetailRoute(':id', ':materialId'),
        element: withSuspense(<MaterialDocumentDetailPage />),
      },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
