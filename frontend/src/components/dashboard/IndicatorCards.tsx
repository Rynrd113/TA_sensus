// frontend/src/components/dashboard/IndicatorCards.tsx
/**
 * CONSOLIDATED Indicator Cards Component
 * 
 * Menggabungkan fungsionalitas dari:
 * - ComprehensiveIndicatorCards.tsx (dashboard version)
 * - ComprehensiveIndicatorCards.tsx (root version)
 * 
 * Menerapkan prinsip:
 * - DRY (Don't Repeat Yourself)
 * - Single Responsibility
 * - Clean Code
 * - Reusable Component
 */

import React, { useEffect, useState } from 'react';
import { 
  UsersIcon, 
  ClockIcon, 
  CalendarIcon,
  RefreshIcon,
  ExclamationTriangleIcon,
  ChartIcon
} from '../icons';
import StatCard from './StatCard';

// Types for better type safety
interface IndicatorStats {
  bor_terkini: number;
  rata_rata_bor_bulanan: number;
  los_bulanan: number;
  bto_bulanan: number;
  toi_bulanan: number;
  periode: string;
  trend_bor: string;
}

interface IndicatorEvaluation {
  status: 'success' | 'warning' | 'critical' | 'excellent' | 'good' | 'poor';
  message: string;
  action: string;
}

interface IndicatorCardsProps {
  className?: string;
  variant?: 'dashboard' | 'detailed' | 'compact';
  showActions?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number; // in seconds
}

/**
 * Centralized Indicator Evaluation Logic
 * Sesuai standar Kemenkes RI
 */
class IndicatorEvaluator {
  static evaluateBOR(value: number): IndicatorEvaluation {
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
  }

  static evaluateLOS(value: number): IndicatorEvaluation {
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
        message: 'Lama rawat terlalu rendah, perlu evaluasi kualitas',
        action: 'Tinjau kembali standar pelayanan'
      };
    }
  }

  static evaluateBTO(value: number): IndicatorEvaluation {
    if (value >= 40 && value <= 50) {
      return { 
        status: 'success', 
        message: 'Turn Over Rate optimal',
        action: 'Pertahankan efisiensi tempat tidur'
      };
    } else if (value > 50) {
      return { 
        status: 'warning', 
        message: 'Turn Over Rate tinggi, beban kerja tinggi',
        action: 'Evaluasi kapasitas dan tenaga medis'
      };
    } else {
      return { 
        status: 'warning', 
        message: 'Turn Over Rate rendah, pemanfaatan kurang optimal',
        action: 'Tingkatkan utilisasi tempat tidur'
      };
    }
  }

  static evaluateTOI(value: number): IndicatorEvaluation {
    if (value <= 3) {
      return { 
        status: 'success', 
        message: 'Turn Over Interval optimal',
        action: 'Pertahankan efisiensi operasional'
      };
    } else {
      return { 
        status: 'warning', 
        message: 'Turn Over Interval tinggi, ada idle capacity',
        action: 'Optimalisasi penjadwalan dan kapasitas'
      };
    }
  }
}

/**
 * UNIFIED Indicator Cards Component
 */
