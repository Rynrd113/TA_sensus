# backend/api/v1/indikator_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from typing import Dict, Any

from database.session import get_db
from models.sensus import SensusHarian
from services.indikator_service import hitung_indikator_bulanan

router = APIRouter(prefix="/indikator", tags=["indikator"])

@router.get("/bulanan")
def get_indikator_bulanan(
    bulan: int = date.today().month,
    tahun: int = date.today().year,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Hitung indikator Kemenkes untuk periode bulanan"""
    
    # Ambil data bulanan
    start_date = date(tahun, bulan, 1)
    if bulan == 12:
        end_date = date(tahun + 1, 1, 1)
    else:
        end_date = date(tahun, bulan + 1, 1)

    data_bulanan = db.query(SensusHarian)\
                     .filter(SensusHarian.tanggal >= start_date, SensusHarian.tanggal < end_date)\
                     .order_by(SensusHarian.tanggal)\
                     .all()
    
    if not data_bulanan:
        return {
            "error": f"Tidak ada data untuk {bulan:02d}/{tahun}",
            "indikator": {"los": 0.0, "bto": 0.0, "toi": 0.0}
        }
    
    # Ambil TT dari data terakhir
    tt_total = data_bulanan[-1].tempat_tidur_tersedia
    
    # Hitung indikator
    indikator = hitung_indikator_bulanan(data_bulanan, tt_total, len(data_bulanan))
    
    return {
        "periode": f"{bulan:02d}/{tahun}",
        "jumlah_hari_data": len(data_bulanan),
        "tempat_tidur_tersedia": tt_total,
        "total_pasien_masuk": sum(d.jml_masuk for d in data_bulanan),
        "total_pasien_keluar": sum(d.jml_keluar for d in data_bulanan),
        "rata_rata_bor": round(sum(d.bor for d in data_bulanan) / len(data_bulanan), 1),
        "indikator": indikator,
        "keterangan": {
            "los": "Length of Stay - Rata-rata lama dirawat (hari)",
            "bto": "Bed Turn Over - Frekuensi pemakaian tempat tidur",
            "toi": "Turn Over Interval - Rata-rata hari kosong tempat tidur"
        }
    }
