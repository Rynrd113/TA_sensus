export interface PrediksiRequest {
  days: number; // Jumlah hari prediksi
  bangsal_id?: number;
  indikator: 'bor' | 'bto' | 'alos' | 'toi';
}

export interface PrediksiResult {
  tanggal: string;
  prediksi_nilai: number;
  confidence_interval_lower: number;
  confidence_interval_upper: number;
  indikator: string;
}

export interface PrediksiResponse {
  indikator: string;
  model_accuracy: number;
  predictions: PrediksiResult[];
  generated_at: string;
  bangsal_id?: number;
  bangsal_nama?: string;
}

export interface PrediksiSummary {
  indikator: string;
  hari_ke_depan: number;
  nilai_prediksi: number;
  status: 'normal' | 'warning' | 'critical';
  rekomendasi: string;
  confidence: number;
}

export interface PrediksiDashboard {
  bor_prediksi: PrediksiSummary[];
  alos_prediksi: PrediksiSummary[];
  tren_minggu_depan: {
    tanggal: string;
    bor: number;
    alos: number;
  }[];
  rekomendasi_umum: string[];
}
