# backend/api/v1/sensus_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from backend.database.session import get_db
from backend.models.sensus import Base, SensusHarian
from backend.database.engine import engine
from backend.schemas.sensus import SensusCreate, SensusResponse, SensusStats
from backend.core.logging_config import log_sensus_activity, log_error

# Buat tabel jika belum ada
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/sensus", tags=["sensus"])

# Fungsi hitung indikator (Standar Kemenkes)
def hitung_indikator(
    pasien_awal: int, 
    masuk: int, 
    keluar: int, 
    tt: int,
    hari_rawat: int = None  # untuk LOS
) -> dict:
    """Hitung semua indikator rawat inap sesuai standar Kemenkes"""
    pasien_akhir = pasien_awal + masuk - keluar
    
    # BOR - Bed Occupancy Rate
    bor = round((pasien_akhir / tt) * 100, 1) if tt > 0 else 0.0
    
    # LOS - Length of Stay (rata-rata lama dirawat)
    # Rumus: Total hari rawat / Jumlah pasien keluar
    los = round(hari_rawat / keluar, 1) if keluar > 0 and hari_rawat else 0.0
    
    # BTO - Bed Turn Over (frekuensi pemakaian tempat tidur)
    # Rumus: Jumlah pasien keluar / Jumlah tempat tidur tersedia
    bto = round(keluar / tt, 1) if tt > 0 else 0.0
    
    # TOI - Turn Over Interval (rata-rata hari kosong tempat tidur)
    # Rumus: ((TT - Hari rawat) x Periode) / Jumlah pasien keluar
    # Asumsi periode = 1 hari
    tt_kosong = max(0, tt - pasien_akhir)
    toi = round(tt_kosong / keluar, 1) if keluar > 0 else 0.0
    
    return {
        "pasien_akhir": pasien_akhir,
        "bor": bor,
        "los": los,
        "bto": bto,
        "toi": toi
    }

