// frontend/src/components/dashboard/ComprehensiveIndicatorCards.tsx
import React, { useEffect, useState } from 'react';
import { 
  UsersIcon, 
  ClockIcon, 
  ScaleIcon, 
  CalendarIcon,
  RefreshIcon,
  ExclamationTriangleIcon
} from '../icons';
import StatCard from './StatCard';

interface IndicatorStats {
  bor_terkini: number;
  rata_rata_bor_bulanan: number;
  los_bulanan: number;
  bto_bulanan: number;
  toi_bulanan: number;
  periode: string;
  trend_bor: string;
}

interface ComprehensiveIndicatorCardsProps {
  className?: string;
}

const ComprehensiveIndicatorCards: React.FC<ComprehensiveIndicatorCardsProps> = ({ 
  className = "" 
}) => {
  const [stats, setStats] = useState<IndicatorStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8000/api/v1/dashboard/stats?bulan=1&tahun=2025');
      if (!response.ok) throw new Error('Failed to fetch dashboard stats');
      
      const data = await response.json();
      setStats({
        bor_terkini: data.stats.bor_terkini,
        rata_rata_bor_bulanan: data.stats.rata_rata_bor_bulanan,
        los_bulanan: data.stats.los_bulanan,
        bto_bulanan: data.stats.bto_bulanan,
        toi_bulanan: data.stats.toi_bulanan,
        periode: data.stats.periode,
        trend_bor: data.stats.trend_bor
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const evaluateIndicator = (type: string, value: number) => {
    switch (type) {
      case 'bor':
        if (value >= 60 && value <= 85) {
          return { 
            status: 'success', 
            message: 'Tingkat hunian optimal sesuai standar Kemenkes',
            action: 'Pertahankan kualitas pelayanan yang baik'
          };
        } else if (value > 85) {
          return { 
            status: 'critical', 
            message: 'Tingkat hunian sangat tinggi, dapat mempengaruhi kualitas pelayanan',
            action: 'Evaluasi kapasitas dan tingkatkan efisiensi'
          };
        } else {
          return { 
            status: 'warning', 
            message: 'Tingkat hunian di bawah standar, menunjukkan kapasitas tidak optimal',
            action: 'Tingkatkan promosi dan akses pelayanan'
          };
        }
      
      case 'los':
        if (value >= 6 && value <= 9) {
          return { 
            status: 'success', 
            message: 'Lama rawat sesuai standar Kemenkes',
            action: 'Pertahankan efisiensi pelayanan'
          };
        } else if (value > 9) {
          return { 
            status: 'critical', 
            message: 'Lama rawat terlalu tinggi, menunjukkan inefisiensi',
            action: 'Evaluasi protokol klinis dan optimasi proses'
          };
        } else {
          return { 
            status: 'warning', 
            message: 'Lama rawat sangat singkat, perlu evaluasi kualitas',
            action: 'Review proses discharge dan follow-up'
          };
        }
      
      case 'bto':
        if (value >= 3 && value <= 5) {
          return { 
            status: 'success', 
            message: 'Tingkat putaran tempat tidur optimal',
            action: 'Efisiensi penggunaan tempat tidur baik'
          };
        } else {
          return { 
            status: 'warning', 
            message: 'Tingkat putaran tempat tidur perlu perhatian',
            action: 'Evaluasi manajemen kapasitas'
          };
        }
      
      case 'toi':
        if (value >= 1 && value <= 3) {
          return { 
            status: 'success', 
            message: 'Interval pergantian optimal',
            action: 'Efisiensi operasional baik'
          };
        } else {
          return { 
            status: 'warning', 
            message: 'Interval pergantian perlu optimasi',
            action: 'Tingkatkan koordinasi tim housekeeping'
          };
        }
      
      default:
        return { 
          status: 'warning', 
          message: 'Data tidak dikenal',
          action: 'Periksa kembali pengolahan data'
        };
    }
  };

  if (loading) {
    return (
      <div className={className}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-2"></div>
              <div className="h-8 bg-gray-200 rounded mb-2"></div>
              <div className="h-3 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className={className}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center gap-3">
            <ExclamationTriangleIcon className="w-8 h-8 text-red-500" />
            <div>
              <h3 className="text-lg font-semibold text-red-800 mb-2">
                Gagal Memuat Data Dashboard
              </h3>
              <p className="text-red-600 mb-4">
                {error || 'Terjadi kesalahan saat mengambil data statistik indikator'}
              </p>
              <button
                onClick={fetchStats}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
              >
                Coba Lagi
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const borEval = evaluateIndicator('bor', stats.rata_rata_bor_bulanan);
  const losEval = evaluateIndicator('los', stats.los_bulanan);
  const btoEval = evaluateIndicator('bto', stats.bto_bulanan);
  const toiEval = evaluateIndicator('toi', stats.toi_bulanan);

  return (
    <div className={className}>
      {/* Simplified Header */}
      <div className="bg-primary-500 rounded-lg p-4 sm:p-6 text-white mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex-1">
            <h2 className="text-xl sm:text-2xl font-bold mb-2">
              Dashboard Indikator
            </h2>
            <p className="text-primary-100 text-sm sm:text-base">
              Monitoring kinerja rumah sakit
            </p>
          </div>
          <button 
            onClick={fetchStats}
            className="px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition-colors text-sm inline-flex items-center justify-center gap-2 whitespace-nowrap"
            disabled={loading}
          >
            <RefreshIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        </div>
      </div>

      {/* Main Indicators Grid - Simplified */}
      <div className="medical-stats-grid">
        {/* BOR Card */}
        <StatCard
          title="BOR"
          value={stats.rata_rata_bor_bulanan.toFixed(1)}
          unit="%"
          description="Standar: 60-85%"
          variant={borEval.status as any}
          icon={<UsersIcon className="w-6 h-6" />}
        />

        {/* LOS Card */}
        <StatCard
          title="LOS"
          value={stats.los_bulanan.toFixed(1)}
          unit="hari"
          description="Standar: 6-9 hari"
          variant={losEval.status as any}
          icon={<ClockIcon className="w-6 h-6" />}
        />

        {/* BTO Card */}
        <StatCard
          title="BTO"
          value={stats.bto_bulanan.toFixed(1)}
          unit="x"
          description="Standar: 3-4x"
          variant={btoEval.status as any}
          icon={<ScaleIcon className="w-6 h-6" />}
        />

        {/* TOI Card */}
        <StatCard
          title="TOI"
          value={stats.toi_bulanan.toFixed(1)}
          unit="hari"
          description="Standar: 1-3 hari"
          variant={toiEval.status as any}
          icon={<CalendarIcon className="w-6 h-6" />}
        />
      </div>

      {/* Quick Status Summary Only */}
      <div className="bg-white border border-primary-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-vmeds-800">
            Status Indikator
          </h3>
          <div className="flex gap-4 text-sm">
            <span className="text-success-600 font-medium">
              ✓ Sesuai: {[borEval, losEval, btoEval, toiEval].filter(evaluation => evaluation.status === 'success').length}/4
            </span>
            <span className="text-warning-600 font-medium">
              ⚠ Perhatian: {[borEval, losEval, btoEval, toiEval].filter(evaluation => evaluation.status === 'warning').length}
            </span>
            <span className="text-error-600 font-medium">
              ⚡ Kritis: {[borEval, losEval, btoEval, toiEval].filter(evaluation => evaluation.status === 'critical').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComprehensiveIndicatorCards;
