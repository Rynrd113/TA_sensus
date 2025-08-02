// frontend/src/components/ComprehensiveIndicatorCards.tsx
import React, { useState, useEffect } from 'react';
import StatCard from './dashboard/StatCard';
import { 
  UsersIcon, 
  ClockIcon, 
  ScaleIcon, 
  CalendarIcon,
  ChartIcon 
} from './icons';

interface IndicatorData {
  code: string;
  name: string;
  value: number;
  unit: string;
  description: string;
  target: {
    min?: number;
    max?: number;
  };
  trend?: number;
}

type IndicatorStatus = 'excellent' | 'good' | 'warning' | 'poor' | 'critical';

const ComprehensiveIndicatorCards: React.FC = () => {
  const [indicators, setIndicators] = useState<IndicatorData[]>([]);
  const [loading, setLoading] = useState(true);

  // Mock data with proper evaluation logic
  const mockIndicators: IndicatorData[] = [
    {
      code: 'BOR',
      name: 'Bed Occupancy Rate',
      value: 75.5,
      unit: '%',
      description: 'Tingkat hunian tempat tidur',
      target: { min: 60, max: 85 },
      trend: 2.1
    },
    {
      code: 'LOS',
      name: 'Length of Stay',
      value: 6.2,
      unit: ' hari',
      description: 'Rata-rata lama rawat',
      target: { min: 6, max: 9 },
      trend: -0.8
    },
    {
      code: 'BTO',
      name: 'Bed Turn Over',
      value: 45.8,
      unit: ' kali',
      description: 'Perputaran tempat tidur',
      target: { min: 40, max: 50 },
      trend: 3.2
    },
    {
      code: 'TOI',
      name: 'Turn Over Interval',
      value: 1.8,
      unit: ' hari',
      description: 'Interval perputaran',
      target: { min: 1, max: 3 },
      trend: -0.5
    }
  ];

  useEffect(() => {
    // Simulate API call
    const fetchData = async () => {
      try {
        // In real app, fetch from backend
        await new Promise(resolve => setTimeout(resolve, 500));
        setIndicators(mockIndicators);
      } catch (error) {
        console.error('Error fetching indicators:', error);
        setIndicators(mockIndicators); // Fallback to mock data
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const evaluateIndicator = (code: string, value: number): IndicatorStatus => {
    const indicator = indicators.find(ind => ind.code === code);
    if (!indicator) return 'good';

    switch (code) {
      case 'BOR':
        if (value >= 70 && value <= 85) return 'excellent';
        if (value >= 60 && value < 70) return 'good';
        if ((value >= 50 && value < 60) || (value > 85 && value <= 90)) return 'warning';
        if ((value >= 40 && value < 50) || (value > 90 && value <= 95)) return 'poor';
        return 'critical';
      
      case 'LOS':
        if (value >= 6 && value <= 9) return 'excellent';
        if ((value >= 5 && value < 6) || (value > 9 && value <= 11)) return 'good';
        if ((value >= 4 && value < 5) || (value > 11 && value <= 14)) return 'warning';
        if ((value >= 3 && value < 4) || (value > 14 && value <= 18)) return 'poor';
        return 'critical';
      
      case 'BTO':
        if (value >= 40 && value <= 50) return 'excellent';
        if ((value >= 30 && value < 40) || (value > 50 && value <= 60)) return 'good';
        if ((value >= 25 && value < 30) || (value > 60 && value <= 70)) return 'warning';
        if ((value >= 15 && value < 25) || (value > 70 && value <= 80)) return 'poor';
        return 'critical';
      
      case 'TOI':
        if (value >= 1 && value <= 3) return 'excellent';
        if ((value >= 0.5 && value < 1) || (value > 3 && value <= 4)) return 'good';
        if ((value >= 0.2 && value < 0.5) || (value > 4 && value <= 6)) return 'warning';
        if ((value >= 0.1 && value < 0.2) || (value > 6 && value <= 8)) return 'poor';
        return 'critical';
      
      default:
        return 'good';
    }
  };

  const getIcon = (code: string) => {
    switch (code) {
      case 'BOR': return <UsersIcon className="w-5 h-5" />;
      case 'LOS': return <ClockIcon className="w-5 h-5" />;
      case 'BTO': return <ScaleIcon className="w-5 h-5" />;
      case 'TOI': return <CalendarIcon className="w-5 h-5" />;
      default: return <ChartIcon className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-4 sm:space-y-6">
        <div className="bg-gray-200 animate-pulse rounded-xl h-24 sm:h-32"></div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-gray-200 animate-pulse rounded-xl h-32 sm:h-40"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header - Responsive */}
      <div className="bg-primary-500 rounded-xl p-4 sm:p-6 text-white">
        <h2 className="text-xl sm:text-2xl font-bold mb-2">Indikator Kemenkes RS</h2>
        <p className="text-primary-100 text-sm sm:text-base">
          Monitoring lengkap 4 indikator utama kinerja rumah sakit
        </p>
      </div>

      {/* Cards Grid - Responsive */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {indicators.map((indicator) => {
          const evaluatedStatus = evaluateIndicator(indicator.code, indicator.value);
          return (
            <StatCard
              key={indicator.code}
              title={indicator.name}
              value={`${indicator.value}${indicator.unit}`}
              description={indicator.description}
              icon={getIcon(indicator.code)}
              variant={evaluatedStatus as any}
              trend={indicator.trend ? `${indicator.trend > 0 ? '+' : ''}${indicator.trend.toFixed(1)}` : undefined}
            />
          );
        })}
      </div>

      {/* Summary Status - Mobile Friendly */}
      <div className="bg-white rounded-xl p-4 sm:p-6 border border-gray-200">
        <h3 className="text-base sm:text-lg font-semibold mb-4">Status Keseluruhan</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
          {indicators.map((indicator) => {
            const status = evaluateIndicator(indicator.code, indicator.value);
            return (
              <div key={indicator.code} className="text-center">
                <div className={`w-10 h-10 sm:w-12 sm:h-12 mx-auto rounded-full flex items-center justify-center mb-2 ${
                  status === 'excellent' ? 'bg-emerald-100 text-emerald-600' :
                  status === 'good' ? 'bg-blue-100 text-blue-600' :
                  status === 'warning' ? 'bg-yellow-100 text-yellow-600' :
                  status === 'poor' ? 'bg-orange-100 text-orange-600' :
                  'bg-red-100 text-red-600'
                }`}>
                  <span className="text-sm sm:text-base">{getIcon(indicator.code)}</span>
                </div>
                <p className="text-xs font-medium text-gray-700">{indicator.code}</p>
                <p className="text-xs text-gray-500 capitalize">{status}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ComprehensiveIndicatorCards;
