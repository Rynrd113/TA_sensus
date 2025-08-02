// Simplified Dashboard - Overview Only
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import StatCard from "../components/dashboard/StatCard";
import { 
  RefreshIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  UsersIcon,
  ClockIcon,
  ScaleIcon,
  CalendarIcon
} from "../components/icons";

interface DashboardStats {
  stats: {
    tanggal_terakhir: string;
    total_pasien_hari_ini: number;
    bor_terkini: number;
    rata_rata_bor_bulanan: number;
    los_bulanan: number;
    bto_bulanan: number;
    toi_bulanan: number;
    tt_total: number;
    jumlah_hari_data: number;
    total_pasien_masuk: number;
    total_pasien_keluar: number;
    kapasitas_kosong: number;
  };
  peringatan: string[];
  periode: string;
  trend_bor: string;
}

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bulan, setBulan] = useState(1); // Use January since that's where data exists
  const [tahun, setTahun] = useState(2025);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      console.log('Fetching dashboard data...', { bulan, tahun });
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch(
        `http://localhost:8000/api/v1/dashboard/stats?bulan=${bulan}&tahun=${tahun}`,
        { 
          signal: controller.signal,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          }
        }
      );

      clearTimeout(timeoutId);
      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Dashboard data received:', data);
      console.log('Stats values:', {
        bor_terkini: data.stats?.bor_terkini,
        total_pasien: data.stats?.total_pasien_hari_ini,
        kapasitas_kosong: data.stats?.kapasitas_kosong,
        tt_total: data.stats?.tt_total
      });
      setDashboardData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to fetch dashboard data');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [bulan, tahun]);

  const handleRefresh = () => {
    fetchDashboardData();
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'naik':
      case 'meningkat':
        return <TrendingUpIcon className="w-4 h-4 text-green-500" />;
      case 'turun':
      case 'menurun':
        return <TrendingDownIcon className="w-4 h-4 text-red-500" />;
      default:
        return <span className="text-gray-500">→</span>;
    }
  };

  const getStatusVariant = (type: string, value: number) => {
    switch (type) {
      case 'bor':
        if (value >= 60 && value <= 85) return 'success';
        if (value > 85) return 'critical';
        return 'warning';
      case 'los':
        if (value >= 6 && value <= 9) return 'success';
        if (value > 9) return 'critical';
        return 'default';
      case 'bto':
        if (value >= 3 && value <= 5) return 'success';
        return 'default';
      case 'toi':
        if (value >= 1 && value <= 3) return 'success';
        return 'default';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 lg:p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header Skeleton */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
          
          {/* Cards Skeleton */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/3 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-primary-50 p-4 lg:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-lg border border-primary-200 p-8 text-center">
            <svg className="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h3 className="text-lg font-semibold text-vmeds-900 mb-2">Error Loading Dashboard</h3>
            <p className="text-vmeds-600 mb-4">{error}</p>
            <button 
              onClick={handleRefresh} 
              className="inline-flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
            >
              <RefreshIcon className="w-4 h-4 mr-2" />
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return null;
  }

  const { stats } = dashboardData;

  return (
    <div className="min-h-screen bg-primary-50 p-4 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Simplified Header */}
        <div className="bg-white rounded-lg border border-primary-200 p-6 mb-6 shadow-sm">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="mb-4 lg:mb-0">
              <h1 className="text-2xl lg:text-3xl font-bold text-vmeds-900 mb-2">
                Dashboard Overview
              </h1>
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 text-sm text-vmeds-600">
                <span>Periode: {dashboardData.periode}</span>
                <span className="hidden sm:inline">•</span>
                <span>Update: {stats.tanggal_terakhir}</span>
                <span className="hidden sm:inline">•</span>
                <div className="flex items-center gap-1">
                  <span>Trend BOR:</span>
                  {getTrendIcon(dashboardData.trend_bor)}
                  <span className="capitalize">{dashboardData.trend_bor}</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <select 
                  value={bulan} 
                  onChange={(e) => setBulan(Number(e.target.value))}
                  className="px-3 py-2 border border-primary-300 bg-white text-vmeds-700 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  {Array.from({length: 12}, (_, i) => (
                    <option key={i+1} value={i+1}>
                      {new Date(2025, i).toLocaleDateString('id-ID', { month: 'long' })}
                    </option>
                  ))}
                </select>
                <select 
                  value={tahun} 
                  onChange={(e) => setTahun(Number(e.target.value))}
                  className="px-3 py-2 border border-primary-300 bg-white text-vmeds-700 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  {Array.from({length: 5}, (_, i) => (
                    <option key={2023+i} value={2023+i}>{2023+i}</option>
                  ))}
                </select>
              </div>
              <button 
                onClick={handleRefresh} 
                className="p-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
              >
                <RefreshIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Alert Cards */}
        {dashboardData.peringatan && dashboardData.peringatan.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-yellow-800 mb-2">Peringatan Sistem</h3>
            <ul className="text-sm text-yellow-700 space-y-1">
              {dashboardData.peringatan.map((alert, index) => (
                <li key={index}>• {alert}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Key Performance Indicators Only */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="BOR Hari Ini"
            value={stats.bor_terkini}
            unit="%"
            description="Tingkat hunian tempat tidur"
            variant={getStatusVariant('bor', stats.bor_terkini)}
            icon={<UsersIcon className="w-5 h-5" />}
            trend={dashboardData.trend_bor}
          />
          
          <StatCard
            title="Total Pasien"
            value={stats.total_pasien_hari_ini}
            description="Pasien hari ini"
            variant="default"
            icon={<UsersIcon className="w-5 h-5" />}
          />
          
          <StatCard
            title="Kapasitas Kosong"
            value={stats.kapasitas_kosong}
            unit="bed"
            description="Tempat tidur tersedia"
            variant={stats.kapasitas_kosong < 10 ? 'warning' : 'success'}
            icon={<ScaleIcon className="w-5 h-5" />}
          />
          
          <StatCard
            title="Total TT"
            value={stats.tt_total}
            unit="bed"
            description="Total tempat tidur"
            variant="default"
            icon={<CalendarIcon className="w-5 h-5" />}
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Link 
            to="/indikator-lengkap" 
            className="bg-white rounded-lg border border-primary-200 p-6 hover:border-primary-300 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary-100 rounded-lg">
                <ScaleIcon className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-vmeds-900 mb-1">Indikator Lengkap</h3>
                <p className="text-sm text-vmeds-600">Lihat BOR, LOS, BTO, TOI detail</p>
              </div>
            </div>
          </Link>

          <Link 
            to="/bangsal" 
            className="bg-white rounded-lg border border-primary-200 p-6 hover:border-primary-300 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary-100 rounded-lg">
                <UsersIcon className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-vmeds-900 mb-1">Input Data</h3>
                <p className="text-sm text-vmeds-600">Tambah data sensus harian</p>
              </div>
            </div>
          </Link>

          <Link 
            to="/chart" 
            className="bg-white rounded-lg border border-primary-200 p-6 hover:border-primary-300 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary-100 rounded-lg">
                <ClockIcon className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-vmeds-900 mb-1">Analytics</h3>
                <p className="text-sm text-vmeds-600">Grafik dan prediksi BOR</p>
              </div>
            </div>
          </Link>
        </div>

        {/* Medical Standards Reference */}
        <div className="bg-white rounded-lg border border-primary-200 p-6">
          <h2 className="text-lg font-semibold text-vmeds-900 mb-4">Standar Indikator Kemenkes RI</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-primary-50 rounded-lg p-4 border border-primary-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-vmeds-900">BOR</h4>
                <span className="text-xs bg-primary-100 text-primary-800 px-2 py-1 rounded-full">Okupansi</span>
              </div>
              <p className="text-sm text-vmeds-600 mb-1">Target: 60-85%</p>
              <p className="text-xs text-vmeds-500">Bed Occupancy Rate</p>
            </div>
            <div className="bg-primary-50 rounded-lg p-4 border border-primary-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-vmeds-900">LOS</h4>
                <span className="text-xs bg-primary-100 text-primary-800 px-2 py-1 rounded-full">Lama Rawat</span>
              </div>
              <p className="text-sm text-vmeds-600 mb-1">Target: 6-9 hari</p>
              <p className="text-xs text-vmeds-500">Length of Stay</p>
            </div>
            <div className="bg-primary-50 rounded-lg p-4 border border-primary-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-vmeds-900">BTO</h4>
                <span className="text-xs bg-primary-100 text-primary-800 px-2 py-1 rounded-full">Perputaran</span>
              </div>
              <p className="text-sm text-vmeds-600 mb-1">Target: 40-50x/tahun</p>
              <p className="text-xs text-vmeds-500">Bed Turn Over</p>
            </div>
            <div className="bg-primary-50 rounded-lg p-4 border border-primary-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-vmeds-900">TOI</h4>
                <span className="text-xs bg-primary-100 text-primary-800 px-2 py-1 rounded-full">Interval</span>
              </div>
              <p className="text-sm text-vmeds-600 mb-1">Target: 1-3 hari</p>
              <p className="text-xs text-vmeds-500">Turn Over Interval</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
