import dayjs from 'dayjs';
import 'dayjs/locale/id';
import relativeTime from 'dayjs/plugin/relativeTime';

// Set locale to Indonesian and add plugins
dayjs.locale('id');
dayjs.extend(relativeTime);

// Format number dengan separator ribuan
export const formatNumber = (value: number | string, decimals: number = 0): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(num)) return '0';
  
  return new Intl.NumberFormat('id-ID', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
};

// Format number sebagai persentase
export const formatPercentage = (value: number | string, decimals: number = 1): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(num)) return '0%';
  
  return `${formatNumber(num, decimals)}%`;
};

// Format currency (Rupiah)
export const formatCurrency = (value: number | string): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(num)) return 'Rp 0';
  
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
};

// Format date dengan berbagai format
export const formatDate = (
  date: string | Date, 
  format: string = 'DD MMMM YYYY'
): string => {
  if (!date) return '';
  
  return dayjs(date).format(format);
};

// Format date untuk input date HTML
export const formatDateForInput = (date: string | Date): string => {
  if (!date) return '';
  
  return dayjs(date).format('YYYY-MM-DD');
};

// Format relative time (misal: "2 hari yang lalu")
export const formatRelativeTime = (date: string | Date): string => {
  if (!date) return '';
  
  return dayjs(date).fromNow();
};

// Format jam
export const formatTime = (date: string | Date): string => {
  if (!date) return '';
  
  return dayjs(date).format('HH:mm');
};

// Format datetime lengkap
export const formatDateTime = (date: string | Date): string => {
  if (!date) return '';
  
  return dayjs(date).format('DD MMMM YYYY, HH:mm');
};

// Get date range (untuk filter)
export const getDateRange = (days: number): { start: string; end: string } => {
  const end = dayjs();
  const start = end.subtract(days, 'day');
  
  return {
    start: start.format('YYYY-MM-DD'),
    end: end.format('YYYY-MM-DD')
  };
};

// Get current month range
export const getCurrentMonthRange = (): { start: string; end: string } => {
  const start = dayjs().startOf('month');
  const end = dayjs().endOf('month');
  
  return {
    start: start.format('YYYY-MM-DD'),
    end: end.format('YYYY-MM-DD')
  };
};

// Validate date string
export const isValidDate = (dateString: string): boolean => {
  return dayjs(dateString).isValid();
};

// Format file size
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Truncate text
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  
  return text.substring(0, maxLength) + '...';
};

// Generate initials from name
export const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase())
    .join('')
    .substring(0, 2);
};
