# backend/models/sensus.py
from sqlalchemy import Column, Integer, Date, Float
from .base import Base

class SensusHarian(Base):
    __tablename__ = "sensus_harian"

    id = Column(Integer, primary_key=True, index=True)
    tanggal = Column(Date, unique=True, index=True)
    jml_pasien_awal = Column(Integer)
    jml_masuk = Column(Integer)
    jml_keluar = Column(Integer)
    jml_pasien_akhir = Column(Integer)
    tempat_tidur_tersedia = Column(Integer)
    hari_rawat = Column(Integer, default=None)  # Total hari rawat untuk LOS
    bor = Column(Float)  # Bed Occupancy Rate (diisi otomatis)
    los = Column(Float, default=None)   # Length of Stay (bisa null)
    bto = Column(Float, default=None)   # Bed Turnover (bisa null)
    toi = Column(Float, default=None)   # Turn Over Interval (bisa null)