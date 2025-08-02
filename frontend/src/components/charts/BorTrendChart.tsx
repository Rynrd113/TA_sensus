// frontend/src/components/charts/BorTrendChart.tsx
import React, { useState, useEffect } from 'react';
import { RefreshIcon } from '../icons';

interface BorData {
  tanggal: string;
  bor: number;
  prediksi?: boolean;
}

const BorTrendChart: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);


  useEffect(() => {
    const fetchData = async () => {
      try {
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (err) {
        setError('Error loading data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const refreshData = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 500));
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-primary-200 p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-primary-200 rounded mb-4 w-48"></div>
          <div className="h-64 bg-primary-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-primary-200 p-6">
        <div className="text-center text-red-600">
          <p className="font-medium">Error loading chart data</p>
          <button
            onClick={refreshData}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-primary-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-vmeds-800">
            BOR Trend + Prediksi
          </h3>
          <p className="text-sm text-vmeds-600 mt-1">
            Data aktual vs prediksi 3 hari ke depan
          </p>
        </div>
        <button
          onClick={refreshData}
          className="px-3 py-1 bg-primary-500 text-white text-xs rounded hover:bg-primary-600 transition-colors"
        >
          <RefreshIcon className="w-4 h-4 inline mr-1" />
          Refresh
        </button>
      </div>

      {/* Chart Visualization */}
      <div className="h-80 bg-vmeds-50 rounded-lg p-4">
        <div className="h-full flex flex-col">
          {/* Current BOR Status */}
          <div className="bg-white rounded-lg p-4 border border-vmeds-200 mb-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-vmeds-800">BOR Saat Ini</h4>
                <p className="text-2xl font-bold text-primary-700">74.1%</p>
                <p className="text-xs text-primary-600">Status: Optimal (60-85%)</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-vmeds-600">Prediksi Besok</p>
                <p className="text-lg font-bold text-blue-700">73.2%</p>
                <p className="text-xs text-blue-600">Tetap optimal</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
          <span className="text-vmeds-600">Data Aktual</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
          <span className="text-vmeds-600">Prediksi ML</span>
        </div>
      </div>
    </div>
  );
};

export default BorTrendChart;
