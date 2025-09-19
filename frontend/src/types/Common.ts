export interface Bangsal {
  id: number;
  kode_bangsal: string;
  nama_bangsal: string;
  departemen: string;
  jenis_bangsal: 'Kelas I' | 'Kelas II' | 'Kelas III' | 'VIP' | 'VVIP' | 'ICU' | 'NICU' | 'PICU' | 'HCU' | 'Isolasi' | 'Emergency';
  lantai: number;
  kapasitas_total: number;
  jumlah_terisi: number;
  jumlah_tersedia: number;
  occupancy_rate: number;
  lokasi_detail?: string;
  pic_bangsal?: string;
  kontak_pic?: string;
  fasilitas?: string;
  status_operasional: 'Aktif' | 'Maintenance' | 'Tutup Sementara' | 'Renovasi';
  keterangan?: string;
  is_emergency_ready: boolean;
  created_at: string;
  updated_at: string;
  rooms?: KamarBangsal[];
}

export interface KamarBangsal {
  id: number;
  bangsal_id: number;
  nomor_kamar: string;
  jenis_kamar: 'Single' | 'Double' | 'Multi' | 'Suite' | 'ICU' | 'Isolasi';
  kapasitas_kamar: number;
  jumlah_terisi: number;
  is_available: boolean;
  tarif_per_hari?: number;
  fasilitas_kamar?: string;
  status_kebersihan: 'Bersih' | 'Kotor' | 'Maintenance';
  keterangan?: string;
  created_at: string;
  updated_at: string;
}

export interface BangsalStats {
  total_bangsal: number;
  total_capacity: number;
  total_occupied: number;
  total_available: number;
  occupancy_rate: number;
  by_department: { [key: string]: any };
  by_type: { [key: string]: any };
  emergency_ready_count: number;
}

export interface BangsalFilter {
  departemen?: string;
  jenis_bangsal?: string;
  lantai?: number;
  status_operasional?: string;
  is_emergency_ready?: boolean;
  min_capacity?: number;
  max_capacity?: number;
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
