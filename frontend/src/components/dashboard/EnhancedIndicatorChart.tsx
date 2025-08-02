// frontend/src/components/dashboard/EnhancedIndicatorChart.tsx
import React, { useEffect, useState } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer, 
  BarChart, 
  Bar,
  ReferenceLine,
  ComposedChart
} from 'recharts';

interface IndicatorData {
  tanggal: string;
  bor: number;
  los: number;
  bto: number;
  toi: number;
}

interface EnhancedIndicatorChartProps {
  className?: string;
}

const EnhancedIndicatorChart: React.FC<EnhancedIndicatorChartProps> = ({ className = "" }) => {
  const [data, setData] = useState<IndicatorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartType, setChartType] = useState<'line' | 'bar' | 'composed'>('composed');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8000/api/v1/sensus/?limit=21');
      if (!response.ok) throw new Error('Failed to fetch data');
      
      const sensusData = await response.json();
      
      const chartData = sensusData.map((item: any) => ({
        tanggal: new Date(item.tanggal).toLocaleDateString('id-ID', { 
          month: 'short', 
          day: 'numeric' 
        }),
        tanggalFull: new Date(item.tanggal).toLocaleDateString('id-ID', { 
          year: 'numeric',
          month: 'long', 
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

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    
    return (
      <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-semibold text-gray-800 mb-3">{data.tanggalFull}</p>
        
        {payload.map((entry: any, index: number) => {
          let statusColor = 'text-gray-600';
          let statusText = '';
          
          // Evaluate status based on indicator type and value
          if (entry.dataKey === 'bor') {
            if (entry.value >= 90) {
              statusColor = 'text-red-600';
              statusText = 'Kritis';
            } else if (entry.value >= 80) {
              statusColor = 'text-yellow-600';
              statusText = 'Tinggi';
            } else if (entry.value >= 60) {
              statusColor = 'text-primary-600';
              statusText = 'Ideal';
            } else {
              statusColor = 'text-vmeds-600';
              statusText = 'Rendah';
            }
          } else if (entry.dataKey === 'los') {
            if (entry.value > 9) {
              statusColor = 'text-red-600';
              statusText = 'Terlalu Lama';
            } else if (entry.value >= 6) {
              statusColor = 'text-primary-600';
              statusText = 'Ideal';
            } else if (entry.value >= 3) {
              statusColor = 'text-vmeds-600';
              statusText = 'Cepat';
            } else {
              statusColor = 'text-yellow-600';
              statusText = 'Terlalu Cepat';
            }
          } else if (entry.dataKey === 'bto') {
            if (entry.value >= 3 && entry.value <= 5) {
              statusColor = 'text-primary-600';
              statusText = 'Efisien';
            } else if (entry.value >= 2) {
              statusColor = 'text-yellow-600';
              statusText = 'Sedang';
            } else {
              statusColor = 'text-red-600';
              statusText = 'Rendah';
            }
          } else if (entry.dataKey === 'toi') {
            if (entry.value >= 1 && entry.value <= 3) {
              statusColor = 'text-primary-600';
              statusText = 'Optimal';
            } else if (entry.value <= 5) {
              statusColor = 'text-yellow-600';
              statusText = 'Sedang';
            } else {
              statusColor = 'text-red-600';
              statusText = 'Tinggi';
            }
          }
          
          return (
            <div key={index} className="flex items-center justify-between gap-4 text-sm mb-1">
              <div className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="font-medium">{entry.name}:</span>
                <span className="text-gray-800 font-bold">
                  {entry.value}
                  {entry.dataKey === 'bor' ? '%' : 
                   entry.dataKey === 'los' || entry.dataKey === 'toi' ? ' hari' : 
                   entry.dataKey === 'bto' ? 'x' : ''}
                </span>
              </div>
              <span className={`text-xs font-medium ${statusColor}`}>
                {statusText}
              </span>
            </div>
          );
        })}
      </div>
    );
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg border border-primary-200 p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-primary-200 rounded mb-4 w-64"></div>
          <div className="h-80 bg-primary-200 rounded"></div>
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
            Tren Lengkap Indikator Kemenkes
          </h3>
          <p className="text-sm text-vmeds-600 mt-1">
            Monitoring 4 indikator utama dalam 21 hari terakhir dengan evaluasi status
          </p>
        </div>
        
        {/* Chart Type Toggle */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setChartType('line')}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              chartType === 'line' 
                ? 'bg-primary-500 text-white' 
                : 'bg-primary-100 text-vmeds-600 hover:bg-primary-200'
            }`}
          >
            Line
          </button>
          <button
            onClick={() => setChartType('bar')}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              chartType === 'bar' 
                ? 'bg-primary-500 text-white' 
                : 'bg-primary-100 text-vmeds-600 hover:bg-primary-200'
            }`}
          >
            Bar
          </button>
          <button
            onClick={() => setChartType('composed')}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              chartType === 'composed' 
                ? 'bg-primary-500 text-white' 
                : 'bg-primary-100 text-vmeds-600 hover:bg-primary-200'
            }`}
          >
            Mixed
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
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === 'line' ? (
            <LineChart data={data} margin={{ top: 5, right: 50, left: 20, bottom: 50 }}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="tanggal" 
                tick={{ fontSize: 11 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              {/* Primary Y-axis for BOR (%) */}
              <YAxis 
                yAxisId="left"
                tick={{ fontSize: 12 }}
                label={{ value: 'BOR (%)', angle: -90, position: 'insideLeft' }}
                domain={[0, 100]}
              />
              {/* Secondary Y-axis for other indicators */}
              <YAxis 
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 12 }}
                label={{ value: 'LOS/BTO/TOI', angle: 90, position: 'insideRight' }}
                domain={[0, 15]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '12px' }}
                iconType="line"
                verticalAlign="top"
                height={36}
              />
              
              {/* Reference lines for BOR standards */}
              <ReferenceLine yAxisId="left" y={85} stroke="#ef4444" strokeDasharray="8 8" label="BOR Kritis (85%)" />
              <ReferenceLine yAxisId="left" y={60} stroke="#f59e0b" strokeDasharray="5 5" label="BOR Minimal (60%)" />
              
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
          ) : chartType === 'bar' ? (
            <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 50 }}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="tanggal" 
                tick={{ fontSize: 11 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                label={{ value: 'Nilai', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '12px' }}
                iconType="rect"
                verticalAlign="top"
                height={36}
              />
              
              <Bar dataKey="bor" fill="#59dcd2" name="BOR (%)" />
              <Bar dataKey="los" fill="#131b62" name="LOS (hari)" />
              <Bar dataKey="bto" fill="#10b981" name="BTO (x)" />
              <Bar dataKey="toi" fill="#f59e0b" name="TOI (hari)" />
            </BarChart>
          ) : (
            <ComposedChart data={data} margin={{ top: 5, right: 50, left: 20, bottom: 50 }}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="tanggal" 
                tick={{ fontSize: 11 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              {/* Primary Y-axis for BOR (%) */}
              <YAxis 
                yAxisId="left"
                tick={{ fontSize: 12 }}
                label={{ value: 'BOR (%)', angle: -90, position: 'insideLeft' }}
                domain={[0, 100]}
              />
              {/* Secondary Y-axis for other indicators */}
              <YAxis 
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 12 }}
                label={{ value: 'LOS/BTO/TOI', angle: 90, position: 'insideRight' }}
                domain={[0, 15]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '12px' }}
                verticalAlign="top"
                height={36}
              />
              
              {/* Reference lines for BOR standards */}
              <ReferenceLine yAxisId="left" y={85} stroke="#ef4444" strokeDasharray="8 8" label="BOR Kritis" />
              <ReferenceLine yAxisId="left" y={60} stroke="#f59e0b" strokeDasharray="5 5" label="BOR Minimal" />
              
              {/* BOR as main line (most important) - Left Y-axis */}
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="bor" 
                stroke="#59dcd2" 
                strokeWidth={4}
                name="BOR (%)"
                dot={{ fill: '#59dcd2', strokeWidth: 2, r: 5 }}
              />
              
              {/* Other indicators as bars - Right Y-axis */}
              <Bar yAxisId="right" dataKey="los" fill="#131b6250" name="LOS (hari)" />
              <Bar yAxisId="right" dataKey="bto" fill="#10b98150" name="BTO (x)" />
              <Bar yAxisId="right" dataKey="toi" fill="#f59e0b50" name="TOI (hari)" />
            </ComposedChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Indicators Summary */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-primary-200">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-4 h-4 bg-teal-400 rounded" style={{backgroundColor: '#59dcd2'}}></div>
            <span className="text-sm font-bold text-vmeds-700">BOR</span>
            <span className="text-xs text-gray-500">(Skala Kiri)</span>
          </div>
          <p className="text-xs text-vmeds-500 mb-1">Bed Occupancy Rate</p>
          <p className="text-xs text-primary-600 font-medium">Ideal: 60-85%</p>
          <p className="text-xs text-vmeds-400">Tingkat hunian tempat tidur</p>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-4 h-4 rounded" style={{backgroundColor: '#131b62'}}></div>
            <span className="text-sm font-bold text-vmeds-700">LOS</span>
            <span className="text-xs text-gray-500">(Skala Kanan)</span>
          </div>
          <p className="text-xs text-vmeds-500 mb-1">Length of Stay</p>
          <p className="text-xs text-vmeds-600 font-medium">Ideal: 6-9 hari</p>
          <p className="text-xs text-vmeds-400">Rata-rata lama dirawat</p>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-4 h-4 rounded" style={{backgroundColor: '#10b981'}}></div>
            <span className="text-sm font-bold text-vmeds-700">BTO</span>
            <span className="text-xs text-gray-500">(Skala Kanan)</span>
          </div>
          <p className="text-xs text-vmeds-500 mb-1">Bed Turn Over</p>
          <p className="text-xs text-green-600 font-medium">Ideal: 40-50x/tahun</p>
          <p className="text-xs text-vmeds-400">Frekuensi pemakaian TT</p>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-4 h-4 rounded" style={{backgroundColor: '#f59e0b'}}></div>
            <span className="text-sm font-bold text-vmeds-700">TOI</span>
            <span className="text-xs text-gray-500">(Skala Kanan)</span>
          </div>
          <p className="text-xs text-vmeds-500 mb-1">Turn Over Interval</p>
          <p className="text-xs text-orange-600 font-medium">Ideal: 1-3 hari</p>
          <p className="text-xs text-vmeds-400">Interval kosong TT</p>
        </div>
      </div>

      {/* Dual Y-axis Information */}
      <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div className="flex items-start gap-2">
          <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold">i</div>
          <div>
            <h4 className="text-sm font-semibold text-blue-800 mb-1">Multi-Indicator Chart</h4>
            <p className="text-xs text-blue-700">
              <strong>BOR (garis tebal teal)</strong> menggunakan skala kiri (0-100%). <br/>
              <strong>LOS, BTO, TOI</strong> menggunakan skala kanan (0-15) untuk visibilitas yang lebih baik.
            </p>
          </div>
        </div>
      </div>

      {/* Status Legend */}
      <div className="mt-4 bg-primary-50 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-vmeds-700 mb-3">Status Evaluasi Indikator:</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-primary-600 font-bold">Ideal</span>
            <span className="text-vmeds-500">Sesuai standar Kemenkes</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-yellow-600 font-bold">Perhatian</span>
            <span className="text-vmeds-500">Perlu monitoring</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-red-600 font-bold">Kritis</span>
            <span className="text-vmeds-500">Perlu tindakan segera</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-vmeds-600 font-bold">Info</span>
            <span className="text-vmeds-500">Perlu evaluasi</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedIndicatorChart;
