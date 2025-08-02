import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy, useEffect } from 'react';
import MainLayout from './layouts/MainLayout';
import ErrorBoundary from './components/ErrorBoundary';

// Lazy load pages with better chunking
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const BangsalPage = lazy(() => import('./pages/BangsalPage'));
const ChartPage = lazy(() => 
  import('./pages/ChartPage').then(module => ({ default: module.default }))
);
const AllIndicatorsPage = lazy(() => import('./pages/AllIndicatorsPage'));

// Medical Loading Component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen bg-primary-50">
    <div className="medical-container">
      <div className="bg-white rounded-xl border border-primary-200 p-8 text-center shadow-lg">
        <div className="animate-spin w-8 h-8 mx-auto mb-4 border-4 border-primary-200 border-t-primary-500 rounded-full"></div>
        <div className="h-4 w-3/4 mx-auto mb-2 bg-primary-200 rounded animate-pulse"></div>
        <div className="h-4 w-1/2 mx-auto bg-primary-200 rounded animate-pulse"></div>
      </div>
    </div>
  </div>
);

function App() {
  // Menandai app sudah loaded untuk hide initial spinner
  useEffect(() => {
    const timer = setTimeout(() => {
      document.body.classList.add('app-loaded');
    }, 100);
    
    return () => clearTimeout(timer);
  }, []);

  return (
    <ErrorBoundary>
      <Router
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true
        }}
      >
        <div className="App">
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={
                <Suspense fallback={<LoadingSpinner />}>
                  <DashboardPage />
                </Suspense>
              } />
              <Route path="bangsal" element={
                <Suspense fallback={<LoadingSpinner />}>
                  <BangsalPage />
                </Suspense>
              } />
              <Route path="chart" element={
                <Suspense fallback={<LoadingSpinner />}>
                  <ChartPage />
                </Suspense>
              } />
              <Route path="indikator" element={
                <Suspense fallback={<LoadingSpinner />}>
                  <AllIndicatorsPage />
                </Suspense>
              } />
              <Route path="indikator-lengkap" element={
                <Suspense fallback={<LoadingSpinner />}>
                  <AllIndicatorsPage />
                </Suspense>
              } />
              <Route path="charts" element={
                <Suspense fallback={<LoadingSpinner />}>
                  <ChartPage />
                </Suspense>
              } />
            </Route>
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;