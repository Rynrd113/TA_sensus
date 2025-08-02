// frontend/src/components/charts/AllIndicatorsChart.tsx
import React from 'react';




const AllIndicatorsChart: React.FC = () => {


  return (
    <div className="bg-white rounded-lg border border-primary-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-vmeds-800">
            Trend Semua Indikator Kemenkes
          </h3>
          <p className="text-sm text-vmeds-600 mt-1">
            BOR, LOS, BTO, dan TOI - 7 hari terakhir
          </p>
        </div>
        {/* Refresh button removed (no dynamic data) */}
      </div>

      {/* Chart Visualization */}
      <div className="h-80 bg-primary-50 rounded-lg p-4">
        <div className="h-full flex flex-col justify-between">
          <div className="grid grid-cols-4 gap-4 text-center mb-4">
            <div className="bg-white rounded-lg p-3 border border-primary-200">
              <div className="flex items-center justify-center gap-2 mb-1">
                <div className="w-3 h-3 bg-primary-500 rounded"></div>
                <span className="text-sm font-medium text-gray-700">BOR</span>
              </div>
              <p className="text-lg font-bold text-primary-700">72.5%</p>
              <p className="text-xs text-primary-600">Target: 60-85%</p>
            </div>
            
            <div className="bg-white rounded-lg p-3 border border-vmeds-200">
              <div className="flex items-center justify-center gap-2 mb-1">
                <div className="w-3 h-3 bg-vmeds-500 rounded"></div>
                <span className="text-sm font-medium text-gray-700">LOS</span>
              </div>
              <p className="text-lg font-bold text-vmeds-700">7.2 hari</p>
              <p className="text-xs text-vmeds-600">Target: 6-9 hari</p>
            </div>
            
            <div className="bg-white rounded-lg p-3 border border-success-200">
              <div className="flex items-center justify-center gap-2 mb-1">
                <div className="w-3 h-3 bg-success-500 rounded"></div>
                <span className="text-sm font-medium text-gray-700">BTO</span>
              </div>
              <p className="text-lg font-bold text-success-700">3.8x</p>
              <p className="text-xs text-success-600">Target: 3-4x</p>
            </div>
            
            <div className="bg-white rounded-lg p-3 border border-warning-200">
              <div className="flex items-center justify-center gap-2 mb-1">
                <div className="w-3 h-3 bg-warning-500 rounded"></div>
                <span className="text-sm font-medium text-gray-700">TOI</span>
              </div>
              <p className="text-lg font-bold text-warning-700">2.1 hari</p>
              <p className="text-xs text-warning-600">Target: 1-3 hari</p>
            </div>
          </div>

          {/* Simulated Chart Area */}
          <div className="flex-1 bg-white rounded-lg border border-primary-200 p-4 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-primary-700 font-medium">Multi-Indicator Chart</p>
              <p className="text-xs text-primary-600 mt-1">
                Visualisasi trend 4 indikator dengan warna berbeda
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Status Summary */}
      <div className="mt-4 bg-success-50 border border-success-200 rounded-lg p-3">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-success-500 rounded-full"></div>
          <span className="text-sm font-medium text-success-800">
            Status: Semua indikator dalam rentang optimal
          </span>
        </div>
      </div>
    </div>
  );
};

export default AllIndicatorsChart;
