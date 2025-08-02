// frontend/src/components/dashboard/SimpleIndicatorChart.tsx
import React, { useEffect, useState } from 'react';

interface IndicatorData {
  tanggal: string;
  bor: number;
  los: number;
  bto: number;
  toi: number;
}

interface SimpleIndicatorChartProps {
  className?: string;
}

const SimpleIndicatorChart: React.FC<SimpleIndicatorChartProps> = ({ className = "" }) => {
  const [data, setData] = useState<IndicatorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8000/api/v1/sensus/?limit=14');
      if (!response.ok) throw new Error('Failed to fetch data');
      
      const sensusData = await response.json();
      
      const chartData = sensusData.map((item: any) => ({
        tanggal: new Date(item.tanggal).toLocaleDateString('id-ID', { 
          month: 'short', 
          day: 'numeric' 
        }),
        bor: parseFloat(item.bor.toFixed(2)),
        los: parseFloat((item.los || 0).toFixed(2)),
        bto: parseFloat((item.bto || 0).toFixed(2)),
        toi: parseFloat((item.toi || 0).toFixed(2))
      }));
      
      setData(chartData.reverse());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getBarHeight = (value: number, max: number) => {
    return Math.max((value / max) * 100, 2); // minimum 2% height
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4 w-64"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
        <div className="text-center text-red-600">
          <p className="font-medium">Error loading chart data</p>
          <p className="text-sm text-gray-500 mt-1">{error}</p>
          <button 
            onClick={fetchData}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const maxValues = {
    bor: Math.max(...data.map(d => d.bor)),
    los: Math.max(...data.map(d => d.los)),
    bto: Math.max(...data.map(d => d.bto)),
    toi: Math.max(...data.map(d => d.toi))
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-800">
            Tren Semua Indikator Kemenkes (14 Hari)
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Visualisasi sederhana untuk BOR, LOS, BTO, dan TOI
          </p>
        </div>
        
        <button 
          onClick={fetchData}
          className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Simple Bar Chart */}
      <div className="space-y-8">
        {/* BOR Chart */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-4 h-4 rounded" style={{backgroundColor: '#59dcd2'}}></div>
            <h4 className="font-semibold text-gray-700">BOR (Bed Occupancy Rate) - %</h4>
            <span className="text-xs text-gray-500">Target: 60-85%</span>
          </div>
          <div className="flex items-end gap-1 h-20 bg-gray-50 rounded p-2">
            {data.map((item, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div 
                  className="w-full rounded-t transition-all hover:opacity-80"
                  style={{ 
                    height: `${getBarHeight(item.bor, 100)}%`,
                    backgroundColor: '#59dcd2'
                  }}
                  title={`${item.tanggal}: ${item.bor}%`}
                ></div>
                <span className="text-xs text-gray-500 mt-1 transform -rotate-45 origin-center">
                  {item.tanggal}
                </span>
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>

        {/* LOS Chart */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-4 h-4 rounded" style={{backgroundColor: '#131b62'}}></div>
            <h4 className="font-semibold text-gray-700">LOS (Length of Stay) - Hari</h4>
            <span className="text-xs text-gray-500">Target: 6-9 hari</span>
          </div>
          <div className="flex items-end gap-1 h-20 bg-gray-50 rounded p-2">
            {data.map((item, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div 
                  className="w-full rounded-t transition-all hover:opacity-80"
                  style={{ 
                    height: `${getBarHeight(item.los, maxValues.los)}%`,
                    backgroundColor: '#131b62'
                  }}
                  title={`${item.tanggal}: ${item.los} hari`}
                ></div>
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0</span>
            <span>{Math.round(maxValues.los / 2)}</span>
            <span>{Math.round(maxValues.los)}</span>
          </div>
        </div>

        {/* BTO Chart */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-4 h-4 rounded" style={{backgroundColor: '#10b981'}}></div>
            <h4 className="font-semibold text-gray-700">BTO (Bed Turn Over) - x/bulan</h4>
            <span className="text-xs text-gray-500">Target: 3-4x/bulan</span>
          </div>
          <div className="flex items-end gap-1 h-20 bg-gray-50 rounded p-2">
            {data.map((item, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div 
                  className="w-full rounded-t transition-all hover:opacity-80"
                  style={{ 
                    height: `${getBarHeight(item.bto, maxValues.bto)}%`,
                    backgroundColor: '#10b981'
                  }}
                  title={`${item.tanggal}: ${item.bto}x`}
                ></div>
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0</span>
            <span>{Math.round(maxValues.bto / 2)}</span>
            <span>{Math.round(maxValues.bto)}</span>
          </div>
        </div>

        {/* TOI Chart */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-4 h-4 rounded" style={{backgroundColor: '#f59e0b'}}></div>
            <h4 className="font-semibold text-gray-700">TOI (Turn Over Interval) - Hari</h4>
            <span className="text-xs text-gray-500">Target: 1-3 hari</span>
          </div>
          <div className="flex items-end gap-1 h-20 bg-gray-50 rounded p-2">
            {data.map((item, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div 
                  className="w-full rounded-t transition-all hover:opacity-80"
                  style={{ 
                    height: `${getBarHeight(item.toi, maxValues.toi)}%`,
                    backgroundColor: '#f59e0b'
                  }}
                  title={`${item.tanggal}: ${item.toi} hari`}
                ></div>
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0</span>
            <span>{Math.round(maxValues.toi / 2)}</span>
            <span>{Math.round(maxValues.toi)}</span>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-3 h-3 rounded" style={{backgroundColor: '#59dcd2'}}></div>
            <span className="text-sm font-bold text-gray-700">BOR</span>
          </div>
          <p className="text-xs text-gray-500 mb-1">Bed Occupancy Rate</p>
          <p className="text-xs font-medium" style={{color: '#59dcd2'}}>Avg: {(data.reduce((sum, d) => sum + d.bor, 0) / data.length).toFixed(1)}%</p>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-3 h-3 rounded" style={{backgroundColor: '#131b62'}}></div>
            <span className="text-sm font-bold text-gray-700">LOS</span>
          </div>
          <p className="text-xs text-gray-500 mb-1">Length of Stay</p>
          <p className="text-xs font-medium" style={{color: '#131b62'}}>Avg: {(data.reduce((sum, d) => sum + d.los, 0) / data.length).toFixed(1)} hari</p>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-3 h-3 rounded" style={{backgroundColor: '#10b981'}}></div>
            <span className="text-sm font-bold text-gray-700">BTO</span>
          </div>
          <p className="text-xs text-gray-500 mb-1">Bed Turn Over</p>
          <p className="text-xs font-medium" style={{color: '#10b981'}}>Avg: {(data.reduce((sum, d) => sum + d.bto, 0) / data.length).toFixed(1)}x</p>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-3 h-3 rounded" style={{backgroundColor: '#f59e0b'}}></div>
            <span className="text-sm font-bold text-gray-700">TOI</span>
          </div>
          <p className="text-xs text-gray-500 mb-1">Turn Over Interval</p>
          <p className="text-xs font-medium" style={{color: '#f59e0b'}}>Avg: {(data.reduce((sum, d) => sum + d.toi, 0) / data.length).toFixed(1)} hari</p>
        </div>
      </div>

      {/* Status Info */}
      <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-green-800 mb-2">
          ✅ Semua Indikator Kemenkes Tersedia
        </h4>
        <p className="text-xs text-green-700">
          Sistem telah mengimplementasikan lengkap semua 4 indikator utama sesuai standar 
          Kementerian Kesehatan RI untuk monitoring efisiensi pelayanan rumah sakit.
        </p>
      </div>
    </div>
  );
};

export default SimpleIndicatorChart;
