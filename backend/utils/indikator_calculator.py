# backend/utils/indikator_calculator.py
"""
Centralized Indikator Calculator
Implementasi DRY untuk perhitungan indikator Kemenkes
"""
from typing import Dict, List, Optional
from datetime import date
from models.sensus import SensusHarian


class IndikatorCalculator:
    """
    Kelas untuk menghitung semua indikator rawat inap sesuai standar Kemenkes
    Menerapkan prinsip DRY dan Single Responsibility
    """
    
    @staticmethod
    def hitung_indikator_harian(
        pasien_awal: int,
        masuk: int,
        keluar: int,
        tt: int,
        hari_rawat: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Hitung indikator harian (untuk data sensus per hari)
        
        Args:
            pasien_awal: Jumlah pasien awal hari
            masuk: Jumlah pasien masuk
            keluar: Jumlah pasien keluar
            tt: Total tempat tidur tersedia
            hari_rawat: Total hari rawat (optional)
        
        Returns:
            Dict dengan pasien_akhir, bor, los, bto, toi
        """
        if tt <= 0:
            return {
                "pasien_akhir": 0,
                "bor": 0.0,
                "los": 0.0,
                "bto": 0.0,
                "toi": 0.0
            }
        
        pasien_akhir = pasien_awal + masuk - keluar
        
        # BOR - Bed Occupancy Rate
        bor = round((pasien_akhir / tt) * 100, 1)
        
        # LOS - Length of Stay (rata-rata lama dirawat)
        los = round(hari_rawat / keluar, 1) if keluar > 0 and hari_rawat else 0.0
        
        # BTO - Bed Turn Over (frekuensi pemakaian tempat tidur)
        bto = round(keluar / tt, 1)
        
        # TOI - Turn Over Interval (rata-rata hari kosong tempat tidur)
        tt_kosong = max(0, tt - pasien_akhir)
        toi = round(tt_kosong / keluar, 1) if keluar > 0 else 0.0
        
        return {
            "pasien_akhir": pasien_akhir,
            "bor": max(0.0, min(100.0, bor)),  # Batas BOR 0-100%
            "los": max(0.0, los),
            "bto": max(0.0, bto),
            "toi": max(0.0, toi)
        }
    
    @staticmethod
    def hitung_indikator_bulanan(
        data_bulanan: List[SensusHarian],
        tt_total: int,
        periode_hari: int = 30
    ) -> Dict[str, float]:
        """
        Hitung indikator bulanan (aggregasi dari data harian)
        
        Args:
            data_bulanan: List data sensus harian dalam 1 bulan
            tt_total: Total tempat tidur tersedia
            periode_hari: Jumlah hari dalam periode
        
        Returns:
            Dict dengan los, bto, toi bulanan
        """
        if not data_bulanan or tt_total <= 0:
            return {"los": 0.0, "bto": 0.0, "toi": 0.0}
        
        total_keluar = sum(d.jml_keluar for d in data_bulanan)
        total_hari_rawat = sum(d.jml_pasien_akhir for d in data_bulanan)
        
        if total_keluar == 0:
            return {"los": 0.0, "bto": 0.0, "toi": 0.0}
        
        # LOS = Total hari rawat / Total pasien keluar
        los = round(total_hari_rawat / total_keluar, 1)
        
        # BTO = Jumlah pasien keluar / (Jumlah TT tersedia / periode)
        bto = round(total_keluar / (tt_total / periode_hari), 1)
        
        # TOI = (Periode × TT - Total hari rawat) / Jumlah pasien keluar
        total_tt_hari = periode_hari * tt_total
        toi = round((total_tt_hari - total_hari_rawat) / total_keluar, 1)
        
        return {
            "los": max(0.0, los),
            "bto": max(0.0, bto),
            "toi": max(0.0, toi)
        }
    
    @staticmethod
    def get_trend_bor(data: List[SensusHarian]) -> str:
        """Analisis trend BOR untuk memberikan insight"""
        if len(data) < 2:
            return "stabil"
        
        recent_bor = [d.bor for d in data[-7:]]  # 7 hari terakhir
        earlier_bor = [d.bor for d in data[-14:-7]]  # 7 hari sebelumnya
        
        if not earlier_bor:
            return "stabil"
        
        avg_recent = sum(recent_bor) / len(recent_bor)
        avg_earlier = sum(earlier_bor) / len(earlier_bor)
        
        if avg_recent > avg_earlier + 2:
            return "meningkat"
        elif avg_recent < avg_earlier - 2:
            return "menurun"
        else:
            return "stabil"
    
    @staticmethod
    def generate_peringatan(latest_data: SensusHarian, avg_bor: float) -> List[str]:
        """Generate peringatan berdasarkan standar Kemenkes"""
        peringatan = []
        
        # Standar BOR ideal: 60-85%
        if latest_data.bor > 90:
            peringatan.append("🚨 BOR > 90% - Kapasitas hampir penuh!")
        elif latest_data.bor < 60:
            peringatan.append("⚠️ BOR < 60% - Pemanfaatan rendah")
        
        # LOS ideal: 6-9 hari
        if latest_data.los and latest_data.los > 9:
            peringatan.append("📊 LOS > 9 hari - Lama rawat tinggi")
        elif latest_data.los and latest_data.los < 3:
            peringatan.append("⚡ LOS < 3 hari - Turnover sangat cepat")
        
        # BTO ideal: 40-50 kali/tahun (1-1.5 per hari)
        if latest_data.bto and latest_data.bto < 1:
            peringatan.append("📉 BTO rendah - Efisiensi tempat tidur kurang")
        elif latest_data.bto and latest_data.bto > 2:
            peringatan.append("📈 BTO tinggi - Turnover sangat aktif")
        
        return peringatan


# Singleton pattern untuk konsistensi
indikator_calculator = IndikatorCalculator()
