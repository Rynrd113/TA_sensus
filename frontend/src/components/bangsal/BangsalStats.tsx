import React from 'react';
import { BangsalStats as BangsalStatsType } from '../../types/Common';
import { BuildingIcon, UsersIcon, CheckCircleIcon, ExclamationTriangleIcon } from '../icons';

interface BangsalStatsProps {
  stats: BangsalStatsType;
  loading?: boolean;
  className?: string;
}

export const BangsalStats: React.FC<BangsalStatsProps> = ({ 
  stats, 
  loading = false, 
  className = "" 
}) => {
  const occupancyRate = Math.round(stats.occupancy_rate);
  const isHighOccupancy = occupancyRate >= 80;
  const isCriticalOccupancy = occupancyRate >= 95;

  if (loading) {
    return (
      <div className={`grid grid-cols-1 md:grid-cols-4 gap-4 ${className}`}>
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="animate-pulse">
              <div className="h-8 w-8 bg-gray-300 rounded mb-4"></div>
              <div className="h-6 bg-gray-300 rounded mb-2"></div>
              <div className="h-4 bg-gray-300 rounded w-3/4"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  const StatCard = ({ 
    icon: Icon, 
    title, 
    value, 
    subtitle, 
    color = "blue",
    warning = false 
  }: {
    icon: React.ComponentType<{ className: string }>,
    title: string,
    value: string | number,
    subtitle: string,
    color?: string,
    warning?: boolean
  }) => {
    const colorClasses = {
      blue: 'bg-blue-50 text-blue-700',
      green: 'bg-green-50 text-green-700',
      yellow: 'bg-yellow-50 text-yellow-700',
      red: 'bg-red-50 text-red-700',
      gray: 'bg-gray-50 text-gray-700'
    };

    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${warning ? 'border-yellow-300 bg-yellow-50' : ''}`}>
        <div className="flex items-center mb-4">
          <div className={`p-2 rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
            <Icon className="w-6 h-6" />
          </div>
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
        </div>
      </div>
    );
  };

  return (
    <div className={`grid grid-cols-1 md:grid-cols-4 gap-4 ${className}`}>
      {/* Total Bangsal */}
      <StatCard
        icon={BuildingIcon}
        title="Total Bangsal"
        value={stats.total_bangsal}
        subtitle="Unit bangsal aktif"
        color="blue"
      />

      {/* Total Kapasitas */}
      <StatCard
        icon={UsersIcon}
        title="Total Kapasitas"
        value={stats.total_capacity}
        subtitle={`${stats.total_available} tersedia`}
        color="gray"
      />

      {/* Tingkat Okupansi */}
      <StatCard
        icon={UsersIcon}
        title="Tingkat Okupansi"
        value={`${occupancyRate}%`}
        subtitle={`${stats.total_occupied} dari ${stats.total_capacity} bed`}
        color={isCriticalOccupancy ? "red" : isHighOccupancy ? "yellow" : "green"}
        warning={isCriticalOccupancy}
      />

      {/* Emergency Ready */}
      <StatCard
        icon={stats.emergency_ready_count > 0 ? CheckCircleIcon : ExclamationTriangleIcon}
        title="Emergency Ready"
        value={stats.emergency_ready_count}
        subtitle="Bangsal siap darurat"
        color={stats.emergency_ready_count > 0 ? "green" : "red"}
        warning={stats.emergency_ready_count === 0}
      />
    </div>
  );
};

// Department breakdown component
export const DepartmentStats: React.FC<{ stats: BangsalStatsType }> = ({ stats }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Distribusi per Departemen
      </h3>
      <div className="space-y-3">
        {Object.entries(stats.by_department).map(([dept, data]: [string, any]) => (
          <div key={dept} className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">{dept}</span>
                <span className="text-sm text-gray-600">{Math.round(data.occupancy_rate)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    data.occupancy_rate >= 90 ? 'bg-red-500' : 
                    data.occupancy_rate >= 80 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(data.occupancy_rate, 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>{data.total_bangsal} bangsal</span>
                <span>{data.total_occupied}/{data.total_capacity} bed</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Type breakdown component  
export const TypeStats: React.FC<{ stats: BangsalStatsType }> = ({ stats }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Distribusi per Jenis
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Object.entries(stats.by_type).map(([type, data]: [string, any]) => (
          <div key={type} className="text-center">
            <div className="text-2xl font-bold text-gray-900">{data.count}</div>
            <div className="text-sm text-gray-600">{type}</div>
            <div className="text-xs text-gray-500">{Math.round(data.occupancy_rate)}% okupansi</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BangsalStats;