export interface IndikatorRS {
  id?: number;
  tanggal: string;
  bor: number; // Bed Occupancy Rate
  bto: number; // Bed Turn Over
  alos: number; // Average Length of Stay
  toi: number; // Turn Over Interval
  bangsal_id: number;
  bangsal_nama?: string;
  created_at?: string;
  updated_at?: string;
}

export interface IndikatorTrend {
  tanggal: string;
  bor: number;
  bto: number;
  alos: number;
  toi: number;
}

export interface IndikatorStats {
  current_month: {
    bor: number;
    bto: number;
    alos: number;
    toi: number;
  };
  previous_month: {
    bor: number;
    bto: number;
    alos: number;
    toi: number;
  };
  trends: IndikatorTrend[];
}

export interface IndikatorFilter {
  tanggal_mulai?: string;
  tanggal_akhir?: string;
  bangsal_id?: number;
}
