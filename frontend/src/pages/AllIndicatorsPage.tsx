// frontend/src/pages/AllIndicatorsPage.tsx
import { useState } from "react";
import { 
  CalendarIcon,
  ClockIcon,
  UsersIcon,
  RefreshIcon,
  ScaleIcon
} from '../components/icons';
import ExportCard from "../components/dashboard/ExportCard";
import AllIndicatorsChart from "../components/charts/AllIndicatorsChart";
import BorTrendChart from "../components/charts/BorTrendChart";
import ComprehensiveIndicatorCards from "../components/dashboard/IndicatorCards";

export default function AllIndicatorsPage() {
  const [loading, setLoading] = useState(false);
  
  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 1000);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Professional Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-vmeds-900">
            Semua Indikator Kemenkes
          </h1>
          <p className="text-vmeds-600 mt-1">
            Analisis lengkap 4 indikator utama: BOR • LOS • BTO • TOI
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <RefreshIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* All 4 Indicators Display */}
      <ComprehensiveIndicatorCards />

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AllIndicatorsChart />
        <BorTrendChart />
      </div>

      {/* Charts & Analysis Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Comprehensive Prediction Table */}
        <div className="xl:col-span-2">
          <div className="bg-white rounded-lg border border-primary-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-vmeds-900">Tabel Chart Prediksi</h3>
                <p className="text-vmeds-600 text-sm mt-1">Proyeksi lengkap semua indikator 7 hari ke depan</p>
              </div>
              <div className="text-xs text-vmeds-500 bg-vmeds-50 px-3 py-1 rounded-full">
                Akurasi Model: 94.2%
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-primary-200 bg-primary-50">
                    <th className="text-left py-3 px-4 font-semibold text-primary-800">Tanggal</th>
                    <th className="text-center py-3 px-4 font-semibold text-primary-800">BOR (%)</th>
                    <th className="text-center py-3 px-4 font-semibold text-primary-800">LOS (hari)</th>
                    <th className="text-center py-3 px-4 font-semibold text-primary-800">BTO (x)</th>
                    <th className="text-center py-3 px-4 font-semibold text-primary-800">TOI (hari)</th>
                    <th className="text-center py-3 px-4 font-semibold text-primary-800">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-primary-100">
                  {/* Data Hari Ini */}
                  <tr className="bg-primary-25 hover:bg-primary-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                        <span className="font-medium text-primary-900">Hari Ini</span>
                      </div>
                    </td>
                    <td className="text-center py-3 px-4">
                      <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-xs font-medium">72.5%</span>
                    </td>
                    <td className="text-center py-3 px-4 text-vmeds-700 font-medium">7.2</td>
                    <td className="text-center py-3 px-4 text-success-700 font-medium">3.8</td>
                    <td className="text-center py-3 px-4 text-warning-700 font-medium">2.1</td>
                    <td className="text-center py-3 px-4">
                      <span className="px-2 py-1 bg-success-100 text-success-700 rounded-full text-xs font-medium">Optimal</span>
                    </td>
                  </tr>
                  
                  {/* Prediksi */}
                  <tr className="bg-blue-25 hover:bg-blue-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span className="font-medium text-blue-900">Besok</span>
                      </div>
                    </td>
                    <td className="text-center py-3 px-4">
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">73.2%</span>
                    </td>
                    <td className="text-center py-3 px-4 text-blue-700 font-medium">7.1</td>
                    <td className="text-center py-3 px-4 text-blue-700 font-medium">3.9</td>
                    <td className="text-center py-3 px-4 text-blue-700 font-medium">2.0</td>
                    <td className="text-center py-3 px-4">
                      <span className="px-2 py-1 bg-success-100 text-success-700 rounded-full text-xs font-medium">Optimal</span>
                    </td>
                  </tr>
                  
                  <tr className="bg-blue-25 hover:bg-blue-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span className="font-medium text-blue-900">+2 hari</span>
                      </div>
                    </td>
                    <td className="text-center py-3 px-4">
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">74.1%</span>
                    </td>
                    <td className="text-center py-3 px-4 text-blue-700 font-medium">7.0</td>
                    <td className="text-center py-3 px-4 text-blue-700 font-medium">4.0</td>
                    <td className="text-center py-3 px-4 text-blue-700 font-medium">1.9</td>
                    <td className="text-center py-3 px-4">
                      <span className="px-2 py-1 bg-success-100 text-success-700 rounded-full text-xs font-medium">Optimal</span>
                    </td>
                  </tr>
                  
                  <tr className="bg-blue-25 hover:bg-blue-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span className="font-medium text-blue-900">+7 hari</span>
                      </div>
                    </td>
                    <td className="text-center py-3 px-4">
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">75.2%</span>
                    </td>
                    <td className="text-center py-3 px-4 text-blue-700 font-medium">6.9</td>
                    <td className="text-center py-3 px-4 text-blue-700 font-medium">4.1</td>
                    <td className="text-center py-3 px-4 text-blue-700 font-medium">1.7</td>
                    <td className="text-center py-3 px-4">
                      <span className="px-2 py-1 bg-success-100 text-success-700 rounded-full text-xs font-medium">Optimal</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            {/* Legend & Summary */}
            <div className="mt-4 flex justify-between items-center pt-4 border-t border-primary-200">
              <div className="flex gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  <span className="text-vmeds-600">Data Aktual</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-vmeds-600">Prediksi ML</span>
                </div>
              </div>
              <div className="text-xs text-vmeds-500">
                Trend: <span className="font-semibold text-success-700">Stabil Optimal</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Export & Summary */}
        <div className="space-y-6">
          <ExportCard />
          
          {/* Quick Summary */}
          <div className="bg-white rounded-lg border border-primary-200 p-6">
            <h3 className="text-lg font-semibold text-vmeds-900 mb-4">Ringkasan Status</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-vmeds-600">Indikator Optimal:</span>
                <span className="px-2 py-1 bg-success-100 text-success-700 rounded text-xs font-medium">4/4</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-vmeds-600">Trend Prediksi:</span>
                <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs font-medium">Stabil</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-vmeds-600">Akurasi Model:</span>
                <span className="px-2 py-1 bg-vmeds-100 text-vmeds-700 rounded text-xs font-medium">94.2%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Extended Analytics Section */}
      <div className="bg-white rounded-lg border border-primary-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-vmeds-900">
              Analisis Detail Indikator
            </h2>
            <p className="text-vmeds-600 mt-1">
              Status lengkap dengan evaluasi standar Kemenkes RI
            </p>
          </div>
        </div>

        {/* Comprehensive Data Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-primary-200 bg-primary-50">
                <th className="text-left py-3 px-4 font-semibold text-primary-800">Indikator</th>
                <th className="text-center py-3 px-4 font-semibold text-primary-800">Nilai Saat Ini</th>
                <th className="text-center py-3 px-4 font-semibold text-primary-800">Target Kemenkes</th>
                <th className="text-center py-3 px-4 font-semibold text-primary-800">Status</th>
                <th className="text-center py-3 px-4 font-semibold text-primary-800">Prediksi 7 Hari</th>
                <th className="text-center py-3 px-4 font-semibold text-primary-800">Rekomendasi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-primary-100">
              <tr className="hover:bg-primary-25">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                      <UsersIcon className="w-4 h-4 text-primary-600" />
                    </div>
                    <div>
                      <p className="font-medium text-vmeds-900">BOR</p>
                      <p className="text-xs text-vmeds-500">Bed Occupancy Rate</p>
                    </div>
                  </div>
                </td>
                <td className="text-center py-3 px-4">
                  <span className="text-lg font-bold text-primary-700">72.5%</span>
                </td>
                <td className="text-center py-3 px-4 text-vmeds-600">60-85%</td>
                <td className="text-center py-3 px-4">
                  <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-xs font-medium">
                    Optimal
                  </span>
                </td>
                <td className="text-center py-3 px-4 text-vmeds-600">73.2%</td>
                <td className="text-center py-3 px-4 text-xs text-vmeds-500">
                  Pertahankan level saat ini
                </td>
              </tr>
              
              <tr className="hover:bg-vmeds-25">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-vmeds-100 rounded-lg flex items-center justify-center">
                      <ClockIcon className="w-4 h-4 text-vmeds-600" />
                    </div>
                    <div>
                      <p className="font-medium text-vmeds-900">LOS</p>
                      <p className="text-xs text-vmeds-500">Length of Stay</p>
                    </div>
                  </div>
                </td>
                <td className="text-center py-3 px-4">
                  <span className="text-lg font-bold text-vmeds-700">7.2 hari</span>
                </td>
                <td className="text-center py-3 px-4 text-vmeds-600">6-9 hari</td>
                <td className="text-center py-3 px-4">
                  <span className="px-2 py-1 bg-success-100 text-success-700 rounded-full text-xs font-medium">
                    Ideal
                  </span>
                </td>
                <td className="text-center py-3 px-4 text-vmeds-600">7.1 hari</td>
                <td className="text-center py-3 px-4 text-xs text-vmeds-500">
                  Sesuai standar pelayanan
                </td>
              </tr>
              
              <tr className="hover:bg-success-25">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                      <ScaleIcon className="w-4 h-4 text-success-600" />
                    </div>
                    <div>
                      <p className="font-medium text-vmeds-900">BTO</p>
                      <p className="text-xs text-vmeds-500">Bed Turn Over</p>
                    </div>
                  </div>
                </td>
                <td className="text-center py-3 px-4">
                  <span className="text-lg font-bold text-success-700">3.8x</span>
                </td>
                <td className="text-center py-3 px-4 text-vmeds-600">3-4x</td>
                <td className="text-center py-3 px-4">
                  <span className="px-2 py-1 bg-success-100 text-success-700 rounded-full text-xs font-medium">
                    Efisien
                  </span>
                </td>
                <td className="text-center py-3 px-4 text-vmeds-600">3.9x</td>
                <td className="text-center py-3 px-4 text-xs text-vmeds-500">
                  Tingkatkan untuk maksimal
                </td>
              </tr>
              
              <tr className="hover:bg-warning-25">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
                      <CalendarIcon className="w-4 h-4 text-warning-600" />
                    </div>
                    <div>
                      <p className="font-medium text-vmeds-900">TOI</p>
                      <p className="text-xs text-vmeds-500">Turn Over Interval</p>
                    </div>
                  </div>
                </td>
                <td className="text-center py-3 px-4">
                  <span className="text-lg font-bold text-warning-700">2.1 hari</span>
                </td>
                <td className="text-center py-3 px-4 text-vmeds-600">1-3 hari</td>
                <td className="text-center py-3 px-4">
                  <span className="px-2 py-1 bg-success-100 text-success-700 rounded-full text-xs font-medium">
                    Optimal
                  </span>
                </td>
                <td className="text-center py-3 px-4 text-vmeds-600">2.0 hari</td>
                <td className="text-center py-3 px-4 text-xs text-vmeds-500">
                  Interval sangat efisien
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Summary Stats */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
            <h4 className="font-semibold text-primary-800 mb-2">Indikator Sesuai Standar</h4>
            <p className="text-2xl font-bold text-primary-700">4/4</p>
            <p className="text-xs text-primary-600">Semua indikator dalam rentang ideal</p>
          </div>
          
          <div className="bg-success-50 border border-success-200 rounded-lg p-4">
            <h4 className="font-semibold text-success-800 mb-2">Efisiensi Pelayanan</h4>
            <p className="text-2xl font-bold text-success-700">92%</p>
            <p className="text-xs text-success-600">Tingkat efisiensi sangat baik</p>
          </div>
          
          <div className="bg-vmeds-50 border border-vmeds-200 rounded-lg p-4">
            <h4 className="font-semibold text-vmeds-800 mb-2">Prediksi Trend</h4>
            <p className="text-2xl font-bold text-vmeds-700">Stabil</p>
            <p className="text-xs text-vmeds-600">Proyeksi 7 hari tetap optimal</p>
          </div>
        </div>
      </div>

      {/* Standards Reference */}
      <div className="bg-white rounded-lg border border-primary-200 p-6">
        <h3 className="text-lg font-semibold text-vmeds-800 mb-4">
          Standar Indikator Kemenkes RI
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
            <p className="font-semibold text-primary-800">BOR (Bed Occupancy Rate)</p>
            <p className="text-primary-600 mt-1">Ideal: 60-85%</p>
            <p className="text-xs text-primary-500 mt-2">
              Mengukur tingkat pemanfaatan tempat tidur
            </p>
          </div>
          
          <div className="bg-vmeds-50 border border-vmeds-200 rounded-lg p-4">
            <p className="font-semibold text-vmeds-800">LOS (Length of Stay)</p>
            <p className="text-vmeds-600 mt-1">Ideal: 6-9 hari</p>
            <p className="text-xs text-vmeds-500 mt-2">
              Rata-rata lama pasien dirawat inap
            </p>
          </div>
          
          <div className="bg-success-50 border border-success-200 rounded-lg p-4">
            <p className="font-semibold text-success-800">BTO (Bed Turn Over)</p>
            <p className="text-success-600 mt-1">Ideal: 3-4x/bulan</p>
            <p className="text-xs text-success-500 mt-2">
              Frekuensi perputaran tempat tidur
            </p>
          </div>
          
          <div className="bg-warning-50 border border-warning-200 rounded-lg p-4">
            <p className="font-semibold text-warning-800">TOI (Turn Over Interval)</p>
            <p className="text-warning-600 mt-1">Ideal: 1-3 hari</p>
            <p className="text-xs text-warning-500 mt-2">
              Interval kosong antar pasien
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}