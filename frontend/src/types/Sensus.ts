export interface SensusData {
  id?: number;
  tanggal: string;
  jumlah_tempat_tidur: number;
  tempat_tidur_terisi: number;
  pasien_masuk: number;
  pasien_keluar: number;
  lama_rawat_rata_rata: number;
  bangsal_id: number;
  created_at?: string;
  updated_at?: string;
}

export interface SensusCreate {
  tanggal: string;
  jumlah_tempat_tidur: number;
  tempat_tidur_terisi: number;
  pasien_masuk: number;
  pasien_keluar: number;
  lama_rawat_rata_rata: number;
  bangsal_id: number;
}

export interface SensusResponse {
  id: number;
  tanggal: string;
  jumlah_tempat_tidur: number;
  tempat_tidur_terisi: number;
  pasien_masuk: number;
  pasien_keluar: number;
  lama_rawat_rata_rata: number;
  bangsal_id: number;
  bangsal_nama?: string;
  created_at: string;
  updated_at: string;
  bor: number;
  bto: number;
  alos: number;
  toi: number;
}

export interface SensusFilter {
  tanggal_mulai?: string;
  tanggal_akhir?: string;
  bangsal_id?: number;
  limit?: number;
  offset?: number;
}

export interface SensusStats {
  total_sensus: number;
  rata_rata_bor: number;
  rata_rata_alos: number;
  total_pasien_masuk: number;
  total_pasien_keluar: number;
  trend_bor: 'naik' | 'turun' | 'stabil';
}
