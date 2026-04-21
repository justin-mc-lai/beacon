import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import { Layout } from '../components/Layout';
import {
  ROUTES,
  buildMaterialDocumentDetailRoute,
  buildMaterialViewerRoute,
  buildProjectDetailRoute,
  buildRecoveryDiagnosticsRoute,
  buildRuntimeCenterRoute,
} from '../constants/routes';
import { HomePage } from '../pages/HomePage';
import { ManagementOverviewPage } from '../pages/ManagementOverviewPage';
import { MaterialDocumentDetailPage } from '../pages/MaterialDocumentDetailPage';
import { MaterialViewerPage } from '../pages/MaterialViewerPage';
import { ProjectDetailPage } from '../pages/ProjectDetailPage';
import { RecoveryDiagnosticsPage } from '../pages/RecoveryDiagnosticsPage';
import { RuntimeCenterPage } from '../pages/RuntimeCenterPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        path: ROUTES.HOME,
        element: <HomePage />,
      },
      {
        path: ROUTES.MANAGEMENT,
        element: <ManagementOverviewPage />,
      },
      {
        path: buildProjectDetailRoute(':id'),
        element: <ProjectDetailPage />,
      },
      {
        path: buildRuntimeCenterRoute(':id'),
        element: <RuntimeCenterPage />,
      },
      {
        path: buildRecoveryDiagnosticsRoute(':id'),
        element: <RecoveryDiagnosticsPage />,
      },
      {
        path: buildMaterialViewerRoute(':id'),
        element: <MaterialViewerPage />,
      },
      {
        path: buildMaterialDocumentDetailRoute(':id', ':materialId'),
        element: <MaterialDocumentDetailPage />,
      },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