@router.post("/", response_model=SensusResponse)
def create_sensus(data: SensusCreate, db: Session = Depends(get_db)):
    """Tambah data sensus harian baru dengan validasi Pydantic"""
    try:
        tgl = date.fromisoformat(data.tanggal)
        
        # Cek duplikat
        exist = db.query(SensusHarian).filter(SensusHarian.tanggal == tgl).first()
        if exist:
            raise HTTPException(status_code=400, detail="Data untuk tanggal ini sudah ada")
        
        # Hitung indikator
        indikator = hitung_indikator(
            data.jml_pasien_awal, 
            data.jml_masuk, 
            data.jml_keluar, 
            data.tempat_tidur_tersedia, 
            data.hari_rawat
        )
        
        sensus = SensusHarian(
            tanggal=tgl,
            jml_pasien_awal=data.jml_pasien_awal,
            jml_masuk=data.jml_masuk,
            jml_keluar=data.jml_keluar,
            jml_pasien_akhir=indikator["pasien_akhir"],
            tempat_tidur_tersedia=data.tempat_tidur_tersedia,
            hari_rawat=data.hari_rawat,  # Simpan hari_rawat untuk LOS
            bor=indikator["bor"],
            los=indikator["los"],
            bto=indikator["bto"],
            toi=indikator["toi"]
        )
        
        db.add(sensus)
        db.commit()
        db.refresh(sensus)
        
        # Log aktivitas
        log_sensus_activity("CREATE", {
            "tanggal": data.tanggal,
            "bor": indikator["bor"],
            "los": indikator["los"]
        })
        
        # Auto re-train model setelah data baru
        try:
            from backend.ml.train import train_arima_and_save
            train_arima_and_save()
            log_sensus_activity("MODEL_RETRAIN", {"status": "success"})
        except Exception as e:
            log_error("MODEL_RETRAIN", str(e))
        
        return sensus
        
    except ValueError as e:
        log_error("CREATE_SENSUS", f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_error("CREATE_SENSUS", f"Database error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Gagal menyimpan data")

@router.get("/", response_model=List[SensusResponse])
def get_sensus(limit: int = 30, db: Session = Depends(get_db)):
    """Ambil data sensus harian (terbaru di atas)"""
    try:
        return db.query(SensusHarian).order_by(
            SensusHarian.tanggal.desc()
        ).limit(limit).all()
    except Exception as e:
        log_error("GET_SENSUS", str(e))
        raise HTTPException(status_code=500, detail="Gagal mengambil data")

@router.get("/{sensus_id}", response_model=SensusResponse)
def get_sensus_by_id(sensus_id: int, db: Session = Depends(get_db)):
    """Ambil data sensus berdasarkan ID"""
    try:
        sensus = db.query(SensusHarian).filter(SensusHarian.id == sensus_id).first()
        if not sensus:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")
        return sensus
    except HTTPException:
        raise
    except Exception as e:
        log_error("GET_SENSUS_BY_ID", str(e))
        raise HTTPException(status_code=500, detail="Gagal mengambil data")

@router.put("/{sensus_id}", response_model=SensusResponse)
def update_sensus(sensus_id: int, data: SensusCreate, db: Session = Depends(get_db)):
    """Update data sensus harian dengan validasi Pydantic"""
    try:
        sensus = db.query(SensusHarian).filter(SensusHarian.id == sensus_id).first()
        if not sensus:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")

        tgl = date.fromisoformat(data.tanggal)
        
        # Cek duplikat tanggal (kecuali data yang sedang diedit)
        exist = db.query(SensusHarian).filter(
            SensusHarian.tanggal == tgl,
            SensusHarian.id != sensus_id
        ).first()
        if exist:
            raise HTTPException(status_code=400, detail="Data untuk tanggal ini sudah ada")

        # Hitung indikator
        indikator = hitung_indikator(
            data.jml_pasien_awal, 
            data.jml_masuk, 
            data.jml_keluar, 
            data.tempat_tidur_tersedia, 
            data.hari_rawat
        )

        # Update data
        sensus.tanggal = tgl
        sensus.jml_pasien_awal = data.jml_pasien_awal
        sensus.jml_masuk = data.jml_masuk
        sensus.jml_keluar = data.jml_keluar
        sensus.jml_pasien_akhir = indikator["pasien_akhir"]
        sensus.tempat_tidur_tersedia = data.tempat_tidur_tersedia
        sensus.bor = indikator["bor"]
        sensus.los = indikator["los"]
        sensus.bto = indikator["bto"]
        sensus.toi = indikator["toi"]

        db.commit()
        db.refresh(sensus)
        
        # Log aktivitas
        log_sensus_activity("UPDATE", {
            "id": sensus_id,
            "tanggal": data.tanggal,
            "bor": indikator["bor"]
        })
        
        return sensus
        
    except ValueError as e:
        log_error("UPDATE_SENSUS", f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_error("UPDATE_SENSUS", f"Database error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Gagal mengupdate data")

@router.delete("/{sensus_id}")
def delete_sensus(sensus_id: int, db: Session = Depends(get_db)):
    """Hapus data sensus dengan error handling"""
    try:
        sensus = db.query(SensusHarian).filter(SensusHarian.id == sensus_id).first()
        if not sensus:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")

        db.delete(sensus)
        db.commit()
        
        # Log aktivitas
        log_sensus_activity("DELETE", {"id": sensus_id, "tanggal": str(sensus.tanggal)})
        
        return {"message": "Data berhasil dihapus"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("DELETE_SENSUS", str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Gagal menghapus data")
@router.get("/stats/summary", response_model=SensusStats)
def get_summary_stats(db: Session = Depends(get_db)):
    """Statistik ringkasan dengan error handling"""
    try:
        data = db.query(SensusHarian).order_by(SensusHarian.tanggal.desc()).all()
        if not data:
            return SensusStats(
                total_records=0,
                avg_bor=0.0,
                avg_los=0.0,
                latest_bor=0.0,
                trend="tidak ada data"
            )
        
        total_records = len(data)
        avg_bor = round(sum(d.bor for d in data) / total_records, 1)
        avg_los = round(sum(d.los for d in data if d.los) / len([d for d in data if d.los]), 1) if any(d.los for d in data) else 0.0
        latest_bor = data[0].bor
        
        # Trend sederhana: bandingkan 3 data terakhir
        trend = "stabil"
        if len(data) >= 3:
            recent_avg = sum(d.bor for d in data[:3]) / 3
            older_avg = sum(d.bor for d in data[-3:]) / 3
            if recent_avg > older_avg + 5:
                trend = "meningkat"
            elif recent_avg < older_avg - 5:
                trend = "menurun"
        
        return SensusStats(
            total_records=total_records,
            avg_bor=avg_bor,
            avg_los=avg_los,
            latest_bor=latest_bor,
            trend=trend
        )
        
    except Exception as e:
        log_error("GET_SUMMARY_STATS", str(e))
        raise HTTPException(status_code=500, detail="Gagal mengambil statistik")