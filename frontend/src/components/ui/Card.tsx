// 🏥 UNIFIED Card Component - Medical UI Framework
// Modern, Clean, Professional for Hospital Applications

import React from 'react';
import { cn } from '../../utils/cn';

interface CardProps {
  title?: string;
  subtitle?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'minimal';
  size?: 'sm' | 'md' | 'lg';
  header?: React.ReactNode;
  footer?: React.ReactNode;
  loading?: boolean;
  hoverable?: boolean;
}

const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  description,
  children,
  className,
  variant = 'default',
  size = 'md',
  header,
  footer,
  loading = false,
  hoverable = false
}) => {
  // Base medical card classes
  const baseClasses = cn(
    'medical-card',
    hoverable && 'medical-card-hover cursor-pointer'
  );

  // Variant classes using medical design system
  const variantClasses = {
    default: '',
    primary: 'border-primary-200 bg-primary-50/30',
    success: 'border-success-200 bg-success-50/30',
    warning: 'border-warning-200 bg-warning-50/30',
    danger: 'border-error-200 bg-error-50/30',
    minimal: 'border-medical-100 shadow-none'
  };

  // Size classes
  const sizeClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  // Title variant classes
  const titleVariantClasses = {
    default: 'text-medical-900',
    primary: 'text-primary-900',
    success: 'text-success-900',
    warning: 'text-warning-900',
    danger: 'text-error-900',
    minimal: 'text-medical-900'
  };

  if (loading) {
    return (
      <div className={cn(baseClasses, variantClasses[variant], sizeClasses[size], className)}>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-medical-200 rounded w-1/4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-medical-200 rounded"></div>
            <div className="h-4 bg-medical-200 rounded w-5/6"></div>
            <div className="h-4 bg-medical-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn(baseClasses, variantClasses[variant], sizeClasses[size], className)}>
      {/* Custom Header */}
      {header && (
        <div className="mb-6">
          {header}
        </div>
      )}

      {/* Standard Header */}
      {(title || subtitle || description) && !header && (
        <div className="mb-6">
          {title && (
            <h3 className={cn('medical-heading text-lg mb-2', titleVariantClasses[variant])}>
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="medical-subheading text-sm mb-2">
              {subtitle}
            </p>
          )}
          {description && (
            <p className="medical-caption">
              {description}
            </p>
          )}
        </div>
      )}

      {/* Content */}
      <div className="flex-1">
        {children}
      </div>

      {/* Footer */}
      {footer && (
        <div className="mt-6 pt-4 border-t border-medical-200">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;
