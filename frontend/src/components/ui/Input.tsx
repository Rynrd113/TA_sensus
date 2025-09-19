import React, { forwardRef } from 'react';
import { cn } from '../../utils/cn';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: 'default' | 'medical' | 'success' | 'warning' | 'error';
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(({
  label,
  error,
  helperText,
  variant = 'default',
  leftIcon,
  rightIcon,
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

  return (
    <div className="w-full">
      {label && (
        <label className="medical-label">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {leftIcon}
          </div>
        )}
        
        <input
          ref={ref}
          className={cn(
            inputVariantClasses[error ? 'error' : variant],
            leftIcon && 'pl-10',
            rightIcon && 'pr-10',
            className
          )}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {rightIcon}
          </div>
        )}
      </div>
      
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
});

Input.displayName = 'Input';

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
