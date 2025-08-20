// frontend/src/components/dashboard/StatCard.tsx
import React from 'react';

interface StatCardProps {
  title: string;
  value: number | string;
  unit?: string;
  subtitle?: string;
  description?: string;
  variant?: 'default' | 'warning' | 'critical' | 'success';
  icon?: React.ReactNode;
  trend?: string;
  benchmark?: string;
  className?: string;
  footer?: React.ReactNode;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  unit = '',
  subtitle,
  description,
  variant = 'default',
  icon,
  trend,
  benchmark,
  className = '',
  footer
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'critical':
        return 'border-red-200 bg-red-50';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50';
      case 'success':
        return 'border-primary-200 bg-primary-50';
      default:
        return 'border-primary-200 bg-white';
    }
  };

  const getTitleColor = () => {
    switch (variant) {
      case 'critical':
        return 'text-red-800';
      case 'warning':
        return 'text-yellow-800';
      case 'success':
        return 'text-primary-800';
      default:
        return 'text-vmeds-800';
    }
  };

  const getValueColor = () => {
    switch (variant) {
      case 'critical':
        return 'text-red-900';
      case 'warning':
        return 'text-yellow-900';
      case 'success':
        return 'text-primary-900';
      default:
        return 'text-vmeds-900';
    }
  };

  return (
    <div className={`rounded-lg border p-6 shadow-sm hover:shadow-md transition-shadow ${getVariantStyles()} ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className={`text-sm font-medium ${getTitleColor()}`}>
          {title}
        </h3>
        {icon && (
          <div className={`p-2 rounded-lg ${
            variant === 'critical' ? 'bg-red-100' :
            variant === 'warning' ? 'bg-yellow-100' :
            variant === 'success' ? 'bg-primary-100' :
            'bg-primary-100'
          }`}>
            {icon}
          </div>
        )}
      </div>
      
      <div className="mb-2">
        <span className={`text-3xl font-bold ${getValueColor()}`}>
          {typeof value === 'number' ? 
            (Number.isInteger(value) ? value.toString() : value.toFixed(2)) : 
            value}
        </span>
        {unit && (
          <span className={`text-lg font-medium ml-1 ${getTitleColor()}`}>
            {unit}
          </span>
        )}
      </div>
      
      {subtitle && (
        <p className="text-sm text-vmeds-600 mb-2">
          {subtitle}
        </p>
      )}
      
      {description && (
        <p className="text-xs text-vmeds-500 mb-2">
          {description}
        </p>
      )}
      
      {benchmark && (
        <p className="text-xs text-vmeds-500 font-medium">
          {benchmark}
        </p>
      )}
      
      {trend && (
        <div className="mt-2 pt-2 border-t border-primary-200">
          <p className="text-xs text-vmeds-500">
            Trend: {trend}
          </p>
        </div>
      )}
      
      {footer && footer}
    </div>
  );
};

export default StatCard;
