export interface Bangsal {
  id: number;
  nama: string;
  kapasitas: number;
  tipe: 'umum' | 'vip' | 'icu' | 'isolasi';
  status: 'aktif' | 'nonaktif';
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  data: T;
  message: string;
  status: 'success' | 'error';
  pagination?: {
    total: number;
    page: number;
    limit: number;
    total_pages: number;
  };
}

export interface LoadingState {
  loading: boolean;
  error: string | null;
}

export interface ChartData {
  tanggal: string;
  [key: string]: string | number;
}

export interface StatCardProps {
  title: string;
  value: number | string;
  unit?: string;
  icon?: React.ReactNode;
  variant?: 'normal' | 'warning' | 'critical' | 'success';
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'stable';
  };
  loading?: boolean;
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'select';
  required?: boolean;
  placeholder?: string;
  options?: { value: string | number; label: string }[];
  min?: number;
  max?: number;
  validation?: (value: any) => string | null;
}
