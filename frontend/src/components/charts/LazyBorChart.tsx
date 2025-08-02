// Lazy-loaded chart component untuk mengurangi bundle size
import { memo, lazy, Suspense } from 'react';

// Lazy import chart component untuk mengurangi initial bundle
const BorChart = lazy(() => import('./BorChart'));

interface LazyBorChartProps {
  data: any[];
  showPrediction?: boolean;
}

// Memoized chart skeleton loader
const ChartSkeleton = memo(() => (
  <div className="bg-white rounded-lg border border-gray-200 p-6">
    <div className="skeleton h-6 w-48 mb-4 rounded"></div>
    <div className="skeleton h-64 w-full rounded-lg"></div>
    <div className="flex justify-between mt-4">
      <div className="skeleton h-4 w-24 rounded"></div>
      <div className="skeleton h-4 w-24 rounded"></div>
    </div>
  </div>
));

ChartSkeleton.displayName = 'ChartSkeleton';

const LazyBorChart = memo<LazyBorChartProps>(({ data, showPrediction }) => {
  return (
    <Suspense fallback={<ChartSkeleton />}>
      <BorChart 
        data={data} 
        showPrediction={showPrediction} 
      />
    </Suspense>
  );
});

LazyBorChart.displayName = 'LazyBorChart';

export default LazyBorChart;
