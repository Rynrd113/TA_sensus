# backend/services/indikator_service.py
from datetime import date, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from backend.models.sensus import SensusHarian

def hitung_indikator_bulanan(
    data_bulanan: List[SensusHarian], 
    tt_total: int,
    periode_hari: int = 30
) -> Dict[str, float]:
    """
    Hitung indikator Kemenkes untuk periode bulanan
    
    Args:
        data_bulanan: List data sensus harian dalam 1 bulan
        tt_total: Total tempat tidur tersedia
        periode_hari: Jumlah hari dalam periode (default 30)
    
    Returns:
        Dict dengan LOS, BTO, TOI
    """
    if not data_bulanan:
        return {"los": 0.0, "bto": 0.0, "toi": 0.0}
    
    total_keluar = sum(d.jml_keluar for d in data_bulanan)
    total_hari_rawat = sum(d.jml_pasien_akhir for d in data_bulanan)  # Approx
    
    if total_keluar == 0:
        return {"los": 0.0, "bto": 0.0, "toi": 0.0}

    # LOS = Total hari rawat / Total pasien keluar
    # Untuk simulasi, kita gunakan estimasi: rata-rata occupancy * jumlah hari
    total_hari_rawat_estimasi = sum(d.jml_pasien_akhir for d in data_bulanan)
    los = round(total_hari_rawat_estimasi / total_keluar, 1)

    # BTO = Jumlah pasien keluar / (Jumlah TT tersedia / periode)
    bto = round(total_keluar / (tt_total / periode_hari), 1)

    # TOI = (Periode × TT - Total hari rawat) / Jumlah pasien keluar
    total_tt_hari = periode_hari * tt_total
    toi = round((total_tt_hari - total_hari_rawat_estimasi) / total_keluar, 1)

    return {
        "los": max(0.0, los),
        "bto": max(0.0, bto), 
        "toi": max(0.0, toi)
    }

def get_trend_bor(data: List[SensusHarian]) -> str:
    """Analisis trend BOR"""
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

def generate_peringatan(latest_data: SensusHarian, avg_bor: float) -> List[str]:
    """Generate peringatan berdasarkan standar Kemenkes"""
    peringatan = []
    
    # Standar BOR ideal: 60-85%
    if latest_data.bor > 90:
        peringatan.append("BOR > 90% - Kapasitas hampir penuh!")
    elif latest_data.bor < 60:
        peringatan.append("BOR < 60% - Pemanfaatan rendah")
    
    # LOS ideal: 6-9 hari
    if latest_data.los and latest_data.los > 9:
        peringatan.append("LOS > 9 hari - Lama rawat tinggi")
    
    # BTO ideal: 40-50 kali/tahun
    if latest_data.bto and latest_data.bto < 1:
        peringatan.append("BTO rendah - Efisiensi tempat tidur kurang")
    
    return peringatan
