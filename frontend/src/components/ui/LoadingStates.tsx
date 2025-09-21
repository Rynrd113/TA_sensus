// 🏥 Enhanced Loading States - Medical UI Framework
import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  message?: string;
  className?: string;
}

interface SkeletonProps {
  variant?: 'card' | 'chart' | 'table' | 'text';
  count?: number;
  className?: string;
}

export const MedicalLoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  message = 'Memuat data...', 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  return (
    <div className={`flex flex-col items-center justify-center p-8 ${className}`}>
      <div className="relative">
        <div className={`${sizeClasses[size]} border-4 border-primary-200 rounded-full animate-spin`}>
          <div className={`${sizeClasses[size]} border-4 border-primary-600 border-t-transparent rounded-full animate-spin`}></div>
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-2 h-2 bg-primary-600 rounded-full animate-pulse"></div>
        </div>
      </div>
      {message && (
        <p className="mt-4 text-sm text-vmeds-600 font-medium animate-pulse">
          {message}
        </p>
      )}
    </div>
  );
};

export const MedicalSkeleton: React.FC<SkeletonProps> = ({ 
  variant = 'card', 
  count = 1, 
  className = '' 
}) => {
  const renderSkeleton = () => {
    switch (variant) {
      case 'card':
        return (
          <div className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse">
            <div className="flex items-center justify-between mb-4">
              <div className="h-4 bg-gray-200 rounded w-1/3"></div>
              <div className="h-8 w-8 bg-gray-200 rounded-lg"></div>
            </div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-3/4 mb-1"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        );
      
      case 'chart':
        return (
          <div className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-64 bg-gray-200 rounded mb-4"></div>
            <div className="flex justify-center gap-4">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-16"></div>
                </div>
              ))}
            </div>
          </div>
        );
      
      case 'table':
        return (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden animate-pulse">
            <div className="bg-gray-50 px-6 py-4 border-b">
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </div>
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="px-6 py-4 border-b border-gray-100">
                <div className="flex gap-4">
                  <div className="h-4 bg-gray-200 rounded flex-1"></div>
                  <div className="h-4 bg-gray-200 rounded w-20"></div>
                  <div className="h-4 bg-gray-200 rounded w-16"></div>
                  <div className="h-4 bg-gray-200 rounded w-24"></div>
                </div>
              </div>
            ))}
          </div>
        );
      
      case 'text':
        return (
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className={className}>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className={count > 1 ? 'mb-4' : ''}>
          {renderSkeleton()}
        </div>
      ))}
    </div>
  );
};

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  retryText?: string;
  className?: string;
  variant?: 'error' | 'warning' | 'info';
}

export const MedicalErrorState: React.FC<ErrorStateProps> = ({
  title = 'Terjadi Kesalahan',
  message = 'Tidak dapat memuat data. Silakan coba lagi.',
  onRetry,
  retryText = 'Coba Lagi',
  className = '',
  variant = 'error'
}) => {
  const variantClasses = {
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };

  const iconClasses = {
    error: 'text-red-400',
    warning: 'text-yellow-400',
    info: 'text-blue-400'
  };

  const buttonClasses = {
    error: 'bg-red-600 hover:bg-red-700',
    warning: 'bg-yellow-600 hover:bg-yellow-700',
    info: 'bg-blue-600 hover:bg-blue-700'
  };

  return (
    <div className={`rounded-lg border p-6 text-center ${variantClasses[variant]} ${className}`}>
      <svg 
        className={`w-12 h-12 mx-auto mb-4 ${iconClasses[variant]}`} 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        {variant === 'error' && (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        )}
        {variant === 'warning' && (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        )}
        {variant === 'info' && (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        )}
      </svg>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="mb-4 opacity-80">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className={`inline-flex items-center px-4 py-2 rounded-lg text-white font-medium transition-colors ${buttonClasses[variant]}`}
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {retryText}
        </button>
      )}
    </div>
  );
};

interface ProgressProps {
  percentage: number;
  label?: string;
  showPercentage?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'success' | 'warning' | 'danger';
  className?: string;
}

export const MedicalProgressBar: React.FC<ProgressProps> = ({
  percentage,
  label,
  showPercentage = true,
  size = 'md',
  variant = 'primary',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  const variantClasses = {
    primary: 'bg-primary-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
    danger: 'bg-red-600'
  };

  const backgroundClasses = {
    primary: 'bg-primary-100',
    success: 'bg-green-100',
    warning: 'bg-yellow-100',
    danger: 'bg-red-100'
  };

  return (
    <div className={`w-full ${className}`}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-2">
          {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
          {showPercentage && <span className="text-sm text-gray-500">{percentage.toFixed(0)}%</span>}
        </div>
      )}
      <div className={`w-full ${backgroundClasses[variant]} rounded-full ${sizeClasses[size]}`}>
        <div
          className={`${sizeClasses[size]} ${variantClasses[variant]} rounded-full transition-all duration-300 ease-out`}
          style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
        />
      </div>
    </div>
  );
};

export default {
  MedicalLoadingSpinner,
  MedicalSkeleton,
  MedicalErrorState,
  MedicalProgressBar
};