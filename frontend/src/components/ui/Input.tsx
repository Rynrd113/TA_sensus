import React from 'react';
import { cn } from '../../utils/cn';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

// 🏥 UNIFIED Input Component - Medical UI Framework
// Modern, Clean, Professional for Hospital Applications

import React, { forwardRef } from 'react';
import { cn } from '../../utils/cn';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: 'default' | 'medical' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  loading?: boolean;
  required?: boolean;
}

const Input = forwardRef<HTMLInputElement, InputProps>(({
  label,
  error,
  helperText,
  variant = 'default',
  size = 'md',
  leftIcon,
  rightIcon,
  loading = false,
  required = false,
  className,
  ...props
}, ref) => {
  const inputVariantClasses = {
    default: 'medical-input',
    medical: 'medical-input border-primary-200 focus:border-primary-400',
    success: 'medical-input border-success-200 focus:border-success-400',
    warning: 'medical-input border-warning-200 focus:border-warning-400',
    error: 'medical-input border-error-400 focus:border-error-500'
  };

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-base',
    lg: 'px-5 py-4 text-lg'
  };

  const iconSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  return (
    <div className="w-full">
      {/* Label */}
      {label && (
        <label className="medical-label flex items-center gap-1 mb-2">
          {label}
          {required && <span className="text-error-500">*</span>}
        </label>
      )}

      {/* Input Container */}
      <div className="relative">
        {/* Left Icon */}
        {leftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-medical-400">
            <div className={iconSizeClasses[size]}>
              {leftIcon}
            </div>
          </div>
        )}

        {/* Input Field */}
        <input
          ref={ref}
          className={cn(
            inputVariantClasses[error ? 'error' : variant],
            sizeClasses[size],
            leftIcon && 'pl-10',
            rightIcon && 'pr-10',
            loading && 'opacity-60 cursor-not-allowed',
            className
          )}
          disabled={loading || props.disabled}
          {...props}
        />

        {/* Right Icon */}
        {rightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-medical-400">
            <div className={iconSizeClasses[size]}>
              {rightIcon}
            </div>
          </div>
        )}

        {/* Loading Spinner */}
        {loading && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-300 border-t-primary-600"></div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <p className="medical-error mt-2">
          {error}
        </p>
      )}

      {/* Helper Text */}
      {helperText && !error && (
        <p className="medical-caption mt-2">
          {helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;

// Select Component
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  options: { value: string | number; label: string }[];
}

export const Select: React.FC<SelectProps> = ({
  label,
  error,
  helperText,
  options,
  className,
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="medical-label">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <select
        className={cn(
          'medical-input',
          error && 'medical-input-error',
          className
        )}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      
      {error && (
        <p className="medical-error-text">
          {error}
        </p>
      )}
      
      {helperText && !error && (
        <p className="medical-helper-text">
          {helperText}
        </p>
      )}
    </div>
  );
};

export default Input;
