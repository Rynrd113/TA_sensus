// frontend/src/pages/ChartPage.tsx
import { useState, useEffect } from "react";
import { 
  CalendarIcon,
  UsersIcon,
  RefreshIcon,
  ScaleIcon,
  ChartIcon
} from '../components/icons';
import BorChart from "../components/charts/BorChart";
import EnhancedIndicatorChart from "../components/dashboard/EnhancedIndicatorChart";
import StatCard from "../components/dashboard/StatCard";

export default function ChartPage() {
  const [selectedTimeRange, setSelectedTimeRange] = useState('7days');
  const [selectedMetric, setSelectedMetric] = useState('bor');
  const [viewMode, setViewMode] = useState<'chart' | 'prediction' | 'comparison'>('chart');
  const [loading, setLoading] = useState(false);
  const [predictionData, setPredictionData] = useState<any[]>([]);
  
  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 1000);
  };

  // Simulasi data prediksi
  useEffect(() => {
    const generatePredictionData = () => {
      const today = new Date();
      const data = [];
      
      // Data aktual 7 hari terakhir
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        data.push({
          tanggal: date.toISOString().split('T')[0],
          bor: 65 + Math.random() * 20,
          jenis: 'aktual'
        });
      }
      
      // Data prediksi 7 hari kedepan
      for (let i = 1; i <= 7; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() + i);
        data.push({
          tanggal: date.toISOString().split('T')[0],
          bor: 70 + Math.random() * 15,
          jenis: 'prediksi'
        });
      }
      
      setPredictionData(data);
    };
    
    generatePredictionData();
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Analytics Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-vmeds-900">
            Analytics & Prediksi
          </h1>
          <p className="text-vmeds-600 mt-1">
            Analisis mendalam dengan machine learning dan prediksi 7 hari kedepan
          </p>
        </div>
        
        <div className="flex gap-3">
          <select 
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="7days">7 Hari</option>
            <option value="14days">14 Hari</option>
            <option value="30days">30 Hari</option>
          </select>
          
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            <RefreshIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* View Mode Selector */}
      <div className="bg-white rounded-lg border border-primary-200 p-4">
        <div className="flex gap-2">
          {[
            { key: 'chart', label: 'Visualisasi Data', icon: ChartIcon },
            { key: 'prediction', label: 'Prediksi ML', icon: CalendarIcon },
            { key: 'comparison', label: 'Perbandingan', icon: ScaleIcon }
          ].map((mode) => (
            <button
              key={mode.key}
              onClick={() => setViewMode(mode.key as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                viewMode === mode.key
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <mode.icon className="w-4 h-4" />
              {mode.label}
            </button>
          ))}
        </div>
      </div>

      {/* Quick Stats for Analytics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Akurasi Model"
          value="92.4"
          unit="%"
          description="Machine Learning Accuracy"
          variant="success"
          icon={<ChartIcon className="w-6 h-6" />}
          benchmark="Model Performance"
        />
        <StatCard
          title="Prediksi Trend"
          value="↗ Naik"
          unit=""
          description="BOR 7 hari kedepan"
          variant="warning"
          icon={<CalendarIcon className="w-6 h-6" />}
          benchmark="Trend Analysis"
        />
        <StatCard
          title="R² Score"
          value="0.89"
          unit=""
          description="Model Reliability"
          variant="success"
          icon={<ScaleIcon className="w-6 h-6" />}
          benchmark="Statistical Measure"
        />
        <StatCard
          title="Data Points"
          value="2,847"
          unit=""
          description="Training Dataset"
          variant="default"
          icon={<UsersIcon className="w-6 h-6" />}
          benchmark="Historical Data"
        />
      </div>

      {/* Main Analytics Content */}
      {viewMode === 'chart' && (
        <div className="space-y-6">
          {/* Interactive Chart Controls */}
          <div className="bg-white rounded-lg border border-primary-200 p-6">
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-vmeds-900">Visualisasi Interaktif</h2>
                <p className="text-vmeds-600 text-sm mt-1">Chart dengan kemampuan zoom, filter, dan analisis mendalam</p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-3">
                <select
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value)}
                  className="px-3 py-2 border border-primary-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="bor">Fokus BOR</option>
                  <option value="los">Fokus LOS</option>
                  <option value="bto">Fokus BTO</option>
                  <option value="toi">Fokus TOI</option>
                </select>
              </div>
            </div>

            {/* Enhanced Chart */}
            <EnhancedIndicatorChart />
          </div>
        </div>
      )}

      {viewMode === 'prediction' && (
        <div className="space-y-6">
          {/* Prediction Chart */}
          <div className="bg-white rounded-lg border border-primary-200 p-6">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-vmeds-900">Prediksi Machine Learning</h2>
              <p className="text-vmeds-600 text-sm mt-1">Model LSTM untuk prediksi BOR 7 hari kedepan</p>
            </div>
            
            <BorChart 
              data={predictionData}
              title="BOR Aktual vs Prediksi ML"
              showPrediction={true}
            />
          </div>

          {/* ML Model Info */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg border border-primary-200 p-6">
              <h3 className="text-lg font-semibold text-vmeds-900 mb-4">Informasi Model</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-vmeds-600">Algoritma:</span>
                  <span className="font-semibold text-vmeds-900">LSTM Neural Network</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-vmeds-600">Training Data:</span>
                  <span className="font-semibold text-vmeds-900">365 hari terakhir</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-vmeds-600">Last Update:</span>
                  <span className="font-semibold text-vmeds-900">Hari ini, 08:00</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-vmeds-600">Confidence:</span>
                  <span className="font-semibold text-vmeds-900">87.3%</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-primary-200 p-6">
              <h3 className="text-lg font-semibold text-vmeds-900 mb-4">Prediksi 7 Hari</h3>
              <div className="space-y-2">
                {predictionData.filter(d => d.jenis === 'prediksi').slice(0, 7).map((item, index) => (
                  <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-vmeds-600 text-sm">
                      {new Date(item.tanggal).toLocaleDateString('id-ID', { 
                        weekday: 'short', 
                        day: 'numeric', 
                        month: 'short' 
                      })}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-vmeds-900">
                        {item.bor.toFixed(1)}%
                      </span>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        item.bor >= 60 && item.bor <= 85 
                          ? 'bg-success-100 text-success-700'
                          : item.bor > 85
                          ? 'bg-warning-100 text-warning-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {item.bor >= 60 && item.bor <= 85 ? 'Optimal' : item.bor > 85 ? 'Tinggi' : 'Rendah'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {viewMode === 'comparison' && (
        <div className="space-y-6">
          {/* Comparison Tools */}
          <div className="bg-white rounded-lg border border-primary-200 p-6">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-vmeds-900">Analisis Perbandingan</h2>
              <p className="text-vmeds-600 text-sm mt-1">Bandingkan performa indikator antar periode</p>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Period Comparison */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-semibold text-vmeds-900 mb-3">Perbandingan Bulanan</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-vmeds-600">BOR Bulan Ini:</span>
                    <span className="font-semibold text-vmeds-900">72.5%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-vmeds-600">BOR Bulan Lalu:</span>
                    <span className="font-semibold text-vmeds-900">68.2%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-vmeds-600">Perubahan:</span>
                    <span className="font-semibold text-success-600">+4.3% ↗</span>
                  </div>
                </div>
              </div>

              {/* Target vs Actual */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-semibold text-vmeds-900 mb-3">Target vs Aktual</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-vmeds-600">Target BOR:</span>
                    <span className="font-semibold text-vmeds-900">60-85%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-vmeds-600">Aktual BOR:</span>
                    <span className="font-semibold text-vmeds-900">72.5%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-vmeds-600">Status:</span>
                    <span className="font-semibold text-success-600">✓ Sesuai Target</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Advanced Analytics */}
          <div className="bg-white rounded-lg border border-primary-200 p-6">
            <h3 className="text-lg font-semibold text-vmeds-900 mb-4">Analisis Lanjutan</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">24.7</div>
                <div className="text-sm text-blue-700">Rata-rata Pasien/Hari</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">6.8</div>
                <div className="text-sm text-green-700">LOS Optimal (hari)</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">95.2%</div>
                <div className="text-sm text-purple-700">Efisiensi Operasional</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Export & Tools */}
      <div className="bg-white rounded-lg border border-primary-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-vmeds-900">Tools & Export</h3>
        </div>
        <div className="flex flex-wrap gap-3">
          <button className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors">
            📊 Export Chart (PNG)
          </button>
          <button className="px-4 py-2 bg-success-500 text-white rounded-lg hover:bg-success-600 transition-colors">
            📈 Export Data (Excel)
          </button>
          <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
            🤖 Download Model Report
          </button>
          <button className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors">
            📋 Analisis Summary (PDF)
          </button>
        </div>
      </div>
    </div>
  );
}
