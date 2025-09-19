# backend/utils/indikator_calculator.py
"""
Centralized Indikator Calculator
Implementasi DRY untuk perhitungan indikator Kemenkes dengan standar terpusat
"""
from typing import Dict, List, Optional
from datetime import date
from models.sensus import SensusHarian
from core.medical_standards import MedicalStandards


class IndikatorCalculator:
    """
    Kelas untuk menghitung semua indikator rawat inap sesuai standar Kemenkes
    Menerapkan prinsip DRY dan Single Responsibility dengan standardisasi medis
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
        # Improved: Consistent logic untuk LOS calculation
        if keluar > 0 and hari_rawat is not None:
            los = round(hari_rawat / keluar, 1)
        elif keluar > 0:
            # Estimate hari_rawat if not provided
            estimated_hari_rawat = (pasien_awal + masuk + keluar) // 2
            los = round(estimated_hari_rawat / keluar, 1)
        else:
            los = 0.0
        
        # BTO - Bed Turn Over (frekuensi pemakaian tempat tidur per hari)
        # Fixed: Konsisten dengan standar medis - normalize ke bulanan
        bto_harian = keluar / tt if tt > 0 else 0.0
        bto = round(bto_harian * 30, 1)  # Normalize to monthly rate
        
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
        Fixed: Consistent calculation logic
        
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
        # Fixed: Use hari_rawat if available, else estimate
        total_hari_rawat = sum(getattr(d, 'hari_rawat', 0) or d.jml_pasien_akhir for d in data_bulanan)
        
        if total_keluar == 0:
            return {"los": 0.0, "bto": 0.0, "toi": 0.0}
        
        # LOS = Total hari rawat / Total pasien keluar
        los = round(total_hari_rawat / total_keluar, 1)
        
        # BTO = Fixed formula - Total keluar per bulan / Total TT
        # Standardized with medical standards
        bto = round(total_keluar / tt_total * periode_hari, 1)
        
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
        """Generate peringatan berdasarkan standar medis terpusat"""
        peringatan = []
        
        # BOR evaluation dengan standard baru
        bor_eval = MedicalStandards.evaluate_bor(latest_data.bor)
        if bor_eval["status"] in ["critical", "critical_low", "warning"]:
            icon = "🚨" if bor_eval["level"] == "danger" else "⚠️"
            peringatan.append(f"{icon} {bor_eval['message']}")
        
        # LOS evaluation
        if latest_data.los:
            los_eval = MedicalStandards.evaluate_los(latest_data.los)
            if los_eval["status"] in ["critical", "critical_short", "warning"]:
                icon = "🚨" if los_eval["level"] == "danger" else "⚠️"
                peringatan.append(f"{icon} {los_eval['message']}")
        
        # BTO evaluation
        if latest_data.bto:
            bto_eval = MedicalStandards.evaluate_bto(latest_data.bto)
            if bto_eval["status"] in ["critical_low", "high", "low"]:
                icon = "🚨" if bto_eval["level"] == "danger" else "📊"
                peringatan.append(f"{icon} {bto_eval['message']}")
        
        return peringatan
    
    @staticmethod
    def get_medical_standards() -> dict:
        """Ambil semua medical standards untuk frontend"""
        return MedicalStandards.get_all_thresholds()


# Singleton pattern untuk konsistensi
indikator_calculator = IndikatorCalculator()
