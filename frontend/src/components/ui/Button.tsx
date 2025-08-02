import React, { forwardRef } from 'react';
import { cn } from '../../utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'ghost';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  children,
  className,
  disabled,
  ...props
}, ref) => {
  const isDisabled = disabled || loading;

  // Modern medical button styling using CSS classes
  const variantClasses = {
    primary: 'medical-btn-primary',
    secondary: 'medical-btn-secondary',
    success: 'medical-btn-success',
    warning: 'medical-btn-warning',
    danger: 'medical-btn-danger',
    ghost: 'medical-btn-ghost'
  };

  const sizeClasses = {
    xs: 'medical-btn-xs',
    sm: 'medical-btn-sm',
    md: 'medical-btn-md',
    lg: 'medical-btn-lg',
    xl: 'medical-btn-xl'
  };

  // Loading spinner component
  const LoadingSpinner = () => (
    <div className="medical-spinner" />
  );

  const renderIcon = () => {
    if (loading) return <LoadingSpinner />;
    if (icon) return <span className="medical-icon-sm">{icon}</span>;
    return null;
  };

  return (
    <button
      ref={ref}
      className={cn(
        'medical-btn',
        variantClasses[variant],
        sizeClasses[size],
        fullWidth && 'w-full',
        className
      )}
      disabled={isDisabled}
      {...props}
    >
      {iconPosition === 'left' && renderIcon()}
      {children}
      {iconPosition === 'right' && renderIcon()}
    </button>
  );
});

Button.displayName = 'Button';

export default Button;
