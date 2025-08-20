// frontend/src/components/ui/baseComponents.tsx
/**
 * Base Components Library
 * Centralized component system untuk menerapkan DRY principle
 * Single source of truth untuk semua UI components
 */

import React from 'react';

// Base Props Interface untuk consistency
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
  'data-testid'?: string;
}

export interface BaseInputProps extends BaseComponentProps {
  id?: string;
  name?: string;
  value?: string | number;
  onChange?: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => void;
  disabled?: boolean;
  required?: boolean;
  placeholder?: string;
}

export interface BaseButtonProps extends BaseComponentProps {
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
}

// Theme constants untuk consistency
export const THEME_COLORS = {
  primary: 'bg-blue-600 hover:bg-blue-700 text-white',
  secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
  danger: 'bg-red-600 hover:bg-red-700 text-white',
  success: 'bg-green-600 hover:bg-green-700 text-white',
  warning: 'bg-yellow-600 hover:bg-yellow-700 text-white',
} as const;

export const THEME_SIZES = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
} as const;

export const COMMON_CLASSES = {
  input: 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
  card: 'bg-white rounded-lg shadow-md p-6',
  button: 'font-medium rounded-md transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2',
  alert: 'p-4 rounded-md border-l-4',
} as const;

// Utility functions
export const combineClasses = (...classes: (string | undefined)[]): string => {
  return classes.filter(Boolean).join(' ');
};

export const getButtonVariantClasses = (variant: BaseButtonProps['variant'] = 'primary'): string => {
  return THEME_COLORS[variant];
};

export const getButtonSizeClasses = (size: BaseButtonProps['size'] = 'md'): string => {
  return THEME_SIZES[size];
};

// Common validation states
export const VALIDATION_STATES = {
  default: '',
  error: 'border-red-500 focus:ring-red-500',
  success: 'border-green-500 focus:ring-green-500',
  warning: 'border-yellow-500 focus:ring-yellow-500',
} as const;

export type ValidationState = keyof typeof VALIDATION_STATES;

// Medical-specific theme (untuk context rumah sakit)
export const MEDICAL_THEME = {
  primary: 'bg-blue-600 hover:bg-blue-700', // Medical blue
  emergency: 'bg-red-600 hover:bg-red-700', // Emergency red
  success: 'bg-green-600 hover:bg-green-700', // Health green
  warning: 'bg-orange-500 hover:bg-orange-600', // Warning orange
  info: 'bg-cyan-500 hover:bg-cyan-600', // Info cyan
} as const;

// Medical icons mapping (dapat diperluas)
export const MEDICAL_ICONS = {
  patient: '👤',
  bed: '🛏️',
  hospital: '🏥',
  chart: '📊',
  report: '📋',
  calendar: '📅',
  warning: '⚠️',
  success: '✅',
  error: '❌',
  info: 'ℹ️',
} as const;

export default {
  THEME_COLORS,
  THEME_SIZES,
  COMMON_CLASSES,
  MEDICAL_THEME,
  MEDICAL_ICONS,
  combineClasses,
  getButtonVariantClasses,
  getButtonSizeClasses,
};
