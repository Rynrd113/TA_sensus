import { createBrowserRouter } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import SensusPage from './pages/SensusPage';
import PrediksiPage from './pages/PrediksiPage';
import ChartPage from './pages/ChartPage';
import AllIndicatorsPage from './pages/AllIndicatorsPage';
import BangsalPage from './pages/BangsalPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <DashboardPage />,
  },
  {
    path: '/dashboard',
    element: <DashboardPage />,
  },
  {
    path: '/sensus',
    element: <SensusPage />,
  },
  {
    path: '/bangsal',
    element: <BangsalPage />,
  },
  {
    path: '/indikator',
    element: <AllIndicatorsPage />,
  },
  {
    path: '/indikator-lengkap',
    element: <AllIndicatorsPage />,
  },
  {
    path: '/prediksi',
    element: <PrediksiPage />,
  },
  {
    path: '/chart',
    element: <ChartPage />,
  },
]);

export default router;
