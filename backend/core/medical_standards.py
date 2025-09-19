# backend/core/medical_standards.py
"""
Standar medis terpusat untuk indikator rumah sakit
Berdasarkan standar Kemenkes RI dan best practices internasional
"""

class MedicalStandards:
    """Konstanta standar medis untuk indikator rumah sakit"""
    
    # BOR (Bed Occupancy Rate) Standards
    BOR_OPTIMAL_MIN = 60.0      # Minimum optimal BOR (%)
    BOR_OPTIMAL_MAX = 85.0      # Maximum optimal BOR (%)  
    BOR_CRITICAL_HIGH = 90.0    # Critical high threshold (%)
    BOR_WARNING_LOW = 50.0      # Warning low threshold (%)
    
    # LOS (Length of Stay) Standards  
    LOS_OPTIMAL_MIN = 6.0       # Minimum optimal LOS (days)
    LOS_OPTIMAL_MAX = 9.0       # Maximum optimal LOS (days)
    LOS_CRITICAL_HIGH = 12.0    # Critical high threshold (days)
    LOS_WARNING_LOW = 3.0       # Warning low threshold (days)
    
    # BTO (Bed Turnover) Standards
    BTO_OPTIMAL_MIN = 40.0      # Minimum optimal BTO (times/month)
    BTO_OPTIMAL_MAX = 50.0      # Maximum optimal BTO (times/month)
    BTO_CRITICAL_LOW = 30.0     # Critical low threshold
    BTO_WARNING_HIGH = 60.0     # Warning high threshold
    
    # TOI (Turn Over Interval) Standards  
    TOI_OPTIMAL_MIN = 1.0       # Minimum optimal TOI (days)
    TOI_OPTIMAL_MAX = 3.0       # Maximum optimal TOI (days)
    TOI_CRITICAL_HIGH = 5.0     # Critical high threshold (days)
    TOI_WARNING_LOW = 0.5       # Warning very low threshold
    
    @classmethod
    def evaluate_bor(cls, bor_value: float) -> dict:
        """Evaluasi status BOR berdasarkan standar medis"""
        if bor_value >= cls.BOR_CRITICAL_HIGH:
            return {
                "status": "critical", 
                "level": "danger",
                "message": f"BOR {bor_value:.1f}% sangat tinggi - Risiko overkapasitas",
                "recommendation": "Tambah kapasitas atau percepat discharge"
            }
        elif bor_value > cls.BOR_OPTIMAL_MAX:
            return {
                "status": "warning", 
                "level": "warning",
                "message": f"BOR {bor_value:.1f}% di atas optimal",
                "recommendation": "Monitor kapasitas dan siapkan rencana darurat"
            }
        elif bor_value >= cls.BOR_OPTIMAL_MIN:
            return {
                "status": "optimal", 
                "level": "success",
                "message": f"BOR {bor_value:.1f}% dalam rentang optimal",
                "recommendation": "Pertahankan tingkat utilisasi ini"
            }
        elif bor_value >= cls.BOR_WARNING_LOW:
            return {
                "status": "low", 
                "level": "info",
                "message": f"BOR {bor_value:.1f}% rendah",
                "recommendation": "Evaluasi strategi pemasaran/rujukan"
            }
        else:
            return {
                "status": "critical_low", 
                "level": "danger",
                "message": f"BOR {bor_value:.1f}% sangat rendah - Under-utilisasi",
                "recommendation": "Review strategi operasional dan marketing"
            }
    
    @classmethod 
    def evaluate_los(cls, los_value: float) -> dict:
        """Evaluasi status LOS berdasarkan standar medis"""
        if los_value >= cls.LOS_CRITICAL_HIGH:
            return {
                "status": "critical", 
                "level": "danger",
                "message": f"LOS {los_value:.1f} hari terlalu panjang",
                "recommendation": "Review protokol discharge dan case management"
            }
        elif los_value > cls.LOS_OPTIMAL_MAX:
            return {
                "status": "warning", 
                "level": "warning", 
                "message": f"LOS {los_value:.1f} hari di atas optimal",
                "recommendation": "Evaluasi efisiensi perawatan"
            }
        elif los_value >= cls.LOS_OPTIMAL_MIN:
            return {
                "status": "optimal", 
                "level": "success",
                "message": f"LOS {los_value:.1f} hari dalam rentang optimal",
                "recommendation": "Pertahankan kualitas perawatan"
            }
        elif los_value >= cls.LOS_WARNING_LOW:
            return {
                "status": "short", 
                "level": "info",
                "message": f"LOS {los_value:.1f} hari pendek",
                "recommendation": "Monitor kualitas outcome pasien"
            }
        else:
            return {
                "status": "critical_short", 
                "level": "warning",
                "message": f"LOS {los_value:.1f} hari sangat pendek",
                "recommendation": "Pastikan tidak ada discharge terlalu dini"
            }
    
    @classmethod
    def evaluate_bto(cls, bto_value: float) -> dict:
        """Evaluasi status BTO berdasarkan standar medis"""
        if bto_value >= cls.BTO_WARNING_HIGH:
            return {
                "status": "high", 
                "level": "warning",
                "message": f"BTO {bto_value:.1f} sangat tinggi",
                "recommendation": "Evaluasi kualitas perawatan dan patient satisfaction"
            }
        elif bto_value >= cls.BTO_OPTIMAL_MIN:
            return {
                "status": "optimal", 
                "level": "success",
                "message": f"BTO {bto_value:.1f} dalam rentang optimal",
                "recommendation": "Pertahankan efisiensi turnover"
            }
        elif bto_value >= cls.BTO_CRITICAL_LOW:
            return {
                "status": "low", 
                "level": "info",
                "message": f"BTO {bto_value:.1f} rendah",
                "recommendation": "Evaluasi strategi admission dan discharge"
            }
        else:
            return {
                "status": "critical_low", 
                "level": "danger",
                "message": f"BTO {bto_value:.1f} sangat rendah",
                "recommendation": "Review komprehensif proses operasional"
            }
    
    @classmethod
    def get_all_thresholds(cls) -> dict:
        """Ambil semua threshold untuk export ke frontend"""
        return {
            "BOR": {
                "optimal_min": cls.BOR_OPTIMAL_MIN,
                "optimal_max": cls.BOR_OPTIMAL_MAX,
                "critical_high": cls.BOR_CRITICAL_HIGH,
                "warning_low": cls.BOR_WARNING_LOW
            },
            "LOS": {
                "optimal_min": cls.LOS_OPTIMAL_MIN,
                "optimal_max": cls.LOS_OPTIMAL_MAX,
                "critical_high": cls.LOS_CRITICAL_HIGH,
                "warning_low": cls.LOS_WARNING_LOW
            },
            "BTO": {
                "optimal_min": cls.BTO_OPTIMAL_MIN,
                "optimal_max": cls.BTO_OPTIMAL_MAX,
                "critical_low": cls.BTO_CRITICAL_LOW,
                "warning_high": cls.BTO_WARNING_HIGH
            },
            "TOI": {
                "optimal_min": cls.TOI_OPTIMAL_MIN,
                "optimal_max": cls.TOI_OPTIMAL_MAX,
                "critical_high": cls.TOI_CRITICAL_HIGH,
                "warning_low": cls.TOI_WARNING_LOW
            }
        }