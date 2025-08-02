# backend/services/dashboard_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from backend.models.sensus import SensusHarian
from datetime import datetime, date
from typing import Dict, List, Any

def get_dashboard_stats(db: Session, bulan: int = None, tahun: int = None) -> Dict[str, Any]:
    """
    Hitung statistik dashboard untuk bulan dan tahun tertentu
    """
    if bulan is None:
        bulan = datetime.now().month
    if tahun is None:
        tahun = datetime.now().year
    
    # Query data bulan tersebut
    data_bulan = db.query(SensusHarian).filter(
        and_(
            extract('month', SensusHarian.tanggal) == bulan,
            extract('year', SensusHarian.tanggal) == tahun
        )
    ).order_by(SensusHarian.tanggal.desc()).all()
    
    if not data_bulan:
        return {
            "error": f"Tidak ada data untuk bulan {bulan}/{tahun}",
            "stats": {},
            "peringatan": [],
            "periode": f"{bulan:02d}/{tahun}",
            "trend_bor": "tidak_ada_data"
        }
    
    # Data terakhir
    data_terakhir = data_bulan[0]
    tt_total = data_terakhir.tempat_tidur_tersedia
    
    # Hitung statistik dasar
    jumlah_hari_data = len(data_bulan)
    total_pasien_masuk = sum(d.jml_masuk for d in data_bulan)
    total_pasien_keluar = sum(d.jml_keluar for d in data_bulan)
    
    # BOR rata-rata
    rata_rata_bor = sum(d.bor for d in data_bulan) / jumlah_hari_data
    
    # Hitung indikator menggunakan service yang sama untuk konsistensi
    from backend.services.indikator_service import hitung_indikator_bulanan
    
    # Gunakan service indikator yang sudah standar
    indikator_bulanan = hitung_indikator_bulanan(data_bulan, tt_total, jumlah_hari_data)
    
    los_bulanan = indikator_bulanan["los"]
    bto_bulanan = indikator_bulanan["bto"]
    toi_bulanan = indikator_bulanan["toi"]
    
    # Kapasitas kosong saat ini
    kapasitas_kosong = tt_total - data_terakhir.jml_pasien_akhir
    
    # Trend BOR (butuh minimal 7 hari data)
    trend_bor = "tidak_cukup_data"
    if jumlah_hari_data >= 7:
        bor_7_hari_terakhir = [d.bor for d in data_bulan[:7]]
        bor_awal = sum(bor_7_hari_terakhir[4:]) / 3  # 3 hari tengah
        bor_akhir = sum(bor_7_hari_terakhir[:3]) / 3  # 3 hari terakhir
        
        if bor_akhir > bor_awal + 2:
            trend_bor = "meningkat"
        elif bor_akhir < bor_awal - 2:
            trend_bor = "menurun"
        else:
            trend_bor = "stabil"
    
    # Peringatan
    peringatan = []
    if data_terakhir.bor >= 95:
        peringatan.append("BOR sangat tinggi > 95% - Rumah sakit penuh!")
    elif data_terakhir.bor >= 90:
        peringatan.append("BOR tinggi > 90% - Perlu perhatian")
    
    if kapasitas_kosong <= 3:
        peringatan.append("Kapasitas kosong sangat terbatas <= 3 tempat tidur")
    elif kapasitas_kosong <= 5:
        peringatan.append("Kapasitas kosong terbatas <= 5 tempat tidur")
    
    if los_bulanan > 10:
        peringatan.append("LOS terlalu tinggi > 10 hari - Efisiensi rendah")
    elif los_bulanan < 3:
        peringatan.append("LOS terlalu rendah < 3 hari - Mungkin ada masalah koding")
    
    if bto_bulanan < 15:  # BTO bulanan, bukan tahunan
        peringatan.append("BTO rendah - Efisiensi tempat tidur kurang")
    
    if toi_bulanan > 3:
        peringatan.append("TOI tinggi > 3 hari - Tempat tidur sering kosong")
    
    stats = {
        "tanggal_terakhir": data_terakhir.tanggal.strftime("%Y-%m-%d"),
        "total_pasien_hari_ini": data_terakhir.jml_pasien_akhir,
        "bor_terkini": round(data_terakhir.bor, 1),
        "rata_rata_bor_bulanan": round(rata_rata_bor, 1),
        "los_bulanan": round(los_bulanan, 1),
        "bto_bulanan": round(bto_bulanan, 1),
        "toi_bulanan": round(toi_bulanan, 1),
        "tt_total": tt_total,
        "jumlah_hari_data": jumlah_hari_data,
        "total_pasien_masuk": total_pasien_masuk,
        "total_pasien_keluar": total_pasien_keluar,
        "kapasitas_kosong": kapasitas_kosong
    }
    
    return {
        "stats": stats,
        "peringatan": peringatan,
        "periode": f"{bulan:02d}/{tahun}",
        "trend_bor": trend_bor
    }
