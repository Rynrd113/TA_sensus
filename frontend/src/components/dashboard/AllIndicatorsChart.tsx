// frontend/src/components/dashboard/AllIndicatorsChart.tsx
import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface IndikatorData {
  tanggal: string;
  bor: number;
  los: number;
  bto: number;
  toi: number;
}

interface AllIndicatorsChartProps {
  className?: string;
}

const AllIndicatorsChart: React.FC<AllIndicatorsChartProps> = ({ className = "" }) => {
  const [data, setData] = useState<IndikatorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'line' | 'bar'>('line');

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch data sensus untuk indikator
      const response = await fetch('http://localhost:8000/api/v1/sensus/?limit=14');
      if (!response.ok) throw new Error('Failed to fetch data');
      
      const sensusData = await response.json();
      
      const chartData = sensusData.map((item: any) => ({
        tanggal: new Date(item.tanggal).toLocaleDateString('id-ID', { 
          month: 'short', 
          day: 'numeric' 
        }),
        bor: parseFloat(item.bor.toFixed(1)),
        los: parseFloat((item.los || 0).toFixed(1)),
        bto: parseFloat((item.bto || 0).toFixed(1)),
        toi: parseFloat((item.toi || 0).toFixed(1))
      }));
      
      setData(chartData.reverse()); // Latest data last
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-semibold text-gray-800 mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div 
              className="w-3 h-3 rounded"
              style={{ backgroundColor: entry.color }}
            />
            <span className="font-medium">{entry.name}:</span>
            <span className="text-gray-600">
              {entry.value}
              {entry.dataKey === 'bor' ? '%' : 
               entry.dataKey === 'los' || entry.dataKey === 'toi' ? ' hari' : 
               entry.dataKey === 'bto' ? 'x' : ''}
            </span>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg border border-primary-200 p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-primary-200 rounded mb-4 w-48"></div>
          <div className="h-64 bg-primary-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg border border-primary-200 p-6 ${className}`}>
        <div className="text-center text-red-600">
          <p className="font-medium">Error loading chart data</p>
          <p className="text-sm text-vmeds-500 mt-1">{error}</p>
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

  return (
    <div className={`bg-white rounded-lg border border-primary-200 p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-vmeds-800">
            Semua Indikator Kemenkes - Tren 14 Hari
          </h3>
          <p className="text-sm text-vmeds-600 mt-1">
            BOR, LOS, BTO, dan TOI - Sistem mengimplementasikan lengkap 4 indikator utama
          </p>
          <div className="flex items-center gap-4 mt-2 text-xs">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
              <span className="text-primary-600 font-medium">Semua Indikator Aktif</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
              <span className="text-primary-600 font-medium">Real-time Update</span>
            </span>
          </div>
        </div>
        
        {/* View Mode Toggle */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode('line')}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              viewMode === 'line' 
                ? 'bg-primary-500 text-white' 
                : 'bg-primary-100 text-vmeds-600 hover:bg-primary-200'
            }`}
          >
            Line
          </button>
          <button
            onClick={() => setViewMode('bar')}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              viewMode === 'bar' 
                ? 'bg-primary-500 text-white' 
                : 'bg-primary-100 text-vmeds-600 hover:bg-primary-200'
            }`}
          >
            Bar
          </button>
          <button 
            onClick={fetchData}
            className="ml-2 px-3 py-1 bg-primary-500 text-white text-xs rounded hover:bg-primary-600 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          {viewMode === 'line' ? (
            <LineChart data={data} margin={{ top: 5, right: 50, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="tanggal" 
                tick={{ fontSize: 12 }}
                tickLine={{ stroke: '#6b7280' }}
              />
              {/* Primary Y-axis for BOR (%) */}
              <YAxis 
                yAxisId="left"
                tick={{ fontSize: 12 }}
                tickLine={{ stroke: '#6b7280' }}
                label={{ value: 'BOR (%)', angle: -90, position: 'insideLeft' }}
                domain={[0, 100]}
              />
              {/* Secondary Y-axis for other indicators */}
              <YAxis 
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 12 }}
                tickLine={{ stroke: '#6b7280' }}
                label={{ value: 'LOS/BTO/TOI', angle: 90, position: 'insideRight' }}
                domain={[0, 15]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '14px' }}
                iconType="line"
              />
              
              {/* BOR - Primary Teal (Left Y-axis) */}
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="bor" 
                stroke="#59dcd2" 
                strokeWidth={4}
                name="BOR (%)"
                dot={{ fill: '#59dcd2', strokeWidth: 2, r: 5 }}
                activeDot={{ r: 7, fill: '#59dcd2' }}
              />
              
              {/* LOS - Navy (Right Y-axis) */}
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="los" 
                stroke="#131b62" 
                strokeWidth={3}
                name="LOS (hari)"
                dot={{ fill: '#131b62', strokeWidth: 2, r: 4 }}
                strokeDasharray="5 5"
              />
              
              {/* BTO - Green (Right Y-axis) */}
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="bto" 
                stroke="#10b981" 
                strokeWidth={3}
                name="BTO (x)"
                dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                strokeDasharray="8 4"
              />
              
              {/* TOI - Orange (Right Y-axis) */}
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="toi" 
                stroke="#f59e0b" 
                strokeWidth={3}
                name="TOI (hari)"
                dot={{ fill: '#f59e0b', strokeWidth: 2, r: 4 }}
                strokeDasharray="2 2"
              />
            </LineChart>
          ) : (
            <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="tanggal" 
                tick={{ fontSize: 12 }}
                tickLine={{ stroke: '#6b7280' }}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickLine={{ stroke: '#6b7280' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '14px' }}
                iconType="rect"
              />
              
              <Bar dataKey="bor" fill="#59dcd2" name="BOR (%)" />
              <Bar dataKey="los" fill="#131b62" name="LOS (hari)" />
              <Bar dataKey="bto" fill="#10b981" name="BTO (x)" />
              <Bar dataKey="toi" fill="#f59e0b" name="TOI (hari)" />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Indicator Info */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-1">
            <div className="w-3 h-3 rounded" style={{backgroundColor: '#59dcd2'}}></div>
            <span className="text-sm font-medium text-gray-700">BOR</span>
            <span className="text-xs text-gray-500">(Skala Kiri)</span>
          </div>
          <p className="text-xs text-gray-500">Bed Occupancy Rate</p>
          <p className="text-xs text-blue-600 font-medium">Ideal: 60-85%</p>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-1">
            <div className="w-3 h-3 rounded" style={{backgroundColor: '#131b62'}}></div>
            <span className="text-sm font-medium text-gray-700">LOS</span>
            <span className="text-xs text-gray-500">(Skala Kanan)</span>
          </div>
          <p className="text-xs text-gray-500">Length of Stay</p>
          <p className="text-xs text-blue-600 font-medium">Ideal: 6-9 hari</p>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-1">
            <div className="w-3 h-3 rounded" style={{backgroundColor: '#10b981'}}></div>
            <span className="text-sm font-medium text-gray-700">BTO</span>
            <span className="text-xs text-gray-500">(Skala Kanan)</span>
          </div>
          <p className="text-xs text-gray-500">Bed Turn Over</p>
          <p className="text-xs text-green-600 font-medium">Ideal: 40-50x/tahun</p>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-1">
            <div className="w-3 h-3 rounded" style={{backgroundColor: '#f59e0b'}}></div>
            <span className="text-sm font-medium text-gray-700">TOI</span>
            <span className="text-xs text-gray-500">(Skala Kanan)</span>
          </div>
          <p className="text-xs text-gray-500">Turn Over Interval</p>
          <p className="text-xs text-orange-600 font-medium">Ideal: 1-3 hari</p>
        </div>
      </div>

      {/* Multi-scale information */}
      <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-3">
        <div className="flex items-start gap-2">
          <div className="w-5 h-5 bg-amber-500 rounded-full flex items-center justify-center text-white text-xs font-bold">!</div>
          <div>
            <h4 className="text-sm font-semibold text-amber-800 mb-1">Dual Y-Axis Chart</h4>
            <p className="text-xs text-amber-700">
              Chart menggunakan 2 skala Y untuk menampilkan semua indikator dengan jelas. 
              <strong>BOR</strong> (skala kiri 0-100%), <strong>LOS/BTO/TOI</strong> (skala kanan 0-15).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AllIndicatorsChart;
