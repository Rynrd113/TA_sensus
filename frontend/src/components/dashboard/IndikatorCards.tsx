// frontend/src/components/dashboard/IndikatorCards.tsx
import React, { useEffect, useState } from 'react';
import StatCard from './StatCard';
import { 
  UsersIcon, 
  ClockIcon, 
  ScaleIcon, 
  CalendarIcon,
  RefreshIcon
} from '../icons';

interface IndikatorStats {
  bor_terkini: number;
  rata_rata_bor_bulanan: number;
  los_bulanan: number;
  bto_bulanan: number;
  toi_bulanan: number;
  periode: string;
  trend_bor: string;
}

interface IndikatorCardsProps {
  className?: string;
}

const IndikatorCards: React.FC<IndikatorCardsProps> = ({ className = "" }) => {
  const [stats, setStats] = useState<IndikatorStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/dashboard/stats');
      if (!response.ok) throw new Error('Failed to fetch stats');
      
      const data = await response.json();
      setStats({
        bor_terkini: data.stats.bor_terkini,
        rata_rata_bor_bulanan: data.stats.rata_rata_bor_bulanan,
        los_bulanan: data.stats.los_bulanan,
        bto_bulanan: data.stats.bto_bulanan,
        toi_bulanan: data.stats.toi_bulanan,
        periode: data.periode,
        trend_bor: data.trend_bor
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  // Helper functions
  const getBORVariant = (bor: number) => {
    if (bor >= 90) return 'critical';
    if (bor >= 80) return 'warning';
    if (bor >= 60) return 'success';
    return 'default';
  };

  const getLOSVariant = (los: number) => {
    if (los > 9) return 'critical';
    if (los >= 6 && los <= 9) return 'success';
    if (los >= 3) return 'warning';
    return 'critical';
  };

  const getBTOVariant = (bto: number) => {
    // BTO bulanan: ideal ~3-4x (dari 40-50x/tahun)
    if (bto >= 3 && bto <= 5) return 'success';
    if (bto >= 2 || bto <= 6) return 'warning';
    return 'critical';
  };

  const getTOIVariant = (toi: number) => {
    if (toi >= 1 && toi <= 3) return 'success';
    if (toi <= 5) return 'warning';
    return 'critical';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'naik': return '📈';
      case 'turun': return '📉';
      default: return '➡️';
    }
  };

  const getIndikatorStatus = (type: string, value: number) => {
    switch (type) {
      case 'bor':
        if (value >= 90) return { status: 'Kritis', desc: 'Hampir penuh' };
        if (value >= 80) return { status: 'Tinggi', desc: 'Perlu perhatian' };
        if (value >= 60) return { status: 'Ideal', desc: 'Sesuai standar' };
        return { status: 'Rendah', desc: 'Utilisasi kurang' };
      
      case 'los':
        if (value > 9) return { status: 'Terlalu Lama', desc: 'Efisiensi rendah' };
        if (value >= 6 && value <= 9) return { status: 'Ideal', desc: 'Sesuai standar' };
        if (value >= 3) return { status: 'Sedang', desc: 'Masih normal' };
        return { status: 'Terlalu Cepat', desc: 'Perlu evaluasi' };
      
      case 'bto':
        if (value >= 3 && value <= 5) return { status: 'Ideal', desc: 'Efisiensi baik' };
        if (value >= 2 || value <= 6) return { status: 'Sedang', desc: 'Bisa ditingkatkan' };
        return { status: 'Kurang', desc: 'Efisiensi rendah' };
      
      case 'toi':
        if (value >= 1 && value <= 3) return { status: 'Ideal', desc: 'Optimal' };
        if (value <= 5) return { status: 'Sedang', desc: 'Cukup baik' };
        return { status: 'Tinggi', desc: 'Banyak kosong' };
      
      default:
        return { status: 'Unknown', desc: 'Data tidak valid' };
    }
  };

  if (loading) {
    return (
      <div className={className}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse">
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
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700 font-medium">Error loading indicators</p>
          <p className="text-red-600 text-sm mt-1">{error}</p>
          <button 
            onClick={fetchStats}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm inline-flex items-center gap-2"
          >
            <RefreshIcon className="w-4 h-4" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-800">
            Indikator Rumah Sakit (Kemenkes)
          </h2>
          <p className="text-sm text-gray-600">
            Periode: {stats.periode} • Trend BOR: {stats.trend_bor} {getTrendIcon(stats.trend_bor)}
          </p>
        </div>
        <button 
          onClick={fetchStats}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm inline-flex items-center gap-2"
          disabled={loading}
        >
          <RefreshIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Indikator Cards Grid */}
      <div className="medical-stats-grid">
        {/* BOR Card */}
        <StatCard
          title="BOR (Bed Occupancy Rate)"
          value={stats.rata_rata_bor_bulanan}
          unit="%"
          subtitle={`Terkini: ${stats.bor_terkini}% • ${getIndikatorStatus('bor', stats.rata_rata_bor_bulanan).status}`}
          description={getIndikatorStatus('bor', stats.rata_rata_bor_bulanan).desc}
          variant={getBORVariant(stats.rata_rata_bor_bulanan)}
          icon={<UsersIcon className="w-6 h-6" />}
          trend={stats.trend_bor}
          benchmark="Ideal: 60-85%"
        />

        {/* LOS Card */}
        <StatCard
          title="LOS (Length of Stay)"
          value={stats.los_bulanan}
          unit="hari"
          subtitle={`${getIndikatorStatus('los', stats.los_bulanan).status}`}
          description={getIndikatorStatus('los', stats.los_bulanan).desc}
          variant={getLOSVariant(stats.los_bulanan)}
          icon={<ClockIcon className="w-6 h-6" />}
          benchmark="Ideal: 6-9 hari"
        />

        {/* BTO Card */}
        <StatCard
          title="BTO (Bed Turn Over)"
          value={stats.bto_bulanan}
          unit="x/bulan"
          subtitle={`${getIndikatorStatus('bto', stats.bto_bulanan).status}`}
          description={getIndikatorStatus('bto', stats.bto_bulanan).desc}
          variant={getBTOVariant(stats.bto_bulanan)}
          icon={<ScaleIcon className="w-6 h-6" />}
          benchmark="Ideal: 3-4x/bulan"
        />

        {/* TOI Card */}
        <StatCard
          title="TOI (Turn Over Interval)"
          value={stats.toi_bulanan}
          unit="hari"
          subtitle={`${getIndikatorStatus('toi', stats.toi_bulanan).status}`}
          description={getIndikatorStatus('toi', stats.toi_bulanan).desc}
          variant={getTOIVariant(stats.toi_bulanan)}
          icon={<CalendarIcon className="w-6 h-6" />}
          benchmark="Ideal: 1-3 hari"
        />
      </div>

      {/* Standar Kemenkes Info */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-800 mb-4">
          Standar Indikator Kemenkes RI
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
          <div className="bg-white p-4 rounded border">
            <p className="font-medium text-blue-800">BOR (Bed Occupancy Rate)</p>
            <p className="text-gray-600 mt-1"><strong>Ideal:</strong> 60-85%</p>
            <p className="text-xs text-gray-500 mt-2">
              Tingkat hunian tempat tidur. Mengukur efisiensi penggunaan kapasitas RS.
            </p>
          </div>
          <div className="bg-white p-4 rounded border">
            <p className="font-medium text-red-800">LOS (Length of Stay)</p>
            <p className="text-gray-600 mt-1">💡 <strong>Ideal:</strong> 6-9 hari</p>
            <p className="text-xs text-gray-500 mt-2">
              Rata-rata lama rawat inap. Indikator kualitas pelayanan dan efisiensi.
            </p>
          </div>
          <div className="bg-white p-4 rounded border">
            <p className="font-medium text-green-800">BTO (Bed Turn Over)</p>
            <p className="text-gray-600 mt-1">💡 <strong>Ideal:</strong> 40-50x/tahun</p>
            <p className="text-xs text-gray-500 mt-2">
              Frekuensi pemakaian tempat tidur. Mengukur produktivitas tempat tidur.
            </p>
          </div>
          <div className="bg-white p-4 rounded border">
            <p className="font-medium text-orange-800">TOI (Turn Over Interval)</p>
            <p className="text-gray-600 mt-1">💡 <strong>Ideal:</strong> 1-3 hari</p>
            <p className="text-xs text-gray-500 mt-2">
              Rata-rata hari kosong tempat tidur. Indikator efisiensi operasional.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IndikatorCards;
