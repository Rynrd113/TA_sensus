// frontend/src/components/dashboard/BorTrendChart.tsx
import { useState, useEffect } from 'react';

interface SensusData {
  tanggal: string;
  bor: number;
}

interface PrediksiData {
  prediksi: Array<{
    tanggal: string;
    bor: number;
  }>;
  rekomendasi: string;
  status: string;
  error?: string;
}

interface DataPoint {
  tanggal: string;
  bor: number;
  type: 'actual' | 'prediction';
}

export default function BorTrendChart() {
  const [chartData, setChartData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch data aktual (7 hari terakhir) - ensure trailing slash
      const sensusResponse = await fetch('http://localhost:8000/api/v1/sensus/?limit=7', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        }
      });
      
      if (!sensusResponse.ok) {
        throw new Error(`Failed to fetch sensus data: ${sensusResponse.status} ${sensusResponse.statusText}`);
      }
      const sensusData: SensusData[] = await sensusResponse.json();

      // Fetch prediksi (3 hari ke depan)
      const prediksiResponse = await fetch('http://localhost:8000/api/v1/prediksi/bor?hari=3', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        }
      });
      
      if (!prediksiResponse.ok) {
        throw new Error(`Failed to fetch prediction data: ${prediksiResponse.status} ${prediksiResponse.statusText}`);
      }
      const prediksiData: PrediksiData = await prediksiResponse.json();

      if (prediksiData.error) {
        setError(`Prediksi error: ${prediksiData.error}`);
        return;
      }

      // Validasi data
      if (!Array.isArray(sensusData) || sensusData.length === 0) {
        setError('Tidak ada data sensus yang tersedia');
        return;
      }

      if (!prediksiData.prediksi || prediksiData.prediksi.length === 0) {
        console.warn('No prediction data available');
        // Lanjutkan tanpa prediksi
      }

      // Gabungkan data aktual dan prediksi
      const actualData: DataPoint[] = sensusData
        .reverse() // Urutkan dari lama ke baru
        .map(item => ({
          tanggal: item.tanggal,
          bor: item.bor,
          type: 'actual' as const
        }));

      const predictionData: DataPoint[] = prediksiData.prediksi 
        ? prediksiData.prediksi.map(item => ({
            tanggal: item.tanggal,
            bor: item.bor,
            type: 'prediction' as const
          }))
        : [];

      setChartData([...actualData, ...predictionData]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error fetching data';
      console.error('BorTrendChart fetch error:', err);
      setError(`Gagal memuat data grafik. ${errorMessage}. Pastikan backend berjalan di port 8000.`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []); // Empty dependency array - only fetch once on mount

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'short'
    });
  };

  // const getBorColor = (bor: number) => {
  //   if (bor >= 90) return '#ef4444'; // red-500
  //   if (bor >= 80) return '#f59e0b'; // amber-500
  //   return '#10b981'; // emerald-500
  // };

  const getMaxBor = () => {
    if (chartData.length === 0) return 100;
    const maxBor = Math.max(...chartData.map(d => d.bor));
    return Math.ceil(maxBor / 10) * 10; // Round up to nearest 10
  };

  const getChartHeight = () => 200;
  const getChartWidth = () => 600;

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Tren BOR (7 Hari Aktual + 3 Hari Prediksi)</h3>
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Tren BOR</h3>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex items-center">
            <div className="text-red-500 mr-2">⚠️</div>
            <p className="text-sm text-red-700">{error}</p>
          </div>
          <button
            onClick={fetchData}
            className="mt-3 px-4 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
          >
            Coba Lagi
          </button>
        </div>
      </div>
    );
  }

  const maxBor = getMaxBor();
  const chartHeight = getChartHeight();
  const chartWidth = getChartWidth();
  const padding = 40;

  // Calculate points for the line
  const actualPoints = chartData
    .filter(d => d.type === 'actual')
    .map((point, index) => {
      const x = padding + (index * (chartWidth - 2 * padding)) / (chartData.length - 1);
      const y = padding + ((maxBor - point.bor) * (chartHeight - 2 * padding)) / maxBor;
      return { x, y, ...point };
    });

  const predictionPoints = chartData
    .filter(d => d.type === 'prediction')
    .map((point, index) => {
      const actualCount = chartData.filter(d => d.type === 'actual').length;
      const totalIndex = actualCount + index - 1;
      const x = padding + (totalIndex * (chartWidth - 2 * padding)) / (chartData.length - 1);
      const y = padding + ((maxBor - point.bor) * (chartHeight - 2 * padding)) / maxBor;
      return { x, y, ...point };
    });

  // Create path string for actual line
  const actualPath = actualPoints.length > 0 
    ? `M ${actualPoints[0].x} ${actualPoints[0].y} ` + 
      actualPoints.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')
    : '';

  // Create path string for prediction line (dashed)
  const allPoints = [...actualPoints, ...predictionPoints];
  const predictionPath = allPoints.length > actualPoints.length
    ? `M ${allPoints[actualPoints.length - 1]?.x || 0} ${allPoints[actualPoints.length - 1]?.y || 0} ` +
      predictionPoints.map(p => `L ${p.x} ${p.y}`).join(' ')
    : '';

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Tren BOR (7 Hari Aktual + 3 Hari Prediksi)
        </h3>
        <button
          onClick={fetchData}
          disabled={loading}
          className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50"
          title="Refresh Chart"
        >
          <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      {chartData.length > 0 ? (
        <div className="relative">
          <svg width={chartWidth} height={chartHeight + 60} className="overflow-visible">
            {/* Background zones */}
            <defs>
              <pattern id="grid" width="1" height="1" patternUnits="userSpaceOnUse">
                <path d="M 1 0 L 0 0 0 1" fill="none" stroke="#f3f4f6" strokeWidth="1"/>
              </pattern>
            </defs>
            
            {/* Grid */}
            <rect width={chartWidth} height={chartHeight} fill="url(#grid)" />
            
            {/* BOR zones */}
            {/* Normal zone (0-80%) */}
            <rect
              x={padding}
              y={padding + ((maxBor - 80) * (chartHeight - 2 * padding)) / maxBor}
              width={chartWidth - 2 * padding}
              height={(80 * (chartHeight - 2 * padding)) / maxBor}
              fill="#dcfdf4"
              fillOpacity="0.3"
            />
            
            {/* Warning zone (80-90%) */}
            <rect
              x={padding}
              y={padding + ((maxBor - 90) * (chartHeight - 2 * padding)) / maxBor}
              width={chartWidth - 2 * padding}
              height={(10 * (chartHeight - 2 * padding)) / maxBor}
              fill="#fef3c7"
              fillOpacity="0.3"
            />
            
            {/* Critical zone (90%+) */}
            <rect
              x={padding}
              y={padding}
              width={chartWidth - 2 * padding}
              height={((maxBor - 90) * (chartHeight - 2 * padding)) / maxBor}
              fill="#fee2e2"
              fillOpacity="0.3"
            />

            {/* Y-axis */}
            <line x1={padding} y1={padding} x2={padding} y2={chartHeight - padding} stroke="#64748b" strokeWidth="1"/>
            
            {/* X-axis */}
            <line x1={padding} y1={chartHeight - padding} x2={chartWidth - padding} y2={chartHeight - padding} stroke="#64748b" strokeWidth="1"/>
            
            {/* Y-axis labels */}
            {Array.from({length: 6}, (_, i) => {
              const value = (i * 20);
              const y = chartHeight - padding - (i * (chartHeight - 2 * padding) / 5);
              return (
                <g key={i}>
                  <line x1={padding - 5} y1={y} x2={padding} y2={y} stroke="#64748b" strokeWidth="1"/>
                  <text x={padding - 10} y={y + 4} textAnchor="end" className="text-xs fill-vmeds-600">
                    {value}%
                  </text>
                </g>
              );
            })}
            
            {/* Data lines */}
            {actualPath && (
              <path
                d={actualPath}
                fill="none"
                stroke="#3b82f6"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="drop-shadow-sm"
              />
            )}
            
            {predictionPath && (
              <path
                d={predictionPath}
                fill="none"
                stroke="#f59e0b"
                strokeWidth="3"
                strokeDasharray="8,4"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="drop-shadow-sm"
              />
            )}            {/* Data points */}
            {allPoints.map((point, index) => (
              <g key={index}>
                <circle
                  cx={point.x}
                  cy={point.y}
                  r="4"
                  fill={point.type === 'actual' ? '#3b82f6' : '#f59e0b'}
                  stroke="white"
                  strokeWidth="2"
                />
                {/* Tooltip on hover */}
                <title>{`${formatDate(point.tanggal)}: ${point.bor}% (${point.type === 'actual' ? 'Aktual' : 'Prediksi'})`}</title>
              </g>
            ))}

            {/* X-axis labels */}
            {allPoints.map((point, index) => (
              <text
                key={index}
                x={point.x}
                y={chartHeight - padding + 15}
                textAnchor="middle"
                fontSize="11"
                fill="#6b7280"
                transform={`rotate(-45, ${point.x}, ${chartHeight - padding + 15})`}
              >
                {formatDate(point.tanggal)}
              </text>
            ))}
          </svg>

          {/* Legend */}
          <div className="flex items-center justify-center space-x-6 mt-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-blue-500"></div>
              <span className="text-gray-600">Data Aktual</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-amber-500" style={{ borderTop: '2px dashed #f59e0b', backgroundColor: 'transparent' }}></div>
              <span className="text-gray-600">Prediksi ARIMA</span>
            </div>
          </div>

          {/* Zone indicators */}
          <div className="flex items-center justify-center space-x-4 mt-2 text-xs">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-green-200 rounded"></div>
              <span className="text-gray-500">Normal (&lt;80%)</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-yellow-200 rounded"></div>
              <span className="text-gray-500">Warning (80-90%)</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-red-200 rounded"></div>
              <span className="text-gray-500">Critical (&gt;90%)</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center h-48 text-gray-500">
          <p>Tidak ada data untuk ditampilkan</p>
        </div>
      )}
    </div>
  );
}
