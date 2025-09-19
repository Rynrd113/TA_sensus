# backend/schemas/bangsal.py
"""
Bangsal (Hospital Ward) Schemas
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# Base Bangsal Schemas
class BangsalBase(BaseModel):
    nama_bangsal: str = Field(..., min_length=1, max_length=100, description="Nama bangsal")
    kode_bangsal: str = Field(..., min_length=1, max_length=20, description="Kode unik bangsal")
    kapasitas_total: int = Field(ge=0, description="Total kapasitas tempat tidur")
    jumlah_kamar: int = Field(ge=0, description="Jumlah kamar")
    departemen: Optional[str] = Field(None, max_length=100, description="Departemen/divisi")
    jenis_bangsal: str = Field(..., max_length=50, description="Jenis bangsal (VIP, Kelas I, II, III, ICU)")
    kategori: Optional[str] = Field(None, max_length=50, description="Kategori bangsal")
    lantai: Optional[int] = Field(None, ge=0, description="Nomor lantai")
    gedung: Optional[str] = Field(None, max_length=100, description="Nama gedung")
    lokasi_detail: Optional[str] = Field(None, description="Detail lokasi")
    is_active: bool = Field(True, description="Status aktif bangsal")
    is_emergency_ready: bool = Field(False, description="Siap untuk emergency")
    kepala_bangsal: Optional[str] = Field(None, max_length=100, description="Nama kepala bangsal")
    perawat_jaga: Optional[str] = Field(None, max_length=100, description="Nama perawat jaga")
    dokter_penanggung_jawab: Optional[str] = Field(None, max_length=100, description="Nama dokter penanggung jawab")
    tarif_per_hari: Optional[float] = Field(None, ge=0, description="Tarif per hari")
    fasilitas: Optional[str] = Field(None, description="Fasilitas dalam format JSON")
    keterangan: Optional[str] = Field(None, description="Keterangan tambahan")

    @validator('jenis_bangsal')
    def validate_jenis_bangsal(cls, v):
        allowed_types = ["VIP", "Kelas I", "Kelas II", "Kelas III", "ICU", "NICU", "PICU", "HCU", "Isolasi"]
        if v not in allowed_types:
            return v  # Allow custom types but validate common ones
        return v

class BangsalCreate(BangsalBase):
    """Schema for creating new bangsal"""
    pass

class BangsalUpdate(BaseModel):
    """Schema for updating bangsal (partial update allowed)"""
    nama_bangsal: Optional[str] = Field(None, min_length=1, max_length=100)
    kode_bangsal: Optional[str] = Field(None, min_length=1, max_length=20)
    kapasitas_total: Optional[int] = Field(None, ge=0)
    jumlah_kamar: Optional[int] = Field(None, ge=0)
    tempat_tidur_tersedia: Optional[int] = Field(None, ge=0)
    tempat_tidur_terisi: Optional[int] = Field(None, ge=0)
    departemen: Optional[str] = Field(None, max_length=100)
    jenis_bangsal: Optional[str] = Field(None, max_length=50)
    kategori: Optional[str] = Field(None, max_length=50)
    lantai: Optional[int] = Field(None, ge=0)
    gedung: Optional[str] = Field(None, max_length=100)
    lokasi_detail: Optional[str] = None
    is_active: Optional[bool] = None
    is_emergency_ready: Optional[bool] = None
    kepala_bangsal: Optional[str] = Field(None, max_length=100)
    perawat_jaga: Optional[str] = Field(None, max_length=100)
    dokter_penanggung_jawab: Optional[str] = Field(None, max_length=100)
    tarif_per_hari: Optional[float] = Field(None, ge=0)
    fasilitas: Optional[str] = None
    keterangan: Optional[str] = None

class BangsalResponse(BangsalBase):
    """Schema for bangsal response"""
    id: int
    tempat_tidur_tersedia: int = Field(..., description="Tempat tidur tersedia")
    tempat_tidur_terisi: int = Field(..., description="Tempat tidur terisi")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    occupancy_rate: Optional[float] = Field(None, description="Tingkat okupansi (%)")
    available_beds: Optional[int] = Field(None, description="Jumlah tempat tidur tersedia")

    class Config:
        from_attributes = True

class BangsalList(BaseModel):
    """Schema for bangsal list with pagination"""
    total: int
    page: int
    per_page: int
    pages: int
    bangsal: List[BangsalResponse]

class BangsalSummary(BaseModel):
    """Schema for bangsal summary/dashboard"""
    id: int
    nama_bangsal: str
    kode_bangsal: str
    kapasitas_total: int
    tempat_tidur_tersedia: int
    tempat_tidur_terisi: int
    occupancy_rate: float
    jenis_bangsal: str
    is_active: bool
    is_emergency_ready: bool

# Room Schemas
class KamarBangsalBase(BaseModel):
    nomor_kamar: str = Field(..., min_length=1, max_length=20, description="Nomor kamar")
    nama_kamar: Optional[str] = Field(None, max_length=100, description="Nama kamar")
    kapasitas_kamar: int = Field(1, ge=1, description="Kapasitas kamar")
    jenis_kamar: Optional[str] = Field(None, max_length=50, description="Jenis kamar")
    fasilitas_kamar: Optional[str] = Field(None, description="Fasilitas kamar (JSON)")
    is_active: bool = Field(True, description="Status aktif kamar")
    status_kebersihan: str = Field("Bersih", description="Status kebersihan")

    @validator('status_kebersihan')
    def validate_status_kebersihan(cls, v):
        allowed_status = ["Bersih", "Kotor", "Maintenance"]
        if v not in allowed_status:
            raise ValueError(f"Status kebersihan harus salah satu dari: {', '.join(allowed_status)}")
        return v

class KamarBangsalCreate(KamarBangsalBase):
    bangsal_id: int = Field(..., description="ID bangsal")

class KamarBangsalUpdate(BaseModel):
    nomor_kamar: Optional[str] = Field(None, min_length=1, max_length=20)
    nama_kamar: Optional[str] = Field(None, max_length=100)
    kapasitas_kamar: Optional[int] = Field(None, ge=1)
    tempat_tidur_terisi: Optional[int] = Field(None, ge=0)
    jenis_kamar: Optional[str] = Field(None, max_length=50)
    fasilitas_kamar: Optional[str] = None
    is_active: Optional[bool] = None
    is_maintenance: Optional[bool] = None
    status_kebersihan: Optional[str] = None

class KamarBangsalResponse(KamarBangsalBase):
    id: int
    bangsal_id: int
    tempat_tidur_terisi: int
    is_maintenance: bool
    created_at: datetime
    updated_at: datetime
    is_available: bool = Field(..., description="Apakah kamar tersedia")
    available_beds: int = Field(..., description="Jumlah tempat tidur tersedia")

    class Config:
        from_attributes = True

# Capacity Management
class CapacityUpdate(BaseModel):
    """Schema for updating bed capacity"""
    tempat_tidur_terisi: int = Field(..., ge=0, description="Jumlah tempat tidur terisi")
    
    @validator('tempat_tidur_terisi')
    def validate_terisi(cls, v, values):
        # This validation will be enhanced in the service layer
        if v < 0:
            raise ValueError("Tempat tidur terisi tidak boleh negatif")
        return v

class OccupancyStats(BaseModel):
    """Schema for occupancy statistics"""
    total_bangsal: int
    active_bangsal: int
    total_capacity: int
    total_occupied: int
    total_available: int
    overall_occupancy_rate: float
    emergency_ready_bangsal: int
    
class BangsalFilter(BaseModel):
    """Schema for filtering bangsal"""
    jenis_bangsal: Optional[str] = None
    departemen: Optional[str] = None
    is_active: Optional[bool] = None
    is_emergency_ready: Optional[bool] = None
    lantai: Optional[int] = None
    gedung: Optional[str] = None
    min_available_beds: Optional[int] = None
    max_occupancy_rate: Optional[float] = None