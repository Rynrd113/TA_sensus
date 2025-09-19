# backend/models/bangsal.py
"""
Bangsal (Hospital Ward) Models
SQLAlchemy models for hospital ward and room management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Bangsal(Base):
    __tablename__ = "bangsal"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    nama_bangsal = Column(String(100), nullable=False, index=True)
    kode_bangsal = Column(String(20), unique=True, nullable=False, index=True)
    
    # Capacity Information
    kapasitas_total = Column(Integer, nullable=False, default=0)
    jumlah_kamar = Column(Integer, nullable=False, default=0)
    tempat_tidur_tersedia = Column(Integer, nullable=False, default=0)
    tempat_tidur_terisi = Column(Integer, nullable=False, default=0)
    
    # Department and Classification
    departemen = Column(String(100), nullable=True)  # Internal Medicine, Surgery, etc.
    jenis_bangsal = Column(String(50), nullable=False)  # VIP, Kelas I, II, III, ICU, etc.
    kategori = Column(String(50), nullable=True)  # Rawat Inap, ICU, NICU, etc.
    
    # Location and Physical Details
    lantai = Column(Integer, nullable=True)
    gedung = Column(String(100), nullable=True)
    lokasi_detail = Column(Text, nullable=True)
    
    # Operational Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_emergency_ready = Column(Boolean, default=False)  # For emergency admissions
    
    # Staff Assignment
    kepala_bangsal = Column(String(100), nullable=True)  # Head of Ward
    perawat_jaga = Column(String(100), nullable=True)  # Nurse on duty
    dokter_penanggung_jawab = Column(String(100), nullable=True)  # Responsible doctor
    
    # Financial Information
    tarif_per_hari = Column(Float, nullable=True, default=0.0)  # Daily rate
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, nullable=True)  # User ID who created
    updated_by = Column(Integer, nullable=True)  # User ID who last updated
    
    # Additional Information
    fasilitas = Column(Text, nullable=True)  # JSON string of facilities
    keterangan = Column(Text, nullable=True)  # Additional notes
    
    # Relationships
    kamar_list = relationship("KamarBangsal", back_populates="bangsal", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Bangsal(id={self.id}, nama='{self.nama_bangsal}', kode='{self.kode_bangsal}')>"
    
    def to_dict(self):
        """Convert bangsal to dictionary"""
        return {
            "id": self.id,
            "nama_bangsal": self.nama_bangsal,
            "kode_bangsal": self.kode_bangsal,
            "kapasitas_total": self.kapasitas_total,
            "jumlah_kamar": self.jumlah_kamar,
            "tempat_tidur_tersedia": self.tempat_tidur_tersedia,
            "tempat_tidur_terisi": self.tempat_tidur_terisi,
            "departemen": self.departemen,
            "jenis_bangsal": self.jenis_bangsal,
            "kategori": self.kategori,
            "lantai": self.lantai,
            "gedung": self.gedung,
            "lokasi_detail": self.lokasi_detail,
            "is_active": self.is_active,
            "is_emergency_ready": self.is_emergency_ready,
            "kepala_bangsal": self.kepala_bangsal,
            "perawat_jaga": self.perawat_jaga,
            "dokter_penanggung_jawab": self.dokter_penanggung_jawab,
            "tarif_per_hari": self.tarif_per_hari,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "fasilitas": self.fasilitas,
            "keterangan": self.keterangan
        }
    
    @property
    def occupancy_rate(self) -> float:
        """Calculate current occupancy rate (BOR for this bangsal)"""
        if self.kapasitas_total == 0:
            return 0.0
        return (self.tempat_tidur_terisi / self.kapasitas_total) * 100
    
    @property
    def available_beds(self) -> int:
        """Get number of available beds"""
        return self.tempat_tidur_tersedia
    
    def update_capacity_from_rooms(self):
        """Update total capacity based on rooms"""
        total_capacity = sum(room.kapasitas_kamar for room in self.kamar_list if room.is_active)
        total_occupied = sum(room.tempat_tidur_terisi for room in self.kamar_list if room.is_active)
        
        self.kapasitas_total = total_capacity
        self.tempat_tidur_terisi = total_occupied
        self.tempat_tidur_tersedia = total_capacity - total_occupied
        self.jumlah_kamar = len([room for room in self.kamar_list if room.is_active])

class KamarBangsal(Base):
    __tablename__ = "kamar_bangsal"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    nomor_kamar = Column(String(20), nullable=False, index=True)
    nama_kamar = Column(String(100), nullable=True)
    
    # Capacity
    kapasitas_kamar = Column(Integer, nullable=False, default=1)
    tempat_tidur_terisi = Column(Integer, nullable=False, default=0)
    
    # Room Details
    jenis_kamar = Column(String(50), nullable=True)  # Single, Double, Suite, etc.
    fasilitas_kamar = Column(Text, nullable=True)  # JSON facilities
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_maintenance = Column(Boolean, default=False)
    status_kebersihan = Column(String(20), default="Bersih")  # Bersih, Kotor, Maintenance
    
    # Relationship
    bangsal_id = Column(Integer, ForeignKey("bangsal.id"), nullable=False)
    bangsal = relationship("Bangsal", back_populates="kamar_list")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<KamarBangsal(id={self.id}, nomor='{self.nomor_kamar}', bangsal_id={self.bangsal_id})>"
    
    @property
    def is_available(self) -> bool:
        """Check if room has available beds"""
        return (self.is_active and 
                not self.is_maintenance and 
                self.tempat_tidur_terisi < self.kapasitas_kamar and
                self.status_kebersihan == "Bersih")
    
    @property
    def available_beds(self) -> int:
        """Get number of available beds in this room"""
        if not self.is_available:
            return 0
        return self.kapasitas_kamar - self.tempat_tidur_terisi