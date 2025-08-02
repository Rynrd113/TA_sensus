// Perhitungan indikator rumah sakit

// BOR (Bed Occupancy Rate) - Tingkat hunian tempat tidur
export const calculateBOR = (
  tempatTidurTerisi: number,
  jumlahTempatTidur: number
): number => {
  if (jumlahTempatTidur === 0) return 0;
  return (tempatTidurTerisi / jumlahTempatTidur) * 100;
};

// BTO (Bed Turn Over) - Frekuensi pemakaian tempat tidur
export const calculateBTO = (
  pasienKeluar: number,
  jumlahTempatTidur: number,
  jumlahHari: number = 30
): number => {
  if (jumlahTempatTidur === 0) return 0;
  return (pasienKeluar * jumlahHari) / jumlahTempatTidur;
};

// ALOS (Average Length of Stay) - Rata-rata lama rawat
export const calculateALOS = (
  totalHariRawat: number,
  pasienKeluar: number
): number => {
  if (pasienKeluar === 0) return 0;
  return totalHariRawat / pasienKeluar;
};

// TOI (Turn Over Interval) - Tenggang perputaran
export const calculateTOI = (
  jumlahTempatTidur: number,
  tempatTidurTerisi: number,
  pasienKeluar: number,
  jumlahHari: number = 30
): number => {
  if (pasienKeluar === 0) return 0;
  const tempatTidurKosong = jumlahTempatTidur - tempatTidurTerisi;
  return (tempatTidurKosong * jumlahHari) / pasienKeluar;
};

// NDR (Net Death Rate) - Angka kematian bersih
export const calculateNDR = (
  pasienMeninggal: number,
  pasienKeluar: number
): number => {
  if (pasienKeluar === 0) return 0;
  return (pasienMeninggal / pasienKeluar) * 100;
};

// GDR (Gross Death Rate) - Angka kematian kasar
export const calculateGDR = (
  pasienMeninggal: number,
  pasienKeluarHidup: number,
  pasienMeninggalKurang48Jam: number
): number => {
  const totalPasienKeluar = pasienKeluarHidup + pasienMeninggal;
  if (totalPasienKeluar === 0) return 0;
  return ((pasienMeninggal + pasienMeninggalKurang48Jam) / totalPasienKeluar) * 100;
};

// Fungsi untuk menentukan status indikator berdasarkan standar nasional
export const getBORStatus = (bor: number): 'normal' | 'warning' | 'critical' => {
  if (bor >= 60 && bor <= 85) return 'normal';
  if (bor > 85 && bor < 95) return 'warning';
  return 'critical';
};

export const getALOSStatus = (alos: number): 'normal' | 'warning' | 'critical' => {
  if (alos >= 3 && alos <= 12) return 'normal';
  if (alos > 12 && alos <= 15) return 'warning';
  return 'critical';
};

export const getBTOStatus = (bto: number): 'normal' | 'warning' | 'critical' => {
  if (bto >= 40 && bto <= 50) return 'normal';
  if (bto >= 30 && bto < 40) return 'warning';
  return 'critical';
};

export const getTOIStatus = (toi: number): 'normal' | 'warning' | 'critical' => {
  if (toi >= 1 && toi <= 3) return 'normal';
  if (toi > 3 && toi <= 5) return 'warning';
  return 'critical';
};

// Fungsi untuk menghitung trend (naik, turun, stabil)
export const calculateTrend = (
  currentValue: number,
  previousValue: number,
  threshold: number = 5
): 'naik' | 'turun' | 'stabil' => {
  const difference = currentValue - previousValue;
  const percentageChange = (Math.abs(difference) / previousValue) * 100;
  
  if (percentageChange < threshold) return 'stabil';
  return difference > 0 ? 'naik' : 'turun';
};

// Fungsi untuk menghitung persentase perubahan
export const calculatePercentageChange = (
  currentValue: number,
  previousValue: number
): number => {
  if (previousValue === 0) return 0;
  return ((currentValue - previousValue) / previousValue) * 100;
};

// Fungsi untuk mendapatkan rekomendasi berdasarkan indikator
export const getBORRecommendation = (bor: number): string => {
  if (bor < 60) {
    return 'BOR rendah. Tingkatkan pemasaran dan kerjasama rujukan.';
  } else if (bor > 85) {
    return 'BOR tinggi. Pertimbangkan penambahan kapasitas atau optimalisasi discharge planning.';
  }
  return 'BOR dalam batas normal. Pertahankan kualitas pelayanan.';
};

export const getALOSRecommendation = (alos: number): string => {
  if (alos > 12) {
    return 'ALOS tinggi. Evaluasi protokol clinical pathway dan discharge planning.';
  } else if (alos < 3) {
    return 'ALOS rendah. Pastikan kualitas pelayanan tetap optimal.';
  }
  return 'ALOS dalam batas normal. Pertahankan efisiensi pelayanan.';
};

// Fungsi untuk memvalidasi data sensus
export const validateSensusData = (data: any): string[] => {
  const errors: string[] = [];
  
  if (!data.tanggal) {
    errors.push('Tanggal harus diisi');
  }
  
  if (data.jumlah_tempat_tidur <= 0) {
    errors.push('Jumlah tempat tidur harus lebih dari 0');
  }
  
  if (data.tempat_tidur_terisi < 0) {
    errors.push('Tempat tidur terisi tidak boleh negatif');
  }
  
  if (data.tempat_tidur_terisi > data.jumlah_tempat_tidur) {
    errors.push('Tempat tidur terisi tidak boleh melebihi kapasitas');
  }
  
  if (data.pasien_masuk < 0) {
    errors.push('Pasien masuk tidak boleh negatif');
  }
  
  if (data.pasien_keluar < 0) {
    errors.push('Pasien keluar tidak boleh negatif');
  }
  
  if (data.lama_rawat_rata_rata < 0) {
    errors.push('Lama rawat rata-rata tidak boleh negatif');
  }
  
  return errors;
};