const IndicatorCards: React.FC<IndicatorCardsProps> = ({ 
  className = "",
  variant = 'dashboard',
  showActions = false,
  autoRefresh = false,
  refreshInterval = 300 // 5 minutes default
}) => {
  const [stats, setStats] = useState<IndicatorStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const currentDate = new Date();
      const bulan = currentDate.getMonth() + 1;
      const tahun = currentDate.getFullYear();
      
      const response = await fetch(
        `http://localhost:8000/api/v1/dashboard/stats?bulan=${bulan}&tahun=${tahun}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch stats`);
      }
      
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
      console.error('Error fetching indicator stats:', err);
    } finally {
      setLoading(false);
    }
  };

  // Auto refresh functionality
  useEffect(() => {
    fetchStats();
    
    if (autoRefresh && refreshInterval > 0) {
      const interval = setInterval(fetchStats, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const handleRefresh = () => {
    fetchStats();
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'meningkat': return '📈';
      case 'menurun': return '📉';
      default: return '➡️';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 ${className}`}>
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
        <div className="flex items-center">
          <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2" />
          <h3 className="text-sm font-medium text-red-800">Error Loading Indicators</h3>
        </div>
        <div className="mt-2 text-sm text-red-700">{error}</div>
        <button
          onClick={handleRefresh}
          className="mt-3 bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded text-sm font-medium"
        >
          Coba Lagi
        </button>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <div className="text-gray-500">No data available</div>
      </div>
    );
  }

  // Evaluate indicators
  const borEval = IndicatorEvaluator.evaluateBOR(stats.bor_terkini);
  const losEval = IndicatorEvaluator.evaluateLOS(stats.los_bulanan);
  const btoEval = IndicatorEvaluator.evaluateBTO(stats.bto_bulanan);
  const toiEval = IndicatorEvaluator.evaluateTOI(stats.toi_bulanan);

  const indicators = [
    {
      code: 'BOR',
      name: 'Bed Occupancy Rate',
      value: stats.bor_terkini,
      unit: '%',
      icon: UsersIcon,
      evaluation: borEval,
      trend: `${getTrendIcon(stats.trend_bor)} ${stats.trend_bor}`,
      subtitle: `Avg: ${stats.rata_rata_bor_bulanan}%`
    },
    {
      code: 'LOS',
      name: 'Length of Stay',
      value: stats.los_bulanan,
      unit: ' hari',
      icon: ClockIcon,
      evaluation: losEval,
      subtitle: 'Rata-rata lama rawat'
    },
    {
      code: 'BTO',
      name: 'Bed Turn Over',
      value: stats.bto_bulanan,
      unit: 'x/bulan',
      icon: RefreshIcon,
      evaluation: btoEval,
      subtitle: 'Frekuensi pemakaian TT'
    },
    {
      code: 'TOI',
      name: 'Turn Over Interval',
      value: stats.toi_bulanan,
      unit: ' hari',
      icon: CalendarIcon,
      evaluation: toiEval,
      subtitle: 'Rata-rata TT kosong'
    }
  ];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with refresh button */}
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-900">
          Indikator Rawat Inap {stats.periode}
        </h2>
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="flex items-center px-3 py-1 text-sm bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-md border border-blue-200 disabled:opacity-50"
        >
          <RefreshIcon className={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Indicator Cards Grid */}
      <div className={`grid grid-cols-1 ${
        variant === 'compact' ? 'md:grid-cols-4' : 
        variant === 'detailed' ? 'md:grid-cols-2 lg:grid-cols-4' : 
        'md:grid-cols-2 lg:grid-cols-4'
      } gap-6`}>
        {indicators.map((indicator) => (
          <StatCard
            key={indicator.code}
            title={indicator.name}
            value={indicator.value}
            unit={indicator.unit}
            icon={<indicator.icon className="h-5 w-5" />}
            subtitle={indicator.subtitle}
            trend={indicator.trend}
            className={`${getStatusColor(indicator.evaluation.status)} border-l-4 ${
              indicator.evaluation.status === 'success' ? 'border-green-500' :
              indicator.evaluation.status === 'warning' ? 'border-yellow-500' :
              'border-red-500'
            }`}
            footer={
              variant === 'detailed' || showActions ? (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <p className="text-xs text-gray-600 mb-1">
                    {indicator.evaluation.message}
                  </p>
                  {showActions && (
                    <p className="text-xs text-blue-600 font-medium">
                      💡 {indicator.evaluation.action}
                    </p>
                  )}
                </div>
              ) : undefined
            }
          />
        ))}
      </div>

      {/* Summary Message */}
      {variant === 'detailed' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <ChartIcon className="h-5 w-5 text-blue-400 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-blue-800">
                Ringkasan Indikator
              </h4>
              <p className="text-sm text-blue-700 mt-1">
                Periode: {stats.periode} • 
                BOR Trend: {getTrendIcon(stats.trend_bor)} {stats.trend_bor} • 
                Status: {borEval.status === 'success' ? '✅ Optimal' : 
                        borEval.status === 'warning' ? '⚠️ Perlu Perhatian' : 
                        '🚨 Kritis'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IndicatorCards;
