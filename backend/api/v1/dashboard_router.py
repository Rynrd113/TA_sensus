# backend/api/v1/dashboard_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import date, timedelta

from database.session import get_db
from models.sensus import SensusHarian

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/periods")
def get_available_periods(db: Session = Depends(get_db)):
    """Get available data periods"""
    # Query untuk mendapatkan periode data yang tersedia
    periods = db.query(
        SensusHarian.tanggal
    ).distinct().order_by(SensusHarian.tanggal.desc()).all()
    
    if not periods:
        return {"periods": [], "latest": None, "earliest": None}
    
    dates = [p.tanggal for p in periods]
    latest = dates[0]
    earliest = dates[-1]
    
    # Group by month-year
    monthly_periods = {}
    for d in dates:
        key = f"{d.month:02d}/{d.year}"
        if key not in monthly_periods:
            monthly_periods[key] = {"month": d.month, "year": d.year, "count": 0}
        monthly_periods[key]["count"] += 1
    
    return {
        "periods": list(monthly_periods.values()),
        "latest": {"month": latest.month, "year": latest.year},
        "earliest": {"month": earliest.month, "year": earliest.year},
        "total_days": len(dates)
    }

@router.get("/stats")
def get_dashboard_stats(
    bulan: int = None,
    tahun: int = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Dashboard statistik dengan indikator bulanan"""
    
    # Set default values - gunakan periode terakhir yang tersedia jika tidak ada parameter
    if bulan is None or tahun is None:
        # Cari data terakhir yang tersedia
        latest_data = db.query(SensusHarian).order_by(SensusHarian.tanggal.desc()).first()
        if latest_data:
            bulan = latest_data.tanggal.month
            tahun = latest_data.tanggal.year
        else:
            # Fallback ke bulan sekarang jika tidak ada data sama sekali
            bulan = date.today().month if bulan is None else bulan
            tahun = date.today().year if tahun is None else tahun
    
    # Query data untuk bulan tertentu
    start_date = date(tahun, bulan, 1)
    if bulan == 12:
        end_date = date(tahun + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(tahun, bulan + 1, 1) - timedelta(days=1)
    
    data_bulanan = db.query(SensusHarian).filter(
        SensusHarian.tanggal >= start_date,
        SensusHarian.tanggal <= end_date
    ).order_by(SensusHarian.tanggal.desc()).all()
    
    if not data_bulanan:
        return {
            "stats": {
                "tanggal_terakhir": date.today().isoformat(),
                "total_pasien_hari_ini": 0,
                "bor_terkini": 0,
                "rata_rata_bor_bulanan": 0,
                "los_bulanan": 0,
                "bto_bulanan": 0,
                "toi_bulanan": 0,
                "tt_total": 0,
                "jumlah_hari_data": 0,
                "total_pasien_masuk": 0,
                "total_pasien_keluar": 0,
                "kapasitas_kosong": 0
            },
            "peringatan": ["Tidak ada data untuk periode ini"],
            "periode": f"{bulan:02d}/{tahun}",
            "trend_bor": "tidak_ada_data"
        }
    
    latest = data_bulanan[0]  # Data terbaru
    tt_total = latest.tempat_tidur_tersedia

    # Hitung indikator bulanan menggunakan service yang sama
    from services.indikator_service import hitung_indikator_bulanan
    
    total_pasien_keluar = sum(d.jml_keluar for d in data_bulanan)
    
    # Gunakan service yang sama untuk konsistensi
    indikator_bulanan = hitung_indikator_bulanan(data_bulanan, tt_total, len(data_bulanan))
    
    los_bulanan = indikator_bulanan["los"]
    bto_bulanan = indikator_bulanan["bto"] 
    toi_bulanan = indikator_bulanan["toi"]
    
    # Hitung rata-rata BOR untuk periode
    avg_bor = sum(d.bor for d in data_bulanan) / len(data_bulanan)
    
    # Generate peringatan
    peringatan = []
    if latest.bor > 90:
        peringatan.append("BOR > 90% - Kapasitas hampir penuh")
    if latest.bor < 60:
        peringatan.append("BOR < 60% - Utilisasi rendah")
    if los_bulanan > 9:
        peringatan.append("LOS > 9 hari - Lama rawat tinggi")
    if bto_bulanan < 1:
        peringatan.append("BTO rendah - Efisiensi tempat tidur kurang")
    
    # Tentukan trend BOR (sederhana - bandingkan 3 hari terakhir vs 3 hari sebelumnya)
    trend_bor = "stabil"
    if len(data_bulanan) >= 6:
        recent_bor = sum(d.bor for d in data_bulanan[:3]) / 3
        older_bor = sum(d.bor for d in data_bulanan[3:6]) / 3
        if recent_bor > older_bor + 2:
            trend_bor = "meningkat"
        elif recent_bor < older_bor - 2:
            trend_bor = "menurun"

    return {
        "stats": {
            "tanggal_terakhir": latest.tanggal.isoformat(),
            "total_pasien_hari_ini": latest.jml_pasien_akhir,
            "bor_terkini": round(latest.bor, 1),
            "rata_rata_bor_bulanan": round(avg_bor, 1),
            "los_bulanan": los_bulanan,
            "bto_bulanan": bto_bulanan,
            "toi_bulanan": toi_bulanan,
            "tt_total": tt_total,
            "jumlah_hari_data": len(data_bulanan),
            "total_pasien_masuk": sum(d.jml_masuk for d in data_bulanan),
            "total_pasien_keluar": sum(d.jml_keluar for d in data_bulanan),
            "kapasitas_kosong": tt_total - latest.jml_pasien_akhir
        },
        "peringatan": peringatan,
        "periode": f"{bulan:02d}/{tahun}",
        "trend_bor": trend_bor
    }

@router.get("/chart-data")
def get_chart_data(days: int = 30, db: Session = Depends(get_db)):
    """Data untuk grafik dashboard"""
    
    # Ambil data N hari terakhir
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    data = db.query(SensusHarian).filter(
        SensusHarian.tanggal >= start_date,
        SensusHarian.tanggal <= end_date
    ).order_by(SensusHarian.tanggal).all()

    chart_data = []
    for d in data:
        chart_data.append({
            "tanggal": d.tanggal.isoformat(),
            "bor": d.bor,
            "pasien_masuk": d.jml_masuk,
            "pasien_keluar": d.jml_keluar,
            "occupancy": d.jml_pasien_akhir,
            "kapasitas": d.tempat_tidur_tersedia
        })

    return {
        "periode": f"{start_date.isoformat()} to {end_date.isoformat()}",
        "data": chart_data,
        "summary": {
            "total_days": len(chart_data),
            "avg_bor": round(sum(d.bor for d in data) / len(data), 1) if data else 0,
            "max_bor": max(d.bor for d in data) if data else 0,
            "min_bor": min(d.bor for d in data) if data else 0
        }
    }
