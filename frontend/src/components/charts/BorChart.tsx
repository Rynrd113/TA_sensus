import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine
} from 'recharts';
import dayjs from 'dayjs';

interface BorDataPoint {
  tanggal: string;
  bor: number;
  jenis: 'aktual' | 'prediksi';
  pasien_akhir?: number;
  tempat_tidur?: number;
}

interface BorChartProps {
  data: BorDataPoint[];
  title?: string;
  showPrediction?: boolean;
}

const BorChart: React.FC<BorChartProps> = ({ 
  data, 
  title = "Grafik BOR Harian & Prediksi",
  showPrediction = true 
}) => {
  
  // Format data untuk chart
  const chartData = data.map(point => ({
    tanggal: dayjs(point.tanggal).format('DD/MM'),
    tanggalFull: dayjs(point.tanggal).format('DD MMM YYYY'),
    bor: Math.round(point.bor * 10) / 10,
    borAktual: point.jenis === 'aktual' ? Math.round(point.bor * 10) / 10 : null,
    borPrediksi: point.jenis === 'prediksi' ? Math.round(point.bor * 10) / 10 : null,
    jenis: point.jenis,
    pasien_akhir: point.pasien_akhir,
    tempat_tidur: point.tempat_tidur,
    isKritis: point.bor > 85,
    isOptimal: point.bor >= 60 && point.bor <= 85
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-800">{data.tanggalFull}</p>
          <p className="text-blue-600">
            BOR: <span className="font-bold">{data.bor}%</span>
          </p>
          {data.pasien_akhir && (
            <p className="text-gray-600 text-sm">
              Pasien: {data.pasien_akhir} / {data.tempat_tidur} TT
            </p>
          )}
          <p className={`text-xs font-medium ${
            data.jenis === 'prediksi' ? 'text-orange-600' : 'text-green-600'
          }`}>
            {data.jenis === 'prediksi' ? 'Prediksi' : 'Data Aktual'}
          </p>
          
          {/* Status BOR */}
          <div className={`text-xs px-2 py-1 rounded mt-1 ${
            data.isKritis ? 'bg-red-100 text-red-700' :
            data.isOptimal ? 'bg-green-100 text-green-700' :
            'bg-yellow-100 text-yellow-700'
          }`}>
            {data.isKritis ? 'Kritis (>85%)' :
             data.isOptimal ? 'Optimal (60-85%)' :
             'Rendah (<60%)'}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full bg-white rounded-lg border border-gray-200 p-6">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>Data Aktual</span>
          </div>
          {showPrediction && (
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
              <span>Prediksi SARIMA</span>
            </div>
          )}
          
          {/* Legend BOR Status */}
          <div className="flex items-center gap-2 text-xs">
            <span className="px-2 py-1 bg-red-100 text-red-700 rounded">Kritis {'>'}85%</span>
            <span className="px-2 py-1 bg-green-100 text-green-700 rounded">Optimal 60-85%</span>
            <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded">Rendah {'<'}60%</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          
          {/* Reference Lines untuk standar BOR */}
          <ReferenceLine y={85} stroke="#ef4444" strokeDasharray="8 8" label="Batas Kritis (85%)" />
          <ReferenceLine y={60} stroke="#f59e0b" strokeDasharray="5 5" label="Batas Minimal (60%)" />
          
          <XAxis 
            dataKey="tanggal" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis 
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            label={{ value: 'BOR (%)', angle: -90, position: 'insideLeft' }}
          />
          
          <Tooltip content={<CustomTooltip />} />
          <Legend />

          {/* Line untuk data aktual */}
          <Line
            type="monotone"
            dataKey="borAktual"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ fill: '#3b82f6', strokeWidth: 2, r: 5 }}
            connectNulls={false}
            name="Data Aktual"
          />
          
          {/* Line untuk data prediksi */}
          {showPrediction && (
            <Line
              type="monotone"
              dataKey="borPrediksi"
              stroke="#f59e0b"
              strokeWidth={3}
              strokeDasharray="8 4"
              dot={{ fill: '#f59e0b', strokeWidth: 2, r: 5, stroke: '#f59e0b' }}
              connectNulls={false}
              name="Prediksi SARIMA"
            />
          )}
        </LineChart>
      </ResponsiveContainer>

      {/* Summary Statistics */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div className="bg-blue-50 p-3 rounded">
          <p className="text-blue-600 font-medium">Rata-rata BOR</p>
          <p className="text-xl font-bold text-blue-800">
            {chartData.length > 0 ? 
              Math.round(chartData.reduce((sum, d) => sum + d.bor, 0) / chartData.length * 10) / 10 
              : 0}%
          </p>
        </div>
        
        <div className="bg-green-50 p-3 rounded">
          <p className="text-green-600 font-medium">BOR Tertinggi</p>
          <p className="text-xl font-bold text-green-800">
            {chartData.length > 0 ? Math.max(...chartData.map(d => d.bor)).toFixed(1) : 0}%
          </p>
        </div>
        
        <div className="bg-orange-50 p-3 rounded">
          <p className="text-orange-600 font-medium">BOR Terendah</p>
          <p className="text-xl font-bold text-orange-800">
            {chartData.length > 0 ? Math.min(...chartData.map(d => d.bor)).toFixed(1) : 0}%
          </p>
        </div>
      </div>
    </div>
  );
};

export default BorChart;
