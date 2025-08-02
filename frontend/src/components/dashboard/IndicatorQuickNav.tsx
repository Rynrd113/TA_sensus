// frontend/src/components/dashboard/IndicatorQuickNav.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { 
  UsersIcon, 
  ClockIcon, 
  ScaleIcon, 
  CalendarIcon,
  ChartIcon 
} from '../icons';

const IndicatorQuickNav: React.FC = () => {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-800">
            Semua Indikator Kemenkes Tersedia
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Sistem mengimplementasikan lengkap 4 indikator utama rumah sakit
          </p>
        </div>
        <Link
          to="/indikator-lengkap"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          Lihat Lengkap →
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* BOR Card */}
        <div className="border border-blue-200 rounded-lg p-4 hover:bg-blue-50 transition-colors">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <UsersIcon className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-blue-800">BOR</h3>
              <p className="text-xs text-blue-600">Bed Occupancy Rate</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 mb-2">
            Tingkat hunian tempat tidur
          </p>
          <div className="flex items-center justify-between">
            <span className="text-xs text-green-600 font-medium">
              ✅ Dengan Prediksi ML
            </span>
            <span className="text-xs text-blue-600 font-medium">
              Ideal: 60-85%
            </span>
          </div>
        </div>

        {/* LOS Card */}
        <div className="border border-red-200 rounded-lg p-4 hover:bg-red-50 transition-colors">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <ClockIcon className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <h3 className="font-semibold text-red-800">LOS</h3>
              <p className="text-xs text-red-600">Length of Stay</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 mb-2">
            Rata-rata lama dirawat
          </p>
          <div className="flex items-center justify-between">
            <span className="text-xs text-green-600 font-medium">
              ✅ Auto Calculated
            </span>
            <span className="text-xs text-red-600 font-medium">
              Ideal: 6-9 hari
            </span>
          </div>
        </div>

        {/* BTO Card */}
        <div className="border border-green-200 rounded-lg p-4 hover:bg-green-50 transition-colors">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <ScaleIcon className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-green-800">BTO</h3>
              <p className="text-xs text-green-600">Bed Turn Over</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 mb-2">
            Frekuensi pemakaian TT
          </p>
          <div className="flex items-center justify-between">
            <span className="text-xs text-green-600 font-medium">
              ✅ Real-time Update
            </span>
            <span className="text-xs text-green-600 font-medium">
              Ideal: 40-50x/tahun
            </span>
          </div>
        </div>

        {/* TOI Card */}
        <div className="border border-orange-200 rounded-lg p-4 hover:bg-orange-50 transition-colors">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <CalendarIcon className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <h3 className="font-semibold text-orange-800">TOI</h3>
              <p className="text-xs text-orange-600">Turn Over Interval</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 mb-2">
            Interval kosong TT
          </p>
          <div className="flex items-center justify-between">
            <span className="text-xs text-green-600 font-medium">
              ✅ Monitoring Daily
            </span>
            <span className="text-xs text-orange-600 font-medium">
              Ideal: 1-3 hari
            </span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex flex-wrap gap-3">
        <Link
          to="/indikator-lengkap"
          className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all text-sm font-medium shadow-sm"
        >
          <ChartIcon className="w-4 h-4" />
          Dashboard Lengkap
        </Link>
        
        <Link
          to="/indikator"
          className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
        >
          <ChartIcon className="w-4 h-4" />
          Chart View
        </Link>
        
        <Link
          to="/prediksi"
          className="inline-flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors text-sm font-medium"
        >
          🔮 Prediksi BOR
        </Link>
      </div>

      {/* Info Footer */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-4">
            <span>✅ Sesuai Standar Kemenkes RI</span>
            <span>Update Real-time</span>
            <span>Dengan Prediksi ML</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            <span>Semua Indikator Aktif</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IndicatorQuickNav;
