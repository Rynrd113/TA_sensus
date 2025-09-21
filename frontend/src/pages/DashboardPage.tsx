// Simplified Dashboard - Overview Only
import { useEffect, useState, useCallback, useMemo } from "react";
import { Link } from "react-router-dom";
import StatCard from "../components/dashboard/StatCard";
import MedicalIndicatorCard from "../components/dashboard/MedicalIndicatorCard";
import SARIMAChart from "../components/dashboard/SARIMAChart";
import { useMedicalStandards } from "../utils/medicalStandards";
import { 
  RefreshIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  UsersIcon,
  ClockIcon,
  ScaleIcon,
  CalendarIcon
} from "../components/icons";

// Enhanced UI Components
import { 
  MedicalLoadingSpinner, 
  MedicalSkeleton, 
  MedicalErrorState,
  MedicalProgressBar 
} from "../components/ui/LoadingStates";
import { 
  ResponsiveGrid, 
  ResponsiveContainer, 
  ResponsiveCard
} from "../components/ui/ResponsiveLayout";

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
  const { fetchStandards } = useMedicalStandards();

  // Load medical standards on component mount
  useEffect(() => {
    fetchStandards();
  }, []);

  const fetchDashboardData = useCallback(async () => {
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
  }, [bulan, tahun]);

  useEffect(() => {
    fetchDashboardData();
  }, [bulan, tahun]);

  const handleRefresh = useCallback(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Memoized computed values untuk performa yang lebih baik
  const computedStats = useMemo(() => {
    if (!dashboardData?.stats) return null;

    const { stats } = dashboardData;
    return {
      borStatus: (stats.bor_terkini >= 60 && stats.bor_terkini <= 85 ? 'success' : 
                 stats.bor_terkini > 85 ? 'critical' : 'warning') as 'success' | 'critical' | 'warning',
      capacityStatus: (stats.kapasitas_kosong < 10 ? 'warning' : 'success') as 'warning' | 'success',
      isHighRisk: stats.bor_terkini > 90,
      isLowUtilization: stats.bor_terkini < 40,
    };
  }, [dashboardData?.stats]);

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

  if (loading) {
    return (
      <div className="min-h-screen bg-primary-50">
        <ResponsiveContainer maxWidth="7xl" padding="lg">
          {/* Enhanced Header Skeleton */}
          <ResponsiveCard variant="elevated" className="mb-6">
            <MedicalSkeleton variant="text" className="mb-4" />
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <MedicalSkeleton variant="text" />
              <div className="flex gap-3">
                <div className="h-10 bg-gray-200 rounded w-24 animate-pulse"></div>
                <div className="h-10 bg-gray-200 rounded w-20 animate-pulse"></div>
                <div className="h-10 bg-gray-200 rounded w-24 animate-pulse"></div>
              </div>
            </div>
          </ResponsiveCard>
          
          {/* Enhanced Cards Skeleton */}
          <ResponsiveGrid cols={{ xs: 1, sm: 2, lg: 4 }} gap={6} className="mb-8">
            <MedicalSkeleton variant="card" count={4} />
          </ResponsiveGrid>

          {/* Charts Skeleton */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <MedicalSkeleton variant="chart" count={2} />
          </div>

          {/* Loading Progress */}
          <ResponsiveCard variant="filled" className="text-center">
            <MedicalLoadingSpinner size="lg" message="Memuat dashboard rumah sakit..." />
            <MedicalProgressBar 
              percentage={75} 
              label="Loading Dashboard Data" 
              variant="primary"
              className="mt-4 max-w-md mx-auto"
            />
          </ResponsiveCard>
        </ResponsiveContainer>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-primary-50">
        <ResponsiveContainer maxWidth="7xl" padding="lg">
          <MedicalErrorState
            title="Error Loading Dashboard"
            message={`Tidak dapat memuat data dashboard: ${error}`}
            onRetry={handleRefresh}
            retryText="Coba Lagi"
            variant="error"
            className="max-w-2xl mx-auto mt-20"
          />
        </ResponsiveContainer>
      </div>
    );
  }

  if (!dashboardData) {
    return null;
  }

  const { stats } = dashboardData;

  return (
    <div className="min-h-screen bg-primary-50">
      <ResponsiveContainer maxWidth="7xl" padding="lg">
        {/* Simplified Header */}
        <ResponsiveCard variant="elevated" className="mb-6">
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
                title="Refresh Data"
              >
                <RefreshIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        </ResponsiveCard>

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
        <ResponsiveGrid cols={{ xs: 1, sm: 2, lg: 4 }} gap={6} className="mb-8">
          <MedicalIndicatorCard
            title="BOR Hari Ini"
            value={stats.bor_terkini}
            unit="%"
            indicatorType="BOR"
            icon={<UsersIcon className="w-5 h-5" />}
            showRecommendation={true}
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
            variant={computedStats?.capacityStatus || 'default'}
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
        </ResponsiveGrid>

        {/* Quick Actions */}
        <ResponsiveGrid cols={{ xs: 1, md: 3 }} gap={6} className="mb-8">
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
        </ResponsiveGrid>

        {/* SARIMA Prediction Section - Sesuai Jurnal Penelitian */}
        <div className="mb-8">
          <div className="bg-white rounded-lg border border-primary-200 p-6 mb-4">
            <h2 className="text-xl font-semibold text-vmeds-900 mb-2 flex items-center gap-2">
              🧠 SARIMA Prediction System
            </h2>
            <p className="text-vmeds-600 text-sm mb-4">
              Implementasi model penelitian: "Peramalan Indikator Rumah Sakit Berbasis Sensus Harian Rawat Inap dengan Model SARIMA"
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                <div className="font-medium text-blue-800">📊 Metodologi</div>
                <div className="text-blue-700">Box-Jenkins SARIMA</div>
              </div>
              <div className="bg-green-50 p-3 rounded-lg border border-green-200">
                <div className="font-medium text-green-800">🎯 Target Akurasi</div>
                <div className="text-green-700">MAPE &lt; 10%</div>
              </div>
              <div className="bg-purple-50 p-3 rounded-lg border border-purple-200">
                <div className="font-medium text-purple-800">📈 Prediksi</div>
                <div className="text-purple-700">BOR 7 hari ke depan</div>
              </div>
            </div>
          </div>
          <SARIMAChart />
        </div>

        {/* Medical Standards Reference */}
        <ResponsiveCard variant="elevated" className="mb-6">
          <h2 className="text-lg font-semibold text-vmeds-900 mb-4">Standar Indikator Kemenkes RI</h2>
          <ResponsiveGrid cols={{ xs: 1, sm: 2, lg: 4 }} gap={4}>
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
          </ResponsiveGrid>
        </ResponsiveCard>
      </ResponsiveContainer>
    </div>
  );
}
